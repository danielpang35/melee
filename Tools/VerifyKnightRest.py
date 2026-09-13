"""Confirm the editable knight rig leaves the supplied rest geometry unchanged."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy
OUT=ROOT/'ArtSource/UserKnight/KN_v001'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Knight_Rig.blend'))
rig=bpy.data.objects['KN01_Rig'];mesh=bpy.data.objects['SK_UserKnight']
assert not rig.animation_data or not rig.animation_data.action
assert len(rig.data.bones)==102
weight_error=max(abs(sum(g.weight for g in v.groups)-1) for v in mesh.data.vertices)
assert weight_error<1.e-5
evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());data=evaluated.to_mesh()
assert len(data.vertices)==len(mesh.data.vertices)
rest_error=max((a.co-b.co).length for a,b in zip(mesh.data.vertices,data.vertices))
assert rest_error<1.e-5
evaluated.to_mesh_clear()
receipt=dict(bones=102,vertices=len(mesh.data.vertices),max_weight_sum_error=weight_error,
    max_rest_deformation_m=rest_error,animation=None,
    files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'Knight_Rig.blend',OUT/'SK_UserKnight.fbx']})
(ROOT/'Saved/UserKnight/rest-verification.json').write_text(json.dumps(receipt,indent=2))
print(receipt)
