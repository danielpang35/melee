"""Preview only the new independent knight rig in its rest pose."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'ArtSource/UserKnight/KN_v001/Knight_Rig.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12
scene.world=bpy.data.worlds.new('KnightReview');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.3,.3,1)
bpy.ops.object.camera_add(location=(2.5,-5,2.0));cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=2.45;scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(1,-3,5));light=bpy.context.object
light.data.energy=800;light.data.shape='DISK';light.data.size=4
light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.frame_set(1)
scene.render.filepath=str(ROOT/'Saved/UserKnight/knight-rest.png')
bpy.ops.render.render(write_still=True)
