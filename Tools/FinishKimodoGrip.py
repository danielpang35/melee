"""Bake an explicitly authored whole-action grasp route into both native arms.

Existing nonstretch two-link posing math; no runtime solver or target rest edits.
Run in Blender with -- --directory <take> --targets <JSON>.
Target JSON: {coordinate_system: 'blender-z-up', samples: [
 {frame: 1, primary_grasp_position_m: [x,y,z], grasp_rotation_wxyz: [w,x,y,z]}]}.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Tools'))
from RetargetKimodo import signature, sha, write, rows, curves


def finish(directory, targets_path, output_name, source_name='MB_Kimodo_Transfer.blend'):
    assert Path(source_name).name == source_name and source_name.endswith('.blend')
    raw = directory / source_name
    assert Path(output_name).name == output_name and output_name.endswith('.blend')
    destination = directory / output_name
    assert not destination.exists(), 'Preserve authored native sources'
    targets = json.loads(targets_path.read_text())
    assert targets.get('coordinate_system') == 'blender-z-up' or targets.get('coordinates', '').startswith('Blender world meters, +Z up, -Y forward;')
    samples = targets['samples']
    raw_hash = sha(raw)
    bpy.ops.wm.open_mainfile(filepath=str(raw))
    scene = bpy.context.scene
    rig = bpy.data.objects['MB_AccuRig']
    body = bpy.data.objects['MB_Rigged_LOD0']
    rest_signature = signature(rig, body)
    assert [s['frame'] for s in samples] == list(range(scene.frame_start, scene.frame_end + 1))
    grasps = {s: bpy.data.objects['Kimodo_Grasp_' + s] for s in ['r', 'l']}
    previous, results, unchanged, persisted = {}, [], {}, {}
    arm_names = {f'{n}_{s}' for s in ['r', 'l'] for n in ['upperarm', 'lowerarm', 'hand']}
    def point(name, endpoint, target):
        p = rig.pose.bones[name]
        q = (rig.pose.bones[endpoint].head - p.head).rotation_difference(target - p.head)
        p.matrix = Matrix.Translation(p.head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-p.head) @ p.matrix
        bpy.context.view_layer.update()
    for sample in samples:
        f = sample['frame']
        scene.frame_set(f)
        bpy.context.view_layer.update()
        # Compare only bones outside the two authored arm subtrees: fingers/twists
        # follow their edited parents, while torso/legs must remain unchanged.
        independent = [p for p in rig.pose.bones if not any(a.name in arm_names for a in [p, *p.parent_recursive])]
        unchanged[f] = {p.name: rows(p.matrix) for p in independent}
        G = Quaternion(sample['grasp_rotation_wxyz']).normalized()
        P = Vector(sample['primary_grasp_position_m'])
        wanted = {'r': P, 'l': P + G @ Vector(sample.get('support_offset_m', targets.get('support_offset_m', [0, 0, -.125])))}
        excess = {}
        for side in ['r', 'l']:
            hand_q = rig.matrix_world.to_quaternion().inverted() @ G @ grasps[side].matrix_basis.to_quaternion().inverted()
            wrist = rig.matrix_world.inverted() @ wanted[side] - hand_q @ grasps[side].matrix_basis.translation
            names = [n + '_' + side for n in ['upperarm', 'lowerarm', 'hand']]
            a, b, c = [rig.pose.bones[n].head.copy() for n in names]
            l1, l2 = (b-a).length, (c-b).length
            delta = wrist-a
            excess[side] = max(0, delta.length-l1-l2, abs(l1-l2)-delta.length) * rig.scale.x
            # Preserve failure honestly; clamp only to produce a retained visible
            # diagnostic. Any positive excess fails the reach gate in the receipt.
            distance = max(abs(l1-l2)+.001, min(delta.length, l1+l2-.001))
            axis = delta.normalized()
            chest = rig.pose.bones['spine_05'].matrix.to_quaternion() @ rig.data.bones['spine_05'].matrix_local.to_quaternion().inverted()
            pole = chest @ Vector(sample.get('elbow_poles_local', {}).get(side, (-1 if side == 'r' else 1, .35, -.55)))
            transverse = pole - axis*pole.dot(axis)
            assert transverse.length > .0001
            along = (l1*l1-l2*l2+distance*distance)/(2*distance)
            elbow = a + axis*along + transverse.normalized()*math.sqrt(max(0, l1*l1-along*along))
            point(names[0], names[1], elbow)
            point(names[1], names[2], a+axis*distance)
            p = rig.pose.bones[names[2]]
            p.matrix = Matrix.LocRotScale(p.head, hand_q, Vector((1, 1, 1)))
            bpy.context.view_layer.update()
            for n in names:
                p = rig.pose.bones[n]
                q = p.rotation_quaternion.copy()
                if n in previous and q.dot(previous[n]) < 0:
                    q.negate()
                p.rotation_quaternion = q
                previous[n] = q.copy()
                for channel in ['location', 'rotation_quaternion', 'scale']:
                    p.keyframe_insert(channel, frame=f, group=n)
        bpy.context.view_layer.update()
        errors = {s: (grasps[s].matrix_world.translation-wanted[s]).length for s in ['r', 'l']}
        gap = (grasps['l'].matrix_world.translation - grasps['r'].matrix_world @ Vector((0, 0, -12.5))).length
        unchanged_error = max(abs(rig.pose.bones[n].matrix[i][j]-matrix[i][j])
                              for n, matrix in unchanged[f].items() for i in range(4) for j in range(4))
        assert unchanged_error < .0001, unchanged_error
        results.append(dict(frame=f, target_error_m=errors, excess_reach_m=excess, support_gap_m=gap))
        if f in {scene.frame_start, (scene.frame_start+scene.frame_end)//2, scene.frame_end}:
            persisted[f] = {n: rows(rig.pose.bones[n].matrix) for n in arm_names}
    for curve in curves(rig.animation_data.action):
        for key in curve.keyframe_points:
            key.interpolation = 'LINEAR'
    assert signature(rig, body) == rest_signature
    rig.animation_data.action.name = 'Kimodo_' + directory.name + '_AuthoredGrip'
    scene['review_status'] = 'Authored native two-arm grasp route over retained generated body; inspect reach and full source; no acceptance.'
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(destination))
    rig = bpy.data.objects['MB_AccuRig']
    reopen_error = 0.0
    for f, poses in persisted.items():
        bpy.context.scene.frame_set(f)
        for n, matrix in poses.items():
            reopen_error = max(reopen_error, max(abs(rig.pose.bones[n].matrix[i][j]-matrix[i][j]) for i in range(4) for j in range(4)))
    assert reopen_error < .0001
    assert signature(rig, bpy.data.objects['MB_Rigged_LOD0']) == rest_signature
    assert sha(raw) == raw_hash
    max_excess = max(value for r in results for value in r['excess_reach_m'].values())
    receipt = 'authored-grip.json' if output_name == 'MB_Kimodo_AuthoredGrip.blend' else destination.stem + '.json'
    write(directory / receipt, dict(source=str(destination.relative_to(ROOT)), source_sha256=sha(destination),
          input_native_source=str(raw.relative_to(ROOT)), raw_source_sha256=raw_hash, targets=str(targets_path.relative_to(ROOT)), targets_sha256=sha(targets_path),
          tool_sha256=sha(Path(__file__)), rest_mesh_weights_signature=rest_signature,
          target_adjustment=targets.get('native_adjustment'),
          unchanged_contract=('Input-native' if source_name == 'MB_Kimodo_Transfer.blend' else 'Reviewed native draft') + ' torso/clavicles/root/legs and rest/mesh/weights unchanged; both arm/hand curves authored; fingers/twists follow parents',
          method='Existing nonstretch two-link native posing with stable outward elbow hints; primary wrist owns retained sword; no runtime solver',
          max_excess_reach_m=max_excess, max_target_error_m=max(v for r in results for v in r['target_error_m'].values()),
          max_support_gap_m=max(r['support_gap_m'] for r in results),
          unreachable_frames=[r['frame'] for r in results if max(r['excess_reach_m'].values()) > .0001],
          reachable=max_excess <= .0001, save_reopen_max_matrix_error=reopen_error, per_frame=results,
          evidence_limit='Numerical reach/persistence only; continuous viewing and human artistic/play acceptance not established'))
    print('KIMODO_AUTHORED_GRIP ' + json.dumps({'max_excess_reach_m': max_excess, 'max_support_gap_m': max(r['support_gap_m'] for r in results)}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', required=True)
    parser.add_argument('--targets', required=True)
    parser.add_argument('--output', default='MB_Kimodo_AuthoredGrip.blend')
    parser.add_argument('--source', default='MB_Kimodo_Transfer.blend', help='Saved native input in take directory; preserves native finishing when revising')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    finish((ROOT / args.directory).resolve(), (ROOT / args.targets).resolve(), args.output, args.source)
