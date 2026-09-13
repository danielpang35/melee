"""Export TP_v001 at native 60 Hz without editing source or any EX/CF baseline.

Run with the existing Python/bpy runtime. Weapon is metadata, not part of the
skeletal FBX. Unreal receives the full CF body on its independent TP skeleton.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Saved/ArtRuntime'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'ArtSource/CharacterReset/TP_v001/TP_v001_RightHorizontal.blend')
    parser.add_argument('--out', type=Path, default=ROOT / 'ArtSource/CharacterReset/TP_v001/Export')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None)
    import bpy
    from mathutils import Matrix

    source = args.source.resolve()
    out = args.out.resolve()
    assert source.parent.name == 'TP_v001', 'Only the separate TP source may be exported'
    out.mkdir(parents=True, exist_ok=True)
    preserved = [ROOT / 'Config/EXPreview.json', ROOT / 'ArtSource/CharacterReset/CF_v001/CF_v001_Character.blend',
                 ROOT / 'ArtSource/CharacterReset/CF_v001/CF_v001_Character.fbx',
                 ROOT / 'ArtSource/CharacterReset/EX_v002/EX_v002_MordhauRight.blend']
    identities = {str(p): sha(p) for p in [source, *preserved]}
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene = bpy.context.scene
    assert scene.render.fps / scene.render.fps_base == 60 and scene.frame_start == 1 and scene.frame_end == 154
    assert abs(scene.unit_settings.scale_length - 1) < 1e-8
    rig = bpy.data.objects['CF01_CharacterRig']
    body = bpy.data.objects['CF01_Body']
    weapon = bpy.data.objects['TP01_WeaponRoot']
    base, tip = [bpy.data.objects[n] for n in ('TP01_BladeBase', 'TP01_BladeTip')]
    assert len(rig.data.bones) == 102 and rig.animation_data and rig.animation_data.action
    hierarchy = {b.name: b.parent.name if b.parent else None for b in rig.data.bones}
    rest = {b.name: b.matrix_local.copy() for b in rig.data.bones}
    samples, skeleton, subframes = [], [], []

    def transform(matrix):
        p, q, s = matrix.decompose()
        return dict(translation_m=list(p), quaternion_wxyz=list(q), scale=list(s))

    def snapshot(time):
        frame = 1 + time * 60
        scene.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
        deps = bpy.context.evaluated_depsgraph_get()
        r = rig.evaluated_get(deps)
        assert max(abs(r.matrix_world[i][j] - Matrix.Identity(4)[i][j]) for i in range(4) for j in range(4)) < 1e-6, 'Rig object must remain in place'
        bones = {}
        for p in r.pose.bones:
            world = r.matrix_world @ p.matrix
            deformation = world @ rest[p.name].inverted()
            bones[p.name] = dict(head_world_m=list(world.translation),
                                 deformation_quaternion_wxyz=list(deformation.to_quaternion().normalized()),
                                 component_scale=list(world.to_scale()))
        wm = weapon.evaluated_get(deps).matrix_world.copy()
        bp = base.evaluated_get(deps).matrix_world.translation.copy()
        tp = tip.evaluated_get(deps).matrix_world.translation.copy()
        from mathutils import Vector
        assert (bp - wm.translation).length < 1e-5
        assert (tp - wm @ Vector((0, 0, 1.035))).length < 1e-5
        assert max(abs(s - 1) for s in wm.to_scale()) < 1e-5
        return dict(time_s=time, weapon_world=transform(wm), blade_base_world_m=list(bp), blade_tip_world_m=list(tp)), dict(time_s=time, bones=bones)

    for i in range(154):
        w, b = snapshot(i / 60)
        w['frame'] = i + 1
        samples.append(w)
        skeleton.append(b)
    # Offsets here are zero-based: carry keys at Blender88/94/100 are87/93/99.
    subframe_offsets = (18.5, 61.5, 62.5, 67.5, 72.5, 79.5, 80.5, 118.5, 152.5,
                        86.5, 87.5, 92.5, 93.5, 98.5, 99.5)
    for offset in sorted(subframe_offsets):
        _, b = snapshot(offset / 60)
        subframes.append(b)
    diagnostic_times = sorted({0., .30, 62/60, 68/60, 80/60, 118/60, 2.55,
                               87/60, 93/60, 99/60, *[o/60 for o in subframe_offsets]})
    scene.frame_set(1)
    selected = {rig, body}
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.parent == rig and obj.parent_type == 'BONE':
            selected.add(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in selected:
        obj.select_set(True)
    exported_names = sorted(o.name for o in selected)
    bpy.context.view_layer.objects.active = rig
    fbx = out / 'TP_v001_RightHorizontal.fbx'
    bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={'ARMATURE', 'MESH'},
                            add_leaf_bones=False, use_armature_deform_only=False, bake_anim=True,
                            bake_anim_use_all_bones=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                            bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=0.0,
                            axis_forward='-Y', axis_up='Z', global_scale=1.0, apply_unit_scale=True,
                            apply_scale_options='FBX_SCALE_NONE', path_mode='STRIP', use_mesh_modifiers=True)
    # Preserve the separately authored grip/guard geometry in weapon-local space.
    # Temporary evaluated copies live only in this exporter process; no source save.
    deps = bpy.context.evaluated_depsgraph_get()
    weapon_inverse = weapon.evaluated_get(deps).matrix_world.inverted()
    weapon_parts = [o for o in bpy.data.objects if o.type == 'MESH' and o.parent == weapon]
    assert {o.name for o in weapon_parts} == {'TP01_Blade', 'TP01_Guard', 'TP01_Grip', 'TP01_Pommel'}
    weapon_materials = {m.name: dict(color=list(m.diffuse_color), metallic=m.metallic, roughness=m.roughness)
                        for o in weapon_parts for m in o.data.materials if m}
    bpy.ops.object.select_all(action='DESELECT')
    for obj in weapon_parts:
        evaluated = obj.evaluated_get(deps)
        data = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=deps)
        copy = bpy.data.objects.new('Export_' + obj.name, data)
        bpy.context.collection.objects.link(copy)
        copy.matrix_world = weapon_inverse @ evaluated.matrix_world
        copy.select_set(True)
    weapon_fbx = out / 'TP_v001_Weapon.fbx'
    bpy.ops.export_scene.fbx(filepath=str(weapon_fbx), use_selection=True, object_types={'MESH'},
                            bake_anim=False, axis_forward='-Y', axis_up='Z', global_scale=1.,
                            apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', path_mode='STRIP')
    write(out / 'TP_v001_WeaponMotion.json', dict(schema_version=1, fps=60, samples=samples,
          authority='TP visual only; never collision authority', source_sha256=identities[str(source)]))
    write(out / 'TP_v001_SkeletonMotion.json', dict(schema_version=2, fps=60, samples=skeleton,
          diagnostic_subframes=subframes, diagnostic_profile='TP_uniform_component_scale_carry_v1',
          diagnostic_sample_times_s=diagnostic_times,
          component_scale_space='Evaluated world pose matrix column magnitudes; rig object identity; compare temporal ratios for uniform authored stretch',
          bone_hierarchy=hierarchy, source_sha256=identities[str(source)]))
    # One FBX roundtrip catches exported joint translations/twist loss. It does
    # not replace the runtime's independent source-to-native import gate.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps = 60
    bpy.ops.import_scene.fbx(filepath=str(fbx), anim_offset=0.0)
    imported = bpy.data.objects['CF01_CharacterRig']
    bpy.context.view_layer.objects.active = imported
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in imported.data.edit_bones:
        bone.use_connect = False
    bpy.ops.object.mode_set(mode='OBJECT')
    assert hierarchy == {b.name: b.parent.name if b.parent else None for b in imported.data.bones}
    from mathutils import Quaternion, Vector
    max_position = max_rotation = 0.0
    for i, row in enumerate(skeleton):
        bpy.context.scene.frame_set(i + 1)
        r = imported.evaluated_get(bpy.context.evaluated_depsgraph_get())
        for p in r.pose.bones:
            expected = row['bones'][p.name]
            world = r.matrix_world @ p.matrix
            max_position = max(max_position, (world.translation - Vector(expected['head_world_m'])).length)
            actual = (world @ p.bone.matrix_local.inverted()).to_quaternion().normalized()
            target = Quaternion(expected['deformation_quaternion_wxyz'])
            max_rotation = max(max_rotation, 2 * math.acos(min(1.0, abs(actual.dot(target)))))
    unchanged = all(sha(Path(path)) == identity for path, identity in identities.items())
    receipt = dict(source_sha256=identities[str(source)], preserved_identities=identities,
                   source_and_baselines_unchanged=unchanged, fps=60, frames=154,
                   roundtrip_position_error_cm=max_position * 100, roundtrip_rotation_error_deg=math.degrees(max_rotation),
                   source_to_native_engine_gate='Loader checks every bone at all154 frames; pending engine import',
                   artistic_acceptance=False)
    receipt['passed'] = unchanged and max_position <= .001 and math.degrees(max_rotation) <= .15
    write(out / 'export-verification.json', receipt)
    assert receipt['passed'], receipt
    manifest = dict(schema_version=1, profile='TP_native_60_v1', source=str(source.relative_to(ROOT)),
                    source_sha256=identities[str(source)], exporter_sha256=sha(Path(__file__)),
                    fps=60, start_frame=1, end_frame=154, duration_s=2.55,
                    gameplay_source_start=.30, release_source=[62/60, 80/60],
                    bone_hierarchy=hierarchy, exported_objects=exported_names,
                    weapon_materials=weapon_materials,
                    files={p.name: sha(p) for p in (fbx, weapon_fbx, out/'TP_v001_WeaponMotion.json', out/'TP_v001_SkeletonMotion.json')},
                    authority='Separate authored TP interpretation; no canonical or FP replacement', artistic_acceptance=False)
    write(out / 'manifest.json', manifest)
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
