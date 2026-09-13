"""Bounded SOMA standard-T-pose BVH -> editable MB AccuRig diagnostic.

blender -b --python Tools/RetargetKimodo.py -- build --directory <candidate>
blender -b --python Tools/RetargetKimodo.py -- render --directory <candidate>

No runtime export, selection, target rest edit or continuous support-hand solver.
After native finishing, render reads the saved blend and never rebuilds it.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
WEAPON_SOURCE = ROOT / 'ArtSource/Cascadeur/KN_v002_20260912/Kit/KN_v002_ImportKit.blend'
CAMERAS = {'primary': (3.1, -5.4, 2.6), 'rear-quarter': (-3.1, 5.4, 2.6),
           'front': (0, -5.4, 1.0), 'rear': (0, 5.4, 1.0),
           'left': (5.4, 0, 1.0), 'right': (-5.4, 0, 1.0)}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def rows(matrix):
    return [list(r) for r in matrix]


def anatomical(direction, reference):
    y = direction.normalized()
    x = reference - y * reference.dot(y)
    assert x.length > 1e-7, 'Degenerate anatomical frame'
    x.normalize()
    return Matrix((x, y, x.cross(y))).transposed().to_quaternion()


def signature(rig, body):
    """Identity of protected editable skeleton, surface and weights, excluding pose."""
    payload = {'rest': [(b.name, b.parent.name if b.parent else None,
                         rows(b.matrix_local), list(b.head_local), list(b.tail_local))
                        for b in rig.data.bones],
               'rig_matrix': rows(rig.matrix_world),
               'vertices': [(list(v.co), [(g.group, g.weight) for g in v.groups])
                            for v in body.data.vertices],
               'polygons': [list(p.vertices) for p in body.data.polygons],
               'groups': [g.name for g in body.vertex_groups]}
    return hashlib.sha256(json.dumps(payload).encode()).hexdigest()


def mapping():
    m = {'pelvis': ('Hips', 'Spine1', 'spine_01'),
         'spine_01': ('Spine1', 'Spine2', 'spine_02'),
         'spine_02': ('Spine1', 'Spine2', 'spine_03'),
         'spine_03': ('Spine2', 'Chest', 'spine_04'),
         'spine_04': ('Chest', 'Neck1', 'spine_05'),
         'spine_05': ('Chest', 'Neck1', 'neck_01'),
         'neck_01': ('Neck1', 'Neck2', 'neck_02'),
         'neck_02': ('Neck2', 'Head', 'head'),
         'head': ('Head', 'HeadEnd', None)}
    for side, prefix in [('l', 'Left'), ('r', 'Right')]:
        for t, s, se, te in [('clavicle', 'Shoulder', 'Arm', 'upperarm'),
                              ('upperarm', 'Arm', 'ForeArm', 'lowerarm'),
                              ('lowerarm', 'ForeArm', 'Hand', 'hand'),
                              ('hand', 'Hand', 'HandMiddle2', 'middle_01'),
                              ('thigh', 'Leg', 'Shin', 'calf'),
                              ('calf', 'Shin', 'Foot', 'foot'),
                              ('foot', 'Foot', 'ToeBase', 'ball'),
                              ('ball', 'ToeBase', 'ToeEnd', None)]:
            m[t + '_' + side] = (prefix + s, prefix + se, te + '_' + side if te else None)
        for digit in ['thumb', 'index', 'middle', 'ring', 'pinky']:
            stem = prefix + 'Hand' + digit.title()
            if digit != 'thumb':
                m[f'{digit}_metacarpal_{side}'] = (stem + '1', stem + '2', f'{digit}_01_{side}')
            for k in range(1, 4):
                source_k = k if digit == 'thumb' else k + 1
                end = str(source_k + 1) if k < 3 else 'End'
                m[f'{digit}_{k:02}_{side}'] = (stem + str(source_k), stem + end,
                                             f'{digit}_{k+1:02}_{side}' if k < 3 else None)
    return m


def curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                yield from bag.fcurves


def setup_weapon(scene, rig, rest):
    grasps = {}
    for side in ['r', 'l']:
        wrist = rig.data.bones[f'hand_{side}']
        head = wrist.head_local
        palm = (rest[f'middle_01_{side}'].translation - head).normalized()
        shaft = (rest[f'index_01_{side}'].translation - rest[f'pinky_01_{side}'].translation).normalized()
        normal = shaft.cross(palm).normalized()
        shaft = palm.cross(normal).normalized()
        x = palm if side == 'r' else -palm
        g = Matrix((x, shaft.cross(x).normalized(), shaft)).transposed().to_4x4()
        g.translation = head + palm * 7.7 - normal * 2.4
        follower = bpy.data.objects.new('Kimodo_Wrist_' + side, None)
        scene.collection.objects.link(follower)
        c = follower.constraints.new('COPY_TRANSFORMS')
        c.target = rig
        c.subtarget = wrist.name
        grasp = bpy.data.objects.new('Kimodo_Grasp_' + side, None)
        scene.collection.objects.link(grasp)
        grasp.parent = follower
        grasp.matrix_basis = wrist.matrix_local.inverted() @ g
        grasp.empty_display_size = 3
        grasps[side] = grasp
    weapon = bpy.data.objects.new('Kimodo_Weapon_PrimaryOwned', None)
    scene.collection.objects.link(weapon)
    weapon.parent = grasps['r']
    weapon.location = (0, 0, 7)
    weapon.scale = (100, 100, 100)
    with bpy.data.libraries.load(str(WEAPON_SOURCE), link=False) as (available, loaded):
        loaded.objects = ['KN_' + n for n in ('Blade', 'Guard', 'Grip', 'Pommel')]
    for obj in loaded.objects:
        assert obj is not None
        scene.collection.objects.link(obj)
        obj.name = 'Kimodo_' + obj.name
        obj.animation_data_clear()
        for mod in list(obj.modifiers):
            obj.modifiers.remove(mod)
        obj.parent = weapon
        obj.matrix_basis = Matrix.Identity(4)
        obj.hide_render = False
        obj.hide_set(False)
    return grasps


def setup_cameras(scene):
    for name, location in CAMERAS.items():
        data = bpy.data.cameras.new('Kimodo_' + name)
        obj = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(obj)
        obj.location = location
        obj.rotation_euler = (Vector((0, 0, 1.0)) - obj.location).to_track_quat('-Z', 'Y').to_euler()
        data.type = 'ORTHO'
        data.ortho_scale = 3.8
    scene.camera = bpy.data.objects['Kimodo_primary']
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.background_type = 'WORLD'
    if scene.world is None:
        scene.world = bpy.data.worlds.new('Kimodo_ReviewWorld')
    scene.world.color = (.045, .055, .07)
    scene.display.render_aa = 'FXAA'


def close_fingers(rig, grasps, count):
    """Reuse the existing diagnostic radial closure, stored as native local curves."""
    scene = bpy.context.scene
    scene.frame_set(1)
    bpy.context.view_layer.update()
    def point(name, target):
        p = rig.pose.bones[name]
        rotation = (p.tail - p.head).rotation_difference(target - p.head)
        p.matrix = Matrix.Translation(p.head) @ rotation.to_matrix().to_4x4() @ Matrix.Translation(-p.head) @ p.matrix
        bpy.context.view_layer.update()
    for side in ['r', 'l']:
        shaft = rig.matrix_world.inverted() @ grasps[side].matrix_world
        inverse = shaft.inverted()
        for digit in ['index', 'middle', 'ring', 'pinky']:
            base = inverse @ rig.pose.bones[f'{digit}_01_{side}'].head
            theta = math.atan2(base.y, base.x)
            for k, (radius, turn) in enumerate([(2.7, .65), (2.5, 1.35), (2.3, 1.95)], 1):
                angle = theta + (1 if side == 'r' else -1) * turn
                point(f'{digit}_{k:02}_{side}', shaft @ Vector((radius * math.cos(angle), radius * math.sin(angle), base.z)))
        for k, xyz in enumerate([(2.1, -1.8, 4.2), (-.2, -2.5, 4), (-2.1, -.9, 3.6)], 1):
            point(f'thumb_{k:02}_{side}', shaft @ Vector(xyz if side == 'r' else (-xyz[0], -xyz[1], xyz[2])))
    fingers = {p.name: p.matrix_basis.copy() for p in rig.pose.bones
               if any(p.name.startswith(d + '_') for d in ['thumb', 'index', 'middle', 'ring', 'pinky'])}
    for f in range(1, count + 1):
        scene.frame_set(f)
        for name, basis in fingers.items():
            p = rig.pose.bones[name]
            p.matrix_basis = basis
            for channel in ['location', 'rotation_quaternion', 'scale']:
                p.keyframe_insert(channel, frame=f, group=name)


def build(directory):
    bvh = directory / 'transfer-standard-tpose.bvh'
    destination = directory / 'MB_Kimodo_Transfer.blend'
    assert not destination.exists(), 'Retain source: use a new take directory'
    text = bvh.read_text()
    count = int(re.search(r'Frames:\s*(\d+)', text).group(1))
    dt = float(re.search(r'Frame Time:\s*([\d.eE+-]+)', text).group(1))
    config = json.loads((ROOT / 'Config/WorkingCharacter.json').read_text())
    target = ROOT / config['native_source']
    protected_paths = [target, WEAPON_SOURCE, ROOT / 'Config/WorkingCharacter.json', ROOT / 'Config/EXPreview.json', bvh]
    protected = {str(p.relative_to(ROOT)): sha(p) for p in protected_paths}
    bpy.ops.wm.open_mainfile(filepath=str(target))
    scene = bpy.data.scenes[config['scene']]
    bpy.context.window.scene = scene
    rig, body = bpy.data.objects[config['armature']], bpy.data.objects[config['body']]
    before = signature(rig, body)
    for obj in scene.objects:
        obj.hide_render = obj not in [rig, body]
        obj.hide_set(obj not in [rig, body])
    rig.animation_data_clear()
    for p in rig.pose.bones:
        p.matrix_basis = Matrix.Identity(4)
        p.rotation_mode = 'QUATERNION'
        for c in list(p.constraints):
            p.constraints.remove(c)
    rest = {b.name: b.matrix_local.copy() for b in rig.data.bones}
    from io_anim_bvh import import_bvh
    import_bvh.load(bpy.context, str(bvh), global_scale=.01,
                    global_matrix=Matrix.Rotation(math.pi / 2, 4, 'X'),
                    rotate_mode='QUATERNION', frame_start=1, use_fps_scale=False,
                    update_scene_fps=False, update_scene_duration=False)
    source = bpy.context.object
    source.name = 'Kimodo_SOMA_TransferSource'
    bpy.context.view_layer.update()
    sr = {b.name: source.matrix_world @ b.matrix_local for b in source.data.bones}
    assert len(sr) >= 77, len(sr)
    m = mapping()
    assert all(n in rest and s in sr and se in sr for n, (s, se, te) in m.items())
    calibration = {}
    for n, (s, se, te) in m.items():
        sv = sr[se].translation - sr[s].translation
        tv = rest[te].translation - rest[n].translation if te else rig.data.bones[n].tail_local - rest[n].translation
        if n == 'head':
            tv = Vector((0, 0, 1))  # AccuRig's head tail is a tiny importer helper.
        if n.startswith('hand_'):
            prefix, side = ('Right' if n.endswith('r') else 'Left'), n[-1]
            sx = sr[prefix + 'HandIndex2'].translation - sr[prefix + 'HandPinky2'].translation
            tx = rest[f'index_01_{side}'].translation - rest[f'pinky_01_{side}'].translation
        else:
            sx = tx = Vector((0, -1, 0))
        if n.startswith('ball_'):
            tv = Vector((0, -1, 0))  # Ball tail points up; actual toes extend forward.
            sx = tx = Vector((1, 0, 0))
        calibration[n] = (anatomical(tv, tx), sx, sv)
    # SOMA BVH rest Hips is zero. Calibrate the standing offset from the sole,
    # then separate horizontal actor travel from pelvis height/turn exactly once.
    source_height = sr['Hips'].translation.z - min(sr[n].translation.z for n in ['LeftToeBase', 'RightToeBase'])
    target_height = (rig.matrix_world @ rest['pelvis'].translation).z
    ratio = target_height / source_height
    assert .5 < ratio < 2, ratio
    scene.render.fps = round(1 / dt)
    scene.render.fps_base = scene.render.fps * dt
    scene.frame_start, scene.frame_end = 1, count
    previous, initial_hip = {}, None
    for f in range(1, count + 1):
        scene.frame_set(f)
        evaluated = source.evaluated_get(bpy.context.evaluated_depsgraph_get())
        pose = {p.name: source.matrix_world @ p.matrix for p in evaluated.pose.bones}
        hip = pose['Hips'].translation
        if initial_hip is None:
            initial_hip = hip.copy()
        travel = Vector((hip.x - initial_hip.x, hip.y - initial_hip.y, 0)) * ratio
        matrices = {}
        for p in rig.pose.bones:
            n, parent = p.name, p.parent
            base = matrices[parent.name] @ rest[parent.name].inverted() @ rest[n] if parent else rest[n].copy()
            if n == 'root':
                base.translation += rig.matrix_world.to_3x3().inverted() @ travel
            if n in m:
                s, se, te = m[n]
                tf, ref, sv = calibration[n]
                deformation = pose[s].to_quaternion() @ sr[s].to_quaternion().inverted()
                direction = pose[se].translation - pose[s].translation
                if n.startswith('hand_'):
                    prefix = 'Right' if n.endswith('r') else 'Left'
                    reference = pose[prefix + 'HandIndex2'].translation - pose[prefix + 'HandPinky2'].translation
                else:
                    reference = deformation @ ref
                q = anatomical(direction, reference) @ tf.inverted() @ rest[n].to_quaternion()
                base = Matrix.LocRotScale(base.translation, q, Vector((1, 1, 1)))
                if n == 'pelvis':
                    base.translation.z = rest[n].translation.z + (hip.z - source_height) * ratio / rig.scale.z
            matrices[n] = base
            p.matrix_basis = p.bone.convert_local_to_pose(base, rest[n],
                parent_matrix=matrices[parent.name] if parent else Matrix.Identity(4),
                parent_matrix_local=rest[parent.name] if parent else Matrix.Identity(4), invert=True)
            q = p.rotation_quaternion.copy()
            if n in previous and q.dot(previous[n]) < 0:
                q.negate()
            p.rotation_quaternion = q
            previous[n] = q.copy()
            for channel in ['location', 'rotation_quaternion', 'scale']:
                p.keyframe_insert(channel, frame=f, group=n)
    action = rig.animation_data.action
    action.name = 'Kimodo_' + directory.name + '_EditableFK'
    for curve in curves(action):
        for key in curve.keyframe_points:
            key.interpolation = 'LINEAR'
    source.hide_render = True
    source.hide_set(True)
    grasps = setup_weapon(scene, rig, rest)
    close_fingers(rig, grasps, count)
    setup_cameras(scene)
    gaps, unreachable, poses = [], [], {}
    for f in range(1, count + 1):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        support = grasps['r'].matrix_world @ Vector((0, 0, -12.5))
        gaps.append((grasps['l'].matrix_world.translation - support).length)
        # Translation required at the current editable support wrist orientation.
        desired_wrist = rig.pose.bones['hand_l'].head + rig.matrix_world.to_3x3().inverted() @ (support - grasps['l'].matrix_world.translation)
        a, b, c = [rig.pose.bones[n].head for n in ['upperarm_l', 'lowerarm_l', 'hand_l']]
        unreachable.append(max(0, (desired_wrist-a).length - (b-a).length - (c-b).length) * rig.scale.x)
        if f in {1, (count + 1) // 2, count}:
            poses[str(f)] = {n: rows(rig.pose.bones[n].matrix) for n in ['root', 'pelvis', 'hand_r', 'hand_l']}
    assert signature(rig, body) == before, 'Target rest/mesh/weights changed'
    grasp_local = {s: rows(grasps[s].matrix_basis) for s in ['r', 'l']}
    scene['review_status'] = 'Diagnostic editable FK transfer; support grip unsolved; no visual or runtime acceptance.'
    scene['kimodo_bvh_sha256'] = sha(bvh)
    scene.frame_set(1)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(destination))
    rig = bpy.data.objects[config['armature']]
    assert signature(rig, bpy.data.objects[config['body']]) == before
    reopen_error = 0.0
    for f, expected in poses.items():
        bpy.context.scene.frame_set(int(f))
        for n, matrix in expected.items():
            reopen_error = max(reopen_error, max(abs(rig.pose.bones[n].matrix[i][j] - matrix[i][j]) for i in range(4) for j in range(4)))
    assert reopen_error < .0001, reopen_error
    assert all(sha(ROOT / p) == h for p, h in protected.items())
    write(directory / 'transfer.json', dict(source=str(destination.relative_to(ROOT)), source_sha256=sha(destination),
        tool_sha256=sha(Path(__file__)), protected=protected, mapping=m,
        rest_mesh_weights_signature=before, target_bones=len(rig.data.bones),
        bvh_joints=len(sr), unit_conversion='BVH centimeters * 0.01 -> meters; Y-up rotated +90 degrees X -> Blender Z-up; target retains 0.01 scale',
        root_policy='Initial horizontal Hips origin removed; horizontal displacement on root, vertical pelvis offset and full pelvis turn; no double application',
        source_standing_height_m=source_height, target_pelvis_height_m=target_height, root_proportion_ratio=ratio,
        source_initial_hip_m=list(initial_hip), frames=count, fps=1 / dt, frame_time_seconds=dt,
        sample_span_seconds=(count - 1) * dt, playback_duration_seconds=count * dt,
        frame_convention='BVH sample 0 -> scene frame 1; N samples occupy N frame periods; last sample at (N-1)*dt; no retiming or added endpoint',
        save_reopen_max_matrix_error=reopen_error, native_action=rig.animation_data.action.name,
        support_gap_m=dict(max=max(gaps), mean=sum(gaps)/len(gaps), mid=gaps[(count-1)//2], per_frame=gaps),
        support_excess_reach_m=dict(max=max(unreachable), mid=unreachable[(count-1)//2]),
        grasp_calibration=dict(wrist_local_cm=grasp_local,
            support_from_primary_cm=[0, 0, -12.5], hilt_from_primary_cm=[0, 0, 7],
            target_rest_joints_cm={n: list(rest[n].translation) for n in ['pelvis', 'upperarm_r', 'lowerarm_r', 'hand_r', 'upperarm_l', 'lowerarm_l', 'hand_l', 'middle_01_r', 'index_01_r', 'pinky_01_r', 'middle_01_l', 'index_01_l', 'pinky_01_l']}),
        grip='Right primary grasp owns retained actual sword; left grasp marker is editable diagnostic, no continuous support solver; rough radial finger closure reused from existing AccuRig diagnostic, native curves editable; generated finger performance unproven',
        cameras=CAMERAS, evidence_limit='Numerical transfer/persistence only; full source-speed multi-angle previews and visible grip/body review required; no artistic/play acceptance'))
    print('KIMODO_TRANSFER ' + json.dumps({'source': str(destination), 'reopen_error': reopen_error, 'max_support_gap_m': max(gaps)}), flush=True)


def finish(directory):
    """One retained diagnostic pass: corrected toe calibration and nonstretch support."""
    raw = directory / 'MB_Kimodo_Transfer.blend'
    destination = directory / 'MB_Kimodo_GripDiagnostic.blend'
    assert not destination.exists()
    raw_hash = sha(raw)
    bpy.ops.wm.open_mainfile(filepath=str(raw))
    scene = bpy.context.scene
    rig = bpy.data.objects['MB_AccuRig']
    source = bpy.data.objects['Kimodo_SOMA_TransferSource']
    body = bpy.data.objects['MB_Rigged_LOD0']
    baseline = signature(rig, body)
    grasps = {s: bpy.data.objects['Kimodo_Grasp_' + s] for s in ['r', 'l']}
    previous, gaps, excess = {}, [], []
    def point(name, endpoint, target):
        p = rig.pose.bones[name]
        delta = rig.pose.bones[endpoint].head - p.head
        q = delta.rotation_difference(target - p.head)
        p.matrix = Matrix.Translation(p.head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-p.head) @ p.matrix
        bpy.context.view_layer.update()
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        for side, prefix in [('l', 'Left'), ('r', 'Right')]:
            p = rig.pose.bones['ball_' + side]
            s = source.pose.bones[prefix + 'ToeBase']
            se = source.pose.bones[prefix + 'ToeEnd']
            deformation = s.matrix.to_quaternion() @ s.bone.matrix_local.to_quaternion().inverted()
            q = anatomical(se.head - s.head, deformation @ Vector((1, 0, 0))) @ anatomical(Vector((0, -1, 0)), Vector((1, 0, 0))).inverted() @ p.bone.matrix_local.to_quaternion()
            p.matrix = Matrix.LocRotScale(p.head, q, Vector((1, 1, 1)))
        bpy.context.view_layer.update()
        # Both grasp frames describe the same shaft; no mirrored/inverted wrist target.
        q = grasps['r'].matrix_world.to_quaternion() @ grasps['l'].matrix_basis.to_quaternion().inverted()
        support = grasps['r'].matrix_world @ Vector((0, 0, -12.5))
        target = rig.matrix_world.inverted() @ support - q @ grasps['l'].matrix_basis.translation
        names = ['upperarm_l', 'lowerarm_l', 'hand_l']
        a, b, c = [rig.pose.bones[n].head.copy() for n in names]
        l1, l2 = (b-a).length, (c-b).length
        delta = target-a
        excess.append(max(0, delta.length-l1-l2) * rig.scale.x)
        distance = max(abs(l1-l2)+.001, min(delta.length, l1+l2-.001))
        axis = delta.normalized()
        transverse = b-a-axis*(b-a).dot(axis)
        if transverse.length < 1e-5:
            transverse = axis.cross(Vector((0, 0, 1)))
        along = (l1*l1-l2*l2+distance*distance)/(2*distance)
        elbow = a + axis*along + transverse.normalized()*math.sqrt(max(0, l1*l1-along*along))
        point(names[0], names[1], elbow)
        point(names[1], names[2], a+axis*distance)
        p = rig.pose.bones['hand_l']
        p.matrix = Matrix.LocRotScale(p.head, q, Vector((1, 1, 1)))
        bpy.context.view_layer.update()
        for n in [*names, 'ball_l', 'ball_r']:
            p = rig.pose.bones[n]
            qn = p.rotation_quaternion.copy()
            if n in previous and qn.dot(previous[n]) < 0:
                qn.negate()
            p.rotation_quaternion = qn
            previous[n] = qn.copy()
            for channel in ['location', 'rotation_quaternion', 'scale']:
                p.keyframe_insert(channel, frame=f, group=n)
        gaps.append((grasps['l'].matrix_world.translation-support).length)
    assert signature(rig, body) == baseline
    rig.animation_data.action.name = 'Kimodo_diagnostic_GripFinish_EditableFK'
    scene['review_status'] = 'Retained one-pass nonstretch support diagnostic; inspect reach failures; no acceptance.'
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
    assert sha(raw) == raw_hash
    write(directory / 'grip-diagnostic.json', dict(source=str(destination.relative_to(ROOT)), source_sha256=sha(destination),
          raw_source_sha256=raw_hash, tool_sha256=sha(Path(__file__)), rest_mesh_weights_signature=baseline,
          toe_fix='Anatomical forward replaces upward ball helper tail calibration',
          support_gap_m=dict(max=max(gaps), mid=gaps[(len(gaps)-1)//2], per_frame=gaps),
          excess_reach_m=dict(max=max(excess), mid=excess[(len(excess)-1)//2], per_frame=excess),
          unreachable_frames=[i+1 for i, value in enumerate(excess) if value > .0001],
          evidence_limit='One existing nonstretch two-link posing pass with coherent left wrist shaft; failed reach is retained, never hidden by scaling; no artistic/runtime acceptance'))
    print('KIMODO_GRIP ' + json.dumps({'gap': max(gaps), 'excess_reach': max(excess)}), flush=True)


def render(directory):
    source = directory / args.source
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene = bpy.context.scene
    out = ROOT / 'Saved/Kimodo/RH_20260913' / directory.name
    if args.source != 'MB_Kimodo_Transfer.blend':
        out = out / source.stem
    out.mkdir(parents=True, exist_ok=True)
    lock = ROOT / 'ArtSource/AnimationLab/render.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, json.dumps({'task': 'Kimodo native preview', 'pid': os.getpid()}).encode())
    os.close(fd)
    outputs = {}
    try:
        scene.render.image_settings.media_type = 'VIDEO'
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
        for name in ['primary', 'rear-quarter']:
            scene.camera = bpy.data.objects['Kimodo_' + name]
            path = out / (name + '.mp4')
            assert not path.exists(), 'Retain exact-source preview: use new take'
            scene.render.filepath = str(path)
            bpy.ops.render.render(animation=True)
            outputs[path.name] = sha(path)
        scene.render.image_settings.media_type = 'IMAGE'
        scene.render.image_settings.file_format = 'PNG'
        # Four body views at middle motion, plus requested source-index beats.
        middle = (scene.frame_start + scene.frame_end) // 2
        body_frame = args.body_frame if args.body_frame is not None else middle
        assert scene.frame_start <= body_frame <= scene.frame_end
        beat_frames = {scene.frame_start, middle}
        if args.sample_indices:
            beat_frames.update(scene.frame_start + int(value) for value in args.sample_indices.split(','))
            beat_frames.add(scene.frame_end)
        assert all(scene.frame_start <= f <= scene.frame_end for f in beat_frames)
        stills = [(n, body_frame) for n in ['front', 'rear', 'left', 'right']]
        stills += [(n, f) for f in sorted(beat_frames) for n in ['primary', 'rear-quarter']]
        for name, f in stills:
            scene.frame_set(f)
            scene.camera = bpy.data.objects['Kimodo_' + name]
            path = out / f'{name}-{f:04}.png'
            assert not path.exists()
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            outputs[path.name] = sha(path)
        write(out / 'preview.json', dict(source=str(source.relative_to(ROOT)), source_sha256=sha(source),
              fps=scene.render.fps / scene.render.fps_base, frames=[scene.frame_start, scene.frame_end],
              playback_rate=1, cameras=CAMERAS, still_frames_views=stills, outputs=outputs,
              evidence_limit='Generated media only; no continuous viewing or human acceptance established'))
    finally:
        lock.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['build', 'finish', 'render'])
    parser.add_argument('--directory', default='ArtSource/Kimodo/RH_20260913/diagnostic')
    parser.add_argument('--source', default='MB_Kimodo_Transfer.blend')
    parser.add_argument('--sample-indices', default='', help='Comma-separated zero-based source indices for both animation views')
    parser.add_argument('--body-frame', type=int, help='Blender frame for four named body views; default is action midpoint')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    directory = (ROOT / args.directory).resolve()
    assert ROOT / 'ArtSource/Kimodo/RH_20260913' in directory.parents
    globals()[args.command](directory)
