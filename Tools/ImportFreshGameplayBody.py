"""Import the preserved fresh foundation into its own skeleton and material packages."""
import hashlib,json
from pathlib import Path
import unreal as u
root=Path(u.Paths.project_dir()).resolve()
source=root/'ArtSource/CharacterReset/CF_v001/CF_v001_Character.fbx'
expected=json.loads((source.parent/'delivery-manifest.json').read_text())[source.name]['sha256']
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
dest='/Game/CharacterReset/CF_v001'
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
options=u.FbxImportUI()
options.automated_import_should_detect_type=False
options.import_mesh=True;options.import_as_skeletal=True
options.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH
options.import_animations=False;options.import_materials=True;options.import_textures=False
options.create_physics_asset=False
task=u.AssetImportTask();task.filename=str(source);task.destination_path=dest
task.destination_name='CF_GameplayBody';task.options=options
task.automated=True;task.replace_existing=False;task.save=True
if not u.EditorAssetLibrary.does_asset_exist(dest+'/CF_GameplayBody'):
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
mesh=u.load_asset(dest+'/CF_GameplayBody')
assert mesh and mesh.get_editor_property('skeleton')
for slot in mesh.get_editor_property('materials'):
    material=slot.get_editor_property('material_interface')
    if isinstance(material,u.Material):
        material.set_editor_property('used_with_skeletal_mesh',True)
        u.MaterialEditingLibrary.recompile_material(material)
        u.EditorAssetLibrary.save_loaded_asset(material)
# Reproduce the foundation's existing rest-space fitted-shorts mask. FBX
# cannot transport Blender's named point attribute/shader graph.
mat=u.load_asset(dest+'/CF_StudySurface')
if not mat:
    mat=u.AssetToolsHelpers.get_asset_tools().create_asset('CF_StudySurface',dest,u.Material,u.MaterialFactoryNew())
if mat:
    u.MaterialEditingLibrary.delete_all_material_expressions(mat)
    def node(cls):return u.MaterialEditingLibrary.create_material_expression(mat,cls)
    def link(a,b,input_name):
        pin='' if input_name=='Input' else input_name
        assert u.MaterialEditingLibrary.connect_material_expressions(a,'',b,pin),(b.get_class().get_name(),pin)
    def constant(value):
        n=node(u.MaterialExpressionConstant);n.set_editor_property('r',value);return n
    def mask(source,axis):
        n=node(u.MaterialExpressionComponentMask)
        for channel in ['r','g','b','a']:n.set_editor_property(channel,channel==axis)
        link(source,n,'Input');return n
    zero,one=constant(0),constant(1)
    rest=node(u.MaterialExpressionPreSkinnedPosition)
    pos=node(u.MaterialExpressionVertexInterpolator);link(rest,pos,'Input')
    z=mask(pos,'b');x=mask(pos,'r');absolute=node(u.MaterialExpressionAbs);link(x,absolute,'Input')
    def less(a,value):
        n=node(u.MaterialExpressionIf);link(a,n,'A');link(constant(value),n,'B')
        link(zero,n,'A > B');link(one,n,'A < B');link(zero,n,'A == B');return n
    upper=less(z,104.5);lower=less(z,80);width=less(absolute,25)
    inv=node(u.MaterialExpressionOneMinus);link(lower,inv,'Input')
    mul=node(u.MaterialExpressionMultiply);link(upper,mul,'A');link(inv,mul,'B')
    region=node(u.MaterialExpressionMultiply);link(mul,region,'A');link(width,region,'B')
    clay=node(u.MaterialExpressionConstant3Vector);clay.set_editor_property('constant',u.LinearColor(.43,.34,.27,1))
    shorts=node(u.MaterialExpressionConstant3Vector);shorts.set_editor_property('constant',u.LinearColor(.035,.058,.075,1))
    color=node(u.MaterialExpressionLinearInterpolate);link(clay,color,'A');link(shorts,color,'B');link(region,color,'Alpha')
    u.MaterialEditingLibrary.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
    u.MaterialEditingLibrary.connect_material_property(constant(.72),'',u.MaterialProperty.MP_ROUGHNESS)
    mat.set_editor_property('used_with_skeletal_mesh',True);u.MaterialEditingLibrary.recompile_material(mat)
    u.EditorAssetLibrary.save_loaded_asset(mat)
# Native setter updates Unreal's serialized material information cache.
assert u.KnightPresentation.persist_surface(mesh,mat)
u.EditorAssetLibrary.save_loaded_asset(mesh)
u.EditorAssetLibrary.save_directory(dest,only_if_is_dirty=False,recursive=True)
receipt=dict(source=str(source),source_sha256=expected,mesh=mesh.get_path_name(),
    skeleton=mesh.get_editor_property('skeleton').get_path_name(),
    assets=list(u.EditorAssetLibrary.list_assets(dest,recursive=True)),
    materials=[s.get_editor_property('material_interface').get_path_name() for s in mesh.get_editor_property('materials')],old_character_assets_used=False)
(root/'Saved/MEL15/production/fresh-body-import.json').write_text(json.dumps(receipt,indent=2))
u.log('FRESH_GAMEPLAY_BODY '+json.dumps(receipt))
