"""Record the exact completed surface-repair evidence without widening its claims."""
import json,hashlib,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'ArtSource/UserMaleBody/MB_v005_SurfaceRepair'
EV=ROOT/'Saved/WorkingBodyRepair'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selection=read(ROOT/'Config/WorkingCharacter.json');source=ROOT/selection['native_source']
assert source==OUT/'Male_Body_SurfaceRepair.blend'
identity=sha(source)
receipts={}
for name in ['source-verification','bake','roundtrip','return-handoff']:
    p=EV/(name+'.json');data=read(p)
    assert data['source_sha256']==identity,name
    receipts[name]=dict(path=str(p.relative_to(ROOT)),sha256=sha(p))
for name in ['source-verification','textured']:
    p=EV/(name+'.json');data=read(p)
    assert data['source_sha256']==identity
    data['visual_review']='Inspected named front/rear/left/right textured captures of all four LODs and rear arm close-ups; rest surface only. No universal deformation or continuous-playback pass.'
    p.write_text(json.dumps(data,indent=2)+'\n')
    receipts[name]=dict(path=str(p.relative_to(ROOT)),sha256=sha(p))
original=ROOT/'ArtSource/UserMaleBody/MB_v004_Project/Male_Body_Project.blend'
assert sha(original)=='a1d1d9120887d0cfbfacda751999bd58b8cd2e8f0a00b56cb4d56ca685c7fdad'
assert sha(ROOT/'Config/EXPreview.json')=='fbb2cae992bcb7daff8a2398893cb23e7593611203e095bc4d6e854f7e282205'
motion=read(EV/'motion-final/preview.json')
assert motion['frames']==145 and motion['fps']==30 and set(motion['views'])=={'primary','rear-quarter'}
assert all(v['timing']['frames']==145 and v['timing']['playback_rate']==1 for v in motion['views'].values())
runtime=read(ROOT/'Saved/WorkingBody/import.json')
imported=runtime.get('source_sha256')==identity and runtime.get('completed') is True
if imported:
    assert sha(ROOT/runtime['runtime_package'])==runtime['runtime_package_sha256']
else:
    backup=EV/'runtime-before/MB_v004_Project'
    assert all(sha(p)==sha(ROOT/'Content/UserMaleBody/MB_v004_Project'/p.relative_to(backup)) for p in backup.rglob('*') if p.is_file()), 'Runtime differs from retained pre-import backup'
manifest=dict(working_character=selection,source_sha256=identity,receipts=receipts,
    export=read(OUT/'export_receipt.json'),original_source_unchanged=True,accepted_ex_config_unchanged=True,
    runtime_import_completed=imported,runtime_import=runtime if imported else None,
    runtime_multi_angle_visual_review='Not completed before user requested wrap-up',
    native_rest_surface='Structural checks passed on four LODs; multi-angle stills inspected',
    animation_deformation='Not a full pass: deep elbow compression and one LOD0 forearm-twist overlap remain',
    preview='Complete native-speed primary and rear-quarter media generated; continuous review not claimed',
    camera_boundary_tests='7 passed; reused unchanged evidence from independent reviewer')
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
checkpoint=OUT/'CHECKPOINT.md';content=checkpoint.read_text()
runtime_note=('corrected mesh, four LODs and materials imported and saved successfully. Fresh multi-angle PIE verification remains pending after the wrap-up request.' if imported else
    'the corrected native source is saved. The import was stopped during slow editor startup after the wrap-up request; runtime packages match the retained original backup. Import and fresh multi-angle PIE verification remain pending.')
content='\n'.join('- **Runtime:** '+runtime_note+' Original runtime packages and selector are retained in `Saved/WorkingBodyRepair/runtime-before`.' if line.startswith('- **Runtime:**') else line for line in content.split('\n'))
content=content.replace('Next useful action: finish fresh Unreal verification, then resolve',
                        'Next useful action: run `Tools/VerifyWorkingBody.py` for fresh Unreal verification, then resolve')
checkpoint.write_text(content)
for name in ['RepairWorkingBody.py','FinalizeWorkingBodyRepair.py','ImportWorkingBody.py','VerifyWorkingBody.py','UseWorkingBodyOnReturn.py','TestWorkingBodyReturn.py','ValidateWorkingBodyDeformation.py']:
    ast.parse((ROOT/'Tools'/name).read_text(),filename=name)
print(json.dumps(dict(source_sha256=identity,runtime_import_completed=imported,original_source_unchanged=True,ex_config_unchanged=True,syntax='passed')))
