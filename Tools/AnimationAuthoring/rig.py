"""Minimal native CF controls. IK assists/supports poses; primary FK authors motion."""
import math
import bpy
from mathutils import Euler, Matrix, Vector


def empty(name, parent=None, matrix=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.empty_display_type = 'ARROWS'
    obj.empty_display_size = .065
    obj.show_in_front = True
    obj.parent = parent
    if matrix is not None:
        obj.matrix_basis = matrix
    return obj


def follow_bone(name, rig, bone):
    obj = empty(name)
    c = obj.constraints.new('COPY_TRANSFORMS')
    c.target, c.subtarget = rig, bone
    return obj


def hand_calibration(rig, side):
    """Actual CF wrist/knuckle landmarks define an editable shaft frame."""
    bones = rig.data.bones
    wrist = bones['wrist.'+side]
    palm = (bones['finger3-1.'+side].head_local-wrist.head_local).normalized()
    shaft = (bones['finger2-1.'+side].head_local-bones['finger5-1.'+side].head_local).normalized()
    normal = shaft.cross(palm).normalized()
    shaft = palm.cross(normal).normalized()
    x = palm if side == 'R' else -palm
    y = shaft.cross(x).normalized()
    frame = Matrix((x, y, shaft)).transposed().to_4x4()
    # Seat shaft at palm depth; offsets remain editable on grasp objects.
    frame.translation = wrist.head_local+palm*.077-normal*.024
    return wrist.matrix_local.inverted()@frame


def setup(foundation):
    bpy.ops.wm.open_mainfile(filepath=str(foundation))
    scene = bpy.context.scene
    deform = bpy.data.objects[scene.get('deform_rig', 'CF01_CharacterRig')]
    deform.animation_data_clear()
    for p in deform.pose.bones:
        p.matrix_basis = Matrix.Identity(4)
        for constraint in list(p.constraints):
            p.constraints.remove(constraint)
    controls = deform.copy()
    controls.data = deform.data.copy()
    controls.name, controls.data.name = 'CF_CTRL', 'CF_ControlRig_v1'
    scene.collection.objects.link(controls)
    controls.show_in_front = True
    controls.data.display_type = 'STICK'
    controls['role'] = 'Editable native FK. R arm drives primary grasp/sword; L arm has optional support constraint. No runtime authority.'
    for p in controls.pose.bones:
        p.rotation_mode = 'XYZ'
        p.bone.use_deform = False
        p['space'] = 'parent-local FK; use native transform orientations for world/body posing'
        p['role'] = ('Finger grasp calibration' if p.name.startswith('finger') else 'Direct FK control')
        c = deform.pose.bones[p.name].constraints.new('COPY_TRANSFORMS')
        c.target, c.subtarget = controls, p.name
    deform.hide_set(True)
    body = bpy.data.objects[scene.get('body_object', 'CF01_Body')]
    for poly in body.data.polygons:
        if .80 < poly.center.z < 1.045 and abs(poly.center.x) < .25:
            poly.material_index = 1
    for mod in body.modifiers:
        if mod.type == 'SUBSURF':
            mod.levels = mod.render_levels = 1
    # Primary and support grasps remain independent, editable palm calibrations.
    grasps = {}
    for side, role in [('R','Primary'),('L','Support')]:
        follower = follow_bone('CF_'+role+'Wrist', controls, 'wrist.'+side)
        grasps[side] = empty('CF_'+role+'Grasp', follower, hand_calibration(controls, side))
        grasps[side]['role'] = 'Editable wrist-local calibrated shaft frame; +Z points guardward'
    support_socket = empty('CF_SupportSocket', grasps['R'], Matrix.Translation((0,0,-.125)))
    support_socket['role'] = 'Editable primary-grasp-relative support placement; primary is guardward'
    articulation = empty('CF_SupportArticulation', support_socket)
    articulation['role'] = 'Live editable support wrist flex/deviation/roll around fixed grasp center; shaft-local XYZ'
    support_target = empty('CF_SupportWristTarget', articulation, grasps['L'].matrix_basis.inverted())
    support_target['role'] = 'Support grasp inverse calibration; update after changing CF_SupportGrasp calibration'
    pole_r, pole_l = empty('CF_ElbowPlane_R'), empty('CF_ElbowPlane_L')
    pole_r['role'] = 'Posing-assistance pole. Primary playback is native FK; re-pose/bake explicitly to use pole changes.'
    pole_l['role'] = 'Live support elbow-plane control, world space'
    return controls, grasps, support_target, {'R':pole_r,'L':pole_l}


def rotate_global(rig, name, rotation):
    p = rig.pose.bones[name]
    p.matrix = Matrix.Translation(p.head)@rotation.to_matrix().to_4x4()@Matrix.Translation(-p.head)@p.matrix
    bpy.context.view_layer.update()


def point_bone(rig, name, endpoint, direction):
    p = rig.pose.bones[name]
    current = rig.pose.bones[endpoint].head-p.head
    rotate_global(rig, name, current.normalized().rotation_difference(Vector(direction).normalized()))


def pose_arm(rig, side, target, pole):
    """Closed-form two-link posing aid, evaluated at authored keys only."""
    upper, lower, wrist = ['%s.%s'%(n,side) for n in ['upperarm01','lowerarm01','wrist']]
    shoulder = rig.pose.bones[upper].head.copy()
    a,b,c = [rig.data.bones[n].head_local for n in [upper,lower,wrist]]
    l1,l2 = (b-a).length,(c-b).length
    delta = target-shoulder
    dist = max(abs(l1-l2)+.0001, min(delta.length,l1+l2-.0001))
    axis = delta.normalized()
    transverse = Vector(pole)-axis*Vector(pole).dot(axis)
    if transverse.length < 1e-5:
        raise ValueError('Elbow posing plane is parallel to shoulder/wrist axis')
    along = (l1*l1-l2*l2+dist*dist)/(2*dist)
    elbow = shoulder+axis*along+transverse.normalized()*math.sqrt(max(0,l1*l1-along*along))
    point_bone(rig,upper,lower,elbow-shoulder)
    point_bone(rig,lower,wrist,target-rig.pose.bones[lower].head)
    return (rig.pose.bones[wrist].head-target).length


def key_world_grasp_orientations(rig, grasp, orientations, side='R'):
    """Convert world grasp rotations after parent curves are final.

    Sampled native FK keys retain direct wrist editing. Sequential decomposition
    avoids sparse parent-local Euler turns; this is an explicit authoring bake,
    never a playback solver or independent weapon track.
    """
    scene = bpy.context.scene
    wrist = rig.pose.bones['wrist.' + side]
    inverse_calibration = grasp.matrix_basis.inverted()
    previous = None
    for frame, orientation in orientations:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        target = rig.matrix_world.inverted() @ orientation @ inverse_calibration
        target.translation = wrist.head
        wrist.matrix = target
        wrist.rotation_euler = (wrist.matrix_basis.to_euler('XYZ', previous)
                                if previous is not None else wrist.matrix_basis.to_euler('XYZ'))
        previous = wrist.rotation_euler.copy()
        wrist.keyframe_insert('rotation_euler', frame=frame, group=wrist.name)
        bpy.context.view_layer.update()


def support_constraint(rig, target, pole):
    rig['support_influence'] = 1.0
    rig.id_properties_ui('support_influence').update(min=0.,max=1.,description='Both support IK and wrist orientation; match evaluated pose to FK before switching')
    ik = rig.pose.bones['lowerarm02.L'].constraints.new('IK')
    ik.name = 'Support grasp assistance (match FK before switching)'
    ik.target, ik.pole_target = target, pole
    ik.chain_count = 4
    ik.use_stretch = False
    ik.iterations = 64
    # The split deform segments remain rigid within each anatomical link.
    for name in ['upperarm02.L','lowerarm02.L']:
        p=rig.pose.bones[name]
        p.lock_ik_x=p.lock_ik_y=p.lock_ik_z=True
    c = rig.pose.bones['wrist.L'].constraints.new('COPY_ROTATION')
    c.name='Support palm orientation'
    c.target=target
    c.target_space=c.owner_space='WORLD'
    for constraint in [ik,c]:
        driver=constraint.driver_add('influence').driver
        driver.expression='influence'
        variable=driver.variables.new();variable.name='influence'
        variable.targets[0].id=rig
        variable.targets[0].data_path='["support_influence"]'
    return ik


def match_support_to_fk(rig):
    """Explicit pose-preserving switch; key both influence and matched FK."""
    names=['upperarm01.L','upperarm02.L','lowerarm01.L','lowerarm02.L','wrist.L']
    bpy.context.view_layer.update()
    matrices={n:rig.pose.bones[n].matrix.copy() for n in names}
    frame=bpy.context.scene.frame_current
    if frame>bpy.context.scene.frame_start:
        rig.keyframe_insert('["support_influence"]',frame=frame-1)
    rig['support_influence']=0.
    rig.keyframe_insert('["support_influence"]')
    for fc in rig.animation_data.action.fcurves:
        if fc.data_path=='["support_influence"]':
            for point in fc.keyframe_points:point.interpolation='CONSTANT'
    bpy.context.view_layer.update()
    for name in names:
        p=rig.pose.bones[name];p.matrix=matrices[name]
        p.keyframe_insert('rotation_euler',group=name)
        p.keyframe_insert('location',group=name)
        bpy.context.view_layer.update()


def weapon(primary):
    root = empty('CF_Weapon', primary, Matrix.Translation((0,0,.070)))
    root['role']='Derived from primary palm; no independent weapon animation'
    def material(name,color):
        m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
    steel=material('CF_ProofSteel',(.55,.64,.69))
    leather=material('CF_ProofGrip',(.10,.045,.025))
    def cube(name,loc,scale,mat):
        bpy.ops.mesh.primitive_cube_add(size=1)
        o=bpy.context.object;o.name=name;o.parent=root;o.location=loc;o.scale=scale;o.data.materials.append(mat)
    verts=[]
    for z,w in [(0,.033),(.88,.026),(1.035,0)]:
        verts.extend([(-w,0,z),(0,-.007,z),(w,0,z),(0,.007,z)])
    faces=[(j,(j+1)%4,(j+1)%4+4,j+4) for j in range(4)]+[(j+4,(j+1)%4+4,(j+1)%4+8,j+8) for j in range(4)]+[(0,3,2,1)]
    mesh=bpy.data.meshes.new('CF_ProofBlade');mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new('CF_Blade',mesh);bpy.context.scene.collection.objects.link(o);o.parent=root;o.data.materials.append(steel)
    cube('CF_Guard',(0,0,-.013),(.27,.035,.026),steel)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.018,depth=.255)
    o=bpy.context.object;o.name='CF_Grip';o.parent=root;o.location=(0,0,-.151);o.data.materials.append(leather)
    cube('CF_Pommel',(0,0,-.293),(.045,.04,.04),steel)
    return root


def calibrate_fingers(rig, side, grasp):
    """Curl actual CF digit links around the shaft; native FK stays editable."""
    bpy.context.view_layer.update()
    frame=grasp.matrix_world.copy()
    inv=frame.inverted()
    for digit in range(2,6):
        base=inv@rig.pose.bones[f'finger{digit}-1.{side}'].head
        theta=math.atan2(base.y,base.x)
        # Different rest knuckles retain their own shaftwise spread.
        for segment,(radius,turn) in enumerate([(.027,.65),(.025,1.35),(.023,1.95)],1):
            name=f'finger{digit}-{segment}.{side}'
            p=rig.pose.bones.get(name)
            if not p: continue
            angle=theta+(1 if side=='R' else -1)*turn
            target=frame@Vector((radius*math.cos(angle),radius*math.sin(angle),base.z))
            current=p.tail-p.head
            rotate_global(rig,name,current.normalized().rotation_difference((target-p.head).normalized()))
    for segment,xyz in enumerate([(.021,-.018,.042),(-.002,-.025,.040),(-.021,-.009,.036)],1):
        name=f'finger1-{segment}.{side}';p=rig.pose.bones.get(name)
        if p:
            target=frame@Vector(xyz if side=='R' else (-xyz[0],-xyz[1],xyz[2]))
            rotate_global(rig,name,(p.tail-p.head).normalized().rotation_difference((target-p.head).normalized()))
