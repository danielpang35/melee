"""Rebuild the edited/layered CC0 combat bank and its level-matched audition.

Requires NumPy and FFmpeg; py7zr is only needed if the towel originals have
not been extracted. All inputs are archived locally; no network at build time.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Saved/ArtRuntime'))
import numpy as np

RATE = 48000
SOURCES = {
    'swish': ('artisticdude_swishes.zip', 'artisticdude', 'https://opengameart.org/content/swishes-sound-pack'),
    'foley': ('artisticdude_rpg.zip', 'artisticdude', 'https://opengameart.org/content/rpg-sound-pack'),
    'wet': ('qubodup_wet_towel.7z', 'Iwan "qubodup" Gabovitch', 'https://opengameart.org/content/40-wet-towel-clubpoundhitattack-sounds'),
    'rpg': ('kenney_rpg-audio.zip', 'Kenney', 'https://kenney.nl/assets/rpg-audio'),
    'impact': ('kenney_impact-sounds.zip', 'Kenney', 'https://kenney.nl/assets/impact-sounds'),
    'weapons1': ('medieval_sfx_weapon_on_weapon_1_of_2.7z', 'Ben Jaszczak & Brian Nelson / Still North Media', 'https://opengameart.org/content/medieval-sound-effects-weapon-impacts'),
    'weapons2': ('medieval_sfx_weapon_on_weapon_2_of_2.7z', 'Ben Jaszczak & Brian Nelson / Still North Media', 'https://opengameart.org/content/medieval-sound-effects-weapon-impacts'),
}


def save_wave(path, signal):
    path.parent.mkdir(parents=True, exist_ok=True)
    assert np.max(np.abs(signal)) < 1, f'Clipping: {path}'
    with wave.open(str(path), 'wb') as out:
        out.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        out.writeframes(np.round(signal * 32767).astype('<i2').tobytes())


def fade(x, attack=.002, release=.025):
    x = x.copy()
    a, r = min(len(x), round(attack * RATE)), min(len(x), round(release * RATE))
    if a: x[:a] *= np.linspace(0, 1, a)
    if r: x[-r:] *= np.linspace(1, 0, r)
    return x


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archives', type=Path, default=ROOT / 'ArtSource/CombatAudio/Archives')
    parser.add_argument('--ffmpeg', type=Path, required=True)
    args = parser.parse_args()
    source = ROOT / 'ArtSource/CombatAudio'
    output = source / 'Export'
    preview = ROOT / 'Docs/Audio/Revision4'
    packs = {k: zipfile.ZipFile(args.archives / v[0]) for k, v in SOURCES.items() if v[0].endswith('.zip')}
    towel_dir = source / 'Originals/qubodup'
    if not (towel_dir / 'wet_towel_on_body/wet_towel_on_body-01.flac').exists():
        import py7zr
        with py7zr.SevenZipFile(args.archives / SOURCES['wet'][0]) as archive:
            archive.extractall(towel_dir)
    for key, example in [('weapons1','Norse Sword Katana Blade on Blade.wav'),('weapons2','Seax Norse Sword Blade on Blade.wav')]:
        if not (source / 'Originals/stillnorth' / example).exists():
            import py7zr
            with py7zr.SevenZipFile(args.archives / SOURCES[key][0]) as archive:
                archive.extractall(source / 'Originals/stillnorth')
    manifest = {'revision': 4, 'sample_rate': RATE, 'license': 'CC0-1.0',
        'mastering': {'method': 'Four repetitions at 0.8 s spacing, FFmpeg EBU R128 integrated measurement',
                      'true_peak_ceiling_dbtp': -3.5, 'runtime_gain': .68},
        'sources': [{'key': k, 'archive': v[0], 'author': v[1], 'url': v[2],
            'archive_sha256': hashlib.sha256((args.archives / v[0]).read_bytes()).hexdigest()}
            for k, v in SOURCES.items()], 'sounds': []}
    cache, rendered = {}, {}

    def layer(pack, name, *, pitch=1., stretch=1., band=(80, 12000), gain=1., delay=0., length=.4, decay=0., attack=.0015, peak_start=False, offset=0., source_length=1., role=''):
        key = (pack, name, pitch, stretch, band, peak_start, offset, source_length)
        if key not in cache:
            if pack == 'wet':
                raw = (towel_dir / 'wet_towel_on_body' / name).read_bytes()
            elif pack.startswith('weapons'):
                raw = (source / 'Originals/stillnorth' / name).read_bytes()
            else:
                member = next(n for n in packs[pack].namelist() if Path(n).name == name and '__MACOSX' not in n)
                raw = packs[pack].read(member)
                original = source / 'Originals' / pack / name
                original.parent.mkdir(parents=True, exist_ok=True)
                original.write_bytes(raw)
            filters = f'aresample={RATE},asetrate={round(RATE*pitch)},aresample={RATE},atempo={1/stretch},highpass=f={band[0]}:p=2,lowpass=f={band[1]}:p=2'
            if pack.startswith('weapons'):
                filters=f'atrim=start={offset}:duration={source_length},asetpts=PTS-STARTPTS,'+filters
            result = subprocess.run([str(args.ffmpeg), '-v', 'error', '-i', 'pipe:0',
                '-af', filters, '-ac', '1', '-ar', str(RATE), '-f', 'f32le', 'pipe:1'],
                input=raw, capture_output=True, check=True)
            x = np.frombuffer(result.stdout, dtype='<f4').astype(np.float64)
            rms = np.sqrt(np.convolve(x*x, np.ones(240)/240, mode='same'))
            active = np.flatnonzero(rms > np.max(rms)*.035)
            if not len(active): raise ValueError(f'Silent source: {name}')
            start = max(0, int(np.argmax(rms))-192) if peak_start else max(0, active[0]-96)
            x = x[start:min(len(x), active[-1]+960)]
            rms_peak = np.sqrt(np.max(np.convolve(x*x, np.ones(480)/480, mode='same')))
            cache[key] = x * (.20 / max(rms_peak, 1e-6))
        x = cache[key][:round(length*RATE)].copy()
        if decay: x *= np.exp(-np.arange(len(x))/RATE/decay)
        x = fade(x, attack, min(.035, length*.2))*gain
        info = {'pack': pack, 'file': name, 'pitch': pitch, 'stretch': stretch,
            'band_hz': band, 'gain': gain, 'delay_seconds': delay,
            'length_seconds': length, 'decay_seconds': decay, 'attack_seconds': attack,
            'peak_start': peak_start, 'source_offset_seconds':offset,
            'source_window_seconds':source_length if pack.startswith('weapons') else None, 'role': role}
        return x, info

    def air(seed, *, length=.5, band=(180,6000), peak=.16, rise=.065, tail=.12, gain=.7, delay=0., role=''):
        # Original, non-tonal turbulence. Smooth spectral skirts avoid a
        # resonant whistle; independent bands breathe through the passage.
        rng = np.random.default_rng(seed)
        n = round(length*RATE)
        padding = 4096
        freq = np.fft.rfftfreq(n+2*padding, 1/RATE)
        lo, hi = band
        spectrum = np.fft.rfft(rng.standard_normal(n+2*padding))
        weights = 1/np.sqrt(1+(lo/np.maximum(freq,1))**8)
        weights *= 1/np.sqrt(1+(freq/hi)**8)
        weights *= 1/np.maximum(freq,lo)**.32
        x = np.fft.irfft(spectrum*weights,n+2*padding)[padding:padding+n]
        x *= .16/max(np.sqrt(np.mean(x*x)),1e-6)
        t = np.arange(n)/RATE
        width = np.where(t<peak,rise,tail)
        envelope = np.exp(-.5*((t-peak)/width)**2)
        envelope *= .94+.04*np.sin(t*2*np.pi*17+seed)+.02*np.sin(t*2*np.pi*31)
        x = fade(x*envelope*gain,.012 if rise>.01 else .001,.035)
        return x, {'pack':'original','seed':seed,'band_hz':band,'length_seconds':length,
            'peak_seconds':peak,'rise_seconds':rise,'tail_seconds':tail,
            'gain':gain,'delay_seconds':delay,'role':role}

    def loudness(x, train=True):
        if train:
            padded = np.zeros(round(.8*RATE)); padded[:len(x)] = x
            x = np.tile(padded, 4)
        result = subprocess.run([str(args.ffmpeg), '-hide_banner', '-nostats',
            '-f', 'f32le', '-ar', str(RATE), '-ac', '1', '-i', 'pipe:0',
            '-af', 'loudnorm=I=-20:TP=-3.5:LRA=7:print_format=json', '-f', 'null', '-'],
            input=x.astype('<f4').tobytes(), capture_output=True, check=True)
        data = json.loads(re.search(r'\{[^{}]+"input_i"[^{}]+\}', result.stderr.decode()).group())
        return {'lufs': float(data['input_i']), 'true_peak_dbtp': float(data['input_tp'])}

    def master(signal, target):
        # Limit only overshooting transients, at 4x sample rate. The 1 ms
        # lookahead is compensated; contact onset is not delayed in the file.
        # Re-measure after limiting so sharp head accents stay level with body.
        for _ in range(10):
            measured = loudness(signal)
            difference = target-measured['lufs']
            if abs(difference)<.10 and measured['true_peak_dbtp']<=-3.5:
                return signal
            signal *= 10**(difference/20)
            result = subprocess.run([str(args.ffmpeg), '-v', 'error', '-f', 'f32le',
                '-ar', str(RATE), '-ac', '1', '-i', 'pipe:0', '-af',
                'aresample=192000,alimiter=limit=0.65:attack=1:release=12:level=false:latency=true,aresample=48000',
                '-f', 'f32le', 'pipe:1'], input=signal.astype('<f4').tobytes(), capture_output=True, check=True)
            signal = np.frombuffer(result.stdout, '<f4').astype(np.float64)
        measured = loudness(signal)
        if abs(target-measured['lufs'])>.15 or measured['true_peak_dbtp']>-3.5:
            raise ValueError(f'Master cannot reach loudness/headroom target: {measured}')
        return signal

    def render(family, index, layers, seconds, target=-20.5):
        signal = np.zeros(round(RATE*seconds))
        for data, info in layers:
            start = round(info['delay_seconds']*RATE)
            count = min(len(data), len(signal)-start)
            signal[start:start+count] += data[:count]
        signal = fade(np.tanh(signal*1.35)/1.35, .001, .025)
        # Remove subsonic offset introduced by asymmetric impact transients
        # and saturation before final level setting.
        dc_blocked = subprocess.run([str(args.ffmpeg), '-v', 'error', '-f', 'f32le',
            '-ar', str(RATE), '-ac', '1', '-i', 'pipe:0', '-af', 'highpass=f=30:p=2',
            '-f', 'f32le', 'pipe:1'], input=signal.astype('<f4').tobytes(), capture_output=True, check=True)
        signal = fade(np.frombuffer(dc_blocked.stdout,'<f4').astype(np.float64),.001,.012)
        signal = master(signal, target)
        name = f'S_{family}_{index:02}'
        path = output / (name+'.wav')
        save_wave(path, signal)
        with wave.open(str(path), 'rb') as w: signal = np.frombuffer(w.readframes(w.getnframes()), '<i2')/32768.
        metrics = loudness(signal)
        freqs = np.fft.rfftfreq(len(signal), 1/RATE)
        power = np.abs(np.fft.rfft(signal))**2
        metrics['spectral_centroid_hz'] = round(float(np.sum(freqs*power)/np.sum(power)), 1)
        metrics['energy_90_600_hz_percent'] = round(float(np.sum(power[(freqs>=90)&(freqs<=600)])/np.sum(power)*100), 2)
        manifest['sounds'].append({'name': name, 'seconds': seconds, 'target_train_lufs': target,
            'measured': metrics, 'layers': [info for _, info in layers],
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        rendered[name] = signal
        print(name, metrics, flush=True)

    for i in range(3):
        wet = f'wet_towel_on_body-{(9,17,31)[i]:02}.flac'
        grain = f'swish-{(4,6,8)[i]}.wav'
        seed = 7300+i*100
        # Clean air only: no sword, blade scrape, metal, or impact recordings.
        render('Swing', i, [
            air(seed, band=(95,650), peak=.14, rise=.065, tail=.14, gain=.72, role='full low air pressure'),
            air(seed+1, band=(450,4200), peak=.17, rise=.065, tail=.11, gain=.58, role='broad moving air'),
            air(seed+2, band=(2300,10000), peak=.18, rise=.045, tail=.075, gain=.20, role='clean fast air edge'),
            layer('swish',grain,pitch=.55+i*.02,stretch=1.35,band=(240,4600),gain=.22,delay=.035,length=.33,attack=.03,role='recorded nonmetallic wood/hanger swish')], .54, -22)
        render('Stab', i, [
            air(seed+3,length=.31,band=(120,1400),peak=.095,rise=.035,tail=.075,gain=.65,role='thrust pressure'),
            air(seed+4,length=.31,band=(1100,7800),peak=.105,rise=.035,tail=.065,gain=.40,role='focused clean thrust air'),
            layer('swish',grain,pitch=.85,band=(400,5000),gain=.2,delay=.018,length=.2,attack=.015,role='nonmetallic passage grain')], .34, -22)
        steel_at=(.21,2.82,4.85)[i]
        mass_at=(.56,2.95,5.28)[i]
        bright_at=(1.21,2.61,4.21)[i]
        slice_at=(.12,1.34,6.01)[i]
        render('Body', i, [
            layer('weapons1','Norse Sword Katana Blade on Blade.wav',offset=steel_at,pitch=.88+i*.025,band=(400,8200),gain=.76,length=.24,decay=.13,peak_start=True,role='real blade-on-blade cutting crack'),
            layer('weapons1','Mace Norse Sword Blade.wav',offset=mass_at,pitch=.70,band=(95,1250),gain=.66,delay=.004,length=.19,decay=.095,peak_start=True,role='dense low steel body'),
            layer('weapons2','Seax Norse Sword Blade on Blade.wav',offset=slice_at,pitch=1.12,stretch=1.15,band=(1700,10800),gain=.43,delay=.013,length=.19,decay=.105,peak_start=True,role='slicing steel follow-through'),
            layer('impact',f'impactPunch_heavy_{i:03}.ogg',pitch=.72,band=(65,450),gain=.60,delay=.008,length=.15,decay=.085,peak_start=True,role='full physical punch'),
            layer('wet',wet,pitch=.95,band=(500,4900),gain=.24,delay=.008,length=.15,decay=.08,peak_start=True,role='restrained organic cutting texture'),
            air(seed+5,length=.23,band=(2300,9200),peak=.033,rise=.014,tail=.052,gain=.14,delay=.01,role='cutting edge texture')], .35, -21.5)
        render('Head', i, [
            layer('weapons1','Sabre Katana Blade on Blade.wav',offset=bright_at,pitch=1.68+i*.035,band=(2600,14500),gain=.84,length=.14,decay=.068,peak_start=True,role='higher piercing steel cut'),
            layer('rpg','metalClick.ogg',pitch=1.8,band=(4300,14500),gain=.36,length=.023,decay=.009,peak_start=True,role='razor-sharp tactile tick'),
            layer('weapons2','Seax Katana Blade on Blade.wav',offset=(.08,1.17,2.92)[i],pitch=1.65,band=(3200,13500),gain=.35,delay=.007,length=.12,decay=.06,peak_start=True,role='bright cutting steel afterbite'),
            layer('wet',wet,pitch=1.65,band=(1800,8800),gain=.23,delay=.006,length=.09,decay=.045,peak_start=True,role='tight slicing texture'),
            layer('impact',f'impactPunch_heavy_{i:03}.ogg',pitch=.96,band=(110,950),gain=.18,delay=.005,length=.10,decay=.055,peak_start=True,role='compact impact weight')], .23, -21.5)
        # Poppy attack with real weapon mass and a controlled metallic bloom.
        render('Parry', i, [
            layer('weapons1','Norse Sword Katana Blade on Blade.wav',offset=steel_at,pitch=.79+i*.025,band=(430,10200),gain=.92,length=.21,decay=.083,peak_start=True,role='decisive weighted steel collision'),
            layer('weapons2','Sabre Norse Sword Hilt on Blade.wav',offset=(.45,1.78,3.45)[i],pitch=.70,band=(110,2100),gain=.70,delay=.004,length=.16,decay=.066,peak_start=True,role='hilt and weapon mass'),
            layer('rpg','metalClick.ogg',pitch=.96,band=(2100,8500),gain=.18,length=.03,decay=.014,peak_start=True,role='precise hard onset'),
            air(seed+7,length=.15,band=(110,750),peak=.012,rise=.005,tail=.034,gain=.48,role='punch beneath steel')], .27, -21.7)
        render('Chamber', i, [
            layer('weapons2','Seax Katana Blade on Blade.wav',offset=(.08,1.17,2.92)[i],pitch=1.07,band=(700,10000),gain=.78,length=.145,decay=.062,peak_start=True,role='short articulated steel catch'),
            layer('weapons1','Mace Norse Sword Blade.wav',offset=mass_at,pitch=.86,band=(150,1450),gain=.48,length=.10,decay=.048,peak_start=True,role='contained catch weight'),
            layer('rpg','metalClick.ogg',pitch=1.15,band=(2600,8700),gain=.20,delay=.012,length=.025,decay=.01,peak_start=True,role='second catching tick')], .21, -22)
        render('Wall', i, [
            layer('impact',f'impactMining_{(i+2)%5:03}.ogg',pitch=.77,band=(160,4800),gain=.75,length=.17,decay=.075,peak_start=True,role='dry surface bite'),
            layer('impact',f'impactMetal_light_{i:03}.ogg',pitch=.8,band=(1200,6500),gain=.18,length=.055,decay=.02,peak_start=True,role='damped edge contact'),
            air(seed+10,length=.15,band=(120,820),peak=.012,rise=.005,tail=.035,gain=.46,role='solid stopped weight')], .23, -22)
        render('Armor', i, [
            layer('foley',f'chainmail{1+i%2}.wav',pitch=.83+i*.045,band=(650,4600),gain=.28,length=.17,attack=.014,role='quiet interlocking links'),
            layer('foley','armor-light.wav',pitch=.78+i*.04,band=(300,3300),gain=.23,delay=.027,length=.15,attack=.016,role='small overlapping plate movement'),
            layer('foley','cloth-heavy.wav',pitch=.85+i*.025,band=(140,2600),gain=.5,length=.20,attack=.018,role='padded fabric movement'),
            layer('rpg','beltHandle1.ogg' if i%2==0 else 'beltHandle2.ogg',pitch=.9,band=(250,2500),gain=.15,delay=.013,length=.16,attack=.012,role='leather fastening')], .23, -34.5)

    # Actual masters at runtime gain. Every whoosh continues untouched through
    # contact; armor remains at its quiet in-game level, including solo examples.
    timeline = []
    audition = np.zeros(RATE*16)
    def place(name, start, strength=1.):
        data = rendered[name]*.68*strength
        offset = round(start*RATE)
        audition[offset:offset+len(data)] += data
        timeline.append({'time':start,'cue':name,'gain':.68*strength})
    for name,start in [('S_Swing_00',.3),('S_Swing_01',1.3),('S_Parry_00',2.4),('S_Parry_01',3.1),('S_Body_00',4.),('S_Head_00',4.8),('S_Body_01',5.6),('S_Head_01',6.4),('S_Armor_00',7.3),('S_Armor_01',7.8)]:
        place(name,start)
    for start,hit,var in [(8.6,'Body',2),(9.8,'Head',2),(11.,'Parry',2),(12.2,'Chamber',1),(13.4,'Body',0)]:
        place(f'S_Armor_{var:02}',start-.23)
        place(f'S_Swing_{var:02}',start)
        place(f'S_{hit}_{var:02}',start+.18)
    place('S_Armor_01',14.35); place('S_Stab_01',14.6); place('S_Head_01',14.72)
    save_wave(preview/'combat-audition.wav',audition)
    preview_metrics=loudness(audition,False)
    (preview/'timeline.json').write_text(json.dumps({'description':'Edited audition, not captured gameplay. Full uncut air through contact; armor at actual quiet level.','sequence':timeline,'measured':preview_metrics},indent=2)+'\n',encoding='utf-8')
    manifest['audition']=preview_metrics
    (source / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    for pack in packs.values(): pack.close()
    print(f'Built {len(rendered)} cues. Audition: {preview_metrics}', flush=True)


if __name__ == '__main__':
    main()
