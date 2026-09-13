"""One rest fitting comparison. Armor overlay exposes body breakthrough."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'ArtSource/UserKnight/KN_v002/Knight_Animation.blend'))
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=12
scene.world.color=(.25,.25,.25)
bpy.ops.object.camera_add(location=(2.5,-5,2.0));cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=2.35;scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(1,-3,5));light=bpy.context.object
light.data.energy=800;light.data.shape='DISK';light.data.size=4
light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
out=ROOT/'Saved/UserKnight/body-fit';out.mkdir(exist_ok=True)
for mode in ['body','armor-fit']:
    bpy.data.collections['Knight Armor (Deferred)'].hide_render=mode=='body'
    scene.render.filepath=str(out/(mode+'.png'));bpy.ops.render.render(write_still=True)
