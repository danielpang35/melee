"""Render a fixed-camera, fixed-light rotation of an existing reviewed clay source."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'Saved/ArtRuntime'),str(ROOT/'Saved/VideoRuntime')]
import bpy
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',required=True,type=Path)
p.add_argument('--frames',type=int,default=180)
p.add_argument('--fps',type=int,default=18)
p.add_argument('--samples',type=int,default=12)
p.add_argument('--device',choices=['CPU','OPTIX'],default='CPU')
args=p.parse_args()
source=args.source.resolve();out=source.parent
frames=out/'TurntableFrames'
if frames.exists() and any(frames.iterdir()):raise SystemExit('Turntable frames already exist; preserve previous evidence.')
frames.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;assembly=bpy.data.objects['Helmet clay assembly']
if args.device=='OPTIX':
    preferences=bpy.context.preferences.addons['cycles'].preferences
    preferences.compute_device_type='OPTIX';preferences.get_devices()
    for device in preferences.devices:device.use=device.type=='OPTIX'
    if not any(device.type=='OPTIX' for device in preferences.devices):raise RuntimeError('No OptiX device available')
    scene.cycles.device='GPU'
else:scene.cycles.device='CPU'
scene.render.resolution_x=448;scene.render.resolution_y=560
scene.render.resolution_percentage=100;scene.cycles.samples=args.samples
scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
start=assembly.rotation_euler.z
records=[]
for frame in range(args.frames):
    angle=360*frame/args.frames
    assembly.rotation_euler.z=start+math.radians(angle)
    scene.render.filepath=str(frames/f'{frame:04d}.png')
    bpy.ops.render.render(write_still=True)
    records.append({'frame':frame,'angle_deg':angle})
    if frame%18==0:print(f'TURNTABLE {frame+1}/{args.frames}',flush=True)

# Alpha compositing is presentation only; retained RGBA frames are the originals.
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
video=out/'turntable.mp4'
command=[ffmpeg,'-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','448x560','-r',str(args.fps),'-i','-',
         '-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
proc=subprocess.Popen(command,stdin=subprocess.PIPE)
contact=Image.new('RGB',(4*448,2*596),(23,27,31))
d=ImageDraw.Draw(contact);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
samples={round(i*args.frames/8):i for i in range(8)}
for frame in range(args.frames):
    im=Image.open(frames/f'{frame:04d}.png').convert('RGBA')
    composite=Image.new('RGB',im.size,(42,46,50));composite.paste(im,(0,0),im)
    proc.stdin.write(composite.tobytes())
    if frame in samples:
        idx=samples[frame];x=(idx%4)*448;y=(idx//4)*596
        contact.paste(composite,(x,y+36))
        d.text((x+12,y+5),f'{360*frame/args.frames:.0f} degrees',font=font,fill='#e8edf0')
proc.stdin.close()
if proc.wait()!=0:raise RuntimeError('ffmpeg encoding failed')
contact.save(out/'turntable-contact.png')
receipt={'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'camera_matrix':[list(row) for row in scene.camera.matrix_world],'frames':args.frames,'fps':args.fps,
         'duration_seconds':args.frames/args.fps,'resolution':[448,560],'samples':args.samples,'device':args.device,
         'motion':'Assembly rotates evenly 0 <= angle < 360 degrees around Z; camera, lights and material remain fixed.',
         'rgba_frames_retained':True,'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'angles':records}
(out/'turntable.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'video':str(video),'contact':str(out/'turntable-contact.png'),'duration':args.frames/args.fps}),flush=True)
