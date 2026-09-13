"""Export the evaluated EX exchange and verify one FBX roundtrip. Never saves source.

Run with the workspace Python that loads Saved/ArtRuntime/bpy, or Blender --python.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Saved/ArtRuntime'))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def transform(matrix):
    p, q, s = matrix.decompose()
    return {'translation_m': list(p), 'quaternion_wxyz': list(q), 'scale': list(s),
            'matrix_row_major': [list(row) for row in matrix]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'ArtSource/CharacterReset/EX_v001/EX_v001_Exchange.blend')
    parser.add_argument('--out', type=Path, default=ROOT / 'ArtSource/CharacterReset/EX_v001/Export')
    parser.add_argument('--rig', default='CF01_CharacterRig')
    parser.add_argument('--weapon', default='EX01_WeaponRoot')
    parser.add_argument('--base', default='EX01_BladeBase')
    parser.add_argument('--tip', default='EX01_BladeTip')
    parser.add_argument('--baseline', type=Path, help='Preserved identity receipt; required for EX_v002')
    parser.add_argument('--position-tolerance-m', type=float, default=0.001)
    parser.add_argument('--rotation-tolerance-rad', type=float, default=0.002)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None)
    import bpy
    from mathutils import Vector
    args.source = args.source.resolve()
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, exist_ok=True)
    source_hash = sha256(args.source)
    candidate = args.source.parent.name == 'EX_v002'
    identities = json.loads((args.baseline or ROOT / 'Docs/RIGHT_HORIZONTAL_BASELINE_IDENTITY.json').read_text()) if candidate else []
    assert all(sha256(Path(i['Path'])).lower() == i['Hash'].lower() for i in identities), 'Preserved baseline identity mismatch'
    controls = json.loads((args.source.parent / 'pose-controls.json').read_text()) if candidate else {}
    bpy.ops.wm.open_mainfile(filepath=str(args.source))
    scene = bpy.context.scene
    fps = scene.render.fps / scene.render.fps_base
    assert abs(fps - (60 if candidate else 30)) < 1e-8, f'Unexpected fps {fps}'
    assert abs(scene.unit_settings.scale_length - 1) < 1e-8, 'Expected meter scene units'
    start, end = scene.frame_start, scene.frame_end
    assert end > start
    rig, weapon, base, tip = [bpy.data.objects[n] for n in (args.rig, args.weapon, args.base, args.tip)]
    assert rig.type == 'ARMATURE'
    assert rig.animation_data and (rig.animation_data.action or rig.animation_data.nla_tracks), 'No authored skeleton animation'
    phases = [{'name': m.name, 'frame': m.frame, 'time_s': (m.frame-start)/fps}
              for m in sorted(scene.timeline_markers, key=lambda m: m.frame) if start <= m.frame <= end]
    assert phases, 'Explicit phase timeline markers required'
    boundaries = sorted({start, end, *[p['frame'] for p in phases]})
    hierarchy = {b.name: b.parent.name if b.parent else None for b in rig.data.bones}
    rest = {b.name: {'head_m': list(b.head_local), 'tail_m': list(b.tail_local), 'basis': transform(b.matrix_local)} for b in rig.data.bones}
    action_name = rig.animation_data.action.name if rig.animation_data.action else None
    selected = {rig, weapon, base, tip}
    for obj in scene.objects:
        if any(m.type == 'ARMATURE' and m.object == rig for m in obj.modifiers):
            selected.add(obj)
        parent = obj.parent
        while parent:
            if parent in (rig, weapon):
                selected.add(obj)
                break
            parent = parent.parent
    # Hidden eyes and authoring grip/elbow helpers are not part of FP delivery.
    selected = {o for o in selected if not o.hide_render or o in (rig, weapon, base, tip)}
    # Include canonical ancestors so FBX preserves source parenting and constraints.
    for obj in list(selected):
        parent = obj.parent
        while parent:
            selected.add(parent)
            parent = parent.parent
    snapshots = {}
    samples = []
    skeletal_samples = []
    camera = scene.camera
    camera_contract = {'name': camera.name, 'world': transform(camera.matrix_world),
        'type': camera.data.type, 'lens_mm': camera.data.lens, 'sensor_width_mm': camera.data.sensor_width,
        'sensor_height_mm': camera.data.sensor_height, 'sensor_fit': camera.data.sensor_fit,
        'shift_x': camera.data.shift_x, 'shift_y': camera.data.shift_y,
        'clip_start_m': camera.data.clip_start, 'clip_end_m': camera.data.clip_end,
        'resolution': [scene.render.resolution_x, scene.render.resolution_y],
        'resolution_percentage': scene.render.resolution_percentage,
        'pixel_aspect': [scene.render.pixel_aspect_x, scene.render.pixel_aspect_y]}
    mesh_frames = sorted(set([start, end] + [p['frame'] for p in phases]))
    source_meshes = {}
    mesh_cache = {}
    def mesh_snapshot():
        deps = bpy.context.evaluated_depsgraph_get()
        result = {}
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.name in mesh_names:
                evaluated = obj.evaluated_get(deps)
                mesh = evaluated.to_mesh()
                result[obj.name] = [list(evaluated.matrix_world @ v.co) for v in mesh.vertices]
                evaluated.to_mesh_clear()
        return result
    mesh_names = {o.name for o in selected if o.type == 'MESH'}
    # Render one central-passage source frame with the saved preview settings.
    preview_receipt = {'checked': False}
    if candidate:
        import numpy as np
        preview_frame = 1 + round((controls['events']['CentralPassage'] - controls['start_time']) * fps)
        scene.frame_set(preview_frame)
        scene.render.filepath = str(args.out / 'source-projection-check.png')
        bpy.ops.render.render(write_still=True)
        prior = args.source.parent / 'Preview/FP' / f'{preview_frame:04d}.png'
        a = bpy.data.images.load(str(prior), check_existing=False)
        b = bpy.data.images.load(scene.render.filepath, check_existing=False)
        ap = np.empty(len(a.pixels), dtype=np.float32); a.pixels.foreach_get(ap)
        bpixels = np.empty(len(b.pixels), dtype=np.float32); b.pixels.foreach_get(bpixels)
        identical = list(a.size) == list(b.size) and np.array_equal(ap, bpixels)
        bpy.data.images.remove(a); bpy.data.images.remove(b)
        preview_receipt = {'checked': True, 'frame': preview_frame, 'existing_preview': str(prior.relative_to(ROOT)),
            'existing_preview_sha256': sha256(prior), 'pixel_identical': identical}

    def rotation_error(a, b):
        # q and -q encode the same rotation; compare the shortest angular distance.
        return 2 * math.acos(min(1.0, abs(a.normalized().dot(b.normalized()))))

    def snapshot(frame, current_rig, current_weapon, current_base, current_tip):
        scene.frame_set(frame)
        deps = bpy.context.evaluated_depsgraph_get()
        r = current_rig.evaluated_get(deps)
        w = current_weapon.evaluated_get(deps).matrix_world.copy()
        b = current_base.evaluated_get(deps).matrix_world.translation.copy()
        t = current_tip.evaluated_get(deps).matrix_world.translation.copy()
        # FBX without leaf bones reconstructs display tail lengths. Compare the
        # actual joint head and the canonical source rest tail under deformation.
        deformation = {p.name: r.matrix_world @ p.matrix @ p.bone.matrix_local.inverted() for p in r.pose.bones}
        bones = {p.name: [list(r.matrix_world @ p.head),
                         list(deformation[p.name] @ Vector(rest[p.name]['tail_m'])),
                         list(deformation[p.name].to_scale())]
                 for p in r.pose.bones if p.name in rest}
        # Pose * inverse(rest) cancels fixed FBX bone-local basis conversions.
        # Unlike head/tail positions, this detects axial wrist/finger/twist loss.
        rotations = {p.name: deformation[p.name].to_quaternion()
                     for p in r.pose.bones}
        return r.matrix_world.copy(), w, b, t, bones, rotations

    for frame in range(start, end+1):
        rm, wm, bp, tp, bones, rotations = snapshot(frame, rig, weapon, base, tip)
        inverse = rm.inverted()
        deps = bpy.context.evaluated_depsgraph_get()
        erig = rig.evaluated_get(deps)
        skeletal_samples.append({'frame': frame, 'time_s': (frame-start)/fps, 'bones': {
            p.name: {'pose_rig_space': transform(p.matrix), 'local_channels': transform(p.matrix_basis),
                     'deformation_world': transform(rm @ p.matrix @ p.bone.matrix_local.inverted())}
            for p in erig.pose.bones}})
        evaluated_meshes = mesh_snapshot()
        for name, vertices in evaluated_meshes.items():
            mesh_cache.setdefault(name, []).append(vertices)
        if frame in mesh_frames:
            source_meshes[frame] = evaluated_meshes
        samples.append({'frame': frame, 'time_s': (frame-start)/fps,
                        'rig_world': transform(rm), 'weapon_world': transform(wm),
                        'weapon_rig_space': transform(inverse @ wm),
                        'blade_base_world_m': list(bp), 'blade_tip_world_m': list(tp),
                        'blade_base_rig_space_m': list(inverse @ bp),
                        'blade_tip_rig_space_m': list(inverse @ tp)})
        snapshots[frame] = (rm, wm, bp, tp, bones, rotations)
    prefix = 'EX_v002' if candidate else 'EX_v001'
    fbx = args.out / (args.source.stem + '.fbx')
    motion = args.out / (prefix + '_WeaponMotion.json')
    skeleton = args.out / (prefix + '_SkeletonMotion.json')
    import numpy as np
    cache_path = args.out / (prefix + '_EvaluatedMeshWorld.npz')
    arrays = {name: np.asarray(vertices, dtype=np.float32) for name, vertices in mesh_cache.items()}
    np.savez_compressed(cache_path, **arrays)
    with np.load(cache_path) as loaded:
        cache_verified = all(np.array_equal(array, loaded[name]) for name, array in arrays.items())
    write(skeleton, {'schema_version': 2, 'fps': fps, 'samples': skeletal_samples})
    write(motion, {'schema_version': 1, 'fps': fps, 'start_frame': start, 'end_frame': end,
                   'authority': 'FP source weapon motion; NOT accepted collision authority',
                   'time_origin': 'start_frame = 0 seconds', 'samples': samples})
    scene.frame_set(start)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in selected:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={'ARMATURE', 'MESH', 'EMPTY'},
        add_leaf_bones=False, use_armature_deform_only=False, bake_anim=True,
        bake_anim_use_all_bones=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=0.0,
        axis_forward='-Y', axis_up='Z', global_scale=1.0, apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_NONE', path_mode='STRIP', use_mesh_modifiers=True)
    manifest = {'schema_version': 1, 'source': str(args.source.relative_to(ROOT)),
        'source_sha256': source_hash, 'exporter_sha256': sha256(Path(__file__)),
        'blender_version': bpy.app.version_string, 'fps': fps, 'start_frame': start, 'end_frame': end,
        'sample_count': len(samples), 'time_origin': 'start_frame = 0 seconds',
        'units': 'meters', 'scene_unit_scale': scene.unit_settings.scale_length,
        'axes': {'up': '+Z', 'forward': '-Y', 'anatomical_right': '-X', 'handedness': 'right'},
        'quaternion_order': 'w,x,y,z', 'matrix_layout': 'row-major, column-vector multiplication',
        'spaces': {'world': 'evaluated Blender world', 'rig_space': 'inverse evaluated rig object world times world; not root-bone space'},
        'canonical_objects': {'rig': rig.name, 'weapon': weapon.name, 'blade_base': base.name, 'blade_tip': tip.name},
        'weapon_local_axis': '+Z from blade base toward tip', 'phase_markers': phases,
        'action': action_name, 'bone_hierarchy': hierarchy, 'rest_bones_rig_space': rest,
        'exported_objects': sorted(o.name for o in selected),
        'fbx_export': {'forward': '-Y', 'up': 'Z', 'global_scale': 1, 'full_skeleton': True, 'sample_step_frames': 1},
        'camera_projection': camera_contract, 'preview_identity': preview_receipt,
        'evaluated_mesh_cache': {'file': cache_path.name, 'space': 'Blender world meters', 'dtype': 'float32',
            'layout': 'Each named mesh is [inclusive frame index, evaluated vertex index, xyz]; frame index 0=start_frame',
            'authority': 'Exact source evaluated vertex positions; FBX skinning approximates post-armature subdivision',
            'shapes': {n: list(a.shape) for n,a in arrays.items()}},
        'preserved_baseline_identities': identities,
        'capture_start_time_s': controls.get('start_time'),
        'observed_events_capture_seconds': controls.get('events'),
        'phase_semantics': 'Observed visual labels only; no approved gameplay release inferred',
        'authority': 'Approved FP baseline; weapon motion NOT accepted collision authority' if candidate else 'Unapproved candidate',
        'files': {fbx.name: sha256(fbx), motion.name: sha256(motion), skeleton.name: sha256(skeleton), cache_path.name: sha256(cache_path)},
        'artistic_acceptance': False, 'engine_integration_tested': False}
    write(args.out / 'manifest.json', manifest)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = round(fps)
    scene.render.fps_base = 1
    bpy.ops.import_scene.fbx(filepath=str(fbx), anim_offset=0.0)
    imported = [bpy.data.objects[n] for n in (args.rig, args.weapon, args.base, args.tip)]
    irig = imported[0]
    # FBX importer reconnects coincident rest joints, suppressing authored local
    # translations on the dedicated FP action. Keep hierarchy, permit translations.
    bpy.context.view_layer.objects.active = irig
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in irig.data.edit_bones:
        bone.use_connect = False
    bpy.ops.object.mode_set(mode='OBJECT')
    ihierarchy = {b.name: b.parent.name if b.parent else None for b in irig.data.bones}
    errors = []
    observed = {}
    mesh_errors = []
    for frame in range(start, end+1):
        rm, wm, bp, tp, bones, rotations = snapshot(frame, *imported)
        observed[frame] = bones
        if frame in source_meshes:
            imported_meshes = mesh_snapshot()
            for name, vertices in source_meshes[frame].items():
                other = imported_meshes.get(name, [])
                same_count = len(vertices) == len(other)
                mesh_errors.append({'frame': frame, 'mesh': name, 'source_vertices': len(vertices),
                    'imported_vertices': len(other), 'topology_count_matches': same_count,
                    'max_vertex_error_m': max(((Vector(a)-Vector(b)).length for a,b in zip(vertices,other)), default=0) if same_count else None})
        srm, swm, sbp, stp, sbones, srotations = snapshots[frame]
        common = set(bones) & set(sbones)
        bone_angles = {n: rotation_error(rotations[n], srotations[n]) for n in common}
        worst_bone = max(bone_angles, key=bone_angles.get)
        errors.append({'frame': frame,
            'phase_boundary': frame in boundaries,
            'bone_endpoint_max_error_m': max((Vector(bones[n][j])-Vector(sbones[n][j])).length for n in common for j in (0,1)),
            'bone_deformation_rotation_max_error_rad': bone_angles[worst_bone],
            'bone_deformation_scale_max_error': max(abs(a-b) for n in common for a,b in zip(bones[n][2], sbones[n][2])),
            'worst_rotation_bone': worst_bone,
            'weapon_position_error_m': (wm.translation-swm.translation).length,
            'weapon_rotation_error_rad': rotation_error(wm.to_quaternion(), swm.to_quaternion()),
            'weapon_scale_max_error': max(abs(a-b) for a,b in zip(wm.to_scale(), swm.to_scale())),
            'blade_base_error_m': (bp-sbp).length, 'blade_tip_error_m': (tp-stp).length})
    def movement(sequence):
        first = sequence[boundaries[0]]
        return max((Vector(bones[n][j])-Vector(first[n][j])).length
                   for bones in sequence.values() for n in first for j in (0,1))
    source_movement = movement({f: snapshots[f][4] for f in snapshots})
    imported_movement = movement(observed)
    action = irig.animation_data.action if irig.animation_data else None
    action_range = list(action.frame_range) if action else None
    timing_ok = bool(action_range and abs(action_range[0]-start)<1e-3 and abs(action_range[1]-end)<1e-3)
    position_keys = ['bone_endpoint_max_error_m', 'weapon_position_error_m', 'blade_base_error_m', 'blade_tip_error_m']
    geometry_ok = all(all(e[k] <= args.position_tolerance_m for k in position_keys) and
                      e['weapon_rotation_error_rad'] <= args.rotation_tolerance_rad and
                      e['bone_deformation_rotation_max_error_rad'] <= args.rotation_tolerance_rad and
                      e['bone_deformation_scale_max_error'] <= 1e-4 and
                      e['weapon_scale_max_error'] <= 1e-4 for e in errors)
    report = {'schema_version': 1, 'fbx_reimports': 1, 'source_sha256': source_hash,
        'baseline_identities_preserved': all(sha256(Path(i['Path'])).lower() == i['Hash'].lower() for i in identities),
        'evaluated_mesh_cache_exact_readback': cache_verified,
        'import_translation_policy': 'Disconnect imported edit bones (use_connect=False), preserving parent hierarchy; raw Blender FBX reconnect suppresses FP joint translations',
        'fbx_geometry_limitation': 'Post-armature subdivision cannot commute with skinning of FBX flattened rest geometry; source evaluated mesh NPZ preserves exact positions',
        'preview_identity': preview_receipt, 'mesh_deformation_checks': mesh_errors,
        'mesh_deformation_matches': all(e['topology_count_matches'] and e['max_vertex_error_m'] <= args.position_tolerance_m for e in mesh_errors),
        'source_unchanged': sha256(args.source) == source_hash,
        'full_hierarchy_matches': hierarchy == ihierarchy, 'source_bones': len(hierarchy), 'imported_bones': len(ihierarchy),
        'fps': fps, 'imported_action_range': action_range, 'timing_matches': timing_ok,
        'source_bone_movement_m': source_movement, 'imported_bone_movement_m': imported_movement,
        'actual_animation_verified': source_movement > .001 and imported_movement > .001,
        'phase_boundary_comparisons': [e for e in errors if e['phase_boundary']],
        'all_frame_comparisons': errors, 'verified_frames': len(errors),
        'bone_orientation_method': 'world pose * inverse rig-space rest; fixed FBX bone-local rest-axis conversion cancels; shortest quaternion angular distance',
        'bone_endpoint_method': 'actual world joint heads plus canonical source rest tails transformed by evaluated pose/rest deformation; ignores FBX reconstructed display tail length',
        'alignment_within_tolerance': geometry_ok,
        'position_tolerance_m': args.position_tolerance_m, 'rotation_tolerance_rad': args.rotation_tolerance_rad,
        'artistic_acceptance': False, 'engine_integration_tested': False}
    report['passed'] = all(report[k] for k in ['source_unchanged', 'baseline_identities_preserved', 'full_hierarchy_matches', 'timing_matches', 'actual_animation_verified', 'alignment_within_tolerance', 'evaluated_mesh_cache_exact_readback']) and (not candidate or preview_receipt['pixel_identical'])
    report['pass_scope'] = 'Skeleton/weapon roundtrip and exact source evaluated mesh cache; does NOT certify FBX surface equivalence'
    write(args.out / 'export-verification.json', report)
    print(json.dumps({'passed': report['passed'], 'report': str(args.out / 'export-verification.json')}))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
