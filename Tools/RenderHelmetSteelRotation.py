"""Read-only fixed-rig motion proof of finalized helmet steel source."""
from pathlib import Path
import argparse,sys,json,hashlib,math,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'Saved/ArtRuntime'),str(ROOT/'Saved/VideoRuntime')]
import bpy
from PIL import Image,ImageDraw
import imageio_ffmpeg
p=argparse.ArgumentParser();p.add_argument('--revision',default='ST_v002');a=p.parse_args()
source=ROOT/'ArtSource/StyleReference/MEL17/SteelTransfer'/a.revision/f'Helmet_Steel_{a.revision}.blend'
review=ROOT/'Saved/ArtReview/UnrealStyle'/a.revision/'Review';out=review/'Rotation'
if out.exists():raise RuntimeError('Immutable rotation already exists')
assert (review/'finalization.json').exists();out.mkdir();frames=out/'Frames';frames.mkdir()
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;assembly=bpy.data.objects['Helmet clay assembly']
scene.render.resolution_x=448;scene.render.resolution_y=560;scene.render.resolution_percentage=100;scene.cycles.samples=12;scene.cycles.device='CPU';scene.cycles.seed=0;scene.render.film_transparent=False
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
light_matrices={o.name:[list(row) for row in o.matrix_world] for o in scene.objects if o.type=='LIGHT'};camera_matrix=[list(row) for row in scene.camera.matrix_world]
records=[];count=36;fps=18
for frame in range(count):
    angle=-25+50*frame/(count-1);assembly.rotation_euler.z=math.radians(angle);scene.frame_set(frame+1);bpy.context.view_layer.update()
    scene.render.filepath=str(frames/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
    image=Image.open(scene.render.filepath);image.load();assert image.size==(448,560);assert max(image.convert('RGB').getextrema()[0])>min(image.convert('RGB').getextrema()[0])
    assert camera_matrix==[list(row) for row in scene.camera.matrix_world]
    assert light_matrices=={o.name:[list(row) for row in o.matrix_world] for o in scene.objects if o.type=='LIGHT'}
    records.append({'frame':frame,'scene_frame':scene.frame_current,'angle_degrees':angle,'assembly_matrix':[list(row) for row in assembly.matrix_world],'sha256':hashlib.sha256(Path(scene.render.filepath).read_bytes()).hexdigest()})
    print('ST_ROTATION_FRAME',frame+1,'of',count,flush=True)
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe();video=out/'rotation.mp4'
subprocess.run([ffmpeg,'-v','error','-framerate',str(fps),'-i',str(frames/'%04d.png'),'-frames:v',str(count),'-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
# Decode full video as validation, not only headers.
decoded=subprocess.run([ffmpeg,'-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,check=True)
assert len(decoded.stdout)==count*448*560*3
contact=Image.new('RGB',(448*4,592*2),(25,25,25));d=ImageDraw.Draw(contact)
for i,frame in enumerate([0,5,10,15,20,25,30,35]):
    x=i%4*448;y=i//4*592;contact.paste(Image.open(frames/f'{frame:04d}.png'),(x,y+32));d.text((x+12,y+10),f'Frame {frame}: {records[frame]["angle_degrees"]:.1f} degrees',fill='white')
contact.save(out/'contact.png')
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
receipt={'source':str(source.relative_to(ROOT)),'source_sha256':source_hash,'frames':count,'fps':fps,'duration_seconds':count/fps,'resolution':[448,560],'samples':12,'engine':'Cycles CPU','camera_matrix':camera_matrix,'lights':light_matrices,'motion':'Continuous linear 50-degree assembly yaw sweep -25 to +25; fixed camera/light/material; no held or missing frames','all_images_fully_decoded':True,'video_fully_decoded_frame_count':count,'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'records':records,'artistic_status':'Pending independent review; motion playback not claimed by renderer'}
(out/'rotation.json').write_text(json.dumps(receipt,indent=2));print('ST_ROTATION_COMPLETE',out,flush=True)

