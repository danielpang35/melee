"""Reimport only the revised combat body and FP arms; retain existing materials."""
from pathlib import Path
import unreal as u
root=Path(u.Paths.project_dir()).resolve()
dest='/Game/Visual/Citadel/Meshes'
glove_path='/Game/Visual/Citadel/Materials/M_CitadelGlove'
glove=u.load_asset(glove_path)
if not glove:
    glove=u.AssetToolsHelpers.get_asset_tools().create_asset('M_CitadelGlove','/Game/Visual/Citadel/Materials',u.Material,u.MaterialFactoryNew())
    color=u.MaterialEditingLibrary.create_material_expression(glove,u.MaterialExpressionConstant3Vector)
    color.set_editor_property('constant',u.LinearColor(.065,.075,.085,1))
    u.MaterialEditingLibrary.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
    rough=u.MaterialEditingLibrary.create_material_expression(glove,u.MaterialExpressionConstant)
    rough.set_editor_property('r',.72)
    u.MaterialEditingLibrary.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
    u.MaterialEditingLibrary.recompile_material(glove)
    u.EditorAssetLibrary.save_loaded_asset(glove)
# The material must compile its skeletal permutation before the game loads it.
# A saved slot binding alone otherwise renders the gloves with the fallback shader.
glove.set_editor_property('used_with_skeletal_mesh',True)
u.MaterialEditingLibrary.recompile_material(glove)
if not u.EditorAssetLibrary.save_loaded_asset(glove):raise RuntimeError('Could not save skeletal glove material')
steel=u.load_asset('/Game/Visual/Citadel/Materials/M_CitadelArmSteel')
if not steel:
    steel=u.AssetToolsHelpers.get_asset_tools().create_asset('M_CitadelArmSteel','/Game/Visual/Citadel/Materials',u.Material,u.MaterialFactoryNew())
    color=u.MaterialEditingLibrary.create_material_expression(steel,u.MaterialExpressionConstant3Vector)
    color.set_editor_property('constant',u.LinearColor(.18,.22,.26,1))
    u.MaterialEditingLibrary.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
    for value,prop in ((.82,u.MaterialProperty.MP_METALLIC),(.36,u.MaterialProperty.MP_ROUGHNESS)):
        node=u.MaterialEditingLibrary.create_material_expression(steel,u.MaterialExpressionConstant);node.set_editor_property('r',value)
        u.MaterialEditingLibrary.connect_material_property(node,'',prop)
steel.set_editor_property('used_with_skeletal_mesh',True)
u.MaterialEditingLibrary.recompile_material(steel)
if not u.EditorAssetLibrary.save_loaded_asset(steel):raise RuntimeError('Could not save arm steel')
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
for source,name in (('SK_CombatKnight','SK_CombatKnight'),('SK_CombatArms','SK_CombatArms')):
    options=u.FbxImportUI()
    options.automated_import_should_detect_type=False
    options.import_mesh=True;options.import_as_skeletal=True
    options.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH
    options.import_animations=False;options.import_materials=False;options.import_textures=False
    options.create_physics_asset=False
    options.skeleton=u.load_asset(dest+'/SKEL_Citadel')
    task=u.AssetImportTask();task.filename=str(root/'ArtSource/Citadel/Export'/(source+'.fbx'))
    task.destination_path=dest;task.destination_name=name;task.options=options
    task.automated=True;task.replace_existing=True;task.save=True
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=u.load_asset(dest+'/'+name)
    if not mesh:raise RuntimeError('Missing imported mesh '+name)
    skeleton=u.CitadelAssetTools.ensure_skeleton(mesh)
    if not skeleton:raise RuntimeError('Failed skeleton contract '+name)
    slots=mesh.get_editor_property('materials')
    # Reimport preserves old slot names, including duplicate KnightPBR names.
    # DCC slots: original armor at 0, gloves/joints at 1, closed arm steel at 2.
    if len(slots)!=3:raise RuntimeError('Expected armor, glove and arm-steel slots on '+name)
    if slots[1].get_editor_property('material_interface')!=glove:raise RuntimeError('Glove binding did not persist on '+name)
    if slots[2].get_editor_property('material_interface')!=steel:raise RuntimeError('Arm steel binding did not persist on '+name)
    if not u.EditorAssetLibrary.save_loaded_asset(mesh):raise RuntimeError("Could not save "+name)
    u.log('COMBAT RIG IMPORTED '+name)
u.log('COMBAT RIG IMPORT COMPLETE')
