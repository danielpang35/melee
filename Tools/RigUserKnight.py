"""Build an independent rest-pose knight rig, ready for new animation.

Reuse the CF bone layout as a starting point, fit its rest pose to the sculpt,
and retain editable initial weights. Never adapt the sculpt to existing clips.
"""
import sys,json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy,bmesh
from mathutils import Vector,Matrix,kdtree
OUT=ROOT/'ArtSource/UserKnight/KN_v001'
# The supplied component breakdown distinguishes adjacent gloves and skirt.
# Use its actual surfaces rather than an ambiguous spatial cutoff.
with bpy.data.libraries.load(str(OUT/'Knight_Components.blend'),link=False) as (src,dst):
    dst.objects=[name for name in src.objects if name.startswith('part_')]
parts=[]
for obj in dst.objects:
    for v in obj.data.vertices:
        p=obj.matrix_world@v.co
        if p.x<0:parts.append((p.copy(),obj.name.split('.')[0]))
cx=(min(p.x for p,_ in parts)+max(p.x for p,_ in parts))*.5
scale=1.8/(max(p.z for p,_ in parts)-min(p.z for p,_ in parts))
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'ArtSource/CharacterReset/CF_v001/CF_v001_Character.blend'))
rig=bpy.data.objects['CF01_CharacterRig'];body=bpy.data.objects['CF01_Body']
rig.animation_data_clear()
for pb in rig.pose.bones:
    for constraint in list(pb.constraints):pb.constraints.remove(constraint)
    pb.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
def aim(name,endpoint,target):
    pb=rig.pose.bones[name]
    pivot=pb.matrix.translation.copy()
    delta=(rig.pose.bones[endpoint].matrix.translation-pivot).rotation_difference(Vector(target)-pivot)
    pb.matrix=Matrix.Translation(pivot)@delta.to_matrix().to_4x4()@Matrix.Translation(-pivot)@pb.matrix
    bpy.context.view_layer.update()
for side,sign in [('L',1),('R',-1)]:
    aim('upperarm01.'+side,'lowerarm01.'+side,(sign*.29,-.015,1.15))
    aim('lowerarm01.'+side,'wrist.'+side,(sign*.35,-.015,.93))
    aim('wrist.'+side,'finger3-1.'+side,(sign*.355,-.015,.86)) if 'finger3-1.'+side in rig.pose.bones else None
deps=bpy.context.evaluated_depsgraph_get()
evaluated=body.evaluated_get(deps);surface=evaluated.to_mesh()
tree=kdtree.KDTree(len(surface.vertices))
for v in surface.vertices:tree.insert(body.matrix_world@v.co,v.index)
tree.balance()
weights={v.index:{body.vertex_groups[g.group].name:g.weight for g in v.groups if g.weight>.001} for v in surface.vertices}
bpy.ops.object.select_all(action='DESELECT')
with bpy.data.libraries.load(str(OUT/'Knight_Components.blend'),link=False) as (src,dst):
    dst.objects=[name for name in src.objects if name.startswith('part_')]
assembly=[]
for obj in dst.objects:
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.x>=0],context='VERTS')
    bm.to_mesh(obj.data);bm.free()
    if not obj.data.vertices:
        bpy.data.objects.remove(obj,do_unlink=True);continue
    for v in obj.data.vertices:v.co=Vector(((v.co.x-cx)*scale,v.co.y*scale,v.co.z*scale))
    mod=obj.modifiers.new('Runtime reduction','DECIMATE');mod.ratio=.08
    bpy.ops.object.modifier_apply(modifier=mod.name)
    attr=obj.data.attributes.new('source_part','INT','POINT')
    part_number=int(obj.name.split('_')[1].split('.')[0])
    for datum in attr.data:datum.value=part_number
    assembly.append(obj);obj.select_set(False)
for obj in assembly:obj.select_set(True)
bpy.context.view_layer.objects.active=assembly[0]
bpy.ops.object.join();knight=bpy.context.object
rotation=Matrix.Rotation(math.radians(-37),4,'Z')
part_ids={v.index:'part_'+str(knight.data.attributes['source_part'].data[v.index].value) for v in knight.data.vertices}
for v in knight.data.vertices:v.co=rotation@(v.co-Vector((.015,-.037,0)))
knight.name='SK_UserKnight'
mat=bpy.data.materials.new('M_UserKnightClay');mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value=(.28,.31,.35,1)
bsdf.inputs['Metallic'].default_value=.65;bsdf.inputs['Roughness'].default_value=.48
knight.data.materials.clear();knight.data.materials.append(mat)
for p in knight.data.polygons:p.material_index=0
for name in rest:knight.vertex_groups.new(name=name)
for v in knight.data.vertices:
    point=v.co.copy();blend={}
    for _,index,distance in tree.find_n(point,4):
        proximity=1/max(distance,.005)**2
        for name,weight in weights[index].items():blend[name]=blend.get(name,0)+weight*proximity
    # Keep helmet shell rigid and gauntlets coherent, instead of transferring
    # tiny facial/finger influences through thick armor surfaces.
    if point.z>1.52:blend={'head':1}
    part=part_ids[v.index]
    if part in ('part_13','part_15') or (part=='part_14' and abs(point.x)>.235 and .74<point.z<1.47):
        side='R' if point.x<0 else 'L'
        allowed={n:w for n,w in blend.items() if n.endswith('.'+side) and any(prefix in n for prefix in ['arm','wrist','finger','metacarpal','shoulder'])}
        blend=allowed or {'lowerarm01.'+side:1}
        if point.z<1.01:blend={'wrist.'+side:1}
    elif point.z<1.13 and point.z>.60:
        blend={'root':1}
    elif point.z<.60:
        blend={n:w for n,w in blend.items() if any(prefix in n for prefix in ['leg','foot','toe'])} or {'root':1}
    chosen=sorted(blend.items(),key=lambda item:item[1],reverse=True)[:4]
    total=sum(w for _,w in chosen)
    assert total>0
    chosen=[(n,w/total) for n,w in chosen]
    for name,weight in chosen:
        knight.vertex_groups[name].add([v.index],weight,'REPLACE')
evaluated.to_mesh_clear()
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='POSE');bpy.ops.pose.armature_apply(selected=False);bpy.ops.object.mode_set(mode='OBJECT')
rig.name='KN01_Rig';rig.data.name='KN01_RestSkeleton'
bpy.context.view_layer.update()
knight.parent=rig
modifier=knight.modifiers.new('Knight skin','ARMATURE');modifier.object=rig
for o in list(bpy.data.objects):
    if o not in (knight,rig):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Knight_Rig.blend'))
bpy.ops.object.select_all(action='DESELECT');knight.select_set(True);rig.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(OUT/'SK_UserKnight.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},
    add_leaf_bones=False,use_armature_deform_only=False,bake_anim=False,axis_forward='-Y',axis_up='Z',
    global_scale=1.,apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',path_mode='STRIP')
(OUT/'rig-receipt.json').write_text(json.dumps(dict(bones=len(rest),vertices=len(knight.data.vertices),
    triangles=len(knight.data.polygons),animation=None,rest_pose='fitted to supplied sculpt; independent of CF animation',
    foundation_sha256=hashlib.sha256((ROOT/'ArtSource/CharacterReset/CF_v001/CF_v001_Character.blend').read_bytes()).hexdigest(),
    limitations='Initial editable skin weights; new animation and deformation refinement are future work. No supplied textures.'),indent=2))
print('KNIGHT_REST_RIG_COMPLETE')
