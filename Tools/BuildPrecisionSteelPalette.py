"""Author the versioned Precision Steel palette from preserved CC0 recordings.

Run from this project with Python 3 + NumPy and the preserved FFmpeg runtime.
No downloads and no writes to the active Unreal bank. Outputs PCM24/48k mono.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Saved/ArtRuntime'))
import numpy as np

SR = 48000
OUT = ROOT / 'ArtSource/CombatAudio/Palettes/PrecisionSteel_v5'
SOURCE = ROOT / 'ArtSource/CombatAudio'
FFMPEG = ROOT / 'Saved/VideoRuntime/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
CACHE = {}
RECORDS = {}


def db(x):
    return float(20 * np.log10(max(float(x), 1e-15)))


def process(x, filters):
    result = subprocess.run([str(FFMPEG), '-v', 'error', '-f', 'f32le', '-ar', str(SR),
        '-ac', '1', '-i', 'pipe:0', '-af', filters, '-f', 'f32le', 'pipe:1'],
        input=np.asarray(x, dtype='<f4').tobytes(), capture_output=True, check=True)
    return np.frombuffer(result.stdout, '<f4').astype(float)


def smooth(x, ms=2):
    n = round(SR*ms/1000)
    return np.sqrt(np.convolve(x*x, np.ones(n)/n, 'same'))


def pad(x, duration):
    y = np.zeros(round(duration*SR))
    y[:min(len(x), len(y))] = x[:len(y)]
    return y


def fade(x, attack=.0006, release=.014):
    y = x.copy()
    a, r = min(len(y), round(attack*SR)), min(len(y), round(release*SR))
    if a: y[:a] *= np.sin(np.linspace(0, np.pi/2, a))**2
    if r: y[-r:] *= np.cos(np.linspace(0, np.pi/2, r))**2
    y[0] = y[-1] = 0
    return y


def source(pack, name):
    key = (pack, name)
    if key in CACHE: return CACHE[key].copy()
    archives = {'swish':'artisticdude_swishes.zip', 'foley':'artisticdude_rpg.zip',
        'rpg':'kenney_rpg-audio.zip', 'impact':'kenney_impact-sounds.zip'}
    if pack == 'steel':
        path = SOURCE / 'Originals/stillnorth' / name
        raw = path.read_bytes()
        location = str(path.relative_to(ROOT)).replace('\\', '/')
    else:
        archive = SOURCE / 'Archives' / archives[pack]
        with zipfile.ZipFile(archive) as z:
            member = next(p for p in z.namelist() if Path(p).name == name and '__MACOSX' not in p)
            raw = z.read(member)
        location = str(archive.relative_to(ROOT)).replace('\\', '/') + '::' + member
    result = subprocess.run([str(FFMPEG), '-v', 'error', '-i', 'pipe:0', '-ar', str(SR),
        '-ac', '1', '-f', 'f32le', 'pipe:1'], input=raw, capture_output=True, check=True)
    x = np.frombuffer(result.stdout, '<f4').astype(float)
    CACHE[key] = x
    RECORDS[pack+'/'+name] = {'location':location, 'sha256':hashlib.sha256(raw).hexdigest()}
    return x.copy()


def isolate(x, index):
    # Select distinct actual contacts from the original multi-strike take.
    size = 96
    blocks = np.sqrt(np.mean(x[:len(x)//size*size].reshape(-1,size)**2, axis=1))
    candidates = np.flatnonzero((blocks > np.max(blocks)*.13) &
        (np.r_[0,blocks[:-1]] <= np.max(blocks)*.13))
    starts = []
    for b in candidates:
        n = max(0, int(b*size)-96)
        if not starts or n-starts[-1] > SR*.38: starts.append(n)
    if len(starts)<5: raise ValueError(f'Only {len(starts)} distinct strikes in take')
    start = starts[index % len(starts)]
    return x[start:start+round(.43*SR)], start/SR


def layer(pack, name, *, index=None, pitch=1., band=(100,8000), duration=.18,
          decay=.08, gain=1., attack=.0006, start=0., stretch=1., align=True, role=''):
    x = source(pack, name)
    offset = start
    if index is not None:
        x, offset = isolate(x, index)
    elif start:
        x = x[round(start*SR):]
    if align:
        env = smooth(x)
        first = np.flatnonzero(env > max(env)*.035)
        trim = max(0, int(first[0])-24) if len(first) else 0
        x = x[trim:]
        offset += trim/SR
    x = process(x, f'asetrate={round(SR*pitch)},aresample={SR},atempo={1/stretch},'
        f'highpass=f={band[0]}:p=2,lowpass=f={band[1]}:p=2')
    x = pad(x, duration)
    x *= .16/max(float(np.max(smooth(x, 10))), 1e-8)
    if decay: x *= np.exp(-np.arange(len(x))/SR/decay)
    x = fade(x, attack, .016)*gain
    info = dict(source=pack+'/'+name, source_start_seconds=round(offset,6),
        pitch_ratio=pitch, stretch_ratio=stretch, band_hz=band, duration=duration,
        decay=decay, gain=gain, attack=attack, role=role)
    return x, info


def noise(seed, duration, band, peak, rise, tail, gain):
    rng = np.random.default_rng(seed)
    n = round(duration*SR)
    f = np.fft.rfftfreq(n+8192, 1/SR)
    weight = 1/np.sqrt(1+(band[0]/np.maximum(f,1))**8)
    weight *= 1/np.sqrt(1+(f/band[1])**8)
    weight *= 1/np.maximum(f, band[0])**.25
    x = np.fft.irfft(np.fft.rfft(rng.normal(size=n+8192))*weight, n+8192)[4096:4096+n]
    x *= .16/np.sqrt(np.mean(x*x))
    t = np.arange(n)/SR
    env = np.exp(-.5*((t-peak)/np.where(t<peak,rise,tail))**2)
    return fade(x*env*gain,.004,.018), dict(source='original_air',seed=seed,
        band_hz=band,peak=peak,rise=rise,tail=tail,gain=gain)


def modes(seed, duration, frequencies, decays, amplitudes, gain=1.):
    # Damped, inharmonic metal modes; never a fixed UI sine beep.
    t = np.arange(round(duration*SR))/SR
    rng = np.random.default_rng(seed)
    x = np.zeros(len(t))
    for f, d, a in zip(frequencies, decays, amplitudes):
        detune = rng.uniform(-.0025,.0025)
        phase = 2*np.pi*f*(1+detune)*t + .018*np.sin(2*np.pi*43*t)
        x += a*np.sin(phase + rng.uniform(-.15,.15))*np.exp(-t/d)
    return fade(x*gain,.0007,.015), dict(source='original_metal_modes',seed=seed,
        modes_hz=frequencies,decays=decays,amplitudes=amplitudes,gain=gain)


def combine(layers, duration, highpass=70, lowpass=8200):
    x = np.zeros(round(duration*SR))
    info = []
    for item in layers:
        sig, recipe, *delay = item
        at = round((delay[0] if delay else 0)*SR)
        count = min(len(sig), len(x)-at)
        x[at:at+count] += sig[:count]
        info.append(dict(recipe, delay_seconds=at/SR))
    # Saturation remains gentle; no compressor pumping or baked ambience.
    x = np.tanh(x*1.1)/1.1
    x = process(x, f'highpass=f={highpass}:p=2,lowpass=f={lowpass}:p=2,'
        'equalizer=f=3600:t=q:w=1.1:g=-1.8')
    return fade(x,.00065,.016), info


def measure(x, train=True):
    if train:
        unit = pad(x, .6)
        x = np.tile(unit, 6)
    result = subprocess.run([str(FFMPEG), '-hide_banner', '-nostats', '-f', 'f32le',
        '-ar',str(SR),'-ac','1','-i','pipe:0','-af',
        'loudnorm=I=-23:TP=-4:LRA=7:print_format=json','-f','null','-'],
        input=x.astype('<f4').tobytes(), capture_output=True, check=True)
    m = json.loads(re.search(r'\{[^{}]+"input_i"[^{}]+\}',result.stderr.decode()).group())
    return {'train_lufs' if train else 'integrated_lufs':float(m['input_i']),
        'true_peak_dbtp':float(m['input_tp'])}


def master(x, target):
    for _ in range(10):
        m = measure(x)
        if abs(m['train_lufs']-target)<.10 and m['true_peak_dbtp']<=-3.5:
            return x
        x *= 10**((target-m['train_lufs'])/20)
        if measure(x)['true_peak_dbtp'] <= -3.8:
            continue
        x = process(x, 'aresample=192000,alimiter=limit=0.62:attack=0.5:release=18:'
            'level=false:latency=true,aresample=48000')
        x = fade(x,.0004,.012)
    m = measure(x)
    if m['true_peak_dbtp'] > -3.5: raise ValueError(f'Excessive transient crest {m}')
    return x


def pcm24(x):
    return np.clip(np.round(x*8388608), -8388608,8388607).astype(np.int32)


def save(path, x):
    path.parent.mkdir(parents=True,exist_ok=True)
    q = pcm24(x)
    if np.max(np.abs(x)) >= 1: raise ValueError(f'Clipped {path}')
    b = np.empty((q.size,3),dtype=np.uint8)
    flat = q.reshape(-1)
    b[:,0] = flat & 255
    b[:,1] = (flat >> 8) & 255
    b[:,2] = (flat >> 16) & 255
    with wave.open(str(path),'wb') as w:
        w.setparams((1 if x.ndim==1 else x.shape[1],3,SR,0,'NONE','not compressed'))
        w.writeframes(b.tobytes())
    return q/8388608.


def diagnostics(x):
    f = np.fft.rfftfreq(len(x),1/SR)
    power = abs(np.fft.rfft(x))**2
    total = np.sum(power)
    cumulative = np.cumsum(x*x)/np.sum(x*x)
    return dict(duration_ms=round(len(x)/SR*1000,2), peak_dbfs=round(db(max(abs(x))),2),
        centroid_hz=round(float(np.sum(f*power)/total),1),
        energy_below_80hz_percent=round(float(np.sum(power[f<80])/total*100),3),
        energy_above_8khz_percent=round(float(np.sum(power[f>8000])/total*100),3),
        energy_95_time_ms=round(float(np.searchsorted(cumulative,.95))/SR*1000,2))


def main():
    global FFMPEG, OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg',type=Path,default=FFMPEG)
    parser.add_argument('--output',type=Path,default=OUT)
    args=parser.parse_args()
    FFMPEG, OUT = args.ffmpeg,args.output
    OUT.mkdir(parents=True,exist_ok=True)
    manifest={'name':'Precision Steel','revision':5,'rate_hz':SR,'bit_depth':24,
        'channels':1,'variants_per_event':5,'baked_reverb':False,
        'measurement':'6 repetitions at 0.6 second spacing; FFmpeg EBU R128 input measurement. Diagnostic loudness proxy for short SFX, not an isolated-event LUFS claim.',
        'master_peak_ceiling_dbtp':-3.5,'sounds':[],'headshot_recipes':[], 'demos':{}}
    rendered={}
    def export(event,i,x,recipes,target,stem=False):
        filename=f'PS_{event}_{i+1:02}.wav'
        rel=Path('Layers' if stem else 'Cues/'+event)/filename
        x=save(OUT/rel,x)
        m=dict(measure(x),**diagnostics(x))
        manifest['sounds'].append(dict(path=rel.as_posix(),event=event,variation=i+1,
            target_train_lufs=target,measurement=m,recipe=recipes,
            sha256=hashlib.sha256((OUT/rel).read_bytes()).hexdigest()))
        rendered[(event,i)]=x
        print(filename,m,flush=True)
        return x

    for i in range(5):
        seed=19260+i*37
        pitch=[.975,1.012,1.,.987,1.022][i]
        duration=[.300,.310,.295,.305,.300][i]
        swing, r=combine([
            noise(seed,duration,(125,650),.073,.040,.063,.66),
            noise(seed+1,duration,(460,3800),.084,.038,.054,.44),
            noise(seed+2,duration,(2100,6900),.090,.026,.037,.15),
            layer('swish',f'swish-{[4,6,8,2,7][i]}.wav',pitch=.75*pitch,band=(350,4400),
                duration=.24,decay=.12,gain=.16,attack=.014,role='restrained recorded air grain')
            ],duration,highpass=85,lowpass=7500)
        export('Swing',i,master(swing,-24),r,-24)

        parry,r=combine([
            layer('steel','Norse Sword Katana Blade on Blade.wav',index=i,pitch=.96*pitch,
                band=(650,7600),duration=.175,decay=.046,gain=.75,role='blade-on-blade cling'),
            layer('steel','Sabre Norse Sword Hilt on Blade.wav',index=i,pitch=.83*pitch,
                band=(180,1250),duration=.095,decay=.034,gain=.28,role='contained hilt mass'),
            modes(seed,.21,[1130*pitch,1871*pitch,2770*pitch,4190*pitch],
                [.040,.035,.027,.018],[.080,.038,.023,.011]),
            layer('rpg','metalClick.ogg',pitch=.95*pitch,band=(1800,7200),duration=.022,
                decay=.008,gain=.10,role='precise contact edge')
            ],.215,highpass=135,lowpass=7900)
        export('Parry',i,master(parry,-23),r,-23)

        # Sliding friction develops first; the final catch is brief and damped.
        scrape, rs=layer('foley',f'sword-unsheathe{[2,3,2,3,2][i]}.wav',
            pitch=.77*pitch,stretch=1.06,band=(560,3300),start=.025+i*.006,
            duration=.145,decay=0,gain=.69,attack=.002,role='recorded steel sliding rasp')
        t=np.arange(len(scrape))/SR
        envelope=(.30+.70*np.minimum(t/.105,1))
        envelope *= 1-.94*np.clip((t-.114)/.030,0,1)
        scrape=fade(scrape*envelope,.001,.012)
        rasp, rr=noise(seed+8,.15,(650,3800),.079,.08,.035,.27)
        t=np.arange(len(rasp))/SR
        pulse=(.5+.5*np.sin(2*np.pi*(95*t+220*t*t)))**2
        rasp*=.36+.64*pulse
        rr['role']='accelerating micro-friction beneath recorded slide'
        chamber,r=combine([
            (scrape,dict(rs,friction_peak_ms=105,friction_release_ms=144)),(rasp,rr),
            (*layer('rpg','metalLatch.ogg',pitch=1.12*pitch,band=(1000,6100),
                duration=.031,decay=.009,gain=.50,role='crisp terminal release'),.125),
            (*layer('steel','Norse Sword Katana Blade on Blade.wav',index=i,pitch=1.02*pitch,
                band=(950,4400),duration=.028,decay=.006,gain=.28,role='damped blade catch'),.123)
            ],.19,highpass=320,lowpass=4400)
        if i == 1:
            t=np.arange(len(chamber))/SR
            chamber *= .35+.65*np.clip(t/.075,0,1)
            r.append({'source':'envelope_edit','role':'shape flatter source into rising friction',
                'initial_gain':.35,'unity_after_ms':75})
        export('Chamber',i,master(chamber,-23.5),r,-23.5)

        hit,r=combine([
            layer('steel','Norse Sword Katana Blade on Blade.wav',index=i,pitch=.88*pitch,
                band=(550,6200),duration=.12,decay=.030,gain=.48,role='tight real steel strike'),
            layer('impact',f'impactPunch_heavy_{i:03}.ogg',pitch=.83*pitch,
                band=(105,1150),duration=.125,decay=.045,gain=.78,role='restrained low-mid contact thump'),
            layer('steel','Mace Norse Sword Blade.wav',index=i,pitch=.76*pitch,
                band=(190,1850),duration=.11,decay=.031,gain=.27,role='weapon mass'),
            layer('impact',f'impactGeneric_light_{i:03}.ogg',pitch=.97*pitch,
                band=(1300,6500),duration=.035,decay=.012,gain=.12,role='dry tactile attack'),
            noise(seed+11,.12,(230,850),.009,.004,.021,.16)
            ],.18,highpass=120,lowpass=7000)
        hit=export('Hit',i,master(hit,-23),r,-23)

        ping,pr=combine([
            modes(seed+20,.18,[2420*pitch,3890*pitch,5610*pitch],
                [.029,.020,.011],[.12,.040,.013]),
            layer('steel','Sabre Katana Blade on Blade.wav',index=i,pitch=1.30*pitch,
                band=(1900,6400),duration=.09,decay=.019,gain=.09,role='real metal detail in ping')
            ],.18,highpass=1700,lowpass=7200)
        # Ping is ~12% of the hit's K-weighted energy. Joint gain preserves
        # base weight and matches the full headshot to body loudness.
        ping=master(ping,-32.2)
        # Slightly stagger excitation inside the stem; import both at time zero.
        ping=np.r_[np.zeros(144),ping[:-144]]
        ping=fade(ping,.0001,.010)
        combination=hit+ping
        g=10**((-23-measure(combination)['train_lufs'])/20)
        # A small joint trim, when needed, preserves exact linear stems and
        # transient shape while reserving headroom for the added ping.
        summed_peak=measure(combination*g)['true_peak_dbtp']
        if summed_peak > -3.65: g *= 10**((-3.65-summed_peak)/20)
        base=export('Headshot_Base',i,hit*g,[{'source':f'Cues/Hit/PS_Hit_{i+1:02}.wav',
            'gain':g,'role':'same hit, compensated together with ping'}],None,True)
        ping=export('Headshot_Ping',i,ping*g,pr,None,True)
        head=export('Headshot',i,base+ping,[{'source':f'Layers/PS_Headshot_Base_{i+1:02}.wav','gain':1},
            {'source':f'Layers/PS_Headshot_Ping_{i+1:02}.wav','gain':1}],-23)
        manifest['headshot_recipes'].append({'variation':i+1,'base_gain_from_hit':g,
            'base_gain_db':db(g),'stem_playback_gain':1,'trigger_offset_ms':0,
            'ping_excitation_offset_ms_baked_in':3,'premix_is_sum_of_stems':True})

    # Edited dry rapid-combat demo: actual delivered masters, unity-relative
    # balance, no ducking, no extra reverb, no limiter. All air plays to its end.
    timeline=[]
    demo=np.zeros(round(10.6*SR))
    def place(event,i,at,gain=.68):
        x=rendered[(event,i)]*gain
        n=round(at*SR)
        demo[n:n+len(x)]+=x
        timeline.append(dict(time_seconds=at,event=event,variation=i+1,gain=gain,
            file=f'Cues/{event}/PS_{event}_{i+1:02}.wav'))
    exchanges=[(.18,'Parry',0),(.64,'Chamber',1),(1.07,'Hit',2),(1.49,'Headshot',3),
        (2.26,'Parry',4),(2.63,'Hit',0),(2.98,'Chamber',2),(3.35,'Headshot',1),
        (4.14,'Hit',3),(4.47,'Parry',2),(4.83,'Chamber',4),(5.15,'Hit',1),
        (5.49,'Headshot',0),(6.26,'Parry',1),(6.57,'Chamber',3),(6.89,'Hit',4),
        (7.19,'Headshot',2),(7.84,'Parry',3),(8.17,'Hit',2),(8.50,'Chamber',0),
        (8.81,'Hit',0),(9.14,'Headshot',4)]
    for at,event,i in exchanges:
        place('Swing',i,at)
        place(event,i,round(at+.088,4))
    # A genuine missed commitment communicates only displaced air.
    place('Swing',4,9.82)
    demo=save(OUT/'Demo/rapid_exchange.wav',demo)
    manifest['demos']['rapid_exchange.wav']=dict(measure(demo,False),**diagnostics(demo))

    # Deliberate hostile overlap test: 12 cue starts/s, full tails, center mono.
    stress=np.zeros(round(5.6*SR))
    stress_events=[]
    event_cycle=['Parry','Hit','Chamber','Headshot']
    for j in range(28):
        at=.12+j/6
        for event,offset in [('Swing',0),(event_cycle[j%4],.072)]:
            i=j%5
            x=rendered[(event,i)]*.68
            n=round((at+offset)*SR)
            stress[n:n+len(x)]+=x
            stress_events.append(dict(time_seconds=round(at+offset,6),event=event,variation=i+1,gain=.68))
    stress=save(OUT/'Demo/dense_mono_stress.wav',stress)
    manifest['demos']['dense_mono_stress.wav']=dict(measure(stress,False),**diagnostics(stress))

    # Clearly spaced family and variation audition, kept at the same playback gain.
    solo=np.zeros(round(25*.62*SR+.5*SR))
    solo_events=[]
    for j,(event,i) in enumerate((e,i) for e in ['Swing','Parry','Chamber','Hit','Headshot'] for i in range(5)):
        at=.15+j*.62
        n=round(at*SR)
        x=rendered[(event,i)]*.68
        solo[n:n+len(x)]+=x
        solo_events.append(dict(time_seconds=round(at,3),event=event,variation=i+1))
    save(OUT/'Demo/palette_audition.wav',solo)
    # Save useful solo comparisons for direct in-app playback.
    for event in ['Swing','Parry','Chamber','Hit','Headshot']:
        sample=np.zeros(round(2.9*SR))
        for i in range(5):
            n=round((.10+i*.53)*SR)
            x=rendered[(event,i)]*.68
            sample[n:n+len(x)]+=x
        save(OUT/f'Demo/{event.lower()}_variations.wav',sample)
    (OUT/'Demo/timeline.json').write_text(json.dumps(dict(
        description='Edited dry sequence, not captured gameplay. Gain 0.68 per voice. Full tails. No bus limiter, reverb, ducking, spatial processing or soundtrack.',
        rapid_exchange=timeline,dense_mono_stress=stress_events,palette_audition=solo_events),indent=2)+'\n')
    manifest['sources']=RECORDS
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('Completed:',OUT,flush=True)


if __name__=='__main__': main()
