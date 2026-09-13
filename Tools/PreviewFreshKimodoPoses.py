"""Bind fresh authored feasibility poses to source timing and cheap named stills.

This is a constraint proof, explicitly not a generated animation proposal.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import bpy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Tools'))
from RetargetKimodo import sha,write,CAMERAS

parser=argparse.ArgumentParser()
parser.add_argument('--directory',required=True)
parser.add_argument('--job',required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
directory=(ROOT/args.directory).resolve();job_path=(ROOT/args.job).resolve()
job=json.loads(job_path.read_text());timing=job['attack_timing']
source=directory/'Fresh_MB_PoseProof.blend'
assert not source.exists()
bpy.ops.wm.open_mainfile(filepath=str(directory/'Fresh_MB_ConstraintPoses.blend'))
scene=bpy.context.scene
assert scene.render.fps/scene.render.fps_base==timing['fps']==30
assert scene.frame_end-scene.frame_start+1==job['frame_count']
for marker in list(scene.timeline_markers):scene.timeline_markers.remove(marker)
for name,index in [('Ready',0),('Open',9),('Gather',23),('ReleaseStart',39),('ReleaseEnd',54),('Carry',68),('Recovery',95)]:
    scene.timeline_markers.new(name,frame=index+1)
assert (scene.timeline_markers['ReleaseEnd'].frame-scene.timeline_markers['ReleaseStart'].frame)/(scene.render.fps/scene.render.fps_base)==.5
scene['required_release_seconds']=.5
scene['review_status']='Fresh rest-authored constraint feasibility proof. No diffusion or inherited animation. Not a generated proposal or accepted performance.'
scene['fresh_job']=str(job_path.relative_to(ROOT))
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
out=ROOT/'Saved/Kimodo/RH_20260913'/directory.name/source.stem
out.mkdir(parents=True,exist_ok=False)
lock=ROOT/'ArtSource/AnimationLab/render.lock'
fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
os.write(fd,json.dumps(dict(task='Fresh constraint pose stills',pid=os.getpid())).encode());os.close(fd)
outputs={}
try:
    scene.render.image_settings.media_type='IMAGE'
    scene.render.image_settings.file_format='PNG'
    stills=[(n,f) for f in [1,10,24,40,45,50,55,69,96] for n in ['primary','rear-quarter']]
    stills += [(n,40) for n in ['front','rear','left','right']]
    for name,f in stills:
        scene.frame_set(f);scene.camera=bpy.data.objects['Kimodo_'+name]
        path=out/f'{name}-{f:04}.png';scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True);outputs[path.name]=sha(path)
    write(out/'preview.json',dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),
        job=str(job_path.relative_to(ROOT)),job_sha256=sha(job_path),constraint_sha256=sha(job_path.parent/'constraints.json'),
        fps=30,frames=[1,96],release_markers={'ReleaseStart':40,'ReleaseEnd':55},required_release_seconds=.5,
        cameras=CAMERAS,still_frames_views=stills,outputs=outputs,
        evidence_limit='Fresh authored constraint feasibility stills only. No generated proposal, full animation preview, continuous viewing, or human acceptance.'))
finally:lock.unlink()
print('FRESH_POSE_STILLS',out,flush=True)
