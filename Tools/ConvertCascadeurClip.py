"""Convert a baked Cascadeur FBX into full skeletal deltas for live preview.

Retains every original game bone. No torso/elbow curve reduction or IK.
Atomic output lets an already running Unreal preview pick up the next edit.
"""
import sys,argparse,csv,os,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy
from mathutils import Matrix
p=argparse.ArgumentParser();p.add_argument('fbx',type=Path)
p.add_argument('--output',type=Path,default=ROOT/'Config/CascadeurPreview.csv')
p.add_argument('--fps',type=int,default=120)
args=p.parse_args()
names=json.loads((ROOT/'ArtSource/Cascadeur/manifest.json').read_text())['original_bones']
def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps=args.fps
    bpy.ops.import_scene.fbx(filepath=str(path),anim_offset=0.)
    rigs=[o for o in bpy.data.objects if o.type=='ARMATURE' and all(n in o.pose.bones for n in names)]
    if len(rigs)!=1:raise RuntimeError('Expected exactly one complete game skeleton')
    return rigs[0]
rig=load(ROOT/'ArtSource/Cascadeur/Knight_Authoring.fbx')
base={n:rig.matrix_world@rig.data.bones[n].matrix_local for n in names}
rig=load(args.fbx)
if not rig.animation_data or not rig.animation_data.action:raise RuntimeError('FBX has no baked animation')
start,end=rig.animation_data.action.frame_range
if end<=start:raise RuntimeError('Single pose export: a moving test clip is required')
source_fps=bpy.context.scene.render.fps/bpy.context.scene.render.fps_base
count=int(round((end-start)/source_fps*args.fps))+1
basis=Matrix.Diagonal((1.,-1.,1.,1.))
temporary=args.output.with_suffix('.tmp')
first={};maximum_motion=0.
with temporary.open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['CASCADEUR_SKELETON_V1',args.fps,count])
    for frame in range(count):
        source_frame=start+frame*source_fps/args.fps
        bpy.context.scene.frame_set(int(source_frame),subframe=source_frame-int(source_frame));bpy.context.view_layer.update()
        for name in names:
            current=rig.matrix_world@rig.pose.bones[name].matrix
            delta=basis@(current@base[name].inverted())@basis
            if max(abs(s-1.) for s in delta.to_scale())>.001:
                raise RuntimeError('Animated bone scale is unsupported: '+name)
            position=delta.translation*100.;q=delta.to_quaternion().normalized()
            if frame==0:first[name]=(position.copy(),q.copy())
            else:maximum_motion=max(maximum_motion,(position-first[name][0]).length,q.rotation_difference(first[name][1]).angle)
            w.writerow([frame,name,*position,q.x,q.y,q.z,q.w])
if maximum_motion<.001:raise RuntimeError('FBX contains repeated poses with no measurable motion')
os.replace(temporary,args.output)
print(f'Baked skeletal preview: {count} frames, {len(names)} bones, {args.fps} fps (source {source_fps} fps) -> {args.output}',flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(0)
