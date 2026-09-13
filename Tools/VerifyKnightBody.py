"""Targeted body separation/rest/native-control checks. No game or render sweep."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'Saved/ArtRuntime'),str(ROOT/'Tools')]
import bpy
from AnimationAuthoring import rig as controls
source=ROOT/'ArtSource/UserKnight/KN_v002/Knight_Animation.blend'
manifest=json.loads(source.with_name('manifest.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(ROOT/p)==value for p,value in manifest['protected_inputs'].items())
assert all(sha(source.parent/p)==value for p,value in manifest['outputs'].items())
bpy.ops.wm.open_mainfile(filepath=str(source))
rig=bpy.data.objects[bpy.context.scene['deform_rig']]
body=bpy.data.objects[bpy.context.scene['body_object']]
assert len(rig.data.bones)==102 and not rig.animation_data
assert all(b.length>1e-6 for b in rig.data.bones)
armor=bpy.data.collections['Knight Armor (Deferred)']
assert armor.hide_render and armor.hide_viewport and len(armor.objects)==1
assert body not in list(armor.objects)
for mod in body.modifiers:
    if mod.type=='SUBSURF': mod.show_viewport=False
weight_error=max(abs(sum(g.weight for g in v.groups)-1) for v in body.data.vertices)
assert weight_error<1e-5,weight_error
def coords(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh();result=[v.co.copy() for v in mesh.vertices];evaluated.to_mesh_clear()
    return result
actual=coords(body)
rest_error=max((v.co-p).length for v,p in zip(body.data.vertices,actual))
assert len(actual)==len(body.data.vertices) and rest_error<1e-5,rest_error
control,*_=controls.setup(source)
body=bpy.data.objects[bpy.context.scene['body_object']]
for mod in body.modifiers:
    if mod.type=='SUBSURF': mod.show_viewport=False
before=coords(body)
control.pose.bones['upperarm01.R'].rotation_euler.x=.5
bpy.context.view_layer.update()
after=coords(body)
movement=max((a-b).length for a,b in zip(before,after))
assert movement>.05,movement
assert bpy.data.collections['Knight Armor (Deferred)'].hide_render
receipt=dict(character='KN_v002',bones=len(control.data.bones),body_vertices=len(before),
    weight_sum_error=weight_error,rest_deformation_m=rest_error,
    native_arm_control_moves_body_m=movement,armor_hidden_after_control_setup=True,
    protected_inputs_unchanged=True,source_sha256=sha(source),human_acceptance=False,
    scope='Rest binding, separation and native arm-control response; no old clip compatibility or armor articulation claim.')
(ROOT/'Saved/UserKnight/body-verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
