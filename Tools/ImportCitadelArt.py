"""Unreal commandlet import; builds persistent, cookable PBR and skeletal assets."""
from pathlib import Path
import unreal as u
ROOT=Path(u.Paths.project_dir()).resolve();SRC=ROOT/'ArtSource/Citadel'
DEST='/Game/Visual/Citadel';A=u.AssetToolsHelpers.get_asset_tools();L=u.MaterialEditingLibrary
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
for folder in ('Meshes','Textures','Materials'):u.EditorAssetLibrary.make_directory(DEST+'/'+folder)

def texture(path,name,kind='color'):
    task=u.AssetImportTask();task.filename=str(path);task.destination_path=DEST+'/Textures';task.destination_name=name
    task.automated=True;task.replace_existing=True;task.save=True;A.import_asset_tasks([task])
    tex=u.load_asset(DEST+'/Textures/'+name)
    if not tex:raise RuntimeError('Texture import failed: '+str(path))
    tex.set_editor_property('srgb',kind=='color')
    if kind=='normal':tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
    elif kind!='color':tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_MASKS)
    u.EditorAssetLibrary.save_loaded_asset(tex);return tex

def material(name,channels,world=False,cloth=False):
    path=DEST+'/Materials/'+name
    mat=u.load_asset(path) or A.create_asset(name,DEST+'/Materials',u.Material,u.MaterialFactoryNew())
    mat.set_editor_property('used_with_instanced_static_meshes',True)
    mat.set_editor_property('used_with_skeletal_mesh',True)
    mat.set_editor_property('two_sided',cloth)
    L.delete_all_material_expressions(mat)
    def node(cls,x,y):return L.create_material_expression(mat,cls,x,y)
    tint=node(u.MaterialExpressionVectorParameter,-300,-450);tint.set_editor_property('parameter_name','BaseColor');tint.set_editor_property('default_value',u.LinearColor(1,1,1,1))
    for index,(pin,tex,kind,channel) in enumerate(channels):
        y=index*230
        if world:
            sample=node(u.MaterialExpressionTextureObject,-900,y);sample.set_editor_property('texture',tex)
            call=node(u.MaterialExpressionMaterialFunctionCall,-500,y)
            fn='WorldAlignedNormal' if kind=='normal' else 'WorldAlignedTexture'
            call.set_material_function(u.load_asset('/Engine/Functions/Engine_MaterialFunctions01/Texturing/'+fn))
            size=node(u.MaterialExpressionConstant3Vector,-900,y+90);size.set_editor_property('constant',u.LinearColor(240,240,240,1))
            assert L.connect_material_expressions(sample,'',call,'TextureObject')
            assert L.connect_material_expressions(size,'',call,'TextureSize')
            output=call;out='XYZ Texture'
            if kind=='normal':out='XYZ Texture'
        else:
            output=node(u.MaterialExpressionTextureSample,-800,y);output.set_editor_property('texture',tex)
            output.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL if kind=='normal' else u.MaterialSamplerType.SAMPLERTYPE_COLOR if kind=='color' else u.MaterialSamplerType.SAMPLERTYPE_MASKS)
            out=channel
        if pin==u.MaterialProperty.MP_BASE_COLOR:
            mul=node(u.MaterialExpressionMultiply,0,y)
            assert L.connect_material_expressions(output,out,mul,'A');assert L.connect_material_expressions(tint,'',mul,'B');output=mul;out=''
        assert L.connect_material_property(output,out,pin),name+' '+str(pin)
    if world:mat.set_editor_property('tangent_space_normal',False)
    if cloth:
        rough=node(u.MaterialExpressionConstant,0,600);rough.set_editor_property('r',.93);L.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
    L.recompile_material(mat);u.EditorAssetLibrary.save_loaded_asset(mat);return mat

mats={}
for name,asset in [('Stone','white_sandstone_blocks_02'),('Paving','cobblestone_floor_08'),('Roof','roof_slates_02')]:
    maps=[]
    for suffix,kind,pin in [('diff','color',u.MaterialProperty.MP_BASE_COLOR),('nor_dx','normal',u.MaterialProperty.MP_NORMAL),('rough','mask',u.MaterialProperty.MP_ROUGHNESS)]:
        tex=texture(SRC/asset/(suffix+'.jpg'),'T_'+name+'_'+suffix,kind);maps.append((pin,tex,kind,'RGB' if kind!='mask' else 'R'))
    mats[name]=material('M_Citadel'+name,maps,True)

maps=[]
for suffix,kind,pin in [('color','color',u.MaterialProperty.MP_BASE_COLOR),('nmap','normal',u.MaterialProperty.MP_NORMAL),('metalness','mask',u.MaterialProperty.MP_METALLIC),('rough','mask',u.MaterialProperty.MP_ROUGHNESS)]:
    tex=texture(SRC/'knight'/('armor_default_'+suffix+'.png'),'T_Knight_'+suffix,kind)
    # Source is OpenGL; Unreal consumes DirectX tangent normals.
    if kind=='normal':tex.set_editor_property('flip_green_channel',True);u.EditorAssetLibrary.save_loaded_asset(tex)
    maps.append((pin,tex,kind,'RGB' if kind!='mask' else 'R'))
mats['Knight']=material('M_CitadelKnight',maps)
diff=texture(SRC/'antique_estoc/textures/antique_estoc_diff_2k.jpg','T_Estoc_Color')
norm=texture(SRC/'antique_estoc/textures/antique_estoc_nor_gl_2k.jpg','T_Estoc_Normal','normal');norm.set_editor_property('flip_green_channel',True);u.EditorAssetLibrary.save_loaded_asset(norm)
arm=texture(SRC/'antique_estoc/textures/antique_estoc_arm_2k.jpg','T_Estoc_ARM','mask')
mats['Sword']=material('M_CitadelSword',[(u.MaterialProperty.MP_BASE_COLOR,diff,'color','RGB'),(u.MaterialProperty.MP_NORMAL,norm,'normal','RGB'),(u.MaterialProperty.MP_AMBIENT_OCCLUSION,arm,'mask','R'),(u.MaterialProperty.MP_ROUGHNESS,arm,'mask','G'),(u.MaterialProperty.MP_METALLIC,arm,'mask','B')])

for file in sorted((SRC/'Export').glob('*.fbx')):
    if file.stem=='SM_EstocSource':continue
    skeletal=file.stem.startswith('SK_');opts=u.FbxImportUI()
    opts.automated_import_should_detect_type=False;opts.import_mesh=True;opts.import_animations=False
    opts.import_as_skeletal=skeletal;opts.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH if skeletal else u.FBXImportType.FBXIT_STATIC_MESH
    opts.import_materials=False;opts.import_textures=False;opts.create_physics_asset=False
    if not skeletal:opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.auto_generate_collision=False
    task=u.AssetImportTask();task.filename=str(file);task.destination_path=DEST+'/Meshes';task.destination_name=file.stem
    task.options=opts;task.automated=True;task.replace_existing=True;task.save=True;A.import_asset_tasks([task])
    mesh=u.load_asset(DEST+'/Meshes/'+file.stem)
    if not mesh:raise RuntimeError('Mesh import failed: '+file.name)
    mat=mats['Knight' if skeletal else 'Sword' if 'Sword' in file.stem else 'Roof' if 'Roof' in file.stem else 'Stone']
    if skeletal:
        if u.EditorAssetLibrary.does_asset_exist(DEST+'/Meshes/SKEL_Citadel'):u.load_asset(DEST+'/Meshes/SKEL_Citadel')
        skeleton=u.CitadelAssetTools.ensure_skeleton(mesh)
        if not skeleton:raise RuntimeError('Skeleton creation failed')
        u.EditorAssetLibrary.save_loaded_asset(skeleton)
        # The native build bridge calls SetMaterials, updating UE 5.8's
        # serialized material cache rather than its transient reflected field.
        if not mesh.get_editor_property('materials'):raise RuntimeError('Missing material slots: '+file.stem)
    else:mesh.set_material(0,mat)
    u.EditorAssetLibrary.save_loaded_asset(mesh)
    u.log('CITADEL IMPORTED '+file.stem)
u.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=False,recursive=True)
u.log('CITADEL ASSET IMPORT COMPLETE')
