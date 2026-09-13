"""Fresh anatomical character study; no Citadel mesh, rig or combat code imports.

Raw topology, morph deltas and anatomical rig/weight reference are CC0 MPFB
graphic assets. See CharacterReset/Reference/source-manifest.json. This script
constructs the character, adjusts limb proportions, builds an independent rig,
and saves source + explicit shoulder review poses. It does not author attacks.
"""
import sys, json, gzip, math, argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy, bmesh
from mathutils import Vector, Matrix, Quaternion

OUT=ROOT/'ArtSource/CharacterReset/CF_v001'
REF=ROOT/'ArtSource/CharacterReset/Reference'
OUT.mkdir(parents=True,exist_ok=True)
REVIEW=OUT/'Review';REVIEW.mkdir(exist_ok=True)
PARAMS={'height_m':1.80,'muscle_blend':.35,'upper_arm_length_scale':1.16,
        'forearm_length_scale':.94,'hand_scale':.92}

def read_source():
    coords=[];uv=[];faces=[];face_uv=[];groups={};group=''
    for line in (REF/'base.obj').read_text().splitlines():
        a=line.split()
        if not a:continue
        if a[0]=='v':coords.append(Vector(tuple(map(float,a[1:]))))
        elif a[0]=='vt':uv.append(tuple(map(float,a[1:3])))
        elif a[0]=='g':group=a[1]
        elif a[0]=='f':
            inds=[int(s.split('/')[0])-1 for s in a[1:]]
            groups.setdefault(group,set()).update(inds)
            if group=='body':
                faces.append(inds);face_uv.append([int(s.split('/')[1])-1 for s in a[1:]])
    # An adult male study. These are source morph category names, not inferred
    # ethnicity or identity. No resemblance to a particular person is intended.
    for name,amount in [('caucasian-male-young',.5),('african-male-young',.25),
                        ('asian-male-young',.25),
                        ('universal-male-young-maxmuscle-averageweight',PARAMS['muscle_blend'])]:
        for line in gzip.decompress((REF/(name+'.target.gz')).read_bytes()).decode().splitlines():
            a=line.split()
            if len(a)==4 and a[0].isdigit():coords[int(a[0])]+=Vector(tuple(map(float,a[1:])))*amount
    floor=min(coords[i].y for i in groups['body'])
    scale=PARAMS['height_m']/(max(coords[i].y for i in groups['body'])-floor)
    coords=[Vector((v.x*scale,-v.z*scale,(v.y-floor)*scale)) for v in coords]
    return coords,faces,uv,face_uv,groups

def material(name,color,roughness=.65):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness
    return m

def select(obj):
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    coords,faces,uv,face_uv,groups=read_source()
    ref_rig=json.loads((REF/'rig.default.json').read_text())
    ref_weights=json.loads((REF/'weights.default.json').read_text())['weights']
    def locate(d):
        if d['strategy']=='CUBE':ids=groups[d['cube_name']]
        elif d['strategy']=='VERTEX':ids=[d['vertex_index']]
        elif d['strategy']=='MEAN':ids=d['vertex_indices']
        else:raise ValueError(d)
        return sum((coords[i] for i in ids),Vector())/len(ids)
    # Retain body, shoulder girdle, twist segments, hands and finger controls.
    # Facial control weights fold into head for this body-deformation study.
    prefixes=('root','spine','neck','head','pelvis','clavicle','shoulder',
              'upperarm','lowerarm','wrist','finger','metacarpal','upperleg','lowerleg','foot','toe')
    keep={n for n in ref_rig if n.startswith(prefixes)}
    def mapped(n):
        if n.startswith('breast'):return 'spine02'
        return n if n in keep else 'head'
    joints={n:{'head':locate(d['head']),'tail':locate(d['tail']),
              'roll':d['roll'],'parent':mapped(d['parent']) if d['parent'] else ''}
              for n,d in ref_rig.items() if n in keep}
    # Rest-pose customization uses piecewise bone-space deformation. The new
    # arm/hand lengths do not inherit the old gameplay IK constants.
    rigdata=bpy.data.armatures.new('Foundation_DeformSkeleton')
    rig=bpy.data.objects.new('CF01_CharacterRig',rigdata);bpy.context.collection.objects.link(rig);select(rig)
    bpy.ops.object.mode_set(mode='EDIT')
    for n,d in joints.items():
        b=rigdata.edit_bones.new(n);b.head=d['head'];b.tail=d['tail'];b.roll=d['roll']
    for n,d in joints.items():
        if d['parent']:rigdata.edit_bones[n].parent=rigdata.edit_bones[d['parent']]
    bpy.ops.object.mode_set(mode='OBJECT')
    old={n:b.matrix_local.copy() for n,b in rigdata.bones.items()}
    new={};length_scale={};width_scale={}
    def fit(n):
        if n in new:return
        d=joints[n];parent=d['parent']
        factor=PARAMS['upper_arm_length_scale'] if n.startswith('upperarm') else PARAMS['forearm_length_scale'] if n.startswith('lowerarm') else PARAMS['hand_scale'] if n.startswith(('wrist','finger','metacarpal')) else 1.
        width=PARAMS['hand_scale'] if n.startswith(('wrist','finger','metacarpal')) else 1.
        length_scale[n]=factor;width_scale[n]=width
        if parent:
            fit(parent)
            offset=d['head']-joints[parent]['head']
            axis=(joints[parent]['tail']-joints[parent]['head']).normalized()
            # Scale all offsets within hands, axial offsets along arm segments.
            lateral=offset-axis*offset.dot(axis)
            head=new[parent]['head']+axis*offset.dot(axis)*length_scale[parent]+lateral*width_scale[parent]
        else:head=d['head'].copy()
        new[n]={'head':head,'tail':head+(d['tail']-d['head'])*factor}
    for n in joints:fit(n)
    bpy.ops.object.mode_set(mode='EDIT')
    for n,d in new.items():rigdata.edit_bones[n].head=d['head'];rigdata.edit_bones[n].tail=d['tail']
    bpy.ops.object.mode_set(mode='OBJECT')
    maps={n:rigdata.bones[n].matrix_local @ Matrix.Diagonal((width_scale[n],length_scale[n],width_scale[n],1.)) @ old[n].inverted() for n in joints}
    weights=[{} for _ in range(13380)]
    for n,values in ref_weights.items():
        target=mapped(n)
        for i,w in values:
            if i<len(weights):weights[i][target]=weights[i].get(target,0.)+w
    # Normalize all original influences; no nearest-bone reconstruction.
    for i,ws in enumerate(weights):
        total=sum(ws.values())
        if total<1e-8:raise RuntimeError('Unweighted body vertex '+str(i))
        weights[i]={n:w/total for n,w in ws.items() if w/total>1e-8}
    fitted=[sum((maps[n]@coords[i]*w for n,w in ws.items()),Vector()) for i,ws in enumerate(weights)]
    mesh=bpy.data.meshes.new('CF01_ContinuousAnatomicalSurface');mesh.from_pydata(fitted,[],faces);mesh.update()
    body=bpy.data.objects.new('CF01_Body',mesh);bpy.context.collection.objects.link(body)
    layer=mesh.uv_layers.new(name='AnatomicalUV')
    for poly,indices in zip(mesh.polygons,face_uv):
        poly.use_smooth=True
        for loop,j in zip(poly.loop_indices,indices):layer.data[loop].uv=uv[j]
    skin=material('Study_WarmClay',(.43,.34,.27),.72)
    shorts=material('Study_FittedShorts',(.035,.058,.075),.85)
    body.data.materials.append(skin);body.data.materials.append(shorts)
    # Simple close-fitting study garment, surface only. Exposes the entire
    # thorax, deltoid, axilla and scapular region for honest shape inspection.
    region=mesh.attributes.new('StudyShortsRegion','FLOAT','POINT')
    for v in mesh.vertices:
        region.data[v.index].value=min(v.co.z-.80,1.045-v.co.z,.25-abs(v.co.x))
    nodes=skin.node_tree.nodes;links=skin.node_tree.links
    attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='StudyShortsRegion'
    inside=nodes.new('ShaderNodeMath');inside.operation='GREATER_THAN';inside.inputs[1].default_value=0
    mix=nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.43,.34,.27,1);mix.inputs[2].default_value=(.035,.058,.075,1)
    links.new(attr.outputs['Fac'],inside.inputs[0]);links.new(inside.outputs[0],mix.inputs[0])
    links.new(mix.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])
    for n in joints:body.vertex_groups.new(name=n)
    for i,ws in enumerate(weights):
        for n,w in ws.items():body.vertex_groups[n].add([i],w,'REPLACE')
    mod=body.modifiers.new('LinearSkinning_ReviewAndExport','ARMATURE');mod.object=rig
    # Use linear skinning deliberately so renders do not hide an export-only
    # regression behind Blender's nonportable dual-quaternion option.
    mod.use_deform_preserve_volume=False
    sub=body.modifiers.new('Surface_Subdivision','SUBSURF');sub.levels=1;sub.render_levels=2
    body.parent=rig
    rig.show_in_front=True;rig.data.display_type='STICK'
    for pb in rig.pose.bones:pb.rotation_mode='QUATERNION'
    for name in ['clavicle.L','clavicle.R','shoulder01.L','shoulder01.R']:
        rig.pose.bones[name]['role']='Independent shoulder girdle: key elevation/protraction with arm motion'
    rig['source']='Independent CF01 rig, derived from CC0 anatomical landmark/weight data; no Citadel compatibility constraint'
    body['source']='MPFB CC0 hm08 topology + adult morph blend, limb proportions customized; see source-manifest.json'
    body['purpose']='Character foundation and deformation study; not final armor or accepted attack animation'
    # Smooth eyeballs are separate anatomy; body/arms remain one mesh island.
    for side in ['L','R']:
        n='eye.'+side;c=locate(ref_rig[n]['head'])
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=.012,location=c)
        eye=bpy.context.object;eye.name='CF01_Eye.'+side
        eye.data.materials.append(material('EyeClay.'+side,(.53,.49,.43),.52))
        for p in eye.data.polygons:p.use_smooth=True
        # Bone parenting keeps the exact rest placement.
        world=eye.matrix_world.copy();eye.parent=rig;eye.parent_type='BONE';eye.parent_bone='head';eye.matrix_world=world
    # Reference skeleton data, measurements and geometry QA.
    bm=bmesh.new();bm.from_mesh(mesh);seen=set();islands=[]
    for v in bm.verts:
        if v in seen:continue
        todo=[v];seen.add(v);count=0
        while todo:
            q=todo.pop();count+=1
            for e in q.link_edges:
                w=e.other_vert(q)
                if w not in seen:seen.add(w);todo.append(w)
        islands.append(count)
    boundary=[e for e in bm.edges if e.is_boundary]
    shoulder_boundary=sum(1 for e in boundary if any(1.25<v.co.z<1.55 and .13<abs(v.co.x)<.32 for v in e.verts))
    report={'parameters':PARAMS,'vertices':len(mesh.vertices),'faces':len(mesh.polygons),
            'quads':sum(len(p.vertices)==4 for p in mesh.polygons),'body_islands':islands,
            'boundary_edges':len(boundary),'shoulder_boundary_edges':shoulder_boundary,
            'bones':len(joints),'linear_skinning':True,'old_character_assets_used':False,
            'source_graphic_assets':'CC0 MakeHuman Community MPFB, see Reference/source-manifest.json'}
    for side in ['L','R']:
        s=rigdata.bones['upperarm01.'+side].head_local;e=rigdata.bones['lowerarm01.'+side].head_local
        w=rigdata.bones['wrist.'+side].head_local;tip=rigdata.bones['finger3-3.'+side].tail_local
        report[side]={'upper_arm_cm':(s-e).length*100,'forearm_cm':(e-w).length*100,'wrist_to_middle_tip_cm':(w-tip).length*100}
    report['joint_centres']={n:{'head':list(b.head_local),'tail':list(b.tail_local)} for n,b in rigdata.bones.items()}
    (OUT/'character-report.json').write_text(json.dumps(report,indent=2));bm.free()
    setup_stage()
    make_pose_action(rig)
    bpy.context.scene.frame_set(1);select(rig)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CF_v001_Character.blend'))
    # Rest skeleton + posed review action; no gameplay arm fitting downstream.
    select(body);rig.select_set(True)
    for obj in bpy.context.scene.objects:
        if obj.name.startswith('CF01_Eye.'):obj.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(OUT/'CF_v001_Character.fbx'),use_selection=True,
        add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,
        bake_anim_simplify_factor=0.,axis_forward='-Y',axis_up='Z',path_mode='STRIP',
        use_mesh_modifiers=True,mesh_smooth_type='FACE')
    print('CHARACTER BUILT',json.dumps({k:v for k,v in report.items() if k!='joint_centres'}),flush=True)
    return rig,body

def setup_stage():
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
    scene.render.threads_mode='FIXED';scene.render.threads=4
    scene.render.resolution_x=900;scene.render.resolution_y=1150;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.world=bpy.data.worlds.new('Review_World');scene.world.color=(.18,.18,.18)
    scene.view_settings.view_transform='AgX'
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005));floor=bpy.context.object;floor.name='Review_Floor'
    floor.data.materials.append(material('Review_Floor',(.065,.080,.095),.9))
    for name,loc,power,size in [('Key',(-3,-4,5),550,4),('Fill',(3,-1,3),350,3),('Rim',(1,3,4),700,3)]:
        d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
        o.location=loc;d.energy=power;d.shape='DISK';d.size=size
        o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
    d=bpy.data.cameras.new('Review_Camera');o=bpy.data.objects.new('Review_Camera',d);bpy.context.collection.objects.link(o);scene.camera=o
    d.type='ORTHO';d.ortho_scale=2.12
    camera((2.7,-5,2.6),target=(0,0,.94))

def camera(loc,target=(0,0,.94),scale=2.12):
    c=bpy.context.scene.camera;c.location=loc;c.data.ortho_scale=scale
    c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()

def world_swing(rig,name,direction):
    bpy.context.view_layer.update();p=rig.pose.bones[name];head=p.head.copy()
    q=(p.tail-p.head).normalized().rotation_difference(Vector(direction).normalized())
    p.matrix=Matrix.Translation(head)@q.to_matrix().to_4x4()@Matrix.Translation(-head)@p.matrix
    bpy.context.view_layer.update()

def pose(rig,name):
    for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
    bpy.context.view_layer.update()
    if name=='bind':return
    for side,sign in [('L',1),('R',-1)]:
        # Explicitly keyed shoulder girdle participation; no physical solver
        # or runtime heuristic is needed to preserve these review poses.
        if name=='elevated':
            world_swing(rig,'clavicle.'+side,(sign*.91,0,.42))
            world_swing(rig,'shoulder01.'+side,(sign*.82,-.05,.57))
            upper=(sign*.42,-.12,.90);lower=(sign*.34,-.18,.92)
        elif name=='reach':
            world_swing(rig,'clavicle.'+side,(sign*.92,-.35,.16))
            world_swing(rig,'shoulder01.'+side,(sign*.90,-.40,-.10))
            upper=(sign*.18,-.975,.12);lower=(-sign*.10,-.97,.20)
        elif name=='cross':
            world_swing(rig,'clavicle.'+side,(sign*.9,-.37,.2))
            world_swing(rig,'shoulder01.'+side,(sign*.85,-.5,-.05))
            upper=(sign*.32,-.72,-.61);lower=(-sign*.55,-.35,.75)
        elif name=='abducted':
            world_swing(rig,'clavicle.'+side,(sign*.98,0,.20))
            world_swing(rig,'shoulder01.'+side,(sign*.98,0,.12))
            upper=(sign,0,.03);lower=(sign,-.05,.02)
        else:upper=(sign*.10,0,-1);lower=(sign*.08,-.10,-1)
        world_swing(rig,'upperarm01.'+side,upper)
        world_swing(rig,'lowerarm01.'+side,lower)
        # Neutral hands continue the forearm axis. This is a body study, not
        # a pre-imposed old sword grip or closed gauntlet pose.
        world_swing(rig,'wrist.'+side,lower)

POSES=[(1,'bind'),(25,'neutral'),(55,'abducted'),(85,'elevated'),(115,'reach'),(145,'cross'),(175,'neutral'),(195,'bind')]
def make_pose_action(rig):
    scene=bpy.context.scene;scene.render.fps=30;scene.frame_start=1;scene.frame_end=195
    for f,name in POSES:
        scene.frame_set(f);pose(rig,name)
        for pb in rig.pose.bones:
            pb.keyframe_insert('rotation_quaternion',frame=f,group=pb.name)
            pb.keyframe_insert('location',frame=f,group=pb.name)
    rig.animation_data.action.name='CF01_ShoulderAndReach_Study'
    for f,name in POSES:scene.timeline_markers.new(name,frame=f)

def render_views():
    scene=bpy.context.scene
    views=[('01_neutral_front',25,(0,-8,2.0),(0,0,.92),2.03),
           ('02_neutral_side',25,(8,0,2.0),(0,0,.92),2.03),
           ('03_neutral_back',25,(0,8,2.0),(0,0,.92),2.03),
           ('04_threequarter',1,(3,-5,2.1),(0,-.03,.94),2.10),
           ('05_shoulders_raised',85,(2.8,-5,2),(0,0,1.55),1.85),
           ('06_forward_reach',115,(3,-4,2.1),(0,-.18,1.35),1.80),
           ('07_elbow_flexion',145,(2,-5,2.0),(0,-.08,1.40),1.22),
           ('08_back_abduction',55,(2.8,5,2.1),(0,0,1.39),1.45)]
    for filename,frame,loc,target,scale in views:
        scene.frame_set(frame);camera(loc,target,scale);scene.render.filepath=str(REVIEW/(filename+'.png'))
        bpy.ops.render.render(write_still=True);print('RENDERED',filename,flush=True)
    scene.frame_set(25);camera((3,-5,2.1));select(bpy.data.objects['CF01_CharacterRig'])
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CF_v001_Character.blend'))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--render',action='store_true');parser.add_argument('--render-only',action='store_true');args=parser.parse_args()
    if args.render_only:bpy.ops.wm.open_mainfile(filepath=str(OUT/'CF_v001_Character.blend'))
    else:build()
    if args.render or args.render_only:render_views()
