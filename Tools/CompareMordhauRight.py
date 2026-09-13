"""Native-speed, release-aligned comparison. Padding never becomes motion evidence."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import statistics

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Saved/VideoRuntime'))
import imageio_ffmpeg


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference', required=True, type=Path)
    p.add_argument('--candidate', required=True, type=Path)
    p.add_argument('--reference-release', required=True, type=float, help='Seconds from reference first frame')
    p.add_argument('--candidate-release', required=True, type=float, help='Seconds from candidate first frame')
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--panel-width', type=int, default=640)
    p.add_argument('--panel-height', type=int, default=360)
    p.add_argument('--fps', type=int, default=60, help='Presentation cadence only; no speed change')
    p.add_argument('--alignment-label', default='visual onset', help='Observed event used to align clips; do not imply measured release')
    p.add_argument('--reference-source-start', type=float, default=0, help='Original capture time corresponding to excerpt first frame')
    p.add_argument('--candidate-source-start', type=float, default=0)
    p.add_argument('--tooling-smoke', action='store_true', help='Burn in a NOT MOTION EVIDENCE label')
    a = p.parse_args()
    if min(a.panel_width, a.panel_height, a.fps) <= 0 or a.panel_width % 2 or a.panel_height % 2:
        p.error('Panel dimensions must be positive even integers; fps must be positive')
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    sources = [a.reference.resolve(), a.candidate.resolve()]
    if a.output.resolve() in sources:
        p.error('Output must differ from inputs')
    durations = []
    timing = []
    for source in sources:
        if not source.is_file():
            p.error(f'Missing input: {source}')
        # Decode actual presentation timestamps; nominal FPS/frame counts are not a VFR clock.
        meta = subprocess.run([ffmpeg, '-hide_banner', '-i', str(source), '-map', '0:v:0',
                               '-vf', 'showinfo', '-fps_mode', 'passthrough', '-an',
                               '-f', 'null', '-'], capture_output=True, text=True, check=True).stderr
        frames = re.findall(r'\bn:\s*\d+\s+pts:.*?pts_time:([\d.eE+\-]+).*?duration_time:([\d.eE+\-]+)', meta)
        if not frames:
            p.error(f'Cannot decode presentation timestamps: {source}')
        pts = [float(frame[0]) for frame in frames]
        last_duration = float(frames[-1][1])
        inferred = last_duration <= 0
        if inferred:
            deltas = [b-a for a, b in zip(pts, pts[1:]) if b > a]
            if not deltas:
                p.error(f'Final frame duration unavailable: {source}')
            last_duration = statistics.median(deltas)
        duration = pts[-1] - pts[0] + last_duration
        durations.append(duration)
        timing.append({'first_pts': pts[0], 'last_pts': pts[-1], 'last_frame_duration': last_duration,
                       'last_duration_inferred_from_median_delta': inferred, 'decoded_frames': len(pts)})
    releases = [a.reference_release, a.candidate_release]
    if any(not 0 <= onset < duration for onset, duration in zip(releases, durations)):
        p.error('Each release must be within its input duration')
    if not re.fullmatch(r'[A-Za-z0-9 _.-]+', a.alignment_label):
        p.error('Alignment label must use letters, numbers, spaces, underscores, periods or hyphens')
    aligned_release = max(releases)
    leads = [aligned_release - onset for onset in releases]
    total = max(lead + duration for lead, duration in zip(leads, durations))
    font = Path('C:/Windows/Fonts/arial.ttf')
    font_option = "fontfile='" + font.as_posix().replace(':', r'\:') + "':" if font.exists() else ''
    def label(text, y=12, enable=None):
        result = f"drawtext={font_option}text='{text}':x=12:y={y}:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.8"
        return result + (f":enable='{enable}'" if enable else '')
    filters = []
    for i, (lead, duration) in enumerate(zip(leads, durations)):
        role = ['REFERENCE', 'CANDIDATE'][i]
        source_stamp = label('Source %{pts\\:hms\\:' + str([a.reference_source_start, a.candidate_source_start][i]) + '}', 38)
        source_stamp = source_stamp.replace('fontsize=18', f'fontsize=18*w/{a.panel_width}').replace('x=12:y=38', f'x=12*w/{a.panel_width}:y=38*w/{a.panel_width}')
        chain = [f'[{i}:v]setpts=PTS-STARTPTS', source_stamp,
                 f'fps={a.fps}:eof_action=pass',
                 f'scale={a.panel_width}:{a.panel_height}:force_original_aspect_ratio=decrease',
                 f'pad={a.panel_width}:{a.panel_height}:(ow-iw)/2:(oh-ih)/2:color=black', 'setsar=1',
                 f'tpad=start_mode=add:start_duration={lead:.6f}:stop_mode=add:stop_duration={total-lead-duration+2/a.fps:.6f}:color=black',
                 label(role),
                 label('Aligned by ' + a.alignment_label, a.panel_height-56),
                 label('NO SOURCE - alignment lead', 68, f'lt(t,{lead:.6f})'),
                 label('NO SOURCE - clip ended', 68, f'gte(t,{lead+duration:.6f})'),
                 'null']
        if a.tooling_smoke:
            chain.append(label('TOOLING SMOKE - NOT MOTION EVIDENCE', a.panel_height-30))
        filters.append(','.join(chain) + f'[v{i}]')
    filters.append('[v0][v1]hstack=inputs=2:shortest=0[out]')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y']
    for source in sources:
        command += ['-i', str(source)]
    command += ['-filter_complex', ';'.join(filters), '-map', '[out]', '-an', '-t', str(total),
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(a.output)]
    subprocess.run(command, check=True)
    receipt = {'status': 'tooling smoke only' if a.tooling_smoke else 'comparison render; perceptual review pending',
               'sources': [str(s) for s in sources], 'source_durations_seconds': durations,
               'alignment_label': a.alignment_label, 'source_alignment_seconds': releases, 'decoded_timing': timing,
               'source_label_offsets': [a.reference_source_start, a.candidate_source_start], 'lead_padding_seconds': leads,
               'aligned_event_seconds': aligned_release, 'planned_duration_seconds': total,
               'speed_multiplier': [1, 1], 'presentation_fps': a.fps,
               'note': 'Source stamps use the supplied source offsets from each first frame. Black lead/tail is not source footage. Audio omitted.'}
    a.output.with_suffix('.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()




