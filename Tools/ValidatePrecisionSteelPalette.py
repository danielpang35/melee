"""Independently validate the delivered Precision Steel combat WAV palette.

Only reads audio/build manifests and writes QC/validation.json and QC/summary.md.
No audition is implied: checks are numerical, including EBU R128 repeated-cue
measurements, PCM24 layer reconstruction, and timing/spectral diagnostics.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Saved/ArtRuntime"))
import numpy as np

RATE = 48000
PCM24_SCALE = 8388608
EVENTS = ("Swing", "Parry", "Chamber", "Hit", "Headshot")
DEFAULT_PALETTE = ROOT / "ArtSource/CombatAudio/Palettes/PrecisionSteel_v5"
DEFAULT_FFMPEG = ROOT / "Saved/VideoRuntime/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"


def db(value: float) -> float:
    return float(20 * np.log10(max(float(value), 1e-15)))


def finite(value: float):
    return float(value) if math.isfinite(value) else None


def read_pcm_wave(path: Path):
    """Decode PCM16/24/32 RIFF or PCM WAVE_FORMAT_EXTENSIBLE without conversion."""
    raw = path.read_bytes()
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ValueError("File is not a RIFF/WAVE container")
    fmt = None
    data = None
    offset = 12
    while offset + 8 <= len(raw):
        chunk_id, size = struct.unpack_from("<4sI", raw, offset)
        payload = raw[offset + 8:offset + 8 + size]
        if len(payload) != size:
            raise ValueError("Truncated RIFF chunk")
        if chunk_id == b"fmt ":
            fmt = payload
        elif chunk_id == b"data":
            data = payload
        offset += 8 + size + size % 2
    if fmt is None or data is None or len(fmt) < 16:
        raise ValueError("Missing or invalid fmt/data chunk")
    tag, channels, rate, byte_rate, block_align, bits = struct.unpack_from("<HHIIHH", fmt)
    valid_bits = bits
    if tag == 65534:
        if len(fmt) < 40:
            raise ValueError("Invalid WAVE_FORMAT_EXTENSIBLE format")
        valid_bits = struct.unpack_from("<H", fmt, 18)[0]
        if fmt[24:40] != bytes.fromhex("0100000000001000800000aa00389b71"):
            raise ValueError("WAVE_FORMAT_EXTENSIBLE audio is not integer PCM")
    elif tag != 1:
        raise ValueError("WAV format is not integer PCM")
    if not channels or bits not in (16, 24, 32):
        raise ValueError("Unsupported PCM format")
    if block_align != channels * bits // 8 or byte_rate != rate * block_align:
        raise ValueError("Inconsistent PCM format byte rate/block alignment")
    if len(data) % block_align:
        raise ValueError("Incomplete PCM frame")
    if bits == 24:
        packed = np.frombuffer(data, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        pcm = packed[:, 0] | packed[:, 1] << 8 | packed[:, 2] << 16
        pcm = np.where(pcm & 0x800000, pcm - 0x1000000, pcm).astype(np.int64)
    else:
        pcm = np.frombuffer(data, dtype="<i2" if bits == 16 else "<i4").astype(np.int64)
    pcm = pcm.reshape(-1, channels)
    scale = float(1 << (bits - 1))
    metadata = {"sample_rate": rate, "channels": channels, "bits_per_sample": bits,
                "valid_bits_per_sample": valid_bits, "frames": len(pcm),
                "sha256": hashlib.sha256(raw).hexdigest()}
    return pcm, pcm.astype(np.float64) / scale, metadata


def measure_loudness(audio, rate, ffmpeg: Path, repeat=False):
    if repeat:
        spacing = round(0.6 * rate)
        train = np.zeros((max(6 * spacing, 5 * spacing + len(audio)), audio.shape[1]))
        for index in range(6):
            train[index * spacing:index * spacing + len(audio)] += audio
        audio = train
    process = subprocess.run(
        [str(ffmpeg), "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(rate),
         "-ac", str(audio.shape[1]), "-i", "pipe:0", "-af",
         "loudnorm=I=-20:TP=-3.5:LRA=7:print_format=json", "-f", "null", "-"],
        input=audio.astype("<f4").tobytes(), capture_output=True, check=True)
    log = process.stderr.decode("utf-8", errors="replace")
    found = re.search(r'\{[^{}]*"input_i"[^{}]*\}', log)
    if found is None:
        raise RuntimeError("FFmpeg did not produce loudnorm measurement JSON")
    result = json.loads(found.group())
    return {"lufs": finite(float(result["input_i"])),
            "true_peak_dbtp": finite(float(result["input_tp"])),
            "lra_lu": finite(float(result["input_lra"]))}


def spectral_energy(audio, rate):
    mono = audio[:, 0] if audio.shape[1] == 1 else np.mean(audio, axis=1)
    spectrum = np.abs(np.fft.rfft(mono)) ** 2
    weights = np.ones_like(spectrum) * 2
    weights[0] = 1
    if len(mono) % 2 == 0:
        weights[-1] = 1
    energy = spectrum * weights / (len(mono) * rate)
    frequencies = np.fft.rfftfreq(len(mono), 1 / rate)
    total = max(float(np.sum(energy)), 1e-30)
    bands = {}
    for name, lo, hi in (("sub_20_80", 20, 80), ("body_80_350", 80, 350),
                         ("mid_350_2000", 350, 2000), ("presence_2000_6000", 2000, 6000),
                         ("top_6000_12000", 6000, 12000), ("ultrahigh_12000_24000", 12000, 24001)):
        power = float(np.sum(energy[(frequencies >= lo) & (frequencies < hi)]))
        bands[name] = {"energy_dbfs_seconds": 10 * math.log10(max(power, 1e-30)),
                       "percent_total_energy": 100 * power / total}
    return bands


def timing_metrics(audio, rate):
    magnitude = np.max(np.abs(audio), axis=1)
    peak = float(np.max(magnitude))
    relative_active = np.flatnonzero(magnitude >= max(peak * 0.01, 1 / PCM24_SCALE))
    audible = np.flatnonzero(magnitude >= 10 ** (-70 / 20))
    squares = np.sum(audio ** 2, axis=1)
    energy = float(np.sum(squares))
    cumulative = np.cumsum(squares)
    e99 = np.searchsorted(cumulative, energy * .99) if energy > 0 else 0
    final = max(1, round(.02 * rate))
    window = max(1, round(.003 * rate))
    moving = np.convolve(squares, np.ones(window) / window, mode="same")
    return {"first_above_minus70_dbfs_ms": float(audible[0] * 1000 / rate) if len(audible) else None,
            "onset_above_minus40_db_relative_ms": float(relative_active[0] * 1000 / rate) if len(relative_active) else None,
            "last_above_minus40_db_relative_ms": float(relative_active[-1] * 1000 / rate) if len(relative_active) else None,
            "sample_peak_time_ms": float(np.argmax(magnitude) * 1000 / rate),
            "rms_3ms_peak_time_ms": float(np.argmax(moving) * 1000 / rate),
            "energy_99_percent_time_ms": float(e99 * 1000 / rate),
            "final_20ms_energy_percent": 100 * float(np.sum(squares[-final:])) / max(energy, 1e-30),
            "final_sample_step_dbfs": db(np.max(np.abs(audio[-1] - audio[-2]))) if len(audio) > 1 else None}


def analyze_file(path: Path, relative: str, role: str, event: str | None, ffmpeg: Path):
    pcm, audio, record = read_pcm_wave(path)
    if not len(audio):
        raise ValueError("Empty WAV")
    record.update({"file": relative, "role": role, "event": event,
                   "duration_seconds": len(audio) / record["sample_rate"],
                   "sample_peak_dbfs": db(np.max(np.abs(audio))),
                   "dc_offset_dbfs": db(np.max(np.abs(np.mean(audio, axis=0)))),
                   "first_frame_pcm": pcm[0].tolist(), "last_frame_pcm": pcm[-1].tolist(),
                   "clipped_sample_count": int(np.count_nonzero((pcm >= (1 << (record["bits_per_sample"] - 1)) - 1)
                                                                | (pcm <= -(1 << (record["bits_per_sample"] - 1)))))})
    record["measurement"] = measure_loudness(audio, record["sample_rate"], ffmpeg, repeat=role != "demo")
    record["timing"] = timing_metrics(audio, record["sample_rate"])
    record["spectrum"] = spectral_energy(audio, record["sample_rate"])
    if role == "cue" and event == "Chamber":
        levels = {}
        for name, begin, end in (("early_rasp_10_50ms", .010, .050),
                                 ("late_rasp_70_115ms", .070, .115),
                                 ("release_120_150ms", .120, .150)):
            section = audio[round(begin * record["sample_rate"]):round(end * record["sample_rate"])]
            levels[name] = db(np.sqrt(np.mean(section ** 2))) if len(section) else None
        record["chamber_window_rms_dbfs"] = levels
    return record, pcm, audio


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--palette", type=Path, default=DEFAULT_PALETTE)
    parser.add_argument("--ffmpeg", type=Path, default=DEFAULT_FFMPEG)
    args = parser.parse_args()
    palette = args.palette.resolve()
    if not palette.is_dir():
        parser.error(f"Palette does not exist: {palette}")
    if not args.ffmpeg.is_file():
        parser.error(f"FFmpeg does not exist: {args.ffmpeg}")
    expected = [(f"Cues/{event}/PS_{event}_{i:02d}.wav", "cue", event)
                for event in EVENTS for i in range(1, 6)]
    expected += [(f"Layers/PS_Headshot_{layer}_{i:02d}.wav", "layer", "Headshot")
                 for layer in ("Base", "Ping") for i in range(1, 6)]
    expected += [(f"Demo/{name}.wav", "demo", None)
                 for name in ("rapid_exchange", "dense_mono_stress")]
    expected += [(f"Demo/{name}.wav", "demo", None)
                 for name in ("palette_audition", *(event.lower() + "_variations" for event in EVENTS))
                 if (palette / f"Demo/{name}.wav").is_file()]
    report = {"palette": palette.name, "validated_utc": datetime.now(timezone.utc).isoformat(),
              "method": {"auditory_listening_performed": False,
                         "loudness": "FFmpeg loudnorm input_i; mono cues/layers repeated six times at 0.6-second starts in a 3.6-second train",
                         "true_peak": "FFmpeg loudnorm input_tp, dynamic mode, 192 kHz internal true-peak analysis",
                         "low_band_weight": "Unwindowed Parseval energy over 80–350 Hz, absolute energy, paired Hit versus Headshot",
                         "timing": "Onset at -40 dB relative to each file peak (6 ms limit, Swing 15 ms); -70 dBFS diagnostic onset; 3 ms RMS envelope peak; 99% energy time",
                         "layer_null": "Integer PCM summation, Base plus Ping minus matching Headshot premix, no gain or offset",
                         "max_cue_true_peak_dbtp": -3.4, "max_demo_true_peak_dbtp": -3.0,
                         "max_within_family_lufs_spread_db": .8, "max_all_cue_lufs_spread_db": 1.5,
                         "max_pair_headshot_hit_delta_db": .6,
                         "max_paired_body_energy_delta_db": 1.5},
              "files": [], "family_loudness": {}, "layer_reconstruction": [],
              "headshot_hit_comparison": [], "variation_similarity": {}, "failures": [], "concerns": []}
    failures, concerns = report["failures"], report["concerns"]
    expected_audio = {relative for relative, _, _ in expected}
    for folder, count in (("Cues", 25), ("Layers", 10), ("Demo", len(expected) - 35)):
        actual = list((palette / folder).rglob("*.wav"))
        if len(actual) != count:
            failures.append(f"{folder}: expected {count} WAV files, found {len(actual)}")
        for path in actual:
            relative = path.relative_to(palette).as_posix()
            if relative not in expected_audio:
                failures.append(f"Unexpected WAV: {relative}")
    valid = []
    for relative, role, event in expected:
        if not (palette / relative).is_file():
            failures.append(f"Missing WAV: {relative}")
        else:
            valid.append((relative, role, event))
    cache = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        jobs = [(relative, executor.submit(analyze_file, palette / relative, relative, role, event, args.ffmpeg))
                for relative, role, event in valid]
        for relative, job in jobs:
            try:
                record, pcm, audio = job.result()
            except Exception as exc:
                failures.append(f"{relative}: analysis failed: {exc}")
                continue
            cache[relative] = (record, pcm, audio)
            report["files"].append(record)
            role, event = record["role"], record["event"]
            if record["sample_rate"] != RATE or record["bits_per_sample"] != 24 or record["valid_bits_per_sample"] != 24:
                failures.append(f"{relative}: requires 48000 Hz, 24-bit integer PCM")
            if role != "demo" and record["channels"] != 1:
                failures.append(f"{relative}: cue/layer requires mono")
            if relative == "Demo/dense_mono_stress.wav" and record["channels"] != 1:
                failures.append(f"{relative}: dense mono stress test requires mono")
            if any(record["first_frame_pcm"]) or any(record["last_frame_pcm"]):
                failures.append(f"{relative}: endpoints are not exactly digital zero")
            if record["clipped_sample_count"]:
                failures.append(f"{relative}: clipped samples")
            true_peak = record["measurement"]["true_peak_dbtp"]
            ceiling = -3.0 if role == "demo" else -3.4
            if true_peak is None or true_peak > ceiling + 1e-6:
                failures.append(f"{relative}: true peak {true_peak} dBTP exceeds {ceiling} dBTP")
            if record["measurement"]["lufs"] is None:
                failures.append(f"{relative}: no measurable integrated loudness")
            if role == "demo":
                continue
            timing = record["timing"]
            onset = timing["onset_above_minus40_db_relative_ms"]
            onset_limit = 15 if event == "Swing" else 6
            if onset is None or onset > onset_limit:
                failures.append(f"{relative}: onset at -40 dB relative peak {onset} ms exceeds {onset_limit} ms")
            if record["duration_seconds"] > .5:
                failures.append(f"{relative}: duration exceeds 500 ms compact-tail bound")
            if timing["final_sample_step_dbfs"] is not None and timing["final_sample_step_dbfs"] > -70:
                concerns.append(f"{relative}: final sample step exceeds -70 dBFS; review ending for truncation")
            if role == "cue":
                peak_ms = timing["rms_3ms_peak_time_ms"]
                bounds = {"Swing": (15, 250), "Chamber": (55, 200),
                          "Parry": (0, 50), "Hit": (0, 50), "Headshot": (0, 50)}[event]
                if not bounds[0] <= peak_ms <= bounds[1]:
                    concerns.append(f"{relative}: 3 ms RMS peak {peak_ms:.1f} ms outside expected {bounds[0]}–{bounds[1]} ms envelope")
                if timing["final_20ms_energy_percent"] > .5:
                    concerns.append(f"{relative}: final 20 ms contains >0.5% energy; review tail compactness")
                if record["spectrum"]["sub_20_80"]["percent_total_energy"] > 20:
                    concerns.append(f"{relative}: >20% spectral energy in 20–80 Hz; review low-frequency rumble")
                top = record["spectrum"]["top_6000_12000"]["percent_total_energy"]
                if top > 35:
                    concerns.append(f"{relative}: >35% energy in 6–12 kHz; review potential upper-frequency fatigue")
                if record["dc_offset_dbfs"] > -50:
                    concerns.append(f"{relative}: DC offset exceeds -50 dBFS")

    all_lufs = []
    for event in EVENTS:
        members = [r for r in report["files"] if r["role"] == "cue" and r["event"] == event]
        levels = [r["measurement"]["lufs"] for r in members if r["measurement"]["lufs"] is not None]
        if levels:
            spread = max(levels) - min(levels)
            report["family_loudness"][event] = {"minimum_lufs": min(levels), "maximum_lufs": max(levels),
                                                 "mean_lufs": float(np.mean(levels)), "spread_db": spread}
            all_lufs.extend(levels)
            if spread > .8 + 1e-6:
                failures.append(f"{event}: within-family loudness spread {spread:.2f} dB exceeds 0.8 dB")
        hashes = [r["sha256"] for r in members]
        if len(hashes) != len(set(hashes)):
            failures.append(f"{event}: duplicate WAV hashes among variants")
        comparisons = []
        for i, first in enumerate(members):
            for second in members[i + 1:]:
                a = cache[first["file"]][2][:, 0]
                b = cache[second["file"]][2][:, 0]
                length = max(len(a), len(b))
                a = np.pad(a, (0, length - len(a)))
                b = np.pad(b, (0, length - len(b)))
                similarity = float(np.dot(a, b) / max(np.linalg.norm(a) * np.linalg.norm(b), 1e-30))
                comparisons.append({"first": first["file"], "second": second["file"],
                                    "normalized_waveform_correlation": similarity})
                if abs(similarity) > .999999:
                    failures.append(f"{event}: variants {Path(first['file']).stem}/{Path(second['file']).stem} have effectively identical waveforms")
        report["variation_similarity"][event] = comparisons
    if all_lufs:
        spread = max(all_lufs) - min(all_lufs)
        report["all_cue_loudness_spread_db"] = spread
        if spread > 1.5 + 1e-6:
            failures.append(f"All cues: loudness spread {spread:.2f} dB exceeds 1.5 dB")

    for i in range(1, 6):
        base_name = f"Layers/PS_Headshot_Base_{i:02d}.wav"
        ping_name = f"Layers/PS_Headshot_Ping_{i:02d}.wav"
        head_name = f"Cues/Headshot/PS_Headshot_{i:02d}.wav"
        hit_name = f"Cues/Hit/PS_Hit_{i:02d}.wav"
        if all(name in cache for name in (base_name, ping_name, head_name)):
            base, ping, head = [cache[name][1] for name in (base_name, ping_name, head_name)]
            if base.shape != ping.shape or base.shape != head.shape:
                failures.append(f"Headshot {i:02d}: layer/premix frame counts do not match")
            else:
                residual = base + ping - head
                peak_lsb = int(np.max(np.abs(residual)))
                rms_lsb = float(np.sqrt(np.mean(residual.astype(float) ** 2)))
                report["layer_reconstruction"].append({"variant": i, "maximum_error_pcm24_lsb": peak_lsb,
                                                       "rms_error_pcm24_lsb": rms_lsb,
                                                       "maximum_error_dbfs": db(peak_lsb / PCM24_SCALE)})
                if peak_lsb > 3:
                    failures.append(f"Headshot {i:02d}: layer sum null residual {peak_lsb} LSB exceeds 3 LSB")
        if all(name in cache for name in (hit_name, head_name)):
            hit, head = cache[hit_name][0], cache[head_name][0]
            hit_lufs, head_lufs = hit["measurement"]["lufs"], head["measurement"]["lufs"]
            if hit_lufs is not None and head_lufs is not None:
                loudness_delta = head_lufs - hit_lufs
                body_delta = head["spectrum"]["body_80_350"]["energy_dbfs_seconds"] - hit["spectrum"]["body_80_350"]["energy_dbfs_seconds"]
                report["headshot_hit_comparison"].append({"variant": i, "headshot_minus_hit_lufs": loudness_delta,
                                                          "headshot_minus_hit_body_energy_db": body_delta})
                if abs(loudness_delta) > .6 + 1e-6:
                    failures.append(f"Headshot {i:02d}: Hit loudness difference {loudness_delta:+.2f} LU exceeds +/-0.6 LU")
                if abs(body_delta) > 1.5 + 1e-6:
                    failures.append(f"Headshot {i:02d}: Hit 80–350 Hz body difference {body_delta:+.2f} dB exceeds +/-1.5 dB")

    manifest_path = palette / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            checked_hashes = 0
            for entry in manifest.get("sounds", []):
                name, expected_hash = entry.get("path"), entry.get("sha256")
                if name in cache and expected_hash:
                    checked_hashes += 1
                    if cache[name][0]["sha256"] != expected_hash:
                        failures.append(f"{name}: WAV hash does not match render manifest")
            report["manifest_consistency"] = {"checked_audio_hashes": checked_hashes,
                                               "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest()}
        except (ValueError, TypeError, AttributeError) as exc:
            failures.append(f"Cannot validate render manifest: {exc}")
    report["status"] = "PASS" if not failures else "FAIL"
    output = palette / "QC"
    output.mkdir(parents=True, exist_ok=True)
    (output / "validation.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = [f"# Precision Steel technical validation — {report['status']}", "",
             f"Checked {len(report['files'])} WAV files: 25 cues, 10 headshot layers, and {len(expected) - 35} demos expected.", "",
             "Numerical validation only; this report does not claim a listening review.", "",
             "| Event | Repeated-cue LUFS range | Spread |", "|---|---:|---:|"]
    for event, levels in report["family_loudness"].items():
        lines.append(f"| {event} | {levels['minimum_lufs']:.2f} to {levels['maximum_lufs']:.2f} | {levels['spread_db']:.2f} dB |")
    if all_lufs:
        lines += ["", f"All-cue loudness spread: {report['all_cue_loudness_spread_db']:.2f} dB (limit 1.50 dB; intentional Swing/Chamber hierarchy)."]
    cue_peaks = [item["measurement"]["true_peak_dbtp"] for item in report["files"]
                 if item["role"] != "demo" and item["measurement"]["true_peak_dbtp"] is not None]
    if cue_peaks:
        lines += ["", f"Maximum cue/layer true peak: {max(cue_peaks):.2f} dBTP (limit -3.40 dBTP)."]
    cue_onsets = [item["timing"]["onset_above_minus40_db_relative_ms"] for item in report["files"]
                  if item["role"] == "cue" and item["timing"]["onset_above_minus40_db_relative_ms"] is not None]
    if cue_onsets:
        lines += ["", f"Cue onset at -40 dB relative to each file peak: {min(cue_onsets):.2f}–{max(cue_onsets):.2f} ms "
                       "(limit 6 ms; Swing 15 ms)."]
    if report["layer_reconstruction"]:
        worst = max(item["maximum_error_pcm24_lsb"] for item in report["layer_reconstruction"])
        lines += ["", f"Worst Headshot Base + Ping reconstruction error: {worst} PCM24 LSB (limit 3)."]
    if report["headshot_hit_comparison"]:
        loud = max(abs(item["headshot_minus_hit_lufs"]) for item in report["headshot_hit_comparison"])
        body = max(abs(item["headshot_minus_hit_body_energy_db"]) for item in report["headshot_hit_comparison"])
        lines += ["", f"Largest paired Headshot/Hit level difference: {loud:.2f} LU; 80–350 Hz body difference: {body:.2f} dB."]
    demos = [item for item in report["files"] if item["role"] == "demo"]
    if demos:
        lines += ["", "| Demo | True peak | Integrated loudness |", "|---|---:|---:|"]
        for item in demos:
            lines.append(f"| {Path(item['file']).name} | {item['measurement']['true_peak_dbtp']} dBTP | {item['measurement']['lufs']} LUFS |")
    lines += ["", "## Failures", ""] + ([f"- {item}" for item in failures] or ["None."])
    lines += ["", "## Review concerns", ""] + ([f"- {item}" for item in concerns] or ["No numerical timing, spectral, or ending concerns triggered."])
    lines += ["", "Measurements use FFmpeg loudnorm input statistics (six starts, 0.6 seconds apart). "
              "True peak uses its internal 192 kHz analysis. Timing and spectral checks are descriptive "
              "proxies; they cannot establish perceptual separation, tactile quality, or absence of fatigue. "
              "Engine spatialization, compression, gameplay gain, and final bus processing require in-engine review.", ""]
    (output / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"{report['status']}: {len(report['files'])} files, {len(failures)} failures, {len(concerns)} review concerns")
    print(output / "summary.md")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
