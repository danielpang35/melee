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
    # Explicit deformation skeleton; closed gloves are authored below.
    joints={
      'root':((0,0,-2.386),(0,0,-2.1),None),
      'pelvis':((0,0,.1),(0,0,.65),'root'),
      'spine_01':((0,0,.65),(0,0,1.25),'pelvis'),
      'spine_02':((0,0,1.25),(0,0,2.15),'spine_01'),
      'neck':((0,0,2.15),(0,0,2.5),'spine_02'),
      'head':((0,0,2.5),(0,0,3.18),'neck')}
    # Place glenohumeral pivots beneath the pauldrons, independently of the
    # armor's outer breadth. Explicit metric deltas keep body proportions and
    # the generated rigid sleeves on the same reference skeleton.
    shoulder_x=.22/scale
    elbow_x=shoulder_x+.21/scale;elbow_z=2.05-.22/scale
    wrist_x=elbow_x+.215/scale;wrist_z=elbow_z-.135/scale
    for side,sign in [('r',-1),('l',1)]:
        joints.update({
          'clavicle_'+side:((sign*.15,0,2.05),(sign*shoulder_x,0,2.05),'spine_02'),
          'upperarm_'+side:((sign*shoulder_x,0,2.05),(sign*elbow_x,0,elbow_z),'clavicle_'+side),
          'lowerarm_'+side:((sign*elbow_x,0,elbow_z),(sign*wrist_x,0,wrist_z),'upperarm_'+side),
          # Translate the existing hand; retain its finger direction, handed
          # frame, palm offset and the continuous finger/thumb construction.
          'hand_'+side:((sign*wrist_x,0,wrist_z),(sign*(wrist_x+.22),-.03,wrist_z-.24),'lowerarm_'+side),
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
    def smooth01(v):
        v=max(0.,min(1.,v));return v*v*(3.-2.*v)
    arms=set()
    for v in obj.data.vertices:
        x,y,z=v.co;side='r' if x<0 else 'l';sign=-1 if x<0 else 1
        shoulder=point(joints['upperarm_'+side][0]);elbow=point(joints['lowerarm_'+side][0]);wrist=point(joints['hand_'+side][0])
        along=((elbow-shoulder).normalized()+(wrist-elbow).normalized()).normalized()
        arm_boundary=.20+max(0.,1.44-z)*.65
        arm_mask=smooth01((abs(x)-arm_boundary)/.09) if z>.85 else 0.
        if arm_mask>0:
            # Continuous joint bands replace nearest-bone Voronoi regions.
            # Most plate vertices remain rigid; only the joint collar blends.
            e=(v.co-elbow).dot(along);w=(v.co-wrist).dot((wrist-elbow).normalized())
            lower=smooth01((e+.018)/.036);hand=smooth01((w+.008)/.016)
            pauldron=smooth01((z-1.43)/.07)
            weights={'clavicle_'+side:(1.-lower)*pauldron,'upperarm_'+side:(1.-lower)*(1.-pauldron),'lowerarm_'+side:lower*(1.-hand),'hand_'+side:lower*hand}
            for name,weight in weights.items():
                if weight*arm_mask>0:groups[name].add([v.index],weight*arm_mask,'REPLACE')
            if arm_mask<1:groups['spine_02'].add([v.index],1.-arm_mask,'REPLACE')
            if arm_mask>.98:arms.add(v.index)
        else:
            if z>1.578:names=['head']
            elif z>1.39:names=['spine_02','neck']
            elif z>.94:names=['spine_01','spine_02']
            elif z>.674:names=['pelvis']
            elif z<.143:names=['foot_'+side]
            else:names=['thigh_'+side,'calf_'+side]
            weights=sorted((dist(v.co,point(joints[n][0]),point(joints[n][1])),n) for n in names)
            if len(weights)>1 and weights[1][0]-weights[0][0]<.035:
                w=.5+.5*(weights[1][0]-weights[0][0])/.035
                groups[weights[0][1]].add([v.index],w,'REPLACE');groups[weights[1][1]].add([v.index],1-w,'REPLACE')
            else:groups[weights[0][1]].add([v.index],1,'REPLACE')
    # The coarse source arm has no usable joint loops. Assigning its faces to
    # separate bones leaves open, jagged cuffs which separate by ~25 cm in play.
    # Keep the body/pauldrons and replace the articulated arm surfaces below them.
    remove_hand=set()
    for v in obj.data.vertices:
        if any(obj.vertex_groups[g.group].name.startswith(('upperarm_','lowerarm_','hand_')) and g.weight>.35 for g in v.groups):remove_hand.add(v.index)
    bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index in remove_hand],context='VERTS');bm.to_mesh(obj.data);bm.free()
    glove=bpy.data.materials.new('GripLeather');glove.diffuse_color=(.065,.075,.085,1)
    steel=bpy.data.materials.new('ArmSteel');steel.diffuse_color=(.18,.22,.26,1)
    pieces=[]
    def sleeve(a,b,profile,bone,material):
        axis=(b-a).normalized();radial=Vector((0,1,0));radial=(radial-axis*radial.dot(axis)).normalized()
        across=axis.cross(radial).normalized();verts=[];faces=[];sides=20
        for along,radius,flatten in profile:
            center=a+axis*along
            for j in range(sides):
                angle=2*math.pi*j/sides
                verts.append(center+radial*(radius*math.cos(angle))+across*(radius*flatten*math.sin(angle)))
        for k in range(len(profile)-1):
            for j in range(sides):
                i=k*sides+j;n=k*sides+(j+1)%sides;faces.append((i,n,n+sides,i+sides))
        faces.extend([tuple(reversed(range(sides))),tuple((len(profile)-1)*sides+j for j in range(sides))])
        data=bpy.data.meshes.new(bone+'_closed_shell');data.from_pydata(verts,[],faces);data.update()
        part=bpy.data.objects.new(bone+'_closed_shell',data);bpy.context.collection.objects.link(part)
        for f in data.polygons:f.use_smooth=True
        part.data.materials.append(material);part.vertex_groups.new(name=bone).add(list(range(len(verts))),1.,'REPLACE');pieces.append(part)
    # The original armor is an outer shell. Keep an opaque gambeson beneath
    # its open armholes when the shoulder plates and arms move independently.
    chest=point(joints['spine_02'][0])
    sleeve(chest,chest+Vector((0,0,1)),[(-.14,.055,3.2),(-.08,.0625,3.3),
        (.08,.075,3.5),(.23,.075,3.6),(.29,.065,3.7),(.35,.0325,2.6)],'spine_02',glove)
    # Hip bending exposes the open waist of the original armor. A rounded
    # gambeson insert overlaps the grounded thigh roots and moving abdomen.
    pelvis=point(joints['pelvis'][0])
    sleeve(pelvis,pelvis+Vector((0,0,1)),[(-.12,.012,1.6),(-.09,.070,1.7),
        (-.03,.105,1.75),(.04,.112,1.8),(.14,.105,1.8),(.26,.085,2.0),(.29,.04,2.)],'pelvis',glove)
    for side in ['r','l']:
        shoulder=point(joints['upperarm_'+side][0]);elbow=point(joints['lowerarm_'+side][0]);wrist=point(joints['hand_'+side][0])
        upper=(elbow-shoulder).length;lower=(wrist-elbow).length
        # Removing the old arm triangles also opens the torso under the
        # pauldron. A closed shoulder socket hides that cut during protraction.
        # It belongs to the clavicle and is omitted from the first-person mesh.
        sleeve(shoulder,elbow,[(-.08,.008,.9),(-.07,.035,.9),(-.04,.068,.9),
            (0,.078,.9),(.04,.068,.9),(.07,.035,.9),(.08,.008,.9)],'clavicle_'+side,glove)
        sleeve(shoulder,elbow,[(-.018,.024,.9),(0,.052,.9),(.03,.061,.9),
            (upper-.055,.052,.9),(upper-.025,.043,.9),(upper-.012,.018,.9)],'upperarm_'+side,steel)
        # The spherical elbow cup overlaps both closed sleeves throughout bending.
        sleeve(elbow,wrist,[(-.052,.008,1),(-.045,.028,1),(-.025,.047,1),(0,.054,1),
            (.025,.047,1),(.045,.028,1),(.052,.008,1)],'lowerarm_'+side,glove)
        sleeve(elbow,wrist,[(.012,.03,.85),(.027,.047,.85),(.047,.049,.85),
            (lower-.04,.034,.8),(lower-.015,.035,.8),(lower,.03,.8)],'lowerarm_'+side,steel)
        # A closed leather wrist joint accommodates palm rotation without a torn cuff.
        sleeve(wrist,wrist+(wrist-elbow),[(-.03,.012,.85),(-.02,.026,.85),(0,.03,.85),
            (.018,.024,.85),(.027,.01,.85)],'hand_'+side,glove)
    def tube(points,radii,axis,bone):
        # Continuous ring topology, including the knuckles: no phalanx cubes.
        verts=[];faces=[];sides=12
        for k,center in enumerate(points):
            tangent=(points[min(k+1,len(points)-1)]-points[max(0,k-1)]).normalized()
            normal=(axis-tangent*axis.dot(tangent)).normalized()
            cross=tangent.cross(normal).normalized()
            for j in range(sides):
                angle=j*2*math.pi/sides
                verts.append(center+radii[k]*(normal*math.cos(angle)+cross*math.sin(angle)))
        for k in range(len(points)-1):
            for j in range(sides):
                i=k*sides+j;n=k*sides+(j+1)%sides
                faces.append((i,n,n+sides,i+sides))
        faces.extend([tuple(reversed(range(sides))),tuple((len(points)-1)*sides+j for j in range(sides))])
        mesh=bpy.data.meshes.new(bone+'_continuous');mesh.from_pydata(verts,[],faces);mesh.update()
        part=bpy.data.objects.new(bone+'_continuous',mesh);bpy.context.collection.objects.link(part)
        part.data.materials.append(glove)
        part.vertex_groups.new(name=bone).add(list(range(len(verts))),1.,'REPLACE');pieces.append(part)
    for side in ['r','l']:
        bone='hand_'+side;wrist=point(joints[bone][0]);finger=(point(joints[bone][1])-wrist).normalized()
        palm=Vector((0,1,0));palm=(palm-finger*palm.dot(finger)).normalized()
        across=finger.cross(palm).normalized();sign=1 if side=='r' else -1
        # Same orthonormal frame and contact centre as the runtime calibration.
        # FBX's Blender -> Unreal handedness conversion negates cross products.
        # Exported grip is -UE Cross(RestFinger,RestPalm)*sign + finger*.8.
        # This chirality puts the knuckles away from the player, with the
        # right thumb facing the player. The old minus sign mirrored hands.
        grip=(across*sign+finger*.8).normalized()
        distal=(finger-grip*finger.dot(grip)).normalized()
        center=wrist+finger*.045+palm*.02
        def local(g,d,p):return center+grip*g+distal*d+palm*p
        # The metacarpals form one broad back of the hand behind the shaft.
        # Loft wrist -> palm -> MCP knuckles, instead of burying finger rings
        # in a round pad. +grip is the radial/index side on BOTH hands.
        profile=[(-.049,-.028,-.021,.019,.016),
                 (-.036,-.024,-.025,.026,.018),
                 (-.021,-.014,-.032,.034,.015),
                 (-.004,-.002,-.034,.040,.013),
                 (.012,0.,-.030,.039,.012),
                 (.022,0.,-.026,.035,.008),
                 (.026,0.,-.024,.028,.003),
                 (.027,0.,-.023,.020,.001)]
        verts=[];faces=[];sides=24
        for d,g,p,width,depth in profile:
            for j in range(sides):
                angle=2*math.pi*j/sides
                verts.append(local(g+width*math.cos(angle),d,p+depth*math.sin(angle)))
        for k in range(len(profile)-1):
            for j in range(sides):
                i=k*sides+j;n=k*sides+(j+1)%sides
                faces.append((i,n,n+sides,i+sides))
        faces.extend([tuple(reversed(range(sides))),tuple((len(profile)-1)*sides+j for j in range(sides))])
        mesh=bpy.data.meshes.new(bone+'_metacarpals');mesh.from_pydata(verts,[],faces);mesh.update()
        part=bpy.data.objects.new(bone+'_metacarpals',mesh);bpy.context.collection.objects.link(part)
        part.data.materials.append(glove);part.vertex_groups.new(name=bone).add(list(range(len(verts))),1.,'REPLACE');pieces.append(part)
        # Index, middle, ring, little: different lengths and knuckle sizes.
        # About half a turn encloses the handle; the old 260-degree loops
        # gave every finger an impossible ~14 cm centreline.
        for along,radius,thickness,end in [(.029,.033,.0095,173),(.0095,.034,.010,184),
                                           (-.010,.033,.0092,177),(-.028,.031,.0078,157)]:
            points=[];radii=[]
            for k in range(29):
                q=k/28;angle=math.radians(24+(end-24)*q)
                # Broad proximal phalanx, PIP/DIP fullness, rounded fingertip.
                taper=1-.27*q
                joint=1+.08*math.exp(-((q-.43)/.09)**2)+.045*math.exp(-((q-.76)/.07)**2)
                tip=math.sqrt(max(.04,1-max(0.,(q-.90)/.105)**2))
                points.append(local(along-.002*q,radius*math.sin(angle),-radius*math.cos(angle)))
                radii.append(thickness*taper*joint*tip)
            tube(points,radii,grip,bone)
        # Thenar root and web are on the INDEX side, toward the guard.
        # The previous across*sign root was on the little-finger side.
        # Reference: Mordhau Montage VI, 164.30 s (opposed thumb over index).
        # The fleshy thenar eminence joins the thumb's basal segment to the
        # palm; exposing that entire segment made the thumb read as a hook.
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=1.)
        thenar=bpy.context.object;thenar.name=bone+'_thenar'
        for v in thenar.data.vertices:
            x,y,z=v.co
            v.co=local(.018+x*.025,-.032+y*.021,-.020+z*.018)
        thenar.data.materials.append(glove)
        thenar.vertex_groups.new(name=bone).add(list(range(len(thenar.data.vertices))),1.,'REPLACE');pieces.append(thenar)
        # Follow the OUTSIDE of the shaft on the proximal side. A Bezier
        # chord through the handle was cut into two stumps by the cavity.
        points=[];radii=[]
        for k in range(25):
            q=k/24;angle=math.radians(-45-120*q);radius=.039+.002*math.sin(math.pi*q)
            points.append(local(.018+.022*math.sin(math.pi*q)+.004*q,
                                radius*math.sin(angle),-radius*math.cos(angle)))
            radii.append((.013-q*.004)*math.sqrt(max(.08,1-max(0.,(q-.88)/.125)**2)))
        tube(points,radii,grip,bone)
        # Union the wrist, palm, fingers and thumb into one closed glove surface.
        hand_parts=[part for part in pieces if part.vertex_groups[0].name==bone]
        select(hand_parts);bpy.ops.object.join();hand=bpy.context.object
        pieces=[part for part in pieces if part not in hand_parts]+[hand]
        remesh=hand.modifiers.new('Continuous glove union','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.0018;remesh.use_smooth_shade=True
        bpy.ops.object.modifier_apply(modifier=remesh.name)
        smooth=hand.modifiers.new('Glove surface relaxation','SMOOTH');smooth.factor=.5;smooth.iterations=3
        bpy.ops.object.modifier_apply(modifier=smooth.name)
        # Measured source leather is approximately 42-46 mm across at the two
        # contact centres. A 48 mm cavity prevents palm/thumb penetration.
        bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.024,depth=.12,location=center)
        cutter=bpy.context.object;cutter.rotation_euler=grip.to_track_quat('Z','Y').to_euler()
        select([hand]);boolean=hand.modifiers.new('Fitted handle cavity','BOOLEAN');boolean.operation='DIFFERENCE';boolean.object=cutter
        bpy.ops.object.modifier_apply(modifier=boolean.name);bpy.data.objects.remove(cutter,do_unlink=True)
        hand.vertex_groups.clear();hand.vertex_groups.new(name=bone).add(list(range(len(hand.data.vertices))),1.,'REPLACE')
        for f in hand.data.polygons:f.use_smooth=True
        bm=bmesh.new();bm.from_mesh(hand.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        assert not any(e.is_boundary or not e.is_manifold for e in bm.edges), 'Glove must be closed after fitting'
        remaining=set(bm.verts);islands=[]
        while remaining:
            todo=[remaining.pop()];island=[]
            while todo:
                vertex=todo.pop();island.append(vertex)
                for edge in vertex.link_edges:
                    other=edge.other_vert(vertex)
                    if other in remaining:remaining.remove(other);todo.append(other)
            islands.append(island)
        islands.sort(key=len,reverse=True)
        for island in islands[1:]:
            # Exact booleans can leave sub-0.5 mm closed numerical slivers
            # (well below the 1.8 mm voxel); never discard a finger/hand part.
            assert len(island)<=16 and max((v.co-island[0].co).length for v in island)<.0005, 'Disconnected glove anatomy'
            bmesh.ops.delete(bm,geom=island,context='VERTS')
        bm.to_mesh(hand.data);bm.free()
        print('CONTINUOUS GLOVE',side,len(hand.data.vertices),'vertices; cavity radius 24 mm')
    select([obj]+pieces);bpy.context.view_layer.objects.active=obj;bpy.ops.object.join()
    # Plate triangles must not bridge independently rotated joints. Duplicate
    # boundary vertices per rigid section, preserving the source UVs. Blending
    # this coarse topology across the elbow/wrist created >8x edge elongation.
    source_mesh=obj.data;group_names=[g.name for g in obj.vertex_groups]
    weights=[{g.group:g.weight for g in v.groups} for v in source_mesh.vertices]
    vertices=[];faces=[];new_weights=[];remap={}
    for face in source_mesh.polygons:
        totals={}
        for index in face.vertices:
            for group,weight in weights[index].items():totals[group]=totals.get(group,0.)+weight
        arm_weight=sum(w for g,w in totals.items() if group_names[g].startswith(('clavicle_','upperarm_','lowerarm_','hand_')))
        shoulder_plate=any(abs(source_mesh.vertices[i].co.x)>.24 and source_mesh.vertices[i].co.z>.84 for i in face.vertices)
        owner=max(totals,key=totals.get) if arm_weight>.05 or shoulder_plate else None
        indices=[]
        for index in face.vertices:
            key=(index,owner)
            if key not in remap:
                remap[key]=len(vertices);vertices.append(tuple(source_mesh.vertices[index].co))
                new_weights.append({owner:1.} if owner is not None else weights[index])
            indices.append(remap[key])
        faces.append(indices)
    rigid_mesh=bpy.data.meshes.new('CitadelRigidPlates');rigid_mesh.from_pydata(vertices,[],faces)
    for material in source_mesh.materials:rigid_mesh.materials.append(material)
    for source_face,target_face in zip(source_mesh.polygons,rigid_mesh.polygons):
        target_face.material_index=source_face.material_index;target_face.use_smooth=source_face.use_smooth
    for layer in source_mesh.uv_layers:
        new_layer=rigid_mesh.uv_layers.new(name=layer.name)
        for i,uv in enumerate(layer.data):new_layer.data[i].uv=uv.uv
    obj.data=rigid_mesh;obj.vertex_groups.clear()
    for name in group_names:obj.vertex_groups.new(name=name)
    for i,ws in enumerate(new_weights):
        for g,w in ws.items():obj.vertex_groups[g].add([i],w,'REPLACE')
    # Joining changes vertex indices: recompute the view-model arm mask from weights.
    arms={v.index for v in obj.data.vertices if sum(g.weight for g in v.groups if any(obj.vertex_groups[g.group].name.startswith(n) for n in ('clavicle_','upperarm_','lowerarm_','hand_')))>.98}
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
    # Keep a stable armor / glove-and-joints / arm-steel material contract.
    old_materials=list(obj.data.materials)
    face_slots=[1 if old_materials[f.material_index]==glove else 2 if old_materials[f.material_index]==steel else 0 for f in obj.data.polygons]
    obj.data.materials.clear()
    for material in [mat,glove,steel]:obj.data.materials.append(material)
    for f,slot in zip(obj.data.polygons,face_slots):f.material_index=slot
    export('SK_CombatKnight',[rig,obj])
    fp=obj.copy();fp.data=obj.data.copy();bpy.context.collection.objects.link(fp);fp.name='SK_CitadelArms'
    bm=bmesh.new();bm.from_mesh(fp.data);bm.verts.ensure_lookup_table()
    # A view model starts below the pauldrons. Full-body shoulder plates enter
    # the near plane and obscure the hands when the grip is raised into view.
    fp_arms={v.index for v in fp.data.vertices if sum(g.weight for g in v.groups if fp.vertex_groups[g.group].name.startswith(('upperarm_','lowerarm_','hand_')))>.98}
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z>.85 and v.index not in fp_arms],context='VERTS');bm.to_mesh(fp.data);bm.free()
    export('SK_CombatArms',[rig,fp])
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
