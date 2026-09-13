"""Import the selected AccuRig body with its own skeleton and four authored LODs.

Run explicitly in UE 5.8 Python; never changes animation selectors or old assets.
LOD API: https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/SkeletalMeshEditorSubsystem
"""
from pathlib import Path
import json, hashlib, time
import unreal as u

ROOT = Path(u.Paths.project_dir()).resolve()
selection = json.loads((ROOT/'Config/WorkingCharacter.json').read_text(encoding='utf-8-sig'))
native_source = (ROOT/selection['native_source']).resolve()
SOURCE = native_source.parent
TEX = (ROOT/selection.get('texture_directory', 'ArtSource/UserMaleBody/MB_v002_GameReady/Textures')).resolve()
assert native_source.is_relative_to(ROOT) and TEX.is_relative_to(ROOT)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
export_path = SOURCE/'export_receipt.json'
export_receipt = json.loads(export_path.read_text(encoding='utf-8-sig'))
source_hash = sha(native_source)
assert export_receipt['source_sha256'] == source_hash, 'Native source changed since export'
assert len(export_receipt['lods']) == 4 and {item['lod'] for item in export_receipt['lods']} == set(range(4))
fbx_inputs = []
for item in sorted(export_receipt['lods'], key=lambda value: value['lod']):
    path = SOURCE/f"SK_MB_Body_LOD{item['lod']}.fbx"
    assert Path(item['file']).name == path.name, 'Export receipt FBX identity mismatch'
    assert sha(path) == item['sha256'], f'FBX changed since export: {path}'
    fbx_inputs.append(dict(lod=item['lod'], file=str(path.relative_to(ROOT)), sha256=item['sha256']))
export_hash = sha(export_path)
DEST = '/Game/UserMaleBody/MB_v004_Project'
OUT = ROOT/'Saved/WorkingBody'
OUT.mkdir(parents=True, exist_ok=True)
assets = u.AssetToolsHelpers.get_asset_tools()
edit = u.get_editor_subsystem(u.SkeletalMeshEditorSubsystem)
u.SystemLibrary.execute_console_command(None, 'Interchange.FeatureFlags.Import.FBX 0')

def import_file(path, name, options=None):
    task = u.AssetImportTask()
    task.filename = str(path)
    task.destination_path = DEST
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.save = True
    if options is not None:
        task.options = options
    assets.import_asset_tasks([task])
    result = u.load_asset(DEST+'/'+name)
    assert result, (name, list(task.imported_object_paths))
    return result

options = u.FbxImportUI()
options.automated_import_should_detect_type = False
options.import_mesh = True
options.import_as_skeletal = True
options.mesh_type_to_import = u.FBXImportType.FBXIT_SKELETAL_MESH
options.import_animations = False
options.import_materials = False
options.import_textures = False
options.create_physics_asset = False
existing = u.load_asset(DEST+'/SK_MB_Body')
# Retain the destination's imported slot metadata before FBX reimport can append renamed slots.
existing_slots = list(existing.get_editor_property('materials')) if existing else []
preserved_slots = None
if len(existing_slots) == 4:
    preserved_slots = []
    # Native struct copying preserves read-only imported slot metadata too.
    preserved_slots = [old_slot.copy() for old_slot in existing_slots]
options.skeleton = existing.get_editor_property('skeleton') if existing else None
options.skeletal_mesh_import_data.set_editor_property('normal_import_method', u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)
options.skeletal_mesh_import_data.set_editor_property('import_morph_targets', False)
skin = import_file(SOURCE/'SK_MB_Body_LOD0.fbx', 'SK_MB_Body', options)
skeleton = skin.get_editor_property('skeleton')
assert skeleton and skeleton.get_path_name().startswith(DEST+'/')
for lod in range(1, 4):
    assert edit.import_lod(skin, lod, str(SOURCE/f'SK_MB_Body_LOD{lod}.fbx')) == lod
assert edit.get_lod_count(skin) == 4

def texture(path, name, srgb, compression):
    tex = import_file(path, name)
    tex.set_editor_property('srgb', srgb)
    tex.set_editor_property('compression_settings', compression)
    assert u.EditorAssetLibrary.save_loaded_asset(tex)
    return tex

base = texture(TEX/'T_MB_BaseColor_2K.png', 'T_MB_BaseColor', True, u.TextureCompressionSettings.TC_DEFAULT)
orm = texture(TEX/'T_MB_ORM_2K.png', 'T_MB_ORM', False, u.TextureCompressionSettings.TC_MASKS)
normals = [texture(TEX/f'Unreal_DirectX/T_MB_Normal_LOD{i}_DX.png', f'T_MB_Normal_LOD{i}', False,
                   u.TextureCompressionSettings.TC_NORMALMAP) for i in range(4)]
mat = u.load_asset(DEST+'/M_MB_Body') or assets.create_asset('M_MB_Body', DEST, u.Material, u.MaterialFactoryNew())
u.MaterialEditingLibrary.delete_all_material_expressions(mat)
mat.set_editor_property('used_with_skeletal_mesh', True)

def sample(tex, parameter, sampler):
    node = u.MaterialEditingLibrary.create_material_expression(mat, u.MaterialExpressionTextureSampleParameter2D)
    node.set_editor_property('parameter_name', parameter)
    node.set_editor_property('texture', tex)
    node.set_editor_property('sampler_type', sampler)
    return node

b = sample(base, 'BaseColor', u.MaterialSamplerType.SAMPLERTYPE_COLOR)
o = sample(orm, 'ORM', u.MaterialSamplerType.SAMPLERTYPE_MASKS)
n = sample(normals[0], 'Normal', u.MaterialSamplerType.SAMPLERTYPE_NORMAL)
for node, output, prop in [(b, 'RGB', u.MaterialProperty.MP_BASE_COLOR),
                           (o, 'R', u.MaterialProperty.MP_AMBIENT_OCCLUSION),
                           (o, 'G', u.MaterialProperty.MP_ROUGHNESS),
                           (o, 'B', u.MaterialProperty.MP_METALLIC),
                           (n, 'RGB', u.MaterialProperty.MP_NORMAL)]:
    assert u.MaterialEditingLibrary.connect_material_property(node, output, prop)
u.MaterialEditingLibrary.recompile_material(mat)
assert u.EditorAssetLibrary.save_loaded_asset(mat)
slots = []
imported_slots = preserved_slots if preserved_slots is not None else list(skin.get_editor_property('materials'))
assert len(imported_slots) == 4, [str(s.imported_material_slot_name) for s in imported_slots]
for lod in range(4):
    name = f'MI_MB_Body_LOD{lod}'
    inst = u.load_asset(DEST+'/'+name) or assets.create_asset(name, DEST, u.MaterialInstanceConstant, u.MaterialInstanceConstantFactoryNew())
    u.MaterialEditingLibrary.set_material_instance_parent(inst, mat)
    # UE 5.8's setter always returns false; verify the stored value instead.
    u.MaterialEditingLibrary.set_material_instance_texture_parameter_value(inst, 'Normal', normals[lod])
    assert u.MaterialEditingLibrary.get_material_instance_texture_parameter_value(inst, 'Normal') == normals[lod]
    u.MaterialEditingLibrary.update_material_instance(inst)
    assert u.EditorAssetLibrary.save_loaded_asset(inst)
    slot = imported_slots[lod]
    slot.set_editor_property('material_interface', inst)
    slots.append(slot)
skin.set_editor_property('materials', slots)
assert len(skin.get_editor_property('materials')) == 4
# Native persistence also sets the four LOD material maps and screen thresholds.
# UE 5.8 removed the reflected SkeletalMesh.lod_info array.
assert u.KnightPresentation.persist_surface(skin, slots[0].get_editor_property('material_interface'))
assert u.EditorAssetLibrary.save_loaded_asset(skin)
assert u.EditorAssetLibrary.save_loaded_asset(skeleton)
lods = []
for lod in range(4):
    assert edit.get_num_sections(skin, lod) == 1
    assert edit.get_lod_material_slot(skin, lod, 0) == lod
    lods.append(dict(lod=lod, render_vertices=edit.get_num_verts(skin, lod),
                     section_material=edit.get_lod_material_slot(skin, lod, 0)))
assert sha(native_source) == source_hash and sha(export_path) == export_hash, 'Source/export receipt changed during import'
for item in fbx_inputs:
    assert sha(ROOT/item['file']) == item['sha256'], 'FBX changed during import'
runtime_package = ROOT/'Content/UserMaleBody/MB_v004_Project/SK_MB_Body.uasset'
receipt = dict(source=str(native_source.relative_to(ROOT)), source_sha256=source_hash,
               export_receipt=str(export_path.relative_to(ROOT)), export_receipt_sha256=export_hash,
               fbx_inputs=fbx_inputs, runtime_package=str(runtime_package.relative_to(ROOT)),
               runtime_package_sha256=sha(runtime_package), mesh=skin.get_path_name(), skeleton=skeleton.get_path_name(), lods=lods,
               materials=[s.material_interface.get_path_name() for s in skin.materials],
               animations_imported=False, morph_targets_imported=False, completed=True)
latest = OUT/'import.json'
if latest.exists():
    history = OUT/f'import-history-{time.time_ns()}.json'
    with history.open('xb') as target:
        target.write(latest.read_bytes())
pending = OUT/'import.pending.json'
pending.write_text(json.dumps(receipt, indent=2)+'\n')
pending.replace(latest)
u.log('WORKING_BODY_IMPORT_SUCCESS '+str(receipt))
