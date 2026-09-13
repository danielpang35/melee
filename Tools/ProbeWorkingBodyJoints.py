"""Focused absolute-size diagnosis of remaining deformed overlap pairs."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
from mathutils import Vector
from RepairWorkingBody import OUT,EVIDENCE,open_source,select_lod,render,intersections
scene=open_source(OUT/'MB_Diagnostic_JointSweep.blend'); obj=bpy.data.objects['MB_Rigged_LOD0'];rig=bpy.data.objects['MB_AccuRig']
select_lod(scene,0); records={}
for name,frame in [('elbows',37),('forearm_twist',61),('wrists',85)]:
    scene.frame_set(frame); ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()); mesh=ev.to_mesh()
    pairs=intersections(mesh)
    rows=[]
    for a,b in pairs:
        centers=[obj.matrix_world@mesh.polygons[f].center for f in (a,b)]
        rows.append(dict(faces=[a,b],centers_cm=[[round(100*x,4) for x in co] for co in centers]))
    edges=[]
    for e in obj.data.edges:
        a,b=e.vertices
        rest=1000*(obj.matrix_world.to_3x3()@(obj.data.vertices[a].co-obj.data.vertices[b].co)).length
        bent=1000*(obj.matrix_world.to_3x3()@(mesh.vertices[a].co-mesh.vertices[b].co)).length
        if rest>.01 and bent/rest>3:
            edges.append(dict(vertices=[a,b],rest_mm=rest,posed_mm=bent,center_cm=[round(100*x,4) for x in obj.matrix_world@((mesh.vertices[a].co+mesh.vertices[b].co)/2)]))
    records[name]=dict(pairs=rows,stretched_edges=edges)
    ev.to_mesh_clear()
    if name in ('wrists','elbows','forearm_twist'):
        for side in 'lr':
            target=rig.matrix_world@rig.pose.bones[('hand_' if name=='wrists' else 'lowerarm_')+side].head
            render(scene,EVIDENCE/'joint-probe-current'/name/side,('rear','front'),target,.34)
(EVIDENCE/'joint-probe-current.json').write_text(json.dumps(records,indent=2))
print('COUNTS',{n:dict(pairs=len(r['pairs']),edges=len(r['stretched_edges'])) for n,r in records.items()})
