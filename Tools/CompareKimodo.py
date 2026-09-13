"""Compose three already-rendered source-speed previews; no source regeneration.

Blender -b --python Tools/CompareKimodo.py -- <manifest.json>
Manifest: {output_directory, candidates:[{label, preview_directory}]}.
"""
import bpy
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
manifest=(ROOT/sys.argv[sys.argv.index('--')+1]).resolve()
plan=json.loads(manifest.read_text())
out=(ROOT/plan['output_directory']).resolve()
assert ROOT in out.parents and len(plan['candidates'])==3
out.mkdir(parents=True,exist_ok=True)
sources=[]
for candidate in plan['candidates']:
    folder=(ROOT/candidate['preview_directory']).resolve()
    receipt=json.loads((folder/'preview.json').read_text())
    sources.append((candidate,folder,receipt))
first=sources[0][2]
assert all(r['frames']==first['frames'] and r['fps']==first['fps'] and r['playback_rate']==1 for _,_,r in sources)
lock=ROOT/'ArtSource/AnimationLab/render.lock'
fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
with os.fdopen(fd,'w') as file:json.dump(dict(task='Kimodo source comparisons',pid=os.getpid()),file)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={}
try:
    for view in ['primary','rear-quarter']:
        dest=out/(view+'.mp4')
        assert not dest.exists(), 'Retain prior comparison'
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene=bpy.context.scene
        scene.render.fps=round(first['fps']);scene.render.fps_base=scene.render.fps/first['fps']
        scene.frame_start=1;scene.frame_end=first['frames'][1]-first['frames'][0]+1
        scene.render.resolution_x=1920;scene.render.resolution_y=640;scene.render.resolution_percentage=100
        editor=scene.sequence_editor_create()
        for i,(candidate,folder,receipt) in enumerate(sources):
            video=folder/(view+'.mp4')
            assert sha(video)==receipt['outputs'][video.name], 'Stale source preview'
            strip=editor.strips.new_movie(candidate['label'],str(video),i+1,1,fit_method='ORIGINAL')
            assert strip.frame_duration==scene.frame_end
            strip.transform.offset_x=(i-1)*640;strip.blend_type='ALPHA_OVER'
            text=editor.strips.new_effect(candidate['label'],type='TEXT',channel=i+4,frame_start=1,length=scene.frame_end)
            text.text=candidate['label']+' | '+view+' | 1x'
            text.font_size=27;text.location=((i+.5)/3,.95);text.color=(1,1,1,1)
        scene.render.image_settings.media_type='VIDEO';scene.render.image_settings.file_format='FFMPEG'
        scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264';scene.render.filepath=str(dest)
        bpy.ops.wm.save_as_mainfile(filepath=str(out/(view+'.blend')))
        bpy.ops.render.render(animation=True)
        clip=bpy.data.movieclips.load(str(dest))
        assert clip.frame_duration==scene.frame_end and list(clip.size)==[1920,640]
        result[view]=dict(file=str(dest.relative_to(ROOT)),sha256=sha(dest),frames=clip.frame_duration,fps=first['fps'],playback_rate=1)
    (out/'comparison.json').write_text(json.dumps(dict(candidates=[dict(label=c['label'],source=r['source'],source_sha256=r['source_sha256']) for c,_,r in sources],views=result,continuous_review=False,human_acceptance=False),indent=2)+'\n')
finally:lock.unlink()
