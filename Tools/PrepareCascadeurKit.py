"""Build a Cascadeur import kit and verify its FBX round trip using Blender.

The moving sword and grip guides are sampled from the unchanged combat code.
Character animation is deliberately left to Cascadeur authoring.
"""
import sys,csv,json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy
from mathutils import Vector,Matrix
OUT=ROOT/'ArtSource/Cascadeur';OUT.mkdir(exist_ok=True,parents=True)
source=ROOT/'ArtSource/Citadel/Export/CitadelKnight_Performance.blend'
if not source.exists():source=ROOT/'ArtSource/Citadel/Export/CitadelKnight_Rig.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
rig=bpy.data.objects['CitadelRig'];body=bpy.data.objects['SK_CitadelKnight']
original_bones={b.name for b in rig.data.bones}
def select(objects):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
select([rig]);bpy.ops.object.mode_set(mode='EDIT')
for side in ['r','l']:
    foot=rig.data.edit_bones['foot_'+side]
    toe=rig.data.edit_bones.new('ball_'+side);toe.head=foot.tail;toe.tail=toe.head+Vector((0,-.035,0));toe.parent=foot
bpy.ops.object.mode_set(mode='OBJECT')
def export(path,objects,animation=False):
    select(objects)
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,add_leaf_bones=False,
        bake_anim=animation,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0.,
        axis_forward='-Y',axis_up='Z',path_mode='COPY',embed_textures=True)
export(OUT/'Knight_Authoring.fbx',[rig,body])

# Adapt the vendor UE4 quick-rig mapping to this actual skeleton. Missing
# fingers/twist bones are not fabricated; fixed grip gloves remain fixed.
template=json.load(open('C:/Program Files/Cascadeur/resources/autorig_templates/UE4_New.qrigcasc'))
template['Document']=[d for d in template['Document'] if d['Title']=='Body']
for section in template['Document'][0]['Sections']:
    for row in section['Names']:
        name='neck' if row['Joint name']=='neck_01' else row['Joint name']
        row['Joint name']=name
        parent=rig.data.bones[name].parent;path=[]
        while parent:path.insert(0,parent.name);parent=parent.parent
        row['Joint path']=path
(OUT/'Knight.qrigcasc').write_text(json.dumps(template,indent=2))

existing=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'ArtSource/Citadel/Export/SM_CitadelSword.fbx'))
sword=next(o for o in bpy.data.objects if o not in existing and o.type=='MESH')
for image in bpy.data.images:
    if image.source=='FILE' and not Path(bpy.path.abspath(image.filepath)).exists():
        candidate=ROOT/'ArtSource/Citadel/antique_estoc/textures'/Path(image.filepath).name
        if candidate.exists():image.filepath=str(candidate)
select([sword]);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
sword.name='ReferenceSwordMesh'
blade_length=1.10
for v in sword.data.vertices:v.co*=blade_length

bpy.ops.object.armature_add();guide=bpy.context.object;guide.name='WeaponReference'
bpy.ops.object.mode_set(mode='EDIT');guide.data.edit_bones.remove(guide.data.edit_bones[0])
base=guide.data.edit_bones.new('ReferenceHilt');base.head=(0,0,0);base.tail=(0,0,.15)
for name,z in [('ReferenceTip',blade_length),('RightGripGuide',-.12*blade_length/1.103061375617981),('LeftGripGuide',-.23*blade_length/1.103061375617981)]:
    b=guide.data.edit_bones.new(name);b.head=(0,0,z);b.tail=(0,0,z+.035);b.parent=base
bpy.ops.object.mode_set(mode='OBJECT')
sword.vertex_groups.clear();sword.vertex_groups.new(name='ReferenceHilt').add(list(range(len(sword.data.vertices))),1.,'REPLACE')
mod=sword.modifiers.new('Reference weapon','ARMATURE');mod.object=guide;sword.parent=guide
rows=list(csv.DictReader(open(OUT/'right_cut_reference.csv')))
scene=bpy.context.scene;scene.render.fps=120;scene.frame_start=1;scene.frame_end=len(rows)
def vec(row,prefix):return Vector((float(row[prefix+'_x']),-float(row[prefix+'_y']),float(row[prefix+'_z'])))/100
bone=guide.pose.bones['ReferenceHilt'];bone.rotation_mode='QUATERNION'
reference=[]
for row in rows:
    frame=int(row['frame']);hilt=vec(row,'hilt');axis=(vec(row,'tip')-hilt).normalized();edge=vec(row,'edge').normalized()
    normal=axis.cross(edge).normalized();edge=normal.cross(axis).normalized()
    matrix=Matrix((edge,normal,axis)).transposed().to_4x4();matrix.translation=hilt
    scene.frame_set(frame);bone.matrix=matrix@guide.data.bones['ReferenceHilt'].matrix_local
    bone.keyframe_insert('location',frame=frame);bone.keyframe_insert('rotation_quaternion',frame=frame)
    reference.append((frame,hilt.copy(),vec(row,'tip'),vec(row,'right'),vec(row,'left')))
for curve in guide.animation_data.action.fcurves:
    for key in curve.keyframe_points:key.interpolation='LINEAR'
for label,frame in [('START_LOAD',31),('START_RELEASE',100),('START_RECOVERY',160),('RETURN_IDLE',241)]:
    scene.timeline_markers.new(label,frame=frame)
export(OUT/'RightCut_WeaponReference.fbx',[guide,sword],True)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Cascadeur_ImportKit.blend'))

# Reimport the actual exported reference and verify handedness, units and
# sampled hilt, tip and both grip positions, rather than trusting exporter flags.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.fps=120
bpy.ops.import_scene.fbx(filepath=str(OUT/'RightCut_WeaponReference.fbx'),anim_offset=0.)
imported=next(o for o in bpy.data.objects if o.type=='ARMATURE')
maximum=0.
for frame,hilt,tip,right,left in reference:
    bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
    for name,expected in [('ReferenceHilt',hilt),('ReferenceTip',tip),('RightGripGuide',right),('LeftGripGuide',left)]:
        observed=imported.matrix_world@imported.pose.bones[name].head
        maximum=max(maximum,(observed-expected).length)
if maximum>.0005:raise RuntimeError(f'FBX reference round trip error {maximum*100:.4f} cm')
manifest={'stage':'prepared_not_yet_imported_into_cascadeur','fps':120,'frames':len(rows),
    'lead_in_seconds':.25,'strike_seconds':[.575,.5,.675],
    'max_weapon_and_grip_roundtrip_error_cm':maximum*100,
    'original_bones':sorted(original_bones),'authoring_only_bones':['ball_l','ball_r'],
    'mesh_source':str(source),'mesh_review':'candidate; not engine-accepted',
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
        ROOT/'Source/MeleeCombatLab/Combat/Attacks/AttackTrajectory.h',ROOT/'Source/MeleeCombatLab/Combat/CombatSimulation.cpp',
        ROOT/'Config/CombatDefaults.json',OUT/'Knight_Authoring.fbx',OUT/'RightCut_WeaponReference.fbx']}}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(f'CASCADEUR KIT VERIFIED: {len(rows)} frames, maximum weapon/grip roundtrip error {maximum*100:.6f} cm',flush=True)
sys.stdout.flush();sys.stderr.flush()
import os
os._exit(0)
