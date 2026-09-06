"""DCC build: source knight -> weighted rig/first-person arms, calibrated sword, masonry kit.

Requires Blender Python (bpy 4.2). Source assets and their licenses are in ArtSource/Citadel.
Run with the project's isolated Saved/ArtRuntime dependency directory or Blender Python.
"""
import sys, math, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy, bmesh
from mathutils import Vector
SRC=ROOT/'ArtSource/Citadel';OUT=SRC/'Export';OUT.mkdir(parents=True,exist_ok=True)

def select(objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects: obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]

def export(name,objects):
    select(objects)
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,
        add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',
        use_mesh_modifiers=True,mesh_smooth_type='FACE',path_mode='STRIP')

def knight():
    bpy.ops.wm.open_mainfile(filepath=str(SRC/'knight/armor.blend'))
    obj=bpy.data.objects['Group61487'];select([obj]);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    # Remove the disconnected shield island; sword is a separate source object.
    bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table();seen=set();remove=[]
    for v in bm.verts:
        if v in seen: continue
        todo=[v];island=[];seen.add(v)
        while todo:
            a=todo.pop();island.append(a)
            for e in a.link_edges:
                b=e.other_vert(a)
                if b not in seen:seen.add(b);todo.append(b)
        if len(island)==930:remove.extend(island)
    assert len(remove)==930, 'Source shield topology changed; inspect before rebuilding'
    bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(obj.data);bm.free()
    for other in list(bpy.data.objects):
        if other!=obj:bpy.data.objects.remove(other,do_unlink=True)
    scale=1.86/5.595
    def point(p):return Vector((p[0]*scale,p[1]*scale,(p[2]+2.386)*scale))
    for v in obj.data.vertices:v.co=point(v.co)
    obj.name='SK_CitadelKnight'
    # An explicit deformation skeleton. Finger silhouettes are retained from source.
    joints={
      'root':((0,0,-2.386),(0,0,-2.1),None),
      'pelvis':((0,0,.1),(0,0,.65),'root'),
      'spine_01':((0,0,.65),(0,0,1.25),'pelvis'),
      'spine_02':((0,0,1.25),(0,0,2.15),'spine_01'),
      'neck':((0,0,2.15),(0,0,2.5),'spine_02'),
      'head':((0,0,2.5),(0,0,3.18),'neck')}
    for side,sign in [('r',-1),('l',1)]:
        joints.update({
          'clavicle_'+side:((sign*.15,0,2.05),(sign*.83,0,2.05),'spine_02'),
          'upperarm_'+side:((sign*.83,0,2.05),(sign*1.38,0,1.49),'clavicle_'+side),
          'lowerarm_'+side:((sign*1.38,0,1.49),(sign*1.90,0,1.12),'upperarm_'+side),
          'hand_'+side:((sign*1.90,0,1.12),(sign*2.12,-.03,.88),'lowerarm_'+side),
          'thigh_'+side:((sign*.34,0,.2),(sign*.43,0,-.91),'pelvis'),
          'calf_'+side:((sign*.43,0,-.91),(sign*.46,.02,-2.05),'thigh_'+side),
          'foot_'+side:((sign*.46,.02,-2.05),(sign*.46,-.46,-2.24),'calf_'+side)})
    bpy.ops.object.armature_add();rig=bpy.context.object;rig.name='CitadelRig'
    bpy.ops.object.mode_set(mode='EDIT');rig.data.edit_bones.remove(rig.data.edit_bones[0])
    for name,(a,b,parent) in joints.items():
        bone=rig.data.edit_bones.new(name);bone.head=point(a);bone.tail=point(b)
        if parent:bone.parent=rig.data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    groups={name:obj.vertex_groups.new(name=name) for name in joints}
    def dist(p,a,b):
        d=b-a;return (p-(a+d*max(0,min(1,(p-a).dot(d)/d.length_squared)))).length
    arms=set()
    for v in obj.data.vertices:
        raw=v.co/scale-Vector((0,0,2.386));x,y,z=raw;side='r' if x<0 else 'l'
        if abs(x)>.74 and z>.63:
            names=['upperarm_'+side,'lowerarm_'+side,'hand_'+side];arms.add(v.index)
            # Shoulder armor follows the upper arm rather than the neck.
        elif z>2.36:names=['head']
        elif z>1.8:names=['spine_02','neck']
        elif z>.45:names=['spine_01','spine_02']
        elif z>-.36:names=['pelvis']
        elif z<-1.96:names=['foot_'+side]
        else:names=['thigh_'+side,'calf_'+side]
        weights=sorted((dist(v.co,point(joints[n][0]),point(joints[n][1])),n) for n in names)
        if len(weights)>1 and weights[1][0]-weights[0][0]<.035:
            w=.5+.5*(weights[1][0]-weights[0][0])/.035
            groups[weights[0][1]].add([v.index],w,'REPLACE');groups[weights[1][1]].add([v.index],1-w,'REPLACE')
        else:groups[weights[0][1]].add([v.index],1,'REPLACE')
    mod=obj.modifiers.new('Deformation','ARMATURE');mod.object=rig;obj.parent=rig
    # Blender -Y forward -> Unreal +X forward (FBX changes handedness).
    rig.rotation_euler.z=math.pi/2
    # Rebuild the source's legacy material as a clean PBR graph.
    mat=bpy.data.materials.new('KnightPBR');mat.use_nodes=True;bsdf=mat.node_tree.nodes.get('Principled BSDF')
    for suffix,pin in [('color','Base Color'),('metalness','Metallic'),('rough','Roughness')]:
        im=bpy.data.images['armor_default_'+suffix+'.png'];im.filepath_raw=str(SRC/'knight'/im.name);im.save()
        tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im
        if suffix!='color':im.colorspace_settings.name='Non-Color'
        mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs[pin])
    im=bpy.data.images['armor_default_nmap.png'];im.filepath_raw=str(SRC/'knight'/im.name);im.save()
    obj.data.materials.clear();obj.data.materials.append(mat)
    export('SK_CitadelKnight',[rig,obj])
    fp=obj.copy();fp.data=obj.data.copy();bpy.context.collection.objects.link(fp);fp.name='SK_CitadelArms'
    bm=bmesh.new();bm.from_mesh(fp.data);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in arms],context='VERTS');bm.to_mesh(fp.data);bm.free()
    export('SK_CitadelArms',[rig,fp])
    bpy.data.objects.remove(fp,do_unlink=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CitadelKnight_Rig.blend'))
    (OUT/'rig.json').write_text(json.dumps({n:{'head':list(point(a)),'tail':list(point(b)),'parent':p} for n,(a,b,p) in joints.items()},indent=2))

def sword():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(SRC/'antique_estoc/antique_estoc.gltf'))
    obj=next(o for o in bpy.data.objects if o.type=='MESH');select([obj]);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    # glTF source inspected below; source runs in Blender Y, tip at the negative end.
    coords=[v.co for v in obj.data.vertices]
    print('SWORD BOUNDS',[(min(v[i] for v in coords),max(v[i] for v in coords)) for i in range(3)])
    length=1.293061375617981-.19
    for v in obj.data.vertices:v.co=Vector((v.co.x/length,v.co.y/length,(v.co.z-.19)/length))
    export('SM_CitadelSword',[obj])

def kit():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    def mesh(name,verts,faces):
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
        obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);select([obj])
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.uv.smart_project();bpy.ops.object.mode_set(mode='OBJECT')
        if name=='SM_HeraldicCloth':
            for poly in data.polygons:
                for loop in poly.loop_indices:
                    co=data.vertices[data.loops[loop].vertex_index].co
                    data.uv_layers.active.data[loop].uv=(co.x+.5,-co.z)
        bevel=obj.modifiers.new('Dressed edges','BEVEL');bevel.width=.012;bevel.segments=3
        obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL');export(name,[obj])
    # 1 m arch, centered; upper half ring, with real intrados and depth.
    verts=[];faces=[];steps=32
    for i in range(steps+1):
        a=math.pi*i/steps
        for depth,r in [(-.5,.40),(-.5,.5),(.5,.40),(.5,.5)]:verts.append((r*math.cos(a),depth,r*math.sin(a)))
    for i in range(steps):
        a=4*i;b=a+4
        for j,k in [(0,1),(1,3),(3,2),(2,0)]:faces.append((a+j,b+j,b+k,a+k))
    faces.extend([(0,2,3,1),(steps*4,steps*4+1,steps*4+3,steps*4+2)])
    mesh('SM_ArcadeArch',verts,faces)
    mesh('SM_DressedBlock',[(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    mesh('SM_SlateRoof',[(-.5,-.5,0),(.5,-.5,0),(.5,.5,0),(-.5,.5,0),(-.5,0,.5),(.5,0,.5)],[(0,1,5,4),(3,4,5,2),(0,4,3),(1,2,5),(0,3,2,1)])
    def turned(name,profile):
        verts=[];faces=[];sides=64
        for z,r in profile:
            for i in range(sides):
                a=i*2*math.pi/sides;verts.append((r*math.cos(a),r*math.sin(a),z))
        for ring in range(len(profile)-1):
            for i in range(sides):
                a=ring*sides+i;b=ring*sides+(i+1)%sides
                faces.append((a,b,b+sides,a+sides))
        mesh(name,verts,faces)
    turned('SM_FountainBaluster',[(0,0),(0,.20),(.035,.20),(.07,.17),(.12,.14),(.17,.10),(.25,.11),(.32,.15),(.43,.17),(.52,.15),(.61,.095),(.70,.065),(.87,.065),(.91,.12),(.94,.18),(1,.18),(1,0)])
    turned('SM_FountainBowl',[(0,0),(0,.13),(.025,.17),(.06,.23),(.11,.35),(.15,.46),(.16,.50),(.19,.50),(.205,.48),(.205,.45),(.17,.43),(.13,.34),(.095,.22),(.07,0)])
    # Cloth with modeled folds and a swallowtail; no flat cube banners.
    verts=[];faces=[];nx,nz=16,24
    for z in range(nz+1):
        t=z/nz
        for x in range(nx+1):
            u=x/nx;bottom=.16*(1-abs(u*2-1))
            verts.append((u-.5,.035*math.sin(u*math.pi*6+t*3)*t+.055*t*t,-t+bottom*t**8))
    for z in range(nz):
        for x in range(nx):
            a=z*(nx+1)+x;faces.append((a,a+1,a+nx+2,a+nx+1))
    mesh('SM_HeraldicCloth',verts,faces)

if __name__=='__main__':
    knight();sword();kit()
    # Exit only after all exporters finish. Avoid embedded bpy's Windows
    # interpreter teardown, which can fail after otherwise successful exports.
    print('CITADEL DCC BUILD COMPLETE',flush=True)
    sys.stderr.flush();sys.stdout.flush()
    import os
    os._exit(0)
