"""Immutable helmet-only Unreal proof source export. Run with Python 3.11.
Next source edit: --revision USP_v002 --source-blend path/to/revised.blend
Wait for engine critique before generating the next revision; existing manifests lock outputs."""
from pathlib import Path
import sys,json,hashlib,math,argparse,re,os
ROOT=Path(__file__).resolve().parents[1]
if '--prepare' in sys.argv or '--bake' in sys.argv:
 sys.path.insert(0,str(ROOT/'Tools'))
 from BuildUnrealStyleTransfer import main
 main()
 raise SystemExit(0)
sys.path[:0]=[str(ROOT/'Saved/ArtRuntime'),str(ROOT/'Saved/VideoRuntime')]
import bpy
import numpy as np
from PIL import Image
from mathutils import Vector,Matrix
p=argparse.ArgumentParser();p.add_argument('--revision',default='USP_v001');p.add_argument('--roughness-regions',type=Path,help='Legacy region recipe for roughness on changed UVs');p.add_argument('--preserve-roughness',type=Path,help='Prior masks PNG: preserve its R channel on identical UVs');p.add_argument('--regions',type=Path,help='Editable JSON list of form-aware region fields');p.add_argument('--source-blend',type=Path,default=ROOT/'ArtSource/StyleReference/MEL17/Helmet_v009/Helmet_v009.blend');args=p.parse_args()
if not re.fullmatch(r'USP_v[0-9]{3}',args.revision):p.error('--revision must match USP_vNNN')
OUT=ROOT/'ArtSource/StyleReference/MEL17/UnrealProof'/args.revision
if (OUT/'manifest.json').exists():raise SystemExit('Immutable revision already exists; choose a new revision')
SOURCE=args.source_blend.expanduser()
if not SOURCE.is_absolute():SOURCE=ROOT/SOURCE
SOURCE=SOURCE.resolve()
if not SOURCE.is_file() or SOURCE.suffix.lower()!='.blend':p.error('--source-blend must name an existing .blend file')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
baseline={}
for material in bpy.data.materials:
 if material.use_nodes:
  node=next((n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if node:baseline[material.name]={'base_color_linear':list(node.inputs['Base Color'].default_value)[:3],'metallic':node.inputs['Metallic'].default_value,'roughness':node.inputs['Roughness'].default_value}
assembly=bpy.data.objects['Helmet proof assembly'];parts=list(assembly.children_recursive)
deps=bpy.context.evaluated_depsgraph_get();copies=[];slit_z_samples=[]
for obj in parts:
 if obj.type not in {'MESH','CURVE'}:continue
 data=bpy.data.meshes.new_from_object(obj.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
 data.transform(obj.matrix_world)
 if obj.name.startswith('Eye slit lower lip'):slit_z_samples.extend(v.co.z for v in data.vertices)
 ob=bpy.data.objects.new(obj.name+'_Final',data);copies.append(ob)
for ob in list(bpy.data.objects):
 if ob not in copies:bpy.data.objects.remove(ob,do_unlink=True)
for ob in copies:bpy.context.collection.objects.link(ob)
coords=np.array([v.co[:] for ob in copies for v in ob.data.vertices]);lo=coords.min(0);hi=coords.max(0);origin=np.array([(lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]]);scale=35/(hi[2]-lo[2])
if not slit_z_samples:raise RuntimeError('Cannot derive slit guard: evaluated Eye slit lower lip missing')
slit_guard_center=(float(np.mean(slit_z_samples))-origin[2])*scale;slit_guard_width=1.1
for ob in copies:
 for v in ob.data.vertices:v.co=Vector((np.array(v.co)-origin)*scale)
 ob.select_set(True)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();obj=bpy.context.object;obj.name=f'SM_Helmet_StyleProof{args.revision[-3:]}';obj.data.name=obj.name
# Collapse material slots to the explicit import contract.
old=list(obj.data.materials);classes=[]
for m in old:classes.append(3 if 'interior' in m.name.lower() else 2 if 'dark' in m.name.lower() else 1 if ('edge' in m.name.lower()) else 0)
slot_sources=[next(m.name for m,k in zip(old,classes) if k==i) for i in range(4)]
slot_values=[baseline[name] for name in slot_sources]
indices=[classes[q.material_index] for q in obj.data.polygons]
obj.data.materials.clear()
for i,name in enumerate(['Steel','Edge','Dark','Interior']):
 v=slot_values[i];color=(*v['base_color_linear'],1);metal=v['metallic'];rough=v['roughness'];m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=color;n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough;obj.data.materials.append(m)
for poly,index in zip(obj.data.polygons,indices):poly.material_index=index
# Angle-defined construction seams; smart projection packs the final helmet islands with padding.
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(55),island_margin=.012,area_weight=.3);bpy.ops.object.mode_set(mode='OBJECT')
tri=obj.modifiers.new('Frozen final triangulation','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=tri.name)
mesh=obj.data;mesh.calc_tangents();uv=mesh.uv_layers.active.data
# Mark actual UV discontinuities as explicit editable seams.
edge_uv={}
for poly in mesh.polygons:
 loops=list(poly.loop_indices)
 for a,b in zip(loops,loops[1:]+loops[:1]):
  va,vb=mesh.loops[a].vertex_index,mesh.loops[b].vertex_index
  edge_uv.setdefault(tuple(sorted((va,vb))),[]).append({va:tuple(uv[a].uv),vb:tuple(uv[b].uv)})
for edge in mesh.edges:
 uses=edge_uv.get(tuple(sorted(edge.vertices)),[]);edge.use_seam=len(uses)!=2 or any(uses[0][v]!=uses[1][v] for v in edge.vertices)
OUT.mkdir(parents=True,exist_ok=True);N=2048
normal=np.zeros((N,N,3),np.float32);normal[:,:,2]=1
packed=np.zeros((N,N,3),np.float32);occupied=np.zeros((N,N),bool);field=np.zeros((N,N,3),np.float32)
# Sparse hand-placed elliptical regions in final Blender cm coordinates, on the actual front/crown.
regions=[{'center':[-5,-9,24],'radius':[3.8,5,4.6],'delta':[.085,0,.04]}, {'center':[5.5,-9,15],'radius':[3.7,4,5],'delta':[-.07,0,.035]}, {'center':[4,-1,31],'radius':[4.5,6,2.8],'delta':[.065,-.045,0]}]
if args.regions:
 recipe=args.regions if args.regions.is_absolute() else ROOT/args.regions
 regions=json.loads(recipe.read_text())
 if not isinstance(regions,list) or not regions:raise ValueError('regions must be a nonempty JSON list')
 for r in regions:
  if any(len(r[k])!=3 for k in ['center','radius','delta']) or min(r['radius'])<=0:raise ValueError('Each region needs 3D center/radius/delta and positive radii')
for r in regions:
 feather=r.get('feather',.32)
 if not isinstance(feather,(int,float)) or not math.isfinite(feather) or not 0<feather<=1:raise ValueError('Region feather must be finite and in (0,1]')
roughness_regions=None
if args.roughness_regions:
 roughness_path=args.roughness_regions if args.roughness_regions.is_absolute() else ROOT/args.roughness_regions
 roughness_regions=json.loads(roughness_path.read_text())
def polygon_field(pos,r):
 polygon=np.asarray(r['polygon_xz'],float);points=pos[:,[0,2]]
 if polygon.ndim!=2 or polygon.shape[1]!=2 or not 3<=len(polygon)<=5:raise ValueError('polygon_xz requires 3 to 5 points')
 inside=np.zeros(len(pos),bool);distance=np.full(len(pos),np.inf)
 for a,b in zip(polygon,np.roll(polygon,-1,axis=0)):
  edge=b-a;t=np.clip(((points-a)@edge)/np.dot(edge,edge),0,1);distance=np.minimum(distance,np.linalg.norm(points-(a+t[:,None]*edge),axis=1))
  inside^=((a[1]>points[:,1])!=(b[1]>points[:,1]))&(points[:,0]<(b[0]-a[0])*(points[:,1]-a[1])/(b[1]-a[1]+1e-12)+a[0])
 width=r.get('contour_width_cm',5);f=np.clip(distance/(r.get('feather',.32)*width),0,1)*inside
 return f*(pos[:,1]<=-origin[1]*scale+.05)
for poly in mesh.polygons:
 ids=list(poly.loop_indices);verts=np.array([mesh.vertices[mesh.loops[k].vertex_index].co[:] for k in ids]);tex=np.array([uv[k].uv[:] for k in ids])*N
 x0,y0=np.maximum(np.floor(tex.min(0)).astype(int),0);x1,y1=np.minimum(np.ceil(tex.max(0)).astype(int),N-1)
 if x1<x0 or y1<y0:continue
 xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5);a,b,c=tex
 den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
 if abs(den)<1e-9:continue
 w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w2=1-w0-w1
 valid=(w0>=-1e-5)&(w1>=-1e-5)&(w2>=-1e-5)
 if not valid.any():continue
 rows,cols=np.nonzero(valid);weights=np.stack([w0[valid],w1[valid],w2[valid]],1);pos=weights@verts;delta=np.zeros_like(pos);inf=np.zeros(len(pos))
 if poly.material_index==0:
  protect=np.clip((abs(pos[:,0])-1.0)/1.6,0,1)*np.clip(abs(pos[:,2]-slit_guard_center)/slit_guard_width,0,1)
  for r in regions:
   q=(pos-r['center'])/r['radius'];distance=np.maximum.reduce([abs(q[:,0]+.22*q[:,2]),abs(q[:,2]-.13*q[:,0]),abs(q[:,1]),abs(.65*q[:,0]+.62*q[:,2])]);f=polygon_field(pos,r)*(float(poly.normal.y)<0) if 'polygon_xz' in r else np.clip((1-distance)/r.get('feather',.32),0,1);f=f*f*(3-2*f)*protect;delta+=f[:,None]*r['delta'];inf=np.maximum(inf,f)
 ns=weights@np.array([mesh.loops[k].normal[:] for k in ids]);ns/=np.linalg.norm(ns,axis=1)[:,None]
 ts=weights@np.array([mesh.loops[k].tangent[:] for k in ids]);ts-=ns*np.sum(ts*ns,axis=1)[:,None];ts/=np.maximum(np.linalg.norm(ts,axis=1)[:,None],1e-8)
 signs=np.array([mesh.loops[k].bitangent_sign for k in ids]);bs=np.cross(ns,ts)*(weights@signs)[:,None]
 desired=ns+delta;desired/=np.linalg.norm(desired,axis=1)[:,None]
 tan=np.stack([np.sum(desired*ts,1),-np.sum(desired*bs,1),np.sum(desired*ns,1)],1);tan/=np.linalg.norm(tan,axis=1)[:,None]
 rr,cc=y0+rows,x0+cols;normal[rr,cc]=tan;field[rr,cc]=delta;occupied[rr,cc]=True
 roughness_inf=inf
 if roughness_regions is not None:
  roughness_inf=np.zeros(len(pos))
  if poly.material_index==0:
   for r in roughness_regions:
    q=(pos-r['center'])/r['radius'];distance=np.maximum.reduce([abs(q[:,0]+.22*q[:,2]),abs(q[:,2]-.13*q[:,0]),abs(q[:,1]),abs(.65*q[:,0]+.62*q[:,2])]);f=np.clip((1-distance)/r.get('feather',.32),0,1);f=f*f*(3-2*f)*protect;roughness_inf=np.maximum(roughness_inf,f)
 rough=slot_values[poly.material_index]['roughness']+.025*roughness_inf
 packed[rr,cc]=np.stack([rough,np.full(len(pos),float(poly.material_index==1)),inf],1)
# Eight texel edge dilation keeps mips off black atlas backgrounds.
mask=occupied.copy()
for iteration in range(8):
 expanded=mask.copy()
 for dy,dx in [(1,0),(-1,0),(0,1),(0,-1)]:
  near=np.roll(mask,(dy,dx),(0,1));take=near&~expanded
  normal[take]=np.roll(normal,(dy,dx),(0,1))[take];packed[take]=np.roll(packed,(dy,dx),(0,1))[take];expanded|=take
 mask=expanded
Image.fromarray(np.rint(np.clip(normal[::-1]*.5+.5,0,1)*255).astype('uint8'),'RGB').save(OUT/'T_Helmet_NormalDX.png')
if args.preserve_roughness:
 prior=args.preserve_roughness if args.preserve_roughness.is_absolute() else ROOT/args.preserve_roughness
 old_masks=np.asarray(Image.open(prior))
 if old_masks.shape!=(N,N,3):raise ValueError('Prior masks must be identical-size RGB')
 packed[:,:,0]=old_masks[::-1,:,0]/255.
Image.fromarray(np.rint(np.clip(packed[::-1],0,1)*255).astype('uint8'),'RGB').save(OUT/'T_Helmet_Masks.png')
np.savez_compressed(OUT/'EditableFields.npz',deviation_blender_cm_axes=field,influence=packed[:,:,2],occupied=occupied)
(OUT/'regions.json').write_text(json.dumps(regions,indent=2))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'Helmet_{args.revision}.blend'))
bpy.ops.export_scene.fbx(filepath=str(OUT/f'SM_Helmet_{args.revision}.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_mesh_modifiers=False,mesh_smooth_type='OFF',use_tspace=True,add_leaf_bones=False,bake_anim=False)
coords=np.array([v.co[:] for v in mesh.vertices]);bounds=[coords.min(0).tolist(),coords.max(0).tolist()]
manifest={'revision':args.revision,'source':str(SOURCE),'fbx':str(OUT/f'SM_Helmet_{args.revision}.fbx'),'normal_texture':str(OUT/'T_Helmet_NormalDX.png'),'masks_texture':str(OUT/'T_Helmet_Masks.png'),'material_slots':['Steel','Edge','Dark','Interior'],'bounds_blender_cm':bounds,'height_cm':35,'origin':'combined bottom center','origin_blender':origin.tolist(),'cm_per_blender_unit':float(scale),'blender_front':'-Y','expected_unreal_mapping':'(BlenderX, -BlenderY, BlenderZ); VERIFY imported landmarks','normal_convention':'DirectX tangent space; green already inverted, Unreal flip_green_channel false','normal_import':{'srgb':False,'compression':'TC_NORMALMAP','flip_green_channel':False},'masks_import':{'srgb':False,'compression':'TC_MASKS','channels':{'R':'roughness','G':'construction edge','B':'authored influence'}},'mesh_import':'Import normals and tangents, do not recompute; final triangulation frozen','zero_strength':'normalize(lerp(float3(0,0,1),decoded_normal,strength)); strength0 exactly mesh normals','uv':{'method':'55 degree construction islands, explicit discontinuity seams','island_margin':.012,'dilation_pixels':8},'triangles':len(mesh.polygons),'vertices':len(mesh.vertices),'regions':regions,'region_count':len(regions),'roughness_region_recipe':str(args.roughness_regions) if args.roughness_regions else None,'roughness_preserved_from':str(args.preserve_roughness) if args.preserve_roughness else None,'slit_guard':{'center_cm':float(slit_guard_center),'width_cm':slit_guard_width,'derivation':'Mean Z of evaluated Eye slit lower lip mesh vertices transformed to normalized cm'},'landmarks_blender_cm':{},'validation':{'unit_normal_max_error':float(np.max(abs(np.linalg.norm(normal[occupied],axis=1)-1))),'uv_coverage':float(occupied.mean()),'influence_coverage_on_mesh':float((packed[:,:,2][occupied]>.01).mean()),'triangle_only':all(len(q.vertices)==3 for q in mesh.polygons)},'limitations':['Source shape preserved; landmarks record exact selected exported vertices','Runtime tangent handedness and UV seam appearance require Unreal lighting validation','Smart-project atlas is editable and seam-marked, not a hand-cut production atlas']}
manifest['source_sha256']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
manifest['source']=Path(os.path.relpath(SOURCE,ROOT)).as_posix()
for key in ['fbx','normal_texture','masks_texture']:manifest[key]=Path(manifest[key]).name
manifest['landmarks_blender_cm']={}
for name,index in [('top_ridge',int(np.argmax(coords[:,2]))),('front_brow',int(np.argmin(coords[:,1]))),('rightmost',int(np.argmax(coords[:,0])))]:manifest['landmarks_blender_cm'][name]={'vertex_index':index,'position':coords[index].tolist()}
manifest['textures']={'normal':{'path':manifest['normal_texture']},'masks':{'path':manifest['masks_texture']}}
manifest['material_slots']=[dict(index=i,name=n,source_material=slot_sources[i],**slot_values[i]) for i,n in enumerate(['Steel','Edge','Dark','Interior'])]
(OUT/'generator.py').write_text(Path(__file__).read_text())
manifest['sha256']={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in OUT.iterdir() if q.is_file()}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));(OUT/'generator.py').write_text(Path(__file__).read_text())
print(json.dumps(manifest['validation']));print('SOURCE_COMPLETE',OUT)



