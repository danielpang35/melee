"""Isolated KN_v002 transfer kit; run in background Blender, never the live UI.

No animation authorship, runtime import or source selection. The canonical guide
uses the original EX source clock; the runtime 500 ms release is metadata only.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'ArtSource/Cascadeur/KN_v002_20260912/Kit'
SOURCE = ROOT / 'ArtSource/UserKnight/KN_v002/Knight_Animation.blend'
MOTION = ROOT / 'ArtSource/CharacterReset/EX_v002/Export/EX_v002_WeaponMotion.json'
TEMPLATE = Path('C:/Program Files/Cascadeur/resources/autorig_templates/UE4_New.qrigcasc')
sys.path.insert(0, str(ROOT / 'Tools'))
from AnimationAuthoring import rig as controls


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def rows(matrix):
    return [list(row) for row in matrix]


def select(objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def export(name, objects, animated=False):
    select(objects)
    bpy.ops.export_scene.fbx(filepath=str(OUT / name), use_selection=True,
        object_types={'ARMATURE', 'MESH'}, add_leaf_bones=False,
        use_armature_deform_only=False, bake_anim=animated,
        bake_anim_use_all_bones=True, bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True,
        bake_anim_step=1., bake_anim_simplify_factor=0., axis_forward='-Y',
        axis_up='Z', global_scale=1., apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_NONE', path_mode='STRIP', use_mesh_modifiers=True)


def make_weapon_rig(name, prefix):
    data = bpy.data.armatures.new(name)
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    select([obj])
    bpy.ops.object.mode_set(mode='EDIT')
    root = data.edit_bones.new(prefix + 'Hilt')
    root.head, root.tail = (0, 0, 0), (0, .05, 0)
    for suffix, z in [('Tip', 1.035), ('PrimaryGrasp', -.070), ('SupportGrasp', -.195)]:
        bone = data.edit_bones.new(prefix + suffix)
        bone.head, bone.tail = (0, 0, z), (0, .025, z)
        bone.parent = root
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Never overwrite a published kit or someone else's pending artifacts.
    assert not (OUT / 'manifest.json').exists(), 'Kit already published; use a new dated take'
    protected_paths = [SOURCE, MOTION, ROOT / 'Config/EXPreview.json',
        ROOT / 'Config/CombatDefaults.json',
        ROOT / 'ArtSource/CharacterReset/EX_v002/EX_v002_MordhauRight.blend']
    protected = {str(p.relative_to(ROOT)): sha(p) for p in protected_paths}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    rig = bpy.data.objects[scene['deform_rig']]
    body = bpy.data.objects[scene['body_object']]
    assert len(rig.data.bones) == 102
    assert max(abs(rig.matrix_world[i][j] - Matrix.Identity(4)[i][j])
               for i in range(4) for j in range(4)) < 1.e-6
    rig.animation_data_clear()
    for pose in rig.pose.bones:
        pose.matrix_basis = Matrix.Identity(4)
        for constraint in list(pose.constraints):
            pose.constraints.remove(constraint)
    scene.frame_start, scene.frame_end = 1, 136
    scene.render.fps, scene.render.fps_base = 60, 1.
    scene.frame_set(1)
    bpy.context.view_layer.update()
    hierarchy = {b.name: b.parent.name if b.parent else None for b in rig.data.bones}
    rest = {b.name: b.matrix_local.copy() for b in rig.data.bones}
    body_parts = [rig, body, bpy.data.objects['KN01_Eye.R'], bpy.data.objects['KN01_Eye.L']]
    export('KN_v002_Authoring.fbx', body_parts)

    mapping = {'pelvis': 'root', 'stomach': 'spine03', 'chest': 'spine01',
               'neck': 'neck01', 'head': 'head'}
    for side in 'LR':
        for role, bone in [('clavicle', 'clavicle'), ('arm', 'upperarm01'),
                ('forearm', 'lowerarm01'), ('hand', 'wrist'), ('thigh', 'upperleg01'),
                ('calf', 'lowerleg01'), ('foot', 'foot'), ('toe', 'toe3-1')]:
            mapping[role + '_' + side.lower()] = bone + '.' + side
        for digit, role in enumerate(('thumb', 'index_finger', 'middle_finger', 'ring_finger', 'pinky'), 1):
            for segment in range(1, 4):
                mapping[f'{role}_{side.lower()}_{segment}'] = f'finger{digit}-{segment}.{side}'
    template = json.loads(TEMPLATE.read_text())
    # KN's serial split links are not UE's side-branch twist bones. Retain every
    # link but do not apply speculative UE twist axis/strength settings.
    template['Document'] = [d for d in template['Document'] if d['Title'] != 'Twist bones']
    for document in template['Document']:
        for section in document['Sections']:
            for entry in section['Names']:
                name = mapping[entry['Bone name']]
                entry['Joint name'] = name
                ancestry = []
                parent = rig.data.bones[name].parent
                while parent:
                    ancestry.insert(0, parent.name)
                    parent = parent.parent
                entry['Joint path'] = [rig.name, *ancestry]
    # Retain real rest pelvis orientation instead of silently changing the bind.
    template['Settings']['Is align pelvis'] = False
    write('KN_v002.qrigcasc', template)

    grasps = {side: controls.hand_calibration(rig, side) for side in 'RL'}
    grasp_metadata = {
        'space': 'Blender meters, column-vector matrices, +Z shaft points guardward',
        'wrist_local_primary': rows(grasps['R']), 'wrist_local_support': rows(grasps['L']),
        'hilt_from_primary': rows(Matrix.Translation((0, 0, .070))),
        'primary_from_hilt': rows(Matrix.Translation((0, 0, -.070))),
        'support_from_hilt': rows(Matrix.Translation((0, 0, -.195))),
        'support_from_primary': rows(Matrix.Translation((0, 0, -.125))),
        'note': 'Palm calibration and neutral shaft-relative support; support articulation remains authorable.'}
    write('grasps.json', grasp_metadata)
    primary = controls.empty('KitPrimaryGrasp')
    weapon = controls.weapon(primary)
    bpy.context.view_layer.update()
    parts = [bpy.data.objects['CF_' + n] for n in ('Blade', 'Guard', 'Grip', 'Pommel')]
    inverse = weapon.matrix_world.inverted()
    weapon_rig = make_weapon_rig('KN_Weapon', 'Weapon')
    weapon_meshes = []
    deps = bpy.context.evaluated_depsgraph_get()
    for part in parts:
        evaluated = part.evaluated_get(deps)
        mesh = bpy.data.meshes.new_from_object(evaluated, depsgraph=deps)
        mesh.transform(inverse @ evaluated.matrix_world)
        obj = bpy.data.objects.new('KN_' + part.name[3:], mesh)
        scene.collection.objects.link(obj)
        obj.parent = weapon_rig
        obj.vertex_groups.new(name='WeaponHilt').add(list(range(len(mesh.vertices))), 1., 'REPLACE')
        obj.modifiers.new('RigidSword', 'ARMATURE').object = weapon_rig
        weapon_meshes.append(obj)
    for obj in [*parts, weapon, primary]:
        bpy.data.objects.remove(obj, do_unlink=True)
    export('KN_v002_Weapon.fbx', [weapon_rig, *weapon_meshes])

    # EX source sample 18 is attack age zero. Keep source-clock time at 1x;
    # EXSourceClock later stretches .300 s source release to .500 s runtime.
    source = json.loads(MOTION.read_text())
    assert source['fps'] == 60 and len(source['samples']) == 154
    guide = make_weapon_rig('EX_CanonicalGuide', 'Guide')
    root = guide.pose.bones['GuideHilt']
    root.rotation_mode = 'QUATERNION'
    offset = Vector((0, .115, .02))
    guide_samples = []
    for index, sample in enumerate(source['samples'][18:], 1):
        world = sample['weapon_world']
        matrix = Quaternion(world['quaternion_wxyz']).to_matrix().to_4x4()
        matrix.translation = Vector(world['translation_m']) + offset
        scene.frame_set(index)
        root.matrix = matrix @ root.bone.matrix_local
        root.keyframe_insert('location', frame=index)
        root.keyframe_insert('rotation_quaternion', frame=index)
        guide_samples.append({'frame': index, 'ex_source_frame': index + 18,
            'source_attack_age_s': (index - 1) / 60,
            'ex_source_time_s': sample['time_s'], 'hilt_matrix': rows(matrix)})
    scene.timeline_markers.clear()
    for label, frame in [('ATTACK_SOURCE_START', 1), ('CANONICAL_RELEASE_START', 45),
                         ('CANONICAL_RELEASE_END', 63), ('SOURCE_END', 136)]:
        scene.timeline_markers.new(label, frame=frame)
    scene.frame_set(1)
    export('EX_CanonicalGuide_Source60.fbx', [guide], animated=True)
    write('guide-samples.json', {'fps': 60, 'samples': guide_samples})
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'KN_v002_ImportKit.blend'))

    # A single neutral transfer QA image, not an authored performance preview.
    # Park the separate sword for visibility only after saving the import kit.
    guide.hide_render = True
    weapon_rig.location = (-.8, 0, .35)
    camera_data = bpy.data.cameras.new('KitQACamera')
    camera = bpy.data.objects.new('KitQACamera', camera_data)
    scene.collection.objects.link(camera)
    camera.location = (2.5, -5., 2.6)
    camera.rotation_euler = (Vector((-.18, 0., .95)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera_data.type, camera_data.ortho_scale = 'ORTHO', 2.4
    scene.camera = camera
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.render.resolution_x, scene.render.resolution_y = 960, 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(OUT / 'neutral-kit.png')
    bpy.ops.render.render(write_still=True)

    # One-time contract evidence: full original hierarchy/rest positions and all
    # 136 guide frames, including explicit sword/grasp landmarks.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(OUT / 'KN_v002_Authoring.fbx'), use_anim=False)
    imported = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
    actual_hierarchy = {b.name: b.parent.name if b.parent else None for b in imported.data.bones}
    assert hierarchy == actual_hierarchy
    body_error = max((imported.matrix_world @ b.matrix_local.translation - rest[b.name].translation).length
                     for b in imported.data.bones) * 100
    bpy.ops.import_scene.fbx(filepath=str(OUT / 'KN_v002_Weapon.fbx'), use_anim=False)
    sword = bpy.data.objects['KN_Weapon']
    landmarks = {'WeaponHilt': 0., 'WeaponTip': 1.035, 'WeaponPrimaryGrasp': -.070, 'WeaponSupportGrasp': -.195}
    sword_error = max((sword.matrix_world @ sword.data.bones[n].head_local - Vector((0, 0, z))).length
                      for n, z in landmarks.items()) * 100
    bpy.context.scene.render.fps = 60
    bpy.ops.import_scene.fbx(filepath=str(OUT / 'EX_CanonicalGuide_Source60.fbx'), anim_offset=0.)
    imported_guide = bpy.data.objects['EX_CanonicalGuide']
    guide_error = 0.
    for sample in guide_samples:
        bpy.context.scene.frame_set(sample['frame'])
        bpy.context.view_layer.update()
        expected = Matrix(sample['hilt_matrix'])
        for name, z in landmarks.items():
            observed = imported_guide.matrix_world @ imported_guide.pose.bones[name.replace('Weapon', 'Guide')].head
            guide_error = max(guide_error, (observed - expected @ Vector((0, 0, z))).length * 100)
    unchanged = all(sha(ROOT / path) == identity for path, identity in protected.items())
    receipt = dict(passed=unchanged and body_error < .01 and sword_error < .01 and guide_error < .01,
        body_bones=102, hierarchy_preserved=True, body_rest_position_error_cm=body_error,
        weapon_landmark_error_cm=sword_error, guide_landmark_error_cm=guide_error,
        guide_frames=136, fps=60, protected_unchanged=unchanged,
        limits='Blender FBX reimport only. Cascadeur rig generation, serial splits, editable controls, performance and engine fidelity unverified.')
    write('reimport-verification.json', receipt)
    assert receipt['passed'], receipt
    write('manifest.json', dict(schema_version=1, policy='MCL-DEV-2026-09-08',
        purpose='Isolated KN technical transfer kit; no authored take or selection',
        source=str(SOURCE.relative_to(ROOT)), protected=protected, body='KN01_Body', rig='KN01_Rig',
        root_rest_head_m=list(rest['root'].translation),
        root_semantics='Anatomical pelvis, not floor/actor root. No actor or root motion is inferred.',
        hierarchy=hierarchy, qrig_mapping=mapping, qrig_template_sha256=sha(TEMPLATE),
        mapping_limits='Body and fingers mapped; all 102 bones retained. Serial split02 bones, extra spine/neck/metacarpal/toe channels remain native unmapped joints. No speculative twist solver.',
        coordinates='Blender meters, FBX -Y forward +Z up; Cascadeur import conversion must be verified.',
        neutral_tp_offset_m=list(offset), guide_origin='EX source .30s = guide frame1 = source attack age0',
        release_guide_frames=[45, 63], release_source_attack_age_s=[44/60, 62/60],
        ex_source_release_s=[62/60, 80/60], source_release_duration_s=.3,
        runtime_release_duration_s=json.loads((ROOT/'Config/CombatDefaults.json').read_text(encoding='utf-8-sig'))['EXReleaseDuration'],
        runtime_clock='EXSourceClock owns phase mapping; do not bake .5s into this .3s guide and apply mapping again.',
        files={p.name: sha(p) for p in OUT.iterdir() if p.is_file()},
        artistic_acceptance=False, cascadeur_verified=False))
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
