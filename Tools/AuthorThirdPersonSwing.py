"""TP_v001: complete editable neutral-right blocking interpretation on CF anatomy.

python Tools/AuthorThirdPersonSwing.py [--inspect|--render]
Authoring-only paired grip and planted leg closure; exported FK needs no solver.
The pose-controls JSON is the high-level editable score; the saved blend also
contains ordinary named FK channels and visible hand/elbow/foot/weapon targets.
"""
import sys, json, math, argparse, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy, bmesh
from mathutils import Vector, Matrix, Quaternion
from AuthorFreshExchange import swing
OUT=ROOT/'ArtSource/CharacterReset/TP_v001'
SOURCE=OUT/'TP_v001_RightHorizontal.blend'
FPS=60
# Explicit full-body poses: frame, hilt xyz, blade xyz, pelvis xyz/yaw,
# chest yaw/forward lean/side lean, right/left shoulder reach, elbow pole xyz,
# support-foot toe pivot yaw R/L. Positive yaw delivers toward anatomical left.
# Anatomical right is -X, forward -Y. Angles are degrees.
BEATS=[
 dict(f=1,name='Relaxed ready',h=(-.055,-.285,1.20),d=(-.20,-.18,.965),p=(0,0,-.032),py=-3,cy=-3,lean=1,side=-1,sr=(.07,.09),er=(-.30,.02,-.40),el=(.25,.01,-.40),feet=(-6,9)),
 dict(f=19,name='Attack start',h=(-.055,-.285,1.20),d=(-.20,-.18,.965),p=(0,0,-.032),py=-3,cy=-3,lean=1,side=-1,sr=(.07,.09),er=(-.30,.02,-.40),el=(.25,.01,-.40),feet=(-6,9)),
 dict(f=36,name='Hand pull and shoulder coil',h=(-.22,-.23,1.13),d=(-.73,.32,.60),p=(-.017,.013,-.037),py=-9,cy=-12,lean=2,side=-3,sr=(.025,.19),er=(-.40,.05,-.36),el=(.21,-.05,-.42),feet=(-7,9)),
 dict(f=52,name='Low right load',h=(-.34,-.20,1.07),d=(-.87,.46,.17),p=(-.026,.012,-.044),py=-14,cy=-19,lean=3,side=-5,sr=(.00,.27),er=(-.37,.10,-.29),el=(.17,-.10,-.39),feet=(-9,9)),
 dict(f=60,name='Rise into commitment',h=(-.34,-.265,1.29),d=(-.97,.12,.20),p=(-.014,-.004,-.037),py=-9,cy=-18,lean=4,side=-4,sr=(.05,.28),er=(-.36,.08,-.26),el=(.14,-.13,-.38),feet=(-8,9)),
 dict(f=63,name='Release start',h=(-.315,-.31,1.45),d=(-.980,-.169,.068),p=(-.003,-.015,-.033),py=-4,cy=-13,lean=5,side=-2,sr=(.10,.30),er=(-.38,.04,-.19),el=(.16,-.15,-.33),feet=(-5,9)),
 dict(f=68,name='Rising cross body',h=(-.14,-.365,1.53),d=(-.585,-.808,.067),p=(.012,-.018,-.027),py=3,cy=-5,lean=5,side=0,sr=(.19,.25),er=(-.36,.03,-.13),el=(.26,-.05,-.25),feet=(-1,9)),
 dict(f=73,name='Central crossing',h=(.065,-.375,1.50),d=(.023,-.998,.044),p=(.020,-.016,-.028),py=9,cy=6,lean=4,side=2,sr=(.27,.18),er=(-.30,-.04,-.16),el=(.34,.04,-.20),feet=(4,9)),
 dict(f=81,name='Release end',h=(.315,-.31,1.31),d=(.605,-.783,-.146),p=(.024,-.006,-.039),py=14,cy=18,lean=3,side=4,sr=(.30,.07),er=(-.15,-.14,-.33),el=(.39,.06,-.28),feet=(9,10)),
 dict(f=94,name='Down left carry',h=(.365,-.225,1.05),d=(.80,-.31,-.515),p=(.020,.004,-.047),py=16,cy=21,lean=3,side=4,sr=(.28,.025),er=(-.17,-.10,-.43),el=(.39,.06,-.35),feet=(10,11)),
 dict(f=108,name='Absorb and return upward',h=(.23,-.255,1.14),d=(.70,-.12,.704),p=(.008,.009,-.042),py=10,cy=16,lean=1,side=2,sr=(.20,.05),er=(-.24,-.04,-.42),el=(.30,.08,-.36),feet=(5,10)),
 dict(f=124,name='Hands inward blade upright',h=(.025,-.29,1.24),d=(.06,-.18,.982),p=(-.004,.002,-.035),py=0,cy=3,lean=1,side=-1,sr=(.10,.07),er=(-.29,.01,-.40),el=(.26,.02,-.39),feet=(-4,9)),
 dict(f=139,name='Ready restored',h=(-.055,-.285,1.20),d=(-.20,-.18,.965),p=(0,0,-.032),py=-3,cy=-3,lean=1,side=-1,sr=(.07,.09),er=(-.30,.02,-.40),el=(.25,.01,-.40),feet=(-6,9)),
 dict(f=154,name='Ready settle',h=(-.055,-.285,1.20),d=(-.20,-.18,.965),p=(0,0,-.032),py=-3,cy=-3,lean=1,side=-1,sr=(.07,.09),er=(-.30,.02,-.40),el=(.25,.01,-.40),feet=(-6,9))]

def quat(axis,angle):return Quaternion(axis,math.radians(angle))
def material(name,col):
    m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);return m
def empty(name):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.empty_display_size=.055;return o
def meshpart(name,vertices,faces,mat,parent):
    m=bpy.data.meshes.new(name);m.from_pydata(vertices,[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o.parent=parent;o.data.materials.append(mat);return o
def cube(name,loc,scale,mat,parent):
    bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.name=name;o.parent=parent;o.location=loc;o.scale=scale;o.data.materials.append(mat);return o
def create_weapon():
    w=empty('TP01_WeaponRoot');w.rotation_mode='QUATERNION'
    steel=material('TP01_Steel',(.55,.64,.69));leather=material('TP01_GripLeather',(.11,.045,.026));metal=material('TP01_Guard',(.23,.27,.29))
    # Width and length equal the EX benchmark visual; no borrowed arm deformation.
    verts=[]
    for z,width in [(0,.033),(.88,.026),(1.035,0)]:verts.extend([(-width,0,z),(0,-.007,z),(width,0,z),(0,.007,z)])
    faces=[(j,(j+1)%4,(j+1)%4+4,j+4) for j in range(4)]+[(j+4,(j+1)%4+4,(j+1)%4+8,j+8) for j in range(4)]+[(0,3,2,1)]
    meshpart('TP01_Blade',verts,faces,steel,w)
    cube('TP01_Guard',(0,0,-.013),(.27,.035,.026),metal,w)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.018,depth=.255);o=bpy.context.object;o.name='TP01_Grip';o.parent=w;o.location=(0,0,-.151);o.data.materials.append(leather)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.027);o=bpy.context.object;o.name='TP01_Pommel';o.parent=w;o.location=(0,0,-.293);o.data.materials.append(metal)
    for name,z in [('TP01_BladeBase',0),('TP01_BladeTip',1.035)]:o=empty(name);o.parent=w;o.location.z=z
    return w

def sample(f):
    for i,(a,b) in enumerate(zip(BEATS,BEATS[1:])):
        if a['f']<=f<=b['f']:
            t=(f-a['f'])/(b['f']-a['f']);prev=BEATS[max(0,i-1)];nxt=BEATS[min(len(BEATS)-1,i+2)];result={}
            for key in a:
                if key in ('f','name'):continue
                values=[Vector(v[key]) if isinstance(v[key],(tuple,list)) else v[key] for v in (prev,a,b,nxt)]
                p0,p1,p2,p3=values
                m1=(p2-p0)*(b['f']-a['f'])/max(1,b['f']-prev['f']);m2=(p3-p1)*(b['f']-a['f'])/max(1,nxt['f']-a['f'])
                if i==0 or a['f']==19:m1*=0
                if i>=len(BEATS)-3:m2*=0
                result[key]=(2*t**3-3*t*t+1)*p1+(t**3-2*t*t+t)*m1+(-2*t**3+3*t*t)*p2+(t**3-t*t)*m2
            return result
    raise ValueError(f)

def rotate_global(rig,name,q):
    p=rig.pose.bones[name];head=p.head.copy();p.matrix=Matrix.Translation(head)@q.to_matrix().to_4x4()@Matrix.Translation(-head)@p.matrix;bpy.context.view_layer.update()
def point_bone(rig,name,endname,direction):
    p=rig.pose.bones[name];delta=rig.pose.bones[endname].head-p.head;q=delta.normalized().rotation_difference(Vector(direction).normalized());rotate_global(rig,name,q)
def limb(rig,upper,lower,end,target,pole,length_scale=1.):
    sh=rig.pose.bones[upper].head.copy();a=rig.data.bones[upper].head_local;b=rig.data.bones[lower].head_local;c=rig.data.bones[end].head_local
    l1=(b-a).length*length_scale;l2=(c-b).length*length_scale;delta=target-sh;dist=min(delta.length,l1+l2-.0005);axis=delta.normalized()
    p=Vector(pole);p=(p-axis*p.dot(axis)).normalized();along=(l1*l1-l2*l2+dist*dist)/(2*dist);height=math.sqrt(max(0,l1*l1-along*along));elbow=sh+axis*along+p*height
    point_bone(rig,upper,lower,elbow-sh);point_bone(rig,lower,end,target-rig.pose.bones[lower].head)
    return (rig.pose.bones[end].head-target).length,elbow

def align_left_hinge(rig, pole, state):
    names=('upperarm01.L','upperarm02.L','lowerarm01.L')
    sh=rig.pose.bones[names[0]].head.copy()
    el=rig.pose.bones[names[2]].head.copy()
    wr=rig.pose.bones['wrist.L'].head.copy()
    wrist_matrix=rig.pose.bones['wrist.L'].matrix.copy()
    saved={n:rig.pose.bones[n].matrix.copy() for n in names}
    sh0=rig.data.bones[names[0]].head_local
    el0=rig.data.bones[names[2]].head_local
    wr0=rig.data.bones['wrist.L'].head_local
    u0=(el0-sh0).normalized(); v0=(wr0-el0).normalized()
    bind_normal=u0.cross(v0)
    if bind_normal.length < 1e-6:
        raise ValueError('Left-arm bind pose has no stable flexion plane')
    bind_normal.normalize()
    u=(el-sh).normalized(); v=(wr-el).normalized()
    normal=u.cross(v)
    axis=(wr-sh).normalized()
    if normal.length < 1e-5:
        # Elbow plane remains defined by the authored pole as the arm extends.
        projected=Vector(pole)-axis*Vector(pole).dot(axis)
        normal=projected.cross(axis)
        if normal.length < 1e-5:
            # A truly degenerate pole transports the last valid plane through
            # the new shoulder-wrist axis. No normalization of a zero vector.
            previous=state.get('normal')
            if previous is not None:
                normal=previous-axis*previous.dot(axis)
            if normal.length < 1e-5:
                # Deterministic first-frame fallback; pick a transverse basis.
                seed=min((Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))),key=lambda x:abs(x.dot(axis)))
                normal=seed-axis*seed.dot(axis)
            if previous is not None and normal.dot(previous)<0:
                normal.negate()
    normal.normalize(); state['normal']=normal.copy()
    def basis(direction, plane):
        transverse=plane-direction*plane.dot(direction)
        if transverse.length < 1e-6:
            # Normally unreachable: flexion normal is transverse to segments.
            seed=min((Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))),key=lambda x:abs(x.dot(direction)))
            transverse=seed-direction*seed.dot(direction)
        transverse.normalize()
        return Matrix((direction,transverse,direction.cross(transverse).normalized())).transposed()
    for name,rest_axis,posed_axis,origin,share in (
        (names[0],u0,u,sh,.25),
        (names[1],(el0-rig.data.bones[names[1]].head_local).normalized(),None,None,1.),
        (names[2],v0,v,el,1.),
    ):
        if name==names[1]:
            origin=rig.pose.bones[name].head.copy()
            posed_axis=(el-origin).normalized()
        target=basis(posed_axis,normal)@basis(rest_axis,bind_normal).transposed()
        bone_rotation=rig.data.bones[name].matrix_local.to_3x3()
        _,current_rotation,world_scale=saved[name].decompose()
        current_transfer=current_rotation.to_matrix()@bone_rotation.inverted()
        transfer=current_transfer.to_quaternion().slerp(target.to_quaternion(),share).to_matrix()
        rig.pose.bones[name].matrix=(Matrix.Translation(origin)@transfer.to_4x4()
            @bone_rotation.to_4x4()@Matrix.Diagonal((*world_scale,1)))
        bpy.context.view_layer.update()
    # Children retain their authored local digit transforms, so reinstating
    # this matrix restores all hand geometry and exact shaft seating.
    rig.pose.bones['wrist.L'].matrix=wrist_matrix
    bpy.context.view_layer.update()


def authored_grasp(rig,side,rot,hilt,depth,settings):
    """Digit-specific local flexion plus an independently opposed thumb chain.

    Mirrored CF hand bases require opposite curl signs. Thumb target points
    live around the actual18mm handle radius, not in shared joint local-X.
    Each authored rotation remains an ordinary editable FK channel.
    """
    for digit in range(2,6):
        if settings[side].get('wrap_polar'):
            base=rot.inverted()@(rig.pose.bones[f'finger{digit}-1.{side}'].head-hilt)
            for segment,(radius,angle,dz) in enumerate(settings[side]['wrap_polar'][str(digit)],1):
                a=math.radians(angle);target=hilt+rot@Vector((radius*math.cos(a),radius*math.sin(a),base.z+dz));n=f'finger{digit}-{segment}.{side}';swing(rig,n,target-rig.pose.bones[n].head)
            continue
        values=settings[side]['fingers_deg'][str(digit)]
        for segment,angle in enumerate(values,1):
            p=rig.pose.bones.get(f'finger{digit}-{segment}.{side}')
            if p:p.rotation_quaternion=quat((1,0,0),angle)
    bpy.context.view_layer.update()
    for segment,xyz in enumerate(settings[side]['thumb_targets_handle'],1):
        n=f'finger1-{segment}.{side}';target=hilt+rot@Vector((xyz[0],xyz[1],depth+xyz[2]));swing(rig,n,target-rig.pose.bones[n].head)

def build():
    global BEATS
    OUT.mkdir(parents=True,exist_ok=True)
    controls=OUT/'pose-controls.json'
    if controls.exists():BEATS=json.loads(controls.read_text())['beats']
    else:controls.write_text(json.dumps({'status':'Initial authored interpretation; artistic acceptance pending','reference':'Docs/ThirdPersonReference20260908/CLIP_A_ANALYSIS.md','lower_body':'authored; Greatsword feet/pelvis cropped','fps':60,'beats':BEATS},indent=2))
    score=json.loads(controls.read_text());grip_settings=score.get('grasp')
    foundation=ROOT/'ArtSource/CharacterReset/CF_v001/CF_v001_Character.blend';foundation_hash=hashlib.sha256(foundation.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(foundation));scene=bpy.context.scene;rig=bpy.data.objects['CF01_CharacterRig'];rig.animation_data_clear()
    for p in rig.pose.bones:
        p.rotation_mode='QUATERNION';p.matrix_basis=Matrix.Identity(4)
        for c in list(p.constraints):p.constraints.remove(c)
    scene.frame_start=1;scene.frame_end=154;scene.render.fps=60;scene.render.fps_base=1;scene.timeline_markers.clear()
    for b in BEATS:scene.timeline_markers.new(b['name'],frame=b['f'])
    weapon=create_weapon();rest={p.name:p.bone.matrix_local.copy() for p in rig.pose.bones}
    helpers={n:empty('TP01_CTRL_'+n) for n in ['Hand_R','Hand_L','Elbow_R','Elbow_L','Foot_R','Foot_L','Pelvis','Chest']}
    for h in helpers.values():h['role']='Editable pose target/score reference; source closure is baked to FK. Rebuild from pose-controls.json or adjust FK directly.'
    body=bpy.data.objects['CF01_Body']
    # Workbench does not evaluate shader shorts; assign existing garment material
    # to its explicit bounded surface region for clothed review in both engines.
    for poly in body.data.polygons:
        c=poly.center
        if .80<c.z<1.045 and abs(c.x)<.25:poly.material_index=1
    for mod in body.modifiers:
        if mod.type=='SUBSURF':mod.levels=1;mod.render_levels=1
    meshobjects=[o for o in scene.objects if o.type=='MESH']
    for o in meshobjects:o.hide_viewport=True
    errors=[];rows=[];previous={};hinge_state={};canonical=json.loads((ROOT/'ArtSource/CharacterReset/EX_v002/Export/EX_v002_WeaponMotion.json').read_text())['samples']
    for f in range(1,155):
        scene.frame_set(f)
        for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
        bpy.context.view_layer.update();v=sample(f)
        root=rig.pose.bones['root'];root.matrix=Matrix.Translation(v['p'])@Matrix.Translation(root.head)@quat((0,0,1),v['py']).to_matrix().to_4x4()@Matrix.Translation(-root.head)@root.matrix
        bpy.context.view_layer.update()
        for n,share in [('spine03',.22),('spine02',.35),('spine01',.43)]:rotate_global(rig,n,quat((0,0,1),v['cy']*share)@quat((1,0,0),v['lean']*share)@quat((0,1,0),v['side']*share))
        # Threat-facing head counterturns the chest, leaving modest living tilt.
        rotate_global(rig,'head',quat((0,0,1),-(v['py']+v['cy'])*.82)@quat((1,0,0),-v['lean']*.7))
        helpers['Pelvis'].location=root.head;helpers['Chest'].location=rig.pose.bones['spine01'].head
        # Feet stay on fixed toe contacts with a small pivot; knee pole points
        # forward. No gait or sine-based decorative movement is authored.
        for idx,(side,sign) in enumerate([('R',-1),('L',1)]):
            ankle=rig.data.bones['foot.'+side].head_local.copy();ankle.x+=sign*.015;ankle.y+=.10 if side=='R' else -.10
            pivot=ankle+Vector((0,-.13,-.05));q=quat((0,0,1),v['feet'][idx]);ankle=pivot+q@(ankle-pivot)
            e,knee=limb(rig,'upperleg01.'+side,'lowerleg01.'+side,'foot.'+side,ankle,(sign*.10,-1,.02))
            p=rig.pose.bones['foot.'+side];p.matrix=Matrix.Translation(p.head)@q.to_matrix().to_4x4()@rest[p.name].to_3x3().to_4x4();bpy.context.view_layer.update();helpers['Foot_'+side].location=ankle
            errors.append({'frame':f,'target':'foot.'+side,'error_m':e})
        # Source-only direction constraint; weapon and both grasps share it.
        if score.get('release_direction_from_canonical',False) and 63<=f<=81:
            c=canonical[f-1];v['d']=Vector(c['blade_tip_world_m'])-Vector(c['blade_base_world_m'])
        rot=v['d'].normalized().to_track_quat('Z','Y')@quat((0,0,1),v.get('weapon_roll_deg',0));hilt=v['h'];weapon.location=hilt;weapon.rotation_quaternion=rot
        if 'weapon' in previous and rot.dot(previous['weapon'])<0:rot.negate();weapon.rotation_quaternion=rot
        previous['weapon']=rot.copy()
        for idx,(side,sign,depth) in enumerate([('R',-1,-.070),('L',1,-.195)]):
            # Protraction changes independently on each side with lever demand.
            reach=v['sr'][idx];bodyq=quat((0,0,1),v['py']+v['cy'])
            swing(rig,'clavicle.'+side,bodyq@Vector((sign,-reach,.12)))
            shoulder_aim=v.get(('left' if side=='L' else 'right')+'_shoulder_aim',Vector((sign,-reach*.85,-.40)))
            swing(rig,'shoulder01.'+side,bodyq@shoulder_aim)
            wrist_rest=rig.data.bones['wrist.'+side].head_local.copy()
            rest_y=(rig.data.bones['finger3-1.'+side].head_local-wrist_rest).normalized();rest_x=(rig.data.bones['finger2-1.'+side].head_local-rig.data.bones['finger5-1.'+side].head_local).normalized();rest_z=rest_x.cross(rest_y).normalized();rest_x=rest_y.cross(rest_z).normalized()
            # Seat each palm around the same shaft; mirror anatomy does not
            # imply opposed palms. Keep the grasp roll editable in the score.
            grip_roll=v.get(('left' if side=='L' else 'right')+'_grasp_roll_deg')
            if grip_roll is None:grip_roll=(grip_settings or {}).get(side,{}).get('shaft_roll_deg',0)
            grasp_rot=rot@quat((0,0,1),grip_roll)
            dst_x=grasp_rot@Vector((0,0,1));dst_y=grasp_rot@Vector((-sign,0,0));dst_z=dst_x.cross(dst_y).normalized()
            # A fist need not meet the shaft at exactly ninety degrees.
            # Cant the palm while the authored digits still enclose the handle.
            cant=math.radians(v.get(('left' if side=='L' else 'right')+'_grasp_cant_deg',0))
            dx,dy=dst_x.copy(),dst_y.copy();dst_x=dx*math.cos(cant)-dy*math.sin(cant);dst_y=dy*math.cos(cant)+dx*math.sin(cant)
            basis=Matrix((dst_x,dst_y,dst_z)).transposed()@Matrix((rest_x,rest_y,rest_z)).transposed().inverted()
            grip=hilt+rot@Vector((0,0,depth));target=grip-dst_y*.077+dst_z*.024
            # Deliberate carry exaggeration: scale the coherent upper/forearm
            # chain from its shoulder pivot. Wrist below restores unit world
            # scale so the approved hand/handle contact remains unchanged.
            upper=rig.pose.bones['upperarm01.'+side]
            upper_rest=(rig.data.bones['lowerarm01.'+side].head_local-rig.data.bones['upperarm01.'+side].head_local).length
            fore_rest=(wrist_rest-rig.data.bones['lowerarm01.'+side].head_local).length
            span=(target-upper.head).length
            extension=max(0.,min(1.,v.get('power_extension',(0.,0.))[idx]))
            bend=math.radians(max(8.,min(150.,v.get('power_bend_deg',(70.,70.))[idx])))
            desired_span=math.sqrt(upper_rest**2+fore_rest**2+2*upper_rest*fore_rest*math.cos(bend))
            authored_scale=max(1.,v.get('arm_scale',(1.,1.))[idx])
            extension_scale=max(1.,span/max(desired_span,1e-6))
            stretch=max(1.,span/max(upper_rest+fore_rest-.0005,1e-6),authored_scale*(1-extension)+extension_scale*extension)
            if stretch!=1.:
                sh=upper.head.copy();upper.matrix=Matrix.Translation(sh)@Matrix.Scale(stretch,4)@Matrix.Translation(-sh)@upper.matrix;bpy.context.view_layer.update()
            error,elbow=limb(rig,'upperarm01.'+side,'lowerarm01.'+side,'wrist.'+side,target,v['er' if side=='R' else 'el'],stretch)
            p=rig.pose.bones['wrist.'+side];p.matrix=Matrix.Translation(p.head)@basis.to_4x4()@rest[p.name].to_3x3().to_4x4();bpy.context.view_layer.update()
            sh=rig.pose.bones['upperarm01.'+side].head.copy()
            upper_length=(rig.data.bones['lowerarm01.'+side].head_local-rig.data.bones['upperarm01.'+side].head_local).length
            fore_length=(wrist_rest-rig.data.bones['lowerarm01.'+side].head_local).length
            errors.append({'frame':f,'target':'wrist.'+side,'error_m':error,'shoulder_to_wrist_m':(target-sh).length,'unscaled_max_reach_m':upper_length+fore_length,'authored_arm_scale':stretch,'shoulder_m':list(sh),'wrist_target_m':list(target)})
            helpers['Hand_'+side].location=target;helpers['Elbow_'+side].location=elbow
            if grip_settings:authored_grasp(rig,side,grasp_rot,hilt,depth,grip_settings)
            else:
                for digit in range(1,6):
                    for segment in range(1,4):
                        p=rig.pose.bones.get(f'finger{digit}-{segment}.{side}')
                        if p:p.rotation_quaternion=Quaternion((1,0,0),(.65 if digit==1 else 1.07)+(0.035 if 60<=f<=94 else 0))
            if side=='L':align_left_hinge(rig,v['el'],hinge_state)
        for p in rig.pose.bones:
            if p.name in previous and p.rotation_quaternion.dot(previous[p.name])<0:p.rotation_quaternion.negate()
            previous[p.name]=p.rotation_quaternion.copy();p.keyframe_insert('rotation_quaternion',frame=f,group=p.name);p.keyframe_insert('location',frame=f,group=p.name);p.keyframe_insert('scale',frame=f,group=p.name)
        weapon.keyframe_insert('location',frame=f);weapon.keyframe_insert('rotation_quaternion',frame=f)
        for helper in helpers.values():helper.keyframe_insert('location',frame=f)
        tip=hilt+rot@Vector((0,0,1.035));c=canonical[f-1]
        rows.append({'frame':f,'time_s':(f-1)/60,'tp_base_m':list(hilt),'tp_tip_m':list(tip),'canonical_base_m':c['blade_base_world_m'],'canonical_tip_m':c['blade_tip_world_m'],'base_delta_m':(hilt-Vector(c['blade_base_world_m'])).length,'tip_delta_m':(tip-Vector(c['blade_tip_world_m'])).length})
    rig.animation_data.action.name='TP01_WholeBody_NeutralRight_Block_v001';weapon.animation_data.action.name='TP01_Weapon_NeutralRight_Block_v001'
    for o in [rig,weapon,*helpers.values()]:
        for fc in o.animation_data.action.fcurves:
            for k in fc.keyframe_points:k.interpolation='LINEAR'
    for o in meshobjects:o.hide_viewport=False
    for name,loc in [('FrontThreeQuarter',(3,-5,2.8)),('RearThreeQuarter',(-2.6,5,2.6)),('Defender',(0,-5,1.65))]:
        d=bpy.data.cameras.new('TP01_'+name);o=bpy.data.objects.new('TP01_'+name,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,-.20,1.13))-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=3.9
    setup_render();scene.camera=bpy.data.objects['TP01_FrontThreeQuarter'];scene.frame_set(1)
    scene['TP01_status']='INITIAL COMPLETE BLOCK; authored lower-body interpretation; human artistic acceptance pending'
    scene['TP01_edit_loop']='Edit pose-controls.json and rebuild, or directly edit CF rig FK / TP weapon action; export and reimport selected TP only.'
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    release=[r for r in rows if 63<=r['frame']<=81]
    reach=[];byframe={r['frame']:r for r in rows}
    for e in errors:
        if not e['target'].startswith('wrist') or not 63<=e['frame']<=81:continue
        r=byframe[e['frame']];ct=Vector(e['wrist_target_m'])+Vector(r['canonical_base_m'])-Vector(r['tp_base_m']);dist=(ct-Vector(e['shoulder_m'])).length
        reach.append({'frame':e['frame'],'side':e['target'][-1],'tp_shoulder_to_wrist_m':e['shoulder_to_wrist_m'],'same_shoulder_canonical_hilt_wrist_distance_m':dist,'unscaled_max_reach_m':e['unscaled_max_reach_m'],'excess_m':dist-e['unscaled_max_reach_m']})
    (OUT/'canonical-overlay.json').write_text(json.dumps({'authority':'Diagnostic only; TP never replaces canonical simulation motion','samples':rows,'release_max_base_delta_m':max(r['base_delta_m'] for r in release),'release_max_tip_delta_m':max(r['tip_delta_m'] for r in release),'limitation':'This block diverges from canonical release positions; this pose diagnostic does not prove all coauthored alternatives impossible. No contact acceptance.','reach_diagnostic':{'scope':'Translate actual TP wrists by canonical-minus-TP hilt, retain TP shoulder and grip orientation. This pose only, not a proof all coauthored poses fail.','samples':reach}},indent=2))
    report={'source':str(SOURCE.relative_to(ROOT)),'foundation_sha256':foundation_hash,'fps':60,'frames':154,'duration_s':2.55,'anatomy_changed':False,'root_object_stationary':True,'source_ik_baked_to_fk':True,'max_wrist_error_m':max(x['error_m'] for x in errors if x['target'].startswith('wrist')),'max_foot_error_m':max(x['error_m'] for x in errors if x['target'].startswith('foot')),'errors_above_1mm':[x for x in errors if x['error_m']>.001],'artistic_acceptance':False,'continuous_playback_viewed':False,'reference_feet_hidden':True}
    report['revision']=json.loads(controls.read_text()).get('revision','Block01')
    report['release_reach_samples']=[e for e in errors if e['target'].startswith('wrist') and 63<=e['frame']<=81]
    report['max_shoulder_to_wrist_m']=max(e['shoulder_to_wrist_m'] for e in errors if e['target'].startswith('wrist'))
    report['max_authored_arm_scale']=max(e['authored_arm_scale'] for e in errors if e['target'].startswith('wrist'))
    report['deformation_intent']='Temporary coherent arm-chain enlargement/extension during left swing-through; hand world scale restored to preserve grasp. Artistic exaggeration, not a physical necessity.'
    (OUT/'motion-report.json').write_text(json.dumps(report,indent=2));print('SOURCE_READY',json.dumps({k:v for k,v in report.items() if k!='release_reach_samples'}),flush=True)

def setup_render():
    s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=.45;s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.055,.065,.080);s.display.shading.show_specular_highlight=True;s.render.resolution_x=900;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
def render(inspect=False,overlay=False,power=False,hands=False,review=False,review_side=False,carry=False):
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));setup_render();s=bpy.context.scene
    cameras=['FrontThreeQuarter','RearThreeQuarter'] if inspect else ['FrontThreeQuarter']
    frames=[19,52,63,73,81,94,108,139] if inspect else range(19,155)
    if power or review_side or carry:
        frames=[63,68,73,81];cameras=['FrontThreeQuarter','Side']
        if not bpy.data.objects.get('TP01_Side'):
            d=bpy.data.cameras.new('TP01_Side');o=bpy.data.objects.new('TP01_Side',d);bpy.context.collection.objects.link(o);o.location=(5,0,1.75);o.rotation_euler=(Vector((0,-.20,1.15))-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=3.9
    if review_side:cameras=['Side'];frames=[52,73,88]
    if carry:cameras=['FrontThreeQuarter','Side'];frames=[52,88,94]
    if review:
        cameras=['FrontThreeQuarter','RearThreeQuarter'];frames=[52,60,63,68,73,81,88,94]
    if hands:
        body=bpy.data.objects['CF01_Body'];keep_groups={g.index for g in body.vertex_groups if g.name.startswith(('wrist','finger','metacarpal'))}
        allowed={v.index for v in body.data.vertices if sum(g.weight for g in v.groups if g.group in keep_groups)>.001}
        hand=body.copy();hand.data=body.data.copy();hand.name='TP01_IsolatedHands_ReviewOnly';bpy.context.collection.objects.link(hand)
        bm=bmesh.new();bm.from_mesh(hand.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in allowed],context='VERTS');bm.to_mesh(hand.data);bm.free()
        for o in s.objects:
            if o.type=='MESH' and not o.name.startswith('TP01_'):o.hide_render=True
        cameras=['HandPalm','HandSide'];frames=[73,94]
        for n in cameras:
            d=bpy.data.cameras.new('TP01_'+n);o=bpy.data.objects.new('TP01_'+n,d);bpy.context.collection.objects.link(o);d.type='ORTHO';d.ortho_scale=.48
    if overlay:
        frames=[63,73,81];cameras=['FrontThreeQuarter'];data={r['frame']:r for r in json.loads((OUT/'canonical-overlay.json').read_text())['samples']}
        cyan=material('Canonical_Cyan',(.04,.85,1));bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.008,depth=1);guide=bpy.context.object;guide.data.materials.append(cyan)
    for cam in cameras:
        s.camera=bpy.data.objects['TP01_'+cam];folder=OUT/'Preview'/('CanonicalOverlay' if overlay else ('Hands_'+cam if hands else ('Keys_'+cam if inspect or power or review or review_side or carry else cam)));folder.mkdir(parents=True,exist_ok=True)
        for f in frames:
            s.frame_set(f)
            if hands:
                w=bpy.data.objects['TP01_WeaponRoot'];q=w.rotation_quaternion;target=w.location+q@Vector((0,0,-.135));offset=Vector((.48,-.6,.07)) if cam=='HandPalm' else Vector((.65,.22,-.03));s.camera.location=target+q@offset;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
            if overlay:
                a=Vector(data[f]['canonical_base_m']);b=Vector(data[f]['canonical_tip_m']);guide.location=(a+b)*.5;guide.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();guide.scale.z=(b-a).length
            s.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
        print('RENDER_DONE',cam,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inspect',action='store_true');p.add_argument('--render',action='store_true');p.add_argument('--overlay',action='store_true');p.add_argument('--power-keys',action='store_true');p.add_argument('--hands',action='store_true');p.add_argument('--review-keys',action='store_true');p.add_argument('--review-side',action='store_true');p.add_argument('--carry-keys',action='store_true');args=p.parse_args()
    if args.inspect or args.render or args.overlay or args.power_keys or args.hands or args.review_keys or args.review_side or args.carry_keys:render(args.inspect,args.overlay,args.power_keys,args.hands,args.review_keys,args.review_side,args.carry_keys)
    else:build()
