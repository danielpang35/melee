"""Check the mesh-only return handoff against an isolated keyed native rig."""
import sys,json,hashlib
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from RepairWorkingBody import OUT,EVIDENCE,open_source,digest
from UseWorkingBodyOnReturn import apply_working_body

scene=open_source(OUT/'MB_Diagnostic_JointSweep.blend')
rig=bpy.data.objects['MB_AccuRig']
frames=[1,13,37,61,85,109,133,145]
def motion():
    data=[]
    for frame in frames:
        scene.frame_set(frame)
        data.append([[list(row) for row in bone.matrix] for bone in rig.pose.bones])
    return hashlib.sha256(json.dumps(data).encode()).hexdigest()
before=motion()
body=apply_working_body(rig,OUT/'Male_Body_SurfaceRepair.blend')
after=motion()
assert before==after
assert body.find_armature()==rig
assert len(body.data.vertices)==30000
assert len(rig.data.bones)==118
scene.frame_set(1)
target=EVIDENCE/'MeshOnlyReturn_HandoffTest.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(target))
(EVIDENCE/'return-handoff.json').write_text(json.dumps(dict(
    source=scene['working_body_source'],source_sha256=scene['working_body_source_sha256'],
    sample_frames=frames,bone_pose_samples_before_sha256=before,bone_pose_samples_after_sha256=after,
    rig_bones=118,mesh_vertices=30000,old_mesh_retained=True,
    output=str(target),output_sha256=digest(target),completed=True),indent=2))
print('HANDOFF_OK',before)
