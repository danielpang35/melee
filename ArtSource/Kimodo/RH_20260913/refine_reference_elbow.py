"""Native B refinement: open the winding elbow, preserve actual saved grasp.

Uses saved native wrist/grasp transforms as edit authority, not old recipes.
"""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools'))
from FinishKimodoGrip import finish
from RetargetKimodo import sha,write
folder=ROOT/'ArtSource/Kimodo/RH_20260913/B_reference_extended_v003'
source=folder/'ReferencePullback.blend'
output='B_ArmLoad_v004.blend'
guide=folder/'native-elbow-guide.json'
assert not guide.exists() and not (folder/output).exists()
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
primary=bpy.data.objects['Kimodo_Grasp_r']
weapon=bpy.data.objects['Kimodo_Weapon_PrimaryOwned']
samples=[];before=[];elbows=[]
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
for f in range(scene.frame_start,scene.frame_end+1):
    scene.frame_set(f);bpy.context.view_layer.update()
    u=smooth((f-7)/17)*(1-smooth((f-40)/15))
    samples.append(dict(frame=f,primary_grasp_position_m=list(primary.matrix_world.translation),
        grasp_rotation_wxyz=list(primary.matrix_world.to_quaternion()),
        elbow_poles_local={'r':[-1,.35,-.55+.70*u],'l':[1,.35,-.55+.10*u]}))
    matrix=weapon.matrix_world.copy()
    before.append([list(matrix.translation),list(matrix@Vector((0,0,1.035)))])
    rig=bpy.data.objects['MB_AccuRig']
    elbows.append(list(rig.matrix_world@rig.pose.bones['lowerarm_r'].head))
write(guide,dict(coordinate_system='blender-z-up',samples=samples,
    input_native_sha256=sha(source),support_offset_m=[0,0,-.125],
    native_adjustment='Raise/open right elbow during winding via pole hint; preserve saved primary grasp, blade route, source clock, generated body and recovery. No regeneration.'))
finish(folder,guide,output,'ReferencePullback.blend')
scene=bpy.context.scene;weapon=bpy.data.objects['Kimodo_Weapon_PrimaryOwned'];rig=bpy.data.objects['MB_AccuRig']
errors=[];elbow_changes=[]
for f in range(1,93):
    scene.frame_set(f);bpy.context.view_layer.update()
    matrix=weapon.matrix_world
    errors.extend([(matrix.translation-Vector(before[f-1][0])).length,
                  (matrix@Vector((0,0,1.035))-Vector(before[f-1][1])).length])
    elbow_changes.append((rig.matrix_world@rig.pose.bones['lowerarm_r'].head-Vector(elbows[f-1])).length)
assert max(errors)<.00002,max(errors)
write(folder/'elbow-change.json',dict(source=str((folder/output).relative_to(ROOT)),source_sha256=sha(folder/output),
    parent_sha256=sha(source),max_hilt_tip_change_m=max(errors),
    max_right_elbow_change_m=max(elbow_changes),loaded_right_elbow_change_m=elbow_changes[29],
    scope='All92 source samples; preserves parent draft blade path, not proof of gameplay contact compatibility',
    human_acceptance=False))
print('ELBOW_REFINEMENT',max(errors),elbow_changes[29],flush=True)
