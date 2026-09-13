"""Save explicit attack markers on a new native take, preserving input curves."""
import json
import sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools'))
from RetargetKimodo import sha,write
from CheckAttackDraftTiming import check_native
folder=(ROOT/sys.argv[sys.argv.index('--')+1]).resolve()
assert folder.parent==ROOT/'ArtSource/Kimodo/RH_20260913'
source=folder/'MB_Kimodo_AuthoredGrip.blend'
dest=folder/'ReferencePullback.blend'
assert not dest.exists()
job=json.loads((folder/'job.json').read_text())
original=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
assert scene.frame_start==1 and scene.frame_end==job['frame_count']
assert abs(scene.render.fps/scene.render.fps_base-job['attack_timing']['fps'])<.00001
scene.render.fps=job['attack_timing']['fps'];scene.render.fps_base=1
scene.timeline_markers.clear()
for name,f in [('Ready',1),('Opening',13),('Loaded',30),('ReleaseStart',40),('ReleaseEnd',55),('Carry',67),('Recovered',92)]:
    scene.timeline_markers.new(name,frame=f)
scene['required_release_seconds']=.5
scene['review_status']='Photo-directed fresh Kimodo proposal with native two-arm finishing; provisional art draft, no runtime/contact/human acceptance.'
result=check_native(scene,.5)
scene.frame_set(30)
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
assert sha(source)==original
write(folder/'native-take.json',dict(source=str(dest.relative_to(ROOT)),source_sha256=sha(dest),
    input_source_sha256=original,job_sha256=sha(folder/'job.json'),
    operation='Native marker metadata and exact integer model FPS; existing native curves unchanged.',**result))
print('NATIVE_ATTACK_SAVED',result,flush=True)
