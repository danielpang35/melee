"""Create an immutable, source-only single-region edit demonstration from accepted ST_v002."""
from pathlib import Path
import sys,json,hashlib,math,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'Saved/ArtRuntime'),str(ROOT/'Saved/VideoRuntime')]
import bpy
import numpy as np
from PIL import Image
from mathutils import Matrix,Vector
BASE=ROOT/'ArtSource/StyleReference/MEL17/SteelTransfer/ST_v002';OUT=BASE.parent/'ST_v003'
REVIEW=ROOT/'Saved/ArtReview/UnrealStyle/ST_v003/Review'
if OUT.exists() or REVIEW.exists():raise RuntimeError('Immutable demonstration already exists')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2),encoding='utf-8')
baseline_hashes={p.name:sha(p) for p in BASE.iterdir() if p.is_file()}
source=json.loads((BASE/'source_manifest.json').read_text());recipe=json.loads((BASE/'regions.json').read_text())
region=next(r for r in recipe['regions'] if r['name']=='Left wrapping brow region 7')
old=Vector(region['target_object']);new=(Matrix.Rotation(math.radians(6),3,'X')@old).normalized()
texture_name='Left_wrapping_brow_Target.png';pixels=np.array(Image.open(BASE/texture_name).convert('RGB'))
old_rgb=np.array([round((x*.5+.5)*255) for x in old],dtype=np.uint8);new_rgb=np.array([round((x*.5+.5)*255) for x in new],dtype=np.uint8)
mask=np.all(pixels==old_rgb,axis=2);assert mask.sum()>100
# Exact matching encoded cells retain shared-edge pixel ownership from the accepted recipe.
y,x=np.nonzero(mask);polygon=region['boundary_chart_polygon'];points=np.stack((x/1023,1-y/1023),axis=1)
sides=[]
for aa,bb in zip(polygon,polygon[1:]+polygon[:1]):sides.append((bb[0]-aa[0])*(points[:,1]-aa[1])-(bb[1]-aa[1])*(points[:,0]-aa[0]))
sides=np.stack(sides);assert np.all(np.all(sides>=-.003,axis=0)|np.all(sides<=.003,axis=0))
edited=pixels.copy();edited[mask]=new_rgb;assert np.all(edited[~mask]==pixels[~mask])
OUT.mkdir();REVIEW.mkdir(parents=True)
for path in BASE.iterdir():
    if path.is_file() and path.suffix!='.blend' and path.name!='generator.py':shutil.copy2(path,OUT/path.name)
Image.fromarray(edited).save(OUT/texture_name)
bpy.ops.wm.open_mainfile(filepath=str(BASE/source['source_blend']));scene=bpy.context.scene
source_blend='Helmet_Steel_ST_v003.blend'
def fingerprint(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles()
    data={'vertices':[list(v.co) for v in mesh.vertices],'triangles':[list(t.vertices) for t in mesh.loop_triangles],'normals':[list(n.vector) for n in mesh.corner_normals]}
    result={'sha256':hashlib.sha256(json.dumps(data).encode()).hexdigest(),'triangles':len(mesh.loop_triangles)};ev.to_mesh_clear();return result
geometry_before={name:fingerprint(bpy.data.objects[name]) for name in source['geometry']};assert geometry_before==source['geometry']
rebound=set()
for part in source['parts']:
    obj=bpy.data.objects[part['part']]
    for slot in obj.material_slots:
        if not slot.material or not slot.material.use_nodes:continue
        for node in slot.material.node_tree.nodes:
            if node.type!='TEX_IMAGE' or not node.image:continue
            image=node.image;name=Path(bpy.path.abspath(image.filepath)).name
            if not name.endswith('_Target.png'):continue
            if image.name in rebound:continue
            if image.packed_file:image.unpack(method='REMOVE')
            image.filepath=str(OUT/name);image.reload();image.pack();rebound.add(image.name)
obj=bpy.data.objects[region['part']]
for index in region.get('graph_seed_faces_diagnostic_only',[]):obj.data.attributes['ST_Target'].data[index].vector=new
region['target_object']=list(new);region['target_world']=list((obj.matrix_world.to_3x3().inverted().transposed()@new).normalized())
provenance={'baseline_revision':'ST_v002','baseline_source_sha256':baseline_hashes[source['source_blend']],'edited_region':region['name'],'part':region['part'],'operation':'Rotate constant target normal +6 degrees around object-space X','old_target_object':list(old),'new_target_object':list(new),'old_encoded_rgb':old_rgb.tolist(),'new_encoded_rgb':new_rgb.tolist(),'modified_target_pixels':int(mask.sum()),'region_footprint_unchanged':True,'alpha_and_strength_unchanged':True,'expected_effect':'Localized vertical change in key reflection within central left brow plane; surrounding regions, construction and silhouette stay unchanged. Maximum interior weight remains .096, so shaded-normal change is about .6 degrees.','render_status':'No renders/export/bake executed for demonstration; engine USP_v017 validation pending','baseline_authorities':source['sources']}
region['edit_provenance']=provenance;recipe['controlled_edit']=provenance
geometry_after={name:fingerprint(bpy.data.objects[name]) for name in source['geometry']};assert geometry_before==geometry_after
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/source_blend))
source['revision']='ST_v003';source['source_blend']=source_blend;source['controlled_edit']=provenance
source['geometry']=geometry_after
dump(OUT/'source_manifest.json',source);dump(OUT/'regions.json',recipe)
texture_hashes={p.name:sha(p) for p in OUT.glob('*_Target.png')};changed_textures=[name for name,h in texture_hashes.items() if baseline_hashes[name]!=h];assert changed_textures==[texture_name]
assert baseline_hashes=={p.name:sha(p) for p in BASE.iterdir() if p.is_file()}
assert all(sha(ROOT/p)==h for p,h in source['sources'].items())
validation={'geometry_and_construction_normals_unchanged':True,'evaluated_metal_triangles':sum(v['triangles'] for v in geometry_after.values()),'changed_textures':changed_textures,'changed_target_pixels':int(mask.sum()),'source_baseline_unchanged':True,'accepted_authorities_unchanged':True,'zero_control':'Normal target edit only; ST Influence=0 mathematically removes target contribution. Baseline pixel proof inherited, not freshly rendered.','controlled_edit':provenance}
dump(OUT/'validation.json',validation)
finalization={'source_sha256':sha(OUT/source_blend),'regions_sha256':sha(OUT/'regions.json'),'texture_hashes':texture_hashes,'scope':'P6 controlled edit demonstration; not a new artistic acceptance','inherited_baseline_review':'Saved/ArtReview/UnrealStyle/ST_v002/Review/finalization.json','inherited_baseline_review_sha256':sha(ROOT/'Saved/ArtReview/UnrealStyle/ST_v002/Review/finalization.json'),'geometry_validation_sha256':sha(OUT/'validation.json'),'controlled_edit':provenance,'render_status':'Not rendered; parent-authorized edit/reimport demonstration'}
dump(REVIEW/'finalization.json',finalization);(OUT/'generator.py').write_text(Path(__file__).read_text(),encoding='utf-8')
print(json.dumps({'manifest':str(OUT/'source_manifest.json'),'source_sha256':finalization['source_sha256'],'region':region['name'],'changed_target_pixels':int(mask.sum()),'geometry_unchanged':True,'triangles':validation['evaluated_metal_triangles']},indent=2))
