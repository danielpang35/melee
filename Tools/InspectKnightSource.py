import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'Saved/ArtRuntime'))
import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(root/'ArtSource/Citadel/knight/armor.blend'))
for obj in bpy.data.objects:
    if obj.type=='MESH':
        coords=[obj.matrix_world@Vector(v) for v in obj.bound_box]
        print(obj.name,len(obj.data.vertices), 'min',tuple(round(min(v[i] for v in coords),3) for i in range(3)), 'max',tuple(round(max(v[i] for v in coords),3) for i in range(3)), 'materials',[m.name for m in obj.data.materials])
print('IMAGES',[(i.name,i.size[:],bool(i.packed_file)) for i in bpy.data.images])
print('ARMATURES',[(o.name,len(o.data.bones)) for o in bpy.data.objects if o.type=='ARMATURE'])
for image in bpy.data.images:
    if image.name.startswith('armor_'):
        image.filepath_raw=str(root/'ArtSource/Citadel/knight'/image.name)
        image.save()
mat=bpy.data.materials.new('Inspection');mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF')
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images['armor_default_color.png']
mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value=.45
for obj in list(bpy.data.objects):
    if obj.type=='MESH': obj.data.materials.clear();obj.data.materials.append(mat)
    else: bpy.data.objects.remove(obj,do_unlink=True)
bpy.ops.object.camera_add(location=(.2,-11,1.0));cam=bpy.context.object
cam.rotation_euler=(Vector((.2,0,.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=6.4
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=16
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1)
for pos,power,size in [((1,-6,7),1200,6),((-5,-3,2),800,5)]:
    bpy.ops.object.light_add(type='AREA',location=pos);light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size
    light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.filepath=str(root/'Saved/knight-source.png');bpy.ops.render.render(write_still=True)
