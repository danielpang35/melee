"""Projected source normal ranges for the single scoped response diagnostic."""
from pathlib import Path
import sys,json,math
root=Path(__file__).resolve().parents[1];sys.path[:0]=[str(root/'Saved/ArtRuntime'),str(root/'Saved/VideoRuntime')]
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from PIL import Image
revision='USP_v011';packet=root/'ArtSource/StyleReference/MEL17/UnrealProof'/revision
bpy.ops.wm.open_mainfile(filepath=str(packet/('Helmet_'+revision+'.blend')))
mesh=next(o.data for o in bpy.data.objects if o.type=='MESH');mesh.calc_tangents();uv=mesh.uv_layers.active.data
bvh=BVHTree.FromPolygons([v.co for v in mesh.vertices],[p.vertices[:] for p in mesh.polygons],all_triangles=True)
normal=np.asarray(Image.open(packet/'T_Helmet_NormalDX.png').convert('RGB'),dtype=float)[::-1]/127.5-1
mask=np.asarray(Image.open(packet/'T_Helmet_Masks.png').convert('RGB'),dtype=float)[::-1]/255
camera=np.array([-50.14,-154.32,29.]);pitch,yaw=map(math.radians,[-40,-45])
key=-np.array([math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch)])
samples=[]
for poly in mesh.polygons:
 if poly.material_index!=0:continue
 ids=list(poly.loop_indices);pos=np.mean([mesh.vertices[mesh.loops[k].vertex_index].co[:] for k in ids],axis=0)
 ns=np.mean([mesh.loops[k].normal[:] for k in ids],axis=0);ns/=np.linalg.norm(ns)
 view=camera-pos;distance2=np.dot(view,view);view/=np.linalg.norm(view);facing=np.dot(ns,view)
 if facing<=0:continue
 hit=bvh.ray_cast(Vector(camera),Vector(-view),math.sqrt(distance2)+.01)
 if hit[0] is None or hit[3]<math.sqrt(distance2)-.005:continue
 tex=np.mean([uv[k].uv[:] for k in ids],axis=0);tx,ty=np.clip((tex*2048).astype(int),0,2047)
 tangent=np.mean([mesh.loops[k].tangent[:] for k in ids],axis=0);tangent-=ns*np.dot(tangent,ns);tangent/=np.linalg.norm(tangent)
 bitangent=np.cross(ns,tangent)*np.mean([mesh.loops[k].bitangent_sign for k in ids]);tn=normal[ty,tx];tn/=np.linalg.norm(tn)
 authored=tangent*tn[0]-bitangent*tn[1]+ns*tn[2];authored/=np.linalg.norm(authored)
 ns[1]*=-1;authored[1]*=-1
 group='cheek' if 5<pos[2]<20 else 'roof' if pos[2]>25 else 'brow'
 samples.append({'group':group,'position':pos.tolist(),'weight':float(poly.area*facing/distance2),'control_ndotl':float(ns@key),'authored_ndotl':float(authored@key),'influence':float(mask[ty,tx,2])})
def stats(rows):
 values=np.array([s['control_ndotl'] for s in rows]);weights=np.array([s['weight'] for s in rows]);order=np.argsort(values);values=values[order];weights=weights[order]
 quantiles=np.interp([.05,.25,.5,.75,.95],np.cumsum(weights)/weights.sum(),values)
 return {'samples':len(rows),'control_min_max':[float(values.min()),float(values.max())],'weighted_control_p05_p25_p50_p75_p95':quantiles.tolist(),'weighted_mean_abs_authored_delta':float(np.average([abs(s['authored_ndotl']-s['control_ndotl']) for s in rows],weights=[s['weight'] for s in rows]))}
result={'revision':revision,'key_direction_surface_to_light_world':key.tolist(),'key_actor_pitch_yaw_deg':[-40,-45],'method':'Perspective triangle-centroid projected-area approximation, front-facing steel with actual source BVH visibility rays; source loop normals/tangents and decoded DX map. No texture filtering. UE normals=(Bx,-By,Bz).','groups':{name:stats([s for s in samples if s['group']==name]) for name in ['cheek','brow','roof']},'active_cheek':stats([s for s in samples if s['group']=='cheek' and s['influence']>.8]),'samples':samples}
out=root/'Saved/ArtReview/UnrealStyle'/revision/'response_normal_ranges.json';out.write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='samples'},indent=2))
