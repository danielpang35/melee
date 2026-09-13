"""Diagnostic-only joint motion on repaired MB; never changes gameplay clips."""
import sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
from mathutils import Quaternion,Vector
from RepairWorkingBody import OUT,EVIDENCE,digest,open_source,select_lod,render,intersections
EVIDENCE=EVIDENCE/'joint-validation-current'
EVIDENCE.mkdir(parents=True,exist_ok=True)

source=OUT/'Male_Body_SurfaceRepair.blend'
scene=open_source(source)
rig=bpy.data.objects['MB_AccuRig']; rig.animation_data_clear()
baseline={p.name:p.matrix_basis.copy() for p in rig.pose.bones}
def arm_axis(side):
    direction=rig.data.bones['hand_'+side].head_local-rig.data.bones['lowerarm_'+side].head_local
    return direction.normalized()
def elbow_axis(side):
    return arm_axis(side).cross(Vector((0,-1,0))).normalized()
poses=[('rest',{}),
       ('shoulders',{'upperarm_l':((0,1,0),-45),'upperarm_r':((0,1,0),45)}),
       ('elbows',{'upperarm_l':((0,1,0),-45),'upperarm_r':((0,1,0),45),
                  'lowerarm_l':(elbow_axis('l'),100),'lowerarm_r':(elbow_axis('r'),100)}),
       ('forearm_twist',{'lowerarm_l':(arm_axis('l'),60),'lowerarm_r':(arm_axis('r'),-60)}),
       ('wrists',{'hand_l':(elbow_axis('l'),35),'hand_r':(elbow_axis('r'),35)}),
       ('torso',{'spine_01':((1,0,0),15),'spine_02':((1,0,0),10)}),
       ('hips_knees',{'thigh_l':((1,0,0),40),'calf_l':((1,0,0),-70),
                      'thigh_r':((1,0,0),-15),'calf_r':((1,0,0),-25)})]

def set_pose(changes):
    for p in rig.pose.bones:p.matrix_basis=baseline[p.name]
    for name,(axis,angle) in changes.items():
        p=rig.pose.bones[name]; rest=p.bone.matrix_local.to_quaternion()
        q=rest.inverted()@Quaternion(axis,math.radians(angle))@rest
        p.matrix_basis=baseline[name]@q.to_matrix().to_4x4()
    bpy.context.view_layer.update()

records=[]; captures=[]
for index,(name,changes) in enumerate(poses):
    set_pose(changes)
    for lod in range(4):
        select_lod(scene,lod)
        obj=bpy.data.objects[f'MB_Rigged_LOD{lod}']
        ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()); mesh=ev.to_mesh()
        bad=sum(not math.isfinite(x) for v in mesh.vertices for x in v.co)
        assert bad==0
        ratios=[]
        for e in obj.data.edges:
            a,b=e.vertices
            rest=(obj.data.vertices[a].co-obj.data.vertices[b].co).length
            if rest>.001:ratios.append((mesh.vertices[a].co-mesh.vertices[b].co).length/rest)
        overlaps=intersections(mesh)
        records.append(dict(pose=name,lod=lod,nonfinite_coordinates=bad,nonadjacent_intersections=len(overlaps),
            overlap_face_pairs=overlaps,
            edge_stretch_max=max(ratios),edge_stretch_above_3=sum(r>3 for r in ratios)))
        ev.to_mesh_clear()
        # All LODs are checked geometrically; complete four-angle pose images at LOD0.
        if lod==0:
            captures += [dict(pose=name,lod=lod,**c) for c in render(scene,EVIDENCE/'deformation'/name)]

select_lod(scene,0)
scene.render.fps=30; scene.render.fps_base=1
scene.frame_start=1; scene.frame_end=145
# Individual movements return to rest; no retiming or attack semantics.
sequence=[(1,{})]
for i,(name,changes) in enumerate(poses[1:]):
    sequence.extend([(13+i*24,changes),(25+i*24,{})])
for frame,changes in sequence:
    set_pose(changes)
    for p in rig.pose.bones:
        p.rotation_mode='QUATERNION'
        p.keyframe_insert('rotation_quaternion',frame=frame,group=p.name)
        p.keyframe_insert('location',frame=frame,group=p.name)
        p.keyframe_insert('scale',frame=frame,group=p.name)
rig.animation_data.action.name='MB_Diagnostic_JointSweep_NotGameplay'
scene.frame_set(1)
scene['validation_source_sha256']=digest(source)
diagnostic=OUT/'MB_Diagnostic_JointSweep.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(diagnostic))
(EVIDENCE/'deformation.json').write_text(json.dumps(dict(source_sha256=digest(source),
    diagnostic_sha256=digest(diagnostic),poses=[n for n,_ in poses],checks=records,captures=captures,
    limitation='Diagnostic source joint movements, not retargeted combat or human playable acceptance',visual_review='pending'),indent=2))
print('DEFORMATION',json.dumps([{k:v for k,v in r.items() if k!='overlap_face_pairs'} for r in records]))
