"""Import only the supplied knight and neutral floor into isolated packages."""
from pathlib import Path
import json
import unreal as u
ROOT=Path(u.Paths.project_dir()).resolve()
(ROOT/'Saved/UserKnight').mkdir(parents=True,exist_ok=True)
DEST='/Game/UserKnight/KN_v001'
assets=u.AssetToolsHelpers.get_asset_tools()
def material(name,color,metal,rough):
    mat=u.load_asset(DEST+'/'+name)
    if mat:return mat
    if not mat:mat=assets.create_asset(name,DEST,u.Material,u.MaterialFactoryNew())
    u.MaterialEditingLibrary.delete_all_material_expressions(mat)
    node=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionConstant3Vector)
    node.set_editor_property('constant',u.LinearColor(*color,1))
    u.MaterialEditingLibrary.connect_material_property(node,'',u.MaterialProperty.MP_BASE_COLOR)
    for value,prop in [(metal,u.MaterialProperty.MP_METALLIC),(rough,u.MaterialProperty.MP_ROUGHNESS)]:
        node=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionConstant)
        node.set_editor_property('r',value)
        u.MaterialEditingLibrary.connect_material_property(node,'',prop)
    u.MaterialEditingLibrary.recompile_material(mat)
    assert u.EditorAssetLibrary.save_loaded_asset(mat)
    return mat
floor=material('M_WhiteFloor',(1,1,1),0,.85)
steel=material('M_UserKnightClay',(.28,.31,.35),.65,.48)
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
options=u.FbxImportUI();options.automated_import_should_detect_type=False
options.import_mesh=True;options.import_as_skeletal=False
options.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH
options.import_materials=False;options.import_textures=False
options.static_mesh_import_data.combine_meshes=True
options.static_mesh_import_data.auto_generate_collision=False
task=u.AssetImportTask();task.filename=str(ROOT/'ArtSource/UserKnight/KN_v001/SM_UserKnight.fbx')
task.destination_path=DEST;task.destination_name='SM_UserKnight';task.options=options
task.automated=True;task.replace_existing=True;task.save=True
if not u.EditorAssetLibrary.does_asset_exist(DEST+'/SM_UserKnight'):
    assets.import_asset_tasks([task])
mesh=u.load_asset(DEST+'/SM_UserKnight');assert mesh
mesh.set_material(0,steel)
assert u.EditorAssetLibrary.save_loaded_asset(mesh)
box=mesh.get_bounding_box();size=box.max-box.min
assert 179<size.z<181, str(size)
receipt=dict(mesh=mesh.get_path_name(),height_cm=size.z,rigged=False,material=steel.get_path_name())
steel.set_editor_property('used_with_skeletal_mesh',True)
u.MaterialEditingLibrary.recompile_material(steel)
assert u.EditorAssetLibrary.save_loaded_asset(steel)
options=u.FbxImportUI();options.automated_import_should_detect_type=False
options.import_mesh=True;options.import_as_skeletal=True
options.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH
options.import_animations=False;options.import_materials=False;options.import_textures=False
options.create_physics_asset=False
options.skeleton=None
task=u.AssetImportTask();task.filename=str(ROOT/'ArtSource/UserKnight/KN_v001/SK_UserKnight.fbx')
task.destination_path=DEST;task.destination_name='SK_UserKnight';task.options=options
task.automated=True;task.replace_existing=True;task.save=True
assets.import_asset_tasks([task])
skin=u.load_asset(DEST+'/SK_UserKnight');assert skin and skin.get_editor_property('skeleton')
skeleton=skin.get_editor_property('skeleton')
assert skeleton.get_path_name().startswith(DEST+'/'),skeleton.get_path_name()
assert u.EditorAssetLibrary.save_loaded_asset(skeleton)
slots=skin.get_editor_property('materials')
for slot in slots:slot.set_editor_property('material_interface',steel)
skin.set_editor_property('materials',slots)
assert u.EditorAssetLibrary.save_loaded_asset(skin)
receipt['skin']=skin.get_path_name();receipt['rigged']=True
receipt['skeleton']=skeleton.get_path_name()
(ROOT/'Saved/UserKnight/import.json').write_text(json.dumps(receipt,indent=2))
u.log('USER_KNIGHT_IMPORT_SUCCESS '+str(receipt))
if '-UserKnightReview' in u.SystemLibrary.get_command_line():
    import sys
    sys.path.insert(0,str(ROOT/'Tools'))
    import VerifyUserKnight
