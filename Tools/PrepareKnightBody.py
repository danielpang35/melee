"""Build the Knight body/armor authoring package without altering KN_v001 or CF.

The supplied sculpt has no complete underlying body. The body is derived from
CF topology/weights in the Knight skeleton's rest pose, never an existing clip.
"""
import hashlib
import math
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'Saved/ArtRuntime'))
import bpy
from mathutils import Matrix, Vector


def fit_point(point):
    """One similarity transform preserves the standalone anatomical shape.

    Armor clearance must never be obtained by crushing the body into its shell.
    Overall scale and placement seat the intact anatomy beneath the armor.
    """
    return Vector(point)*.96 + Vector((0.,.080,0.))

OUT = ROOT/'ArtSource/UserKnight/KN_v002'
OUT.mkdir(parents=True, exist_ok=True)
foundation = ROOT/'ArtSource/CharacterReset/CF_v001/CF_v001_Character.blend'
armor_source = ROOT/'ArtSource/UserKnight/KN_v001/Knight_Rig.blend'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {str(p.relative_to(ROOT)): sha(p) for p in [foundation, armor_source, ROOT/'Config/EXPreview.json']}
bpy.ops.wm.open_mainfile(filepath=str(armor_source))
rig = bpy.data.objects['KN01_Rig']
armor = bpy.data.objects['SK_UserKnight']
armor.name = 'KN01_Armor'
with bpy.data.libraries.load(str(foundation), link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n in ('CF01_CharacterRig','CF01_Body') or n.startswith('CF01_Eye.')]
loaded = [o for o in dst.objects if o]
for obj in loaded:
    bpy.context.scene.collection.objects.link(obj)
donor = next(o for o in loaded if o.type == 'ARMATURE')
donor.animation_data_clear()
for bone in donor.pose.bones:
    for constraint in list(bone.constraints):
        bone.constraints.remove(constraint)
    bone.matrix_basis = Matrix.Identity(4)
# Assign parent-first absolute rest transforms; this changes rest geometry only.
for bone in donor.pose.bones:
    bone.matrix = rig.data.bones[bone.name].matrix_local
    bpy.context.view_layer.update()
# Pose intact legs into the armor stance; rotate feet along the boot axes.
# Rotations preserve bone lengths and local anatomical proportions.
for side, sign in [('L',1),('R',-1)]:
    for name,angle,axis in [('upperleg01.'+side,-sign*math.radians(4),'Y'),
                            ('foot.'+side,sign*math.radians(20),'Z')]:
        bone=donor.pose.bones[name]
        pivot=bone.matrix.translation.copy()
        bone.matrix=Matrix.Translation(pivot)@Matrix.Rotation(angle,4,axis)@Matrix.Translation(-pivot)@bone.matrix
        bpy.context.view_layer.update()
fitted_rest={bone.name:bone.matrix.copy() for bone in donor.pose.bones}
body_meshes = [o for o in loaded if o.type == 'MESH']
assert body_meshes
for obj in body_meshes:
    bpy.ops.object.select_all(action='DESELECT')
    obj.hide_set(False); obj.hide_viewport = False; obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if obj.parent_type == 'BONE':
        world = obj.matrix_world.copy()
        for vertex in obj.data.vertices: vertex.co = world@vertex.co
        obj.parent = None; obj.parent_type = 'OBJECT'; obj.matrix_world = Matrix.Identity(4)
        obj.vertex_groups.new(name='head').add(list(range(len(obj.data.vertices))),1.,'REPLACE')
    for mod in list(obj.modifiers):
        if mod.type == 'ARMATURE':
            mod.object = donor
            bpy.ops.object.modifier_apply(modifier=mod.name)
    for vertex in obj.data.vertices:
        vertex.co = fit_point(vertex.co)
    obj.parent = rig
    mod = obj.modifiers.new('Knight body skin', 'ARMATURE'); mod.object = rig
    # Deformation must precede subdivision.
    bpy.ops.object.modifier_move_up(modifier=mod.name)
    obj['knight_role'] = 'body'
    obj.hide_render = False
body = next(o for o in body_meshes if o.name.startswith('CF01_Body'))
body.name = 'KN01_Body'
for obj in body_meshes:
    if obj != body: obj.name = obj.name.replace('CF01_', 'KN01_')
bpy.data.objects.remove(donor, do_unlink=True)
# Skin binding uses the fitted rest skeleton. No animation data is transferred.
bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='POSE')
for bone in rig.pose.bones:
    bone.matrix=fitted_rest[bone.name]
    bpy.context.view_layer.update()
bpy.ops.pose.armature_apply(selected=False)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.mode_set(mode='EDIT')
for bone in rig.data.edit_bones:
    bone.head = fit_point(bone.head); bone.tail = fit_point(bone.tail)
bpy.ops.object.mode_set(mode='OBJECT')
rig.data.name = 'KN02_BodySkeleton'
rig['knight_role'] = 'deform_rig'
armor['knight_role'] = 'armor'
armor['status'] = 'Supplied armor/clothing preserved; binding is initial only; deferred deformation work.'
body['provenance'] = 'CF_v001 topology fitted to KN01 rest skeleton; no hidden body was supplied in Knight FBX.'
scene = bpy.context.scene
scene['character_id'] = 'KN_v002'
scene['body_object'] = body.name
scene['deform_rig'] = rig.name
scene['body_provenance'] = body['provenance']
scene['armor_policy'] = 'Hidden by default. Enable Knight Armor (Deferred) collection for fitting only.'
for name, objects in [('Knight Body (Animate)', [rig, *body_meshes]), ('Knight Armor (Deferred)', [armor])]:
    collection = bpy.data.collections.new(name); scene.collection.children.link(collection)
    for obj in objects:
        for old in list(obj.users_collection): old.objects.unlink(obj)
        collection.objects.link(obj)
    if armor in objects:
        collection.hide_viewport = True; collection.hide_render = True
for action in list(bpy.data.actions):
    if action.users == 0: bpy.data.actions.remove(action)
scene.frame_start = 1; scene.frame_end = 60; scene.frame_set(1)
rig.show_in_front = True
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True); bpy.context.view_layer.objects.active = rig
source = OUT/'Knight_Animation.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source), compress=True)
# Runtime body only, on the new fitted KN02 rest skeleton.
bpy.ops.object.select_all(action='DESELECT')
for obj in [rig, *body_meshes]: obj.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(OUT/'SK_KnightBody.fbx'), use_selection=True,
    object_types={'ARMATURE','MESH'}, add_leaf_bones=False,
    use_armature_deform_only=False, bake_anim=False, axis_forward='-Y', axis_up='Z',
    global_scale=1., apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', path_mode='STRIP')
assert all(sha(ROOT/p) == value for p, value in before.items())
manifest = dict(character_id='KN_v002', body=body.name, rig=rig.name,
    body_origin=body['provenance'], armor=armor.name, armor_hidden=True,
    skeleton_compatible_with='KN02 independent fitted rest; KN_v001 names/hierarchy retained, rest transforms differ. Do not bind old clips.',
    fit='Anatomy preserved by uniform 0.96 scale and 0.08m rearward placement; 4-degree hip abduction and 20-degree outward foot rotation fit the stance. No head/limb compression or shell projection. Local armor refitting is deferred.',
    bones=len(rig.data.bones), source=source.name, runtime_body='SK_KnightBody.fbx',
    animation=None, protected_inputs=before,
    outputs={p.name:sha(p) for p in [source, OUT/'SK_KnightBody.fbx']},
    limitations='Foundation-derived body; initial proportions/weights, armor fit and final character art remain reviewable work. No animation acceptance.')
(OUT/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print('KNIGHT_BODY_PACKAGE_READY', json.dumps(manifest))
