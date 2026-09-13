"""Preserve supplied knight and prepare a scaled static Unreal asset and preview."""
import sys, json, hashlib, shutil, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy, bmesh
from mathutils import Vector
OUT=ROOT/'ArtSource/UserKnight/KN_v001'
OUT.mkdir(parents=True,exist_ok=True)
sources=['D:/fHHDATOQt9zB6wsFpnZJw.fbx','D:/20260909174448_72c77e03.fbx']
records=[]
for src in sources:
    target=OUT/'Originals'/Path(src).name
    target.parent.mkdir(exist_ok=True)
    if not target.exists():shutil.copy2(src,target)
    records.append(dict(file=target.name,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(OUT/'Originals/20260909174448_72c77e03.fbx'))
obj=next(o for o in bpy.data.objects if o.type=='MESH')
bpy.context.view_layer.objects.active=obj
obj.select_set(True)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
# The supplied combined file contains two separate reconstructed figures.
# Select the front-facing figure on negative X; originals retain both.
bm=bmesh.new();bm.from_mesh(obj.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.x>=0],context='VERTS')
bm.to_mesh(obj.data);bm.free()
center_x=(min(v.co.x for v in obj.data.vertices)+max(v.co.x for v in obj.data.vertices))*.5
minimum=min(v.co.z for v in obj.data.vertices)
height=max(v.co.z for v in obj.data.vertices)-minimum
scale=1.8/height
for v in obj.data.vertices:v.co=Vector(((v.co.x-center_x)*scale,v.co.y*scale,(v.co.z-minimum)*scale))
obj.name='SM_UserKnight'
mat=bpy.data.materials.new('M_UserKnightClay');mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value=(.28,.31,.35,1)
bsdf.inputs['Roughness'].default_value=.48
bsdf.inputs['Metallic'].default_value=.65
obj.data.materials.clear();obj.data.materials.append(mat)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Knight_Source.blend'))
# Preserve full-resolution source; reduce only the engine presentation copy.
mod=obj.modifiers.new('Runtime reduction','DECIMATE');mod.ratio=.08
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.export_scene.fbx(filepath=str(OUT/'SM_UserKnight.fbx'),use_selection=True,object_types={'MESH'},
    axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False)
(OUT/'manifest.json').write_text(json.dumps(dict(originals=records,source_height_m=height,
    selection='negative-X front-facing figure',scale_to_180cm=scale,engine_triangles=len(obj.data.polygons),rigged=False,textures_supplied=False),indent=2))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.25,.25,1)
bpy.ops.object.camera_add(location=(2.5,-5,2.2));cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,.95))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=2.6;scene.camera=cam
for pos,power,size in [((1,-4,5),700,4),((-3,-1,3),500,3)]:
    bpy.ops.object.light_add(type='AREA',location=pos);light=bpy.context.object
    light.data.energy=power;light.data.shape='DISK';light.data.size=size
    light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.filepath=str(ROOT/'Saved/UserKnight/source-preview.png')
bpy.ops.render.render(write_still=True)
