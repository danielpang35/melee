"""Explicit selected Knight body import. No clips or gameplay selectors change."""
from pathlib import Path
import json
import unreal as u

ROOT=Path(u.Paths.project_dir()).resolve()
DEST='/Game/UserKnight/KN_v002'
assets=u.AssetToolsHelpers.get_asset_tools()
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
options=u.FbxImportUI();options.automated_import_should_detect_type=False
options.import_mesh=True;options.import_as_skeletal=True
options.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH
options.import_animations=False;options.import_materials=False;options.import_textures=False
options.create_physics_asset=False
existing=u.load_asset(DEST+'/SK_KnightBody')
options.skeleton=existing.get_editor_property('skeleton') if existing else None
task=u.AssetImportTask();task.filename=str(ROOT/'ArtSource/UserKnight/KN_v002/SK_KnightBody.fbx')
task.destination_path=DEST;task.destination_name='SK_KnightBody';task.options=options
task.automated=True;task.replace_existing=True;task.save=True
materials_only='-KnightMaterialsOnly' in u.SystemLibrary.get_command_line()
if materials_only:
    assert existing, 'Import the selected body before updating its materials'
else:
    assets.import_asset_tasks([task])
skin=u.load_asset(DEST+'/SK_KnightBody');assert skin
skeleton=skin.get_editor_property('skeleton')
assert skeleton and skeleton.get_path_name().startswith(DEST+'/')
assert u.EditorAssetLibrary.save_loaded_asset(skeleton)

def material(name,color):
    mat=u.load_asset(DEST+'/'+name)
    if not mat:
        mat=assets.create_asset(name,DEST,u.Material,u.MaterialFactoryNew())
        node=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionConstant3Vector)
        node.set_editor_property('constant',u.LinearColor(*color,1))
        u.MaterialEditingLibrary.connect_material_property(node,'',u.MaterialProperty.MP_BASE_COLOR)
        rough=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionConstant)
        rough.set_editor_property('r',.72)
        u.MaterialEditingLibrary.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
    mat.set_editor_property('used_with_skeletal_mesh',True)
    u.MaterialEditingLibrary.recompile_material(mat)
    assert u.EditorAssetLibrary.save_loaded_asset(mat)
    return mat

body=material('M_KnightBody',(.48,.39,.30))
# FBX does not carry Blender's StudyShortsRegion attribute/shader graph.
# Reuse the foundation's pre-skinned-position mask at the Knight's uniform scale.
u.MaterialEditingLibrary.delete_all_material_expressions(body)
def node(cls):return u.MaterialEditingLibrary.create_material_expression(body,cls)
def link(a,b,pin):
    assert u.MaterialEditingLibrary.connect_material_expressions(a,'',b,'' if pin=='Input' else pin)
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
upper=less(z,104.5*.96);lower=less(z,80*.96);width=less(absolute,25*.96)
inv=node(u.MaterialExpressionOneMinus);link(lower,inv,'Input')
mul=node(u.MaterialExpressionMultiply);link(upper,mul,'A');link(inv,mul,'B')
region=node(u.MaterialExpressionMultiply);link(mul,region,'A');link(width,region,'B')
clay=node(u.MaterialExpressionConstant3Vector);clay.set_editor_property('constant',u.LinearColor(.43,.34,.27,1))
cloth=node(u.MaterialExpressionConstant3Vector);cloth.set_editor_property('constant',u.LinearColor(.035,.058,.075,1))
color=node(u.MaterialExpressionLinearInterpolate);link(clay,color,'A');link(cloth,color,'B');link(region,color,'Alpha')
assert u.MaterialEditingLibrary.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
assert u.MaterialEditingLibrary.connect_material_property(constant(.72),'',u.MaterialProperty.MP_ROUGHNESS)
u.MaterialEditingLibrary.recompile_material(body)
assert u.EditorAssetLibrary.save_loaded_asset(body)
shorts=material('M_KnightShorts',(.045,.075,.09))
eyes=material('M_KnightEyes',(.53,.49,.43))
slots=[]
slot_receipt=[]
for slot in skin.get_editor_property('materials'):
    name=str(slot.get_editor_property('imported_material_slot_name'))
    chosen=eyes if 'Eye' in name else shorts if any(s in name.lower() for s in ['short','modesty','cloth']) else body
    slot.set_editor_property('material_interface',chosen)
    # Unreal returns struct copies when iterating its Array; retain each edit.
    slots.append(slot)
    slot_receipt.append(dict(slot=name,material=chosen.get_path_name()))
skin.set_editor_property('materials',slots)
assert all(slot.get_editor_property('material_interface') for slot in skin.get_editor_property('materials'))
# The reflected array setter leaves Unreal's serialized material cache stale.
# Reuse the native setter already used by the foundation import.
assert u.KnightPresentation.persist_surface(skin,slots[0].get_editor_property('material_interface'))
assert u.EditorAssetLibrary.save_loaded_asset(skin)
receipt=dict(mesh=skin.get_path_name(),skeleton=skeleton.get_path_name(),materials=slot_receipt,
    source='ArtSource/UserKnight/KN_v002/SK_KnightBody.fbx',armor_imported=False,animations_imported=False,
    materials_only=materials_only,native_material_cache_updated=True)
(ROOT/'Saved/UserKnight/body-import.json').write_text(json.dumps(receipt,indent=2))
u.log('KNIGHT_BODY_IMPORT_SUCCESS '+str(receipt))
if '-UserKnightReview' in u.SystemLibrary.get_command_line():
    import sys
    sys.path.insert(0,str(ROOT/'Tools'))
    import VerifyUserKnight
