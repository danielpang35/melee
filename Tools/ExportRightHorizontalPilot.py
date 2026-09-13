"""Bake selected native D_v08 to an isolated 60 Hz Unreal export, at unchanged speed.

Blender --background --python Tools/ExportRightHorizontalPilot.py
Never writes the editable source, approved EX, or legacy TP export.
"""
import hashlib
import json
import math
import argparse
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'ArtSource/Selected/D_arc_weight_v08/D_arc_weight_v08.blend'
parser=argparse.ArgumentParser()
parser.add_argument('--source');parser.add_argument('--source-sha256')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
if args.source:
    assert args.source_sha256,'Explicit source identity required'
    SOURCE=ROOT/args.source
OUT = SOURCE.parent / 'Export'
OUT.mkdir(parents=True, exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, value): (OUT/name).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
protected = [SOURCE, ROOT/'Config/EXPreview.json', ROOT/'ArtSource/CharacterReset/EX_v002/EX_v002_MordhauRight.blend']
before = {str(p.relative_to(ROOT)): sha(p) for p in protected}
assert sha(SOURCE) == (args.source_sha256 if args.source else 'f77e1a5e4edc28bb158b467964fed9a143413ec33dcc4d35a08325b7c9e1d70e')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
source_rate=scene.render.fps/scene.render.fps_base
assert scene.frame_start==1 and abs((scene.frame_end-1)/source_rate-73/30)<1.e-8
rig = bpy.data.objects[scene['deform_rig']]
body = bpy.data.objects[scene['body_object']]
weapon = bpy.data.objects['CF_Weapon']
assert len(rig.data.bones)==102
rest = {b.name:b.matrix_local.copy() for b in rig.data.bones}
hierarchy = {b.name:b.parent.name if b.parent else None for b in rig.data.bones}
samples, skeleton, poses = [], [], []
for i in range(147):
    frame=1+i*source_rate/60
    scene.frame_set(int(frame), subframe=frame-int(frame))
    deps=bpy.context.evaluated_depsgraph_get()
    r=rig.evaluated_get(deps)
    assert max(abs(r.matrix_world[a][b]-Matrix.Identity(4)[a][b]) for a in range(4) for b in range(4)) < 1e-6
    pose={p.name:p.matrix.copy() for p in r.pose.bones}
    poses.append(pose)
    wm=weapon.evaluated_get(deps).matrix_world.copy()
    p,q,s=wm.decompose()
    assert max(abs(v-1) for v in s)<1e-5
    samples.append(dict(time_s=i/60, frame=i+1, weapon_world=dict(translation_m=list(p),quaternion_wxyz=list(q),scale=list(s)),
        blade_base_world_m=list(p),blade_tip_world_m=list(wm@Vector((0,0,1.035)))))
    skeleton.append(dict(time_s=i/60,bones={name:dict(head_world_m=list(m.translation),
        deformation_quaternion_wxyz=list((m@rest[name].inverted()).to_quaternion().normalized()),component_scale=list(m.to_scale())) for name,m in pose.items()}))
# Bake only the independent deform rig. Controls/native source are not rewritten.
rig.animation_data_clear()
for p in rig.pose.bones:
    for c in list(p.constraints): p.constraints.remove(c)
    p.rotation_mode='QUATERNION'
scene.frame_start=1;scene.frame_end=147;scene.render.fps=60;scene.render.fps_base=1
for i,pose in enumerate(poses):
    scene.frame_set(i+1)
    for p in rig.pose.bones:
        parent=p.parent
        p.matrix_basis=p.bone.convert_local_to_pose(pose[p.name],rest[p.name],
            parent_matrix=pose[parent.name] if parent else Matrix.Identity(4),
            parent_matrix_local=rest[parent.name] if parent else Matrix.Identity(4),invert=True)
        for channel in ('location','rotation_quaternion','scale'):p.keyframe_insert(channel,frame=i+1,group=p.name)
rig.animation_data.action.name=SOURCE.stem+'_1x_deform_bake'
bake_error=0.
for i in range(147):
    scene.frame_set(i+1)
    r=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
    bake_error=max(bake_error,max((p.matrix.translation-poses[i][p.name].translation).length*100 for p in r.pose.bones))
print('BAKE_POSITION_CM',bake_error,flush=True)
assert bake_error<.01,bake_error
selected=[rig,body,bpy.data.objects['KN01_Eye.R'],bpy.data.objects['KN01_Eye.L']]
scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
for o in selected:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=rig
fbx=OUT/'TP_v001_RightHorizontal.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,
    use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_bones=True,bake_anim_use_all_actions=False,
    bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,bake_anim_step=1.,bake_anim_simplify_factor=0.,
    axis_forward='-Y',axis_up='Z',global_scale=1.,apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',path_mode='STRIP',use_mesh_modifiers=True)
# Export the visible sword in its own rigid shaft frame, excluding diagnostic marks.
bpy.ops.object.select_all(action='DESELECT')
deps=bpy.context.evaluated_depsgraph_get()
inverse=weapon.evaluated_get(deps).matrix_world.inverted()
parts=[bpy.data.objects['CF_'+n] for n in ('Blade','Guard','Grip','Pommel')]
materials={m.name:dict(color=list(m.diffuse_color),metallic=m.metallic,roughness=m.roughness) for o in parts for m in o.data.materials if m}
for obj in parts:
    evaluated=obj.evaluated_get(deps)
    data=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps)
    copy=bpy.data.objects.new('Export_'+obj.name,data);scene.collection.objects.link(copy)
    copy.matrix_world=inverse@evaluated.matrix_world;copy.select_set(True)
weapon_fbx=OUT/'TP_v001_Weapon.fbx'
bpy.ops.export_scene.fbx(filepath=str(weapon_fbx),use_selection=True,object_types={'MESH'},bake_anim=False,
    axis_forward='-Y',axis_up='Z',global_scale=1.,apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',path_mode='STRIP')
write('TP_v001_WeaponMotion.json',dict(schema_version=1,fps=60,samples=samples,source_sha256=sha(SOURCE),authority='Visual only; EX owns collision'))
write('TP_v001_SkeletonMotion.json',dict(schema_version=2,fps=60,samples=skeleton,bone_hierarchy=hierarchy,
    diagnostic_profile='TP_native_attack_age_v1',diagnostic_sample_times_s=[0.,22/30,28/30,31/30,43/30,73/30],source_sha256=sha(SOURCE)))
# One selected export roundtrip, no additional preview renders.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.fps=60
bpy.ops.import_scene.fbx(filepath=str(fbx),use_anim=True,ignore_leaf_bones=False,anim_offset=0.0)
imported=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
bpy.context.view_layer.objects.active=imported
bpy.ops.object.mode_set(mode='EDIT')
for bone in imported.data.edit_bones:bone.use_connect=False
bpy.ops.object.mode_set(mode='OBJECT')
max_pos=max_rot=0.
for i in range(147):
    bpy.context.scene.frame_set(i+1)
    r=imported.evaluated_get(bpy.context.evaluated_depsgraph_get())
    for p in r.pose.bones:
        expected=poses[i][p.name];actual=r.matrix_world@p.matrix
        max_pos=max(max_pos,(actual.translation-expected.translation).length*100)
        actual_rotation=(actual@p.bone.matrix_local.inverted()).to_quaternion().normalized()
        expected_rotation=(expected@rest[p.name].inverted()).to_quaternion().normalized()
        max_rot=max(max_rot,2*math.acos(min(1.,abs(actual_rotation.dot(expected_rotation))))*180/math.pi)
unchanged=all(sha(ROOT/p)==h for p,h in before.items())
receipt=dict(passed=unchanged and max_pos<.1 and max_rot<.15,protected=before,unchanged=unchanged,
    roundtrip_position_cm=max_pos,roundtrip_rotation_deg=max_rot,source_rate=source_rate,export_rate=60,playback_rate=1,duration_s=73/30)
write('export-verification.json',receipt)
assert receipt['passed'],receipt
write('manifest.json',dict(schema_version=1,profile='TP_native_attack_age_v1',source=str(SOURCE.relative_to(ROOT)),source_sha256=sha(SOURCE),
    fps=60,start_frame=1,end_frame=147,duration_s=73/30,idle_source_s=0,exporter_sha256=sha(Path(__file__)),
    bone_hierarchy=hierarchy,exported_objects=['KN01_Rig','KN01_Body','KN01_Eye.R','KN01_Eye.L'],
    weapon_materials=materials,files={p.name:sha(p) for p in (fbx,weapon_fbx,OUT/'TP_v001_WeaponMotion.json',OUT/'TP_v001_SkeletonMotion.json')},
    authority='Selected native source at attack age 1x; EX clock and contact unchanged; .183333s cosmetic recovery tail',artistic_acceptance=False))
print(json.dumps(receipt))
