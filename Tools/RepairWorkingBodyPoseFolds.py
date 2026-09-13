"""Bounded local rest-surface relaxation against diagnostic linear skin poses.

Writes an isolated trial, never a selector or runtime asset.
"""
import bpy,sys,json,math,numpy as np
from pathlib import Path
from mathutils import Quaternion,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from RepairWorkingBody import OUT,EVIDENCE,open_source,intersections,audit,select_lod,render
scene=open_source(OUT/'Male_Body_SurfaceRepair.blend');rig=bpy.data.objects['MB_AccuRig'];rig.animation_data_clear()
base={p.name:p.matrix_basis.copy() for p in rig.pose.bones}
def pose(kind):
    for p in rig.pose.bones:p.matrix_basis=base[p.name]
    for side,angle in [('l',-45),('r',45)]:
        direction=(rig.data.bones['hand_'+side].head_local-rig.data.bones['lowerarm_'+side].head_local).normalized()
        changes=[]
        if kind=='elbows':changes=[('upperarm_'+side,Vector((0,1,0)),angle),('lowerarm_'+side,direction.cross(Vector((0,-1,0))).normalized(),100)]
        if kind=='twist':changes=[('lowerarm_'+side,direction,60 if side=='l' else -60)]
        for name,axis,degrees in changes:
            p=rig.pose.bones[name];q=p.bone.matrix_local.to_quaternion()
            p.matrix_basis=base[name]@(q.inverted()@Quaternion(axis,math.radians(degrees))@q).to_matrix().to_4x4()
    bpy.context.view_layer.update()
records={}
for lod in range(4):
    pose('rest');obj=bpy.data.objects[f'MB_Rigged_LOD{lod}'];mesh=obj.data
    original=np.array([list(v.co) for v in mesh.vertices])
    keys=[(k.name,k.value,np.array([list(v.co) for v in k.data])) for k in mesh.shape_keys.key_blocks] if mesh.shape_keys else []
    obj.shape_key_clear()
    adjacency=[set() for v in mesh.vertices]
    for e in mesh.edges:
        a,b=e.vertices;adjacency[a].add(b);adjacency[b].add(a)
    transforms={}
    for kind in ['rest','elbows','twist']:
        pose(kind)
        mats={g.index:np.array(obj.matrix_world.inverted()@rig.matrix_world@rig.pose.bones[g.name].matrix@rig.data.bones[g.name].matrix_local.inverted()@rig.matrix_world.inverted()@obj.matrix_world)
              for g in obj.vertex_groups if g.name in rig.data.bones}
        blend=np.array([sum((mats[g.group]*g.weight for g in v.groups if g.group in mats),np.zeros((4,4))) for v in mesh.vertices])
        transforms[kind]=(blend,np.linalg.inv(blend[:,:3,:3]))
    coords=original.copy();history=[]
    for iteration in range(60):
        counts=[]
        for kind in ['elbows','twist','rest']:
            blend,inverse=transforms[kind]
            posed=np.einsum('nij,nj->ni',blend[:,:3,:3],coords)+blend[:,:3,3]
            mesh.vertices.foreach_set('co',posed.ravel());mesh.update()
            pairs=intersections(mesh)
            opposed={p.index for p in mesh.polygons if any(mesh.corner_normals[i].vector.dot(p.normal)<-.05 for i in p.loop_indices)}
            counts.append([len(pairs),len(opposed)])
            core={v for pair in pairs for f in pair for v in mesh.polygons[f].vertices}
            core.update(v for f in opposed for v in mesh.polygons[f].vertices)
            ring1={n for v in core for n in adjacency[v]}-core
            ring2={n for v in ring1 for n in adjacency[v]}-core-ring1
            strength={**{v:.06 for v in ring2},**{v:.15 for v in ring1},**{v:.30 for v in core}}
            for i,s in strength.items():
                delta=s*(np.mean(posed[list(adjacency[i])],axis=0)-posed[i])
                delta=inverse[i]@delta
                length=np.linalg.norm(delta)
                if length>.15:delta*=.15/length
                coords[i]+=delta
        history.append(counts)
        if iteration%10==0:print('FOLD',lod,iteration,counts,float(np.max(np.linalg.norm(coords-original,axis=1))),flush=True)
        if not any(sum(c) for c in counts):break
    pose('rest');mesh.vertices.foreach_set('co',coords.ravel());mesh.update()
    delta=coords-original
    for name,value,old in keys:
        key=obj.shape_key_add(name=name,from_mix=False);key.data.foreach_set('co',(old+delta).ravel());key.value=value
    records[lod]=dict(history=history,maximum_displacement_cm=float(np.max(np.linalg.norm(delta,axis=1))),audit=audit(obj))
pose('rest');select_lod(scene,0)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'SurfaceRepair_PoseFoldTrial.blend'))
pose('elbows')
target=rig.matrix_world@rig.pose.bones['lowerarm_l'].head
render(scene,EVIDENCE/'pose-fold-trial',('front','rear','left','right'),target,.34)
(EVIDENCE/'pose-fold-trial.json').write_text(json.dumps(records,indent=2))
