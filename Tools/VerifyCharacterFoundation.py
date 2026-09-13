"""Reopen saved source, export the complete character, and inspect FBX roundtrip."""
import sys,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy
P=ROOT/'ArtSource/CharacterReset/CF_v001'
bpy.ops.wm.open_mainfile(filepath=str(P/'CF_v001_Character.blend'))
scene=bpy.context.scene;scene.frame_set(1)
body=bpy.data.objects['CF01_Body'];rig=bpy.data.objects['CF01_CharacterRig']
source_bones=len(rig.data.bones)
source_height=max(v.co.z for v in body.data.vertices)-min(v.co.z for v in body.data.vertices)
assert abs(source_height-1.8)<.005,source_height
assert rig.animation_data and rig.animation_data.action
source_landmarks={name:list(rig.data.bones[name].head_local) for name in ['upperarm01.L','lowerarm01.L','wrist.L','head']}
bpy.ops.object.select_all(action='DESELECT')
for o in scene.objects:
    if o.name.startswith(('CF01_Body','CF01_CharacterRig','CF01_Eye.')):o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(P/'CF_v001_Character.fbx'),use_selection=True,
    add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,
    bake_anim_simplify_factor=0.,axis_forward='-Y',axis_up='Z',path_mode='STRIP',
    use_mesh_modifiers=True,mesh_smooth_type='FACE')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(P/'CF_v001_Character.fbx'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
body=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('CF01_Body'))
assert len(rig.data.bones)==source_bones,(len(rig.data.bones),source_bones)
assert len(body.vertex_groups)>50 and len(body.data.vertices)>=13380
assert any(m.type=='ARMATURE' for m in body.modifiers)
assert rig.animation_data and rig.animation_data.action
errors={n:(rig.matrix_world@rig.data.bones[n].head_local-__import__('mathutils').Vector(pos)).length for n,pos in source_landmarks.items()}
assert max(errors.values())<1e-4,errors
report={'source_reopened':True,'height_m':source_height,'source_and_roundtrip_bones':source_bones,
 'fbx_reimported':True,'animation_action_present':True,'fbx_body_vertices':len(body.data.vertices),
 'landmark_error_m':errors,'eye_objects':len([o for o in bpy.context.scene.objects if o.name.startswith('CF01_Eye.')]),
 'engine_integration_tested':False,'artistic_acceptance':False}
(P/'export-verification.json').write_text(json.dumps(report,indent=2));print('PASS',json.dumps(report))
