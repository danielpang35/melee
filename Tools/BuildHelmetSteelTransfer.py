"""Immutable Clay_v005 to Steel_v025 source transfer and accepted-rig still proof."""
from pathlib import Path
import sys,json,hashlib,argparse,heapq,math
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'Saved/ArtRuntime'),str(ROOT/'Saved/VideoRuntime')]
import bpy
import numpy as np
from mathutils import Vector,Matrix,kdtree
from PIL import Image,ImageDraw
P=argparse.ArgumentParser();P.add_argument('--revision',default='ST_v001');P.add_argument('--samples',type=int,default=32);P.add_argument('--finalize',action='store_true');a=P.parse_args()
OUT=ROOT/'ArtSource/StyleReference/MEL17/SteelTransfer'/a.revision
REVIEW=ROOT/'Saved/ArtReview/UnrealStyle'/a.revision/'Review'
if a.finalize:
    import numpy as np
    finalpath=REVIEW/'finalization.json'
    if finalpath.exists():raise RuntimeError('Already finalized; choose a new revision')
    if not (REVIEW/'index.html').exists():raise RuntimeError('Stills are not complete')
    blend=OUT/f'Helmet_Steel_{a.revision}.blend'
    bpy.ops.wm.open_mainfile(filepath=str(blend));scene=bpy.context.scene
    camera=bpy.data.objects['ST matched helmet camera'];scene.camera=camera
    camera.location=(0,-4,.98);camera.rotation_euler=(Vector((0,-.01,.75))-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.resolution_x=900;scene.render.resolution_y=1100
    links=[]
    for mat in bpy.data.materials:
        if not mat.use_nodes or not mat.node_tree.nodes.get('ST Influence'):continue
        t=mat.node_tree;p=t.nodes.get('Principled BSDF');link=p.inputs['Normal'].links[0];links.append((t,link.from_socket,p.inputs['Normal']));t.links.remove(link)
    scene.render.filepath=str(REVIEW/'front_construction_baseline.png');bpy.ops.render.render(write_still=True)
    baseline=np.asarray(Image.open(scene.render.filepath).convert('RGB'),dtype=float)
    zero=np.asarray(Image.open(REVIEW/'front_smooth.png').convert('RGB'),dtype=float)
    error=np.abs(baseline-zero)
    receipt={'zero_control_pixel_check':{'compared':'front_smooth (influence zero) versus front_construction_baseline (normal socket disconnected)','mean_abs_8bit':float(error.mean()),'max_abs_8bit':float(error.max()),'pixels_over_2_levels':int(np.sum(np.max(error,axis=2)>2))}}
    assert error.mean()<.1 and np.mean(np.max(error,axis=2)>2)<.001
    for t,source,dest in links:t.links.new(source,dest)
    # Exact comparator control excludes the transfer helmet from all ray types.
    parts=list(bpy.data.objects['Helmet clay assembly'].children)
    for o in parts:o.hide_render=True
    for o in scene.objects:
        if o.type in ['MESH','CURVE'] and o not in parts:o.visible_camera=True
    scene.camera=bpy.data.objects['StudyCamera'];scene.render.resolution_x=1440;scene.render.resolution_y=1000
    receipt['comparator']='accepted_armor_comparator.png excludes helmet from all rays; original comparator datablocks, transforms and rig unchanged'
    accepted_image=ROOT/'ArtSource/StyleReference/MEL17/Steel_v025/steel-study.png'
    if accepted_image.exists():
        aa=np.asarray(Image.open(accepted_image).convert('RGB'),dtype=float);bb=np.asarray(Image.open(REVIEW/'accepted_armor_comparator.png').convert('RGB'),dtype=float)
        if aa.shape==bb.shape:receipt['accepted_comparator_pixel_difference']={'mean_abs_8bit':float(np.abs(aa-bb).mean()),'max_abs_8bit':float(np.abs(aa-bb).max()),'note':'Thread count may differ; geometry/material/light/world/camera sources unchanged'}
    for o in parts:o.hide_render=o.name=='Neutral recessed neck support'
    for o in scene.objects:
        if o.type in ['MESH','CURVE'] and o not in parts and o.name!='Plane':o.visible_camera=False
    scene.camera=camera;camera.location=(-1.45,-4,1.22);camera.rotation_euler=(Vector((0,-.01,.75))-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.resolution_x=900;scene.render.resolution_y=1100
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    receipt['source_sha256']=hashlib.sha256(blend.read_bytes()).hexdigest()
    receipt['generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    receipt['artistic_status']='Pending independent critique; continuous chart region correction'
    recipe=json.loads((OUT/'regions.json').read_text())
    for r in recipe['regions']:
        r['graph_seed_faces_diagnostic_only']=r.pop('faces',r.get('graph_seed_faces_diagnostic_only',[]))
        obj=bpy.data.objects[r['part']];uv=obj.data.uv_layers['ST_SurfaceChart'];poly=r['boundary_chart_polygon']
        def inside(point):
            signs=[]
            for aa,bb in zip(poly,poly[1:]+poly[:1]):signs.append((bb[0]-aa[0])*(point[1]-aa[1])-(bb[1]-aa[1])*(point[0]-aa[0]))
            return all(x>=-1e-7 for x in signs) or all(x<=1e-7 for x in signs)
        r['face_centroid_membership']=[f.index for f in obj.data.polygons if inside(sum((uv.data[i].uv for i in f.loop_indices),Vector((0,0)))/len(f.loop_indices))]
        r['membership_authority']='Continuous chart polygon clipped to this plate; face centroid membership is diagnostic, texture sampling drives shader'
    (OUT/'regions.json').write_text(json.dumps(recipe,indent=2))
    reference=ROOT/'ArtSource/StyleReference/MEL17/06-riot-inspired.png'
    Image.open(reference).crop((420,175,565,370)).save(REVIEW/'reference_helmet_native.png')
    native=Image.new('RGB',(720,250),(28,28,28));draw=ImageDraw.Draw(native)
    native.paste(Image.open(REVIEW/'reference_helmet_native.png'),(12,40));draw.text((12,12),'Original ~184px helmet',fill='white')
    for x,label in [(225,'smooth'),(460,'authored')]:
        im=Image.open(REVIEW/('front_'+label+'.png')).crop((205,172,685,903));im=im.resize((121,184),Image.Resampling.LANCZOS)
        native.paste(im,(x,40));draw.text((x,12),'Transfer '+label+' ~184px',fill='white')
    native.save(REVIEW/'reference_native_comparison.png')
    receipt['regions_sha256']=hashlib.sha256((OUT/'regions.json').read_bytes()).hexdigest()
    receipt['texture_hashes']={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in OUT.glob('*_Target.png')}
    receipt['native_comparison']={'original_reference_crop':[420,175,565,370],'original_helmet_crown_chin_y':[179,363],'render_front_crop':[205,172,685,903],'render_crop_resized':[121,184],'note':'Original reference is unscaled; rendered helmet downsampled to approximate reference height, not gameplay distance'}
    finalpath.write_text(json.dumps(receipt,indent=2))
    index=REVIEW/'index.html';index.write_text(index.read_text().replace('</body>', '<h2>Original portrait and reference-scale comparison</h2><img src="reference_helmet_native.png"><br><img src="reference_native_comparison.png"><p>Reference remains at native pixels; render downsampled to approximate 184px helmet height.</p></body>'))
    (OUT/'generator.py').write_text(Path(__file__).read_text())
    print('ST_FINALIZED',receipt,flush=True)
    sys.exit(0)
if OUT.exists() or REVIEW.exists():raise RuntimeError('Immutable revision already exists')
OUT.mkdir(parents=True);REVIEW.mkdir(parents=True)
CLAY=ROOT/'ArtSource/StyleReference/MEL17/GeometryReview/Clay_v005/Helmet_Clay_v005.blend'
STEEL=ROOT/'ArtSource/StyleReference/MEL17/Steel_v025/Steel_v025.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
identities={str(p.relative_to(ROOT)):sha(p) for p in [CLAY,STEEL]}
assert sha(CLAY)=='a9937b6b9cb04973a4a3b4b383f4a635c55e63c2241f737e9f573489a631c263'
bpy.ops.wm.open_mainfile(filepath=str(CLAY));scene=bpy.context.scene
assembly=bpy.data.objects['Helmet clay assembly'];parts=list(assembly.children)
metal=[o for o in parts if o.type=='MESH' and o.data.materials[0].name.startswith('Uniform neutral clay')]
assert len(metal)==15

def fingerprint(o):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
    data={'vertices':[list(v.co) for v in m.vertices],'triangles':[list(t.vertices) for t in m.loop_triangles],'normals':[list(n.vector) for n in m.corner_normals]}
    h=hashlib.sha256(json.dumps(data).encode()).hexdigest();n=len(m.loop_triangles);ev.to_mesh_clear();return {'sha256':h,'triangles':n}
before={o.name:fingerprint(o) for o in metal};regions=[];mapping=[];controls=[];checks=[]
for o in metal:
    m=o.data;active=any(s in o.name for s in ['convex peaked crown','wrapping brow','compound cheek and chin','Continuous inferred'])
    # Evaluate construction first. Target sampling comes from evaluated split normals.
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());em=ev.to_mesh();kd=kdtree.KDTree(len(em.vertices))
    for v in em.vertices:kd.insert(v.co,v.index)
    kd.balance();evaluated_normals=[v.normal.copy() for v in em.vertices]
    adjacency=[set() for p in m.polygons];edgefaces={}
    for p in m.polygons:
        for key in p.edge_keys:edgefaces.setdefault(tuple(sorted(key)),[]).append(p.index)
    protected=set()
    for edge,fs in edgefaces.items():
        if len(fs)==2:
            adjacency[fs[0]].add(fs[1]);adjacency[fs[1]].add(fs[0])
        else:protected.update(edge)
    # Three vertex rings protect actual open construction borders and returns.
    va=[set() for v in m.vertices]
    for e in m.edges:
        x,y=e.vertices;va[x].add(y);va[y].add(x)
    distance={v:0 for v in protected};front=set(protected)
    for ring in range(1,4):
        front={j for i in front for j in va[i] if j not in distance}
        distance.update({v:ring for v in front})
    group=o.vertex_groups.new(name='ST Construction protection');group.add(sorted(protected) if protected else list(range(len(m.vertices))),1,'REPLACE')
    at=m.attributes.new('ST_Target','FLOAT_VECTOR','FACE');al=m.attributes.new('ST_Alpha','FLOAT','POINT')
    for v in m.vertices:al.data[v.index].value=(min(distance.get(v.index,4)/3,1)*(.10 if 'crown' in o.name else .24)) if active else 0
    # Multi-source graph Voronoi has connected cells by construction; each part is independent.
    count=max(1,round(len(m.polygons)/100)) if active else 1
    seeds=[len(m.polygons)//2];labels=[]
    def flood(seeds):
        dist=[float('inf')]*len(m.polygons);lab=[-1]*len(m.polygons);q=[]
        for r,s in enumerate(seeds):dist[s]=0;heapq.heappush(q,(0,r,s))
        while q:
            d,r,i=heapq.heappop(q)
            if d>dist[i]:continue
            lab[i]=r
            for j in adjacency[i]:
                nd=d+(m.polygons[i].center-m.polygons[j].center).length
                if nd<dist[j]:dist[j]=nd;heapq.heappush(q,(nd,r,j))
        return dist,lab
    for _ in range(count-1):
        ds,labels=flood(seeds);seeds.append(max(range(len(ds)),key=lambda i:ds[i]))
    ds,labels=flood(seeds)
    assert -1 not in labels
    normalmat=o.matrix_world.to_3x3().inverted().transposed()
    # A continuous per-plate chart removes base-grid stair steps without altering geometry.
    def chart(co):
        if 'crown' in o.name:return (co.x,co.y)
        if 'Continuous inferred' in o.name:return (math.atan2(co.x,-co.y) % (2*math.pi),co.z)
        return (co.x,co.z)
    raw=np.array([chart(v.co) for v in m.vertices]);low=raw.min(axis=0);extent=np.maximum(raw.max(axis=0)-low,1e-6)
    uv=m.uv_layers.new(name='ST_SurfaceChart')
    for loop in m.loops:uv.data[loop.index].uv=(raw[loop.vertex_index]-low)/extent
    sites=np.array([(np.array(chart(m.polygons[i].center))-low)/extent for i in seeds])
    weights=extent**2
    if 'Continuous inferred' in o.name:weights[0]*=.27**2
    target_image=Image.new('RGB',(1024,1024),(128,128,255));painter=ImageDraw.Draw(target_image)
    for r,s in enumerate(seeds):
        member=[i for i,x in enumerate(labels) if x==r];seen={member[0]};todo=[member[0]]
        while todo:
            for j in adjacency[todo.pop()]:
                if labels[j]==r and j not in seen:seen.add(j);todo.append(j)
        assert len(seen)==len(member)
        center=m.polygons[s].center;_,vi,_=kd.find(center);nt=evaluated_normals[vi].normalized()
        for i in member:at.data[i].vector=nt
        site=sites[r];polygon=[np.array(q,float) for q in [(0,0),(1,0),(1,1),(0,1)]]
        for other_index,other in enumerate(sites):
            if other_index==r:continue
            axis=(other-site)*weights;limit=((other**2-site**2)*weights).sum()*.5;cut=[]
            for aa,bb in zip(polygon,polygon[1:]+polygon[:1]):
                da=aa@axis-limit;db=bb@axis-limit
                if da<=1e-10:cut.append(aa)
                if (da<0)!=(db<0):cut.append(aa+(bb-aa)*da/(da-db))
            polygon=cut
            if not polygon:break
        if len(polygon)>=3:painter.polygon([(float(u)*1023,(1-float(v))*1023) for u,v in polygon],fill=tuple(round((x*.5+.5)*255) for x in nt))
        boundary=[list(e) for e,fs in edgefaces.items() if any(i in member for i in fs) and (len(fs)<2 or any(labels[i]!=r for i in fs))]
        regions.append({'name':o.name+' region '+str(r),'part':o.name,'graph_seed_faces_diagnostic_only':member,'boundary_edges_diagnostic_base_faces':boundary,'boundary_chart_polygon':[list(q) for q in polygon],'chart':'per-plate projection, crown XY; face XZ; rear azimuth Z','chart_low':list(low),'chart_extent':list(extent),'target_object':list(nt),'target_world':list((normalmat@nt).normalized()),'alpha_floor':.10 if 'crown' in o.name else .24,'influence':'0.4 * alpha * ST Influence','transition_width':'3 base-mesh edge rings at construction boundary; continuous chart polygon boundary, one texture pixel filtering','protected_vertices':sorted(protected),'connected':True,'active':active})
    target_path=OUT/(o.name.replace(' ','_')+'_Target.png');target_image.save(target_path)
    ev.to_mesh_clear()
    mat=bpy.data.materials.new(o.name+' ST steel');mat.use_nodes=True;t=mat.node_tree;n=t.nodes;l=t.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(.29,.285,.275,1);p.inputs['Metallic'].default_value=1;p.inputs['Roughness'].default_value=.30
    g=n.new('ShaderNodeNewGeometry');target=n.new('ShaderNodeTexImage');target.image=bpy.data.images.load(str(target_path));target.image.colorspace_settings.name='Non-Color';target.interpolation='Linear';target.extension='EXTEND';uvnode=n.new('ShaderNodeUVMap');uvnode.uv_map='ST_SurfaceChart';l.new(uvnode.outputs[0],target.inputs[0]);decode=n.new('ShaderNodeVectorMath');decode.operation='MULTIPLY_ADD';decode.inputs[1].default_value=(2,2,2);decode.inputs[2].default_value=(-1,-1,-1);l.new(target.outputs['Color'],decode.inputs[0]);alpha=n.new('ShaderNodeAttribute');alpha.attribute_name='ST_Alpha'
    tr=n.new('ShaderNodeVectorTransform');tr.vector_type='NORMAL';tr.convert_from='OBJECT';tr.convert_to='WORLD';l.new(decode.outputs[0],tr.inputs[0])
    norm=n.new('ShaderNodeVectorMath');norm.operation='NORMALIZE';l.new(tr.outputs[0],norm.inputs[0])
    influence=n.new('ShaderNodeValue');influence.name='ST Influence';influence.outputs[0].default_value=1;controls.append(influence)
    factor=n.new('ShaderNodeMath');factor.operation='MULTIPLY';factor.inputs[1].default_value=.4;l.new(alpha.outputs['Fac'],factor.inputs[0])
    enable=n.new('ShaderNodeMath');enable.operation='MULTIPLY';l.new(factor.outputs[0],enable.inputs[0]);l.new(influence.outputs[0],enable.inputs[1])
    mix=n.new('ShaderNodeMixRGB');l.new(enable.outputs[0],mix.inputs[0]);l.new(g.outputs['Normal'],mix.inputs[1]);l.new(norm.outputs[0],mix.inputs[2])
    final=n.new('ShaderNodeVectorMath');final.operation='NORMALIZE';l.new(mix.outputs[0],final.inputs[0]);l.new(final.outputs[0],p.inputs['Normal'])
    for i,node in enumerate(n):node.location=(i%5*210,-(i//5)*220)
    old=[s.name for s in m.materials];m.materials[0]=mat
    mapping.append({'part':o.name,'export':True,'slots':[{'index':0,'source':old[0],'material':mat.name,'role':'steel'}],'normal_region_active':active,'selective_edge_roughness':None,'edge_reason':'Existing bevels retained at .30; no additional polish justified before still review','matrix_world':[list(r) for r in o.matrix_world],'modifiers':[{'name':x.name,'type':x.type} for x in o.modifiers]})
    for category,idx in [('edge',next(iter(protected),0)),('interior',max(range(len(m.vertices)),key=lambda i:al.data[i].value)),('seam',0)]:
        ns=(normalmat@m.vertices[idx].normal).normalized();zero=(ns*1+Vector((0,0,1))*0).normalized();checks.append({'part':o.name,'category':category,'vertex':idx,'zero_error':(zero-ns).length,'alpha':al.data[idx].value})
for o in parts:
    if o not in metal:mapping.append({'part':o.name,'export':o.name!='Neutral recessed neck support','slots':[{'index':i,'material':s.material.name,'role':'dark'} for i,s in enumerate(o.material_slots)]})
after={o.name:fingerprint(o) for o in metal};assert before==after
# Retain the entire accepted reflection environment and comparator datablocks.
for o in list(scene.objects):
    if o not in parts and o!=assembly:bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(STEEL),link=False) as (src,dst):dst.scenes=src.scenes
accepted=dst.scenes[0];comparators=[]
for o in list(accepted.objects):
    if o.name not in scene.objects:scene.collection.objects.link(o)
    if o.type in ['MESH','CURVE'] and o.name!='Plane':comparators.append(o)
scene.world=accepted.world
for key in ['view_transform','look','exposure','gamma','use_curve_mapping']:setattr(scene.view_settings,key,getattr(accepted.view_settings,key))
scene.display_settings.display_device=accepted.display_settings.display_device
accepted_camera=accepted.camera
camera=bpy.data.objects.new('ST matched helmet camera',bpy.data.cameras.new('ST orthographic'));scene.collection.objects.link(camera);camera.data.type='ORTHO';camera.data.ortho_scale=1.32;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=a.samples;scene.cycles.use_denoising=True;scene.cycles.seed=0;scene.render.threads_mode='FIXED';scene.render.threads=6
scene.render.resolution_percentage=100;scene.render.film_transparent=False;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
# Comparator occupies its original coordinates. Camera-ray hiding prevents overlap while preserving reflection surroundings.
for o in comparators:o.visible_camera=False
for o in parts:o.visible_camera=True
camera.location=(-1.45,-4,1.22);camera.rotation_euler=(Vector((0,-.01,.75))-camera.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'Helmet_Steel_{a.revision}.blend'))
dump(OUT/'regions.json',{'schema':1,'normal_space':'OBJECT targets transformed inverse-transpose to WORLD then normalized before blending with Geometry Normal','formula':'normalize((1-w)*Ns+w*Nt), w=.4*alpha*ST Influence','regions':regions})
dump(OUT/'source_manifest.json',{'schema':'helmet-steel-transfer-source-1','revision':a.revision,'sources':identities,'assembly':{'name':assembly.name,'scale':list(assembly.scale),'matrix_world':[list(r) for r in assembly.matrix_world]},'parts':mapping,'landmarks_world':{'crown_ridge':[0,-.075,1.205],'front_brow_aperture_edge':[0,-.394,.806],'front_cheek_aperture_edge':[0,-.389,.778],'slit_center':[0,-.3915,.792],'front_chin':[0,-.277,.357]},'normal_contract':{'target':'Packed per-part *_Target.png, linear decode 2*RGB-1; normalize inverse-transpose object to world; FACE ST_Target is diagnostic only','uv':'ST_SurfaceChart','alpha':'ST_Alpha FLOAT POINT, evaluated modifier interpolation','weight':'.4 * alpha * ST Influence'},'geometry':after,'source_blend':f'Helmet_Steel_{a.revision}.blend','roughness':.30,'base_color_linear':[.29,.285,.275],'metallic':1})
dump(OUT/'validation.json',{'geometry_and_construction_normals_unchanged':before==after,'evaluated_metal_triangles':sum(x['triangles'] for x in after.values()),'zero_checks':checks,'zero_control_graph':'Only ST Influence changes; geometry, construction normals, base color and roughness shared','accepted_sources_unchanged':all(sha(ROOT/p)==h for p,h in identities.items()),'connected_regions':True})
settings={'engine':'Cycles CPU','samples':a.samples,'rig_source':'Saved/ArtReview/UnrealStyle/AcceptedSteelTransfer/rig_audit.json','comparator_placement':'Original accepted world matrices, no transforms; camera-ray visibility disabled only during helmet renders; still present to secondary rays','helmet_placement':'Original Clay_v005 assembly unchanged','display':{k:getattr(scene.view_settings,k) for k in ['view_transform','look','exposure','gamma']},'renders':[]}
def render(name):
    scene.render.filepath=str(REVIEW/(name+'.png'));bpy.context.view_layer.update();bpy.ops.render.render(write_still=True)
    im=Image.open(scene.render.filepath);im.load();assert im.size==(scene.render.resolution_x,scene.render.resolution_y);assert max(im.convert('RGB').getextrema()[0])-min(im.convert('RGB').getextrema()[0])>0
    settings['renders'].append({'name':name,'sha256':sha(Path(scene.render.filepath)),'dimensions':list(im.size),'camera_matrix':[list(r) for r in scene.camera.matrix_world],'ortho_scale':scene.camera.data.ortho_scale});dump(REVIEW/'settings.json',settings)
scene.render.resolution_x=900;scene.render.resolution_y=1100
for name,pos in [('front',(0,-4,.98)),('three_quarter',(-1.45,-4,1.22))]:
    camera.location=pos;camera.rotation_euler=(Vector((0,-.01,.75))-camera.location).to_track_quat('-Z','Y').to_euler()
    for label,value in [('smooth',0),('authored',1)]:
        for c in controls:c.outputs[0].default_value=value
        render(name+'_'+label)
for o in parts:o.hide_render=True
for o in comparators:o.visible_camera=True
scene.camera=accepted_camera;scene.render.resolution_x=1440;scene.render.resolution_y=1000;render('accepted_armor_comparator')
# Native pixel pairs and unscaled portrait details retain actual rendered pixels.
for view in ['front','three_quarter']:
    pair=Image.new('RGB',(1800,1140),(28,28,28));d=ImageDraw.Draw(pair)
    for x,label in [(0,'smooth'),(900,'authored')]:pair.paste(Image.open(REVIEW/(view+'_'+label+'.png')),(x,40));d.text((x+12,12),view+' '+label,fill='white')
    pair.save(REVIEW/(view+'_native_pair.png'))
    Image.open(REVIEW/(view+'_authored.png')).crop((220,130,680,940)).save(REVIEW/(view+'_portrait_detail.png'))
for o in parts:o.hide_render=o.name=='Neutral recessed neck support'
for o in comparators:o.visible_camera=False
scene.camera=camera
assert all(sha(ROOT/p)==h for p,h in identities.items())
(REVIEW/'index.html').write_text('<html><body style="background:#222;color:white;font:18px sans-serif"><h1>'+a.revision+' actual source still review</h1><p>Technical source proof; artistic acceptance pending. Native pairs: smooth left, authored right. Accepted comparator unchanged at original placement.</p>'+''.join('<h2>'+n+'</h2><img style="max-width:100%" src="'+n+'.png">' for n in ['front_native_pair','three_quarter_native_pair','accepted_armor_comparator'])+'</body></html>')
print('ST_STILLS_COMPLETE',REVIEW,flush=True)
