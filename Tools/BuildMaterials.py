"""Run with UnrealEditor-Cmd -run=pythonscript -script=... to regenerate shared assets."""
import unreal as u
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve()
assets=u.AssetToolsHelpers.get_asset_tools();lib=u.MaterialEditingLibrary
for folder in ['/Game/Visual/Textures','/Game/Visual/Materials']:u.EditorAssetLibrary.make_directory(folder)
for name in ['T_SurfaceNoise','T_SurfaceNormal']:
 task=u.AssetImportTask();task.filename=str(root/'ArtSource/Textures'/f'{name}.png');task.destination_path='/Game/Visual/Textures';task.automated=True;task.replace_existing=True;task.save=True;assets.import_asset_tasks([task])
 tex=u.load_asset('/Game/Visual/Textures/'+name);tex.set_editor_property('srgb',False)
 tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP if 'Normal' in name else u.TextureCompressionSettings.TC_MASKS)
 u.EditorAssetLibrary.save_loaded_asset(tex)
noise=u.load_asset('/Game/Visual/Textures/T_SurfaceNoise');normal=u.load_asset('/Game/Visual/Textures/T_SurfaceNormal')
def master(name,water=False):
 path='/Game/Visual/Materials/'+name
 m=u.load_asset(path) if u.EditorAssetLibrary.does_asset_exist(path) else assets.create_asset(name,'/Game/Visual/Materials',u.Material,u.MaterialFactoryNew())
 lib.delete_all_material_expressions(m)
 def node(cls,x=0,y=0):return lib.create_material_expression(m,cls,x,y)
 def scalar(name,value,y):
  n=node(u.MaterialExpressionScalarParameter,-600,y);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',value);return n
 def vector(name,value,y):
  n=node(u.MaterialExpressionVectorParameter,-600,y);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',u.LinearColor(*value));return n
 def link(a,b,pin='A',out=''):lib.connect_material_expressions(a,out,b,pin)
 color=vector('BaseColor',(.5,.5,.5,1),-500);tint=vector('Tint',(1,1,1,1),-400)
 rough=scalar('Roughness',.7,-300);metal=scalar('Metallic',0,-200);dirt=scalar('DirtAmount',.12,0);edge=scalar('EdgeWear',.03,100);scale=scalar('TextureScale',2,200);strength=scalar('NormalIntensity',.3,300)
 uv=node(u.MaterialExpressionTextureCoordinate,-800,500);mul=node(u.MaterialExpressionMultiply,-400,500);link(uv,mul);link(scale,mul,'B');coords=mul
 if water:
  pan=node(u.MaterialExpressionPanner,-200,500);pan.set_editor_property('speed_x',.025);pan.set_editor_property('speed_y',.017);link(mul,pan,'Coordinate');coords=pan
 n=node(u.MaterialExpressionTextureSampleParameter2D,0,500);n.set_editor_property('parameter_name','SurfaceNoise');n.set_editor_property('texture',noise);n.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_MASKS);link(coords,n,'Coordinates')
 d=node(u.MaterialExpressionMultiply,200,300);link(n,d,out='R');link(dirt,d,'B');one=node(u.MaterialExpressionOneMinus,350,300);link(d,one,'Input')
 ct=node(u.MaterialExpressionMultiply,-100,-500);link(color,ct);link(tint,ct,'B');shade=node(u.MaterialExpressionMultiply,500,-300);link(ct,shade);link(one,shade,'B')
 fres=node(u.MaterialExpressionFresnel,200,-100);em=node(u.MaterialExpressionMultiply,400,-100);link(fres,em);link(edge,em,'B');final=node(u.MaterialExpressionAdd,650,-200);link(shade,final);link(em,final,'B');lib.connect_material_property(final,'',u.MaterialProperty.MP_BASE_COLOR)
 lib.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS);lib.connect_material_property(metal,'',u.MaterialProperty.MP_METALLIC)
 norm=node(u.MaterialExpressionTextureSampleParameter2D,0,800);norm.set_editor_property('parameter_name','SurfaceNormal');norm.set_editor_property('texture',normal);norm.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL);link(coords,norm,'Coordinates')
 flat=vector('FlatNormal',(0,0,1,1),900);lerp=node(u.MaterialExpressionLinearInterpolate,400,700);link(flat,lerp);link(norm,lerp,'B');link(strength,lerp,'Alpha');lib.connect_material_property(lerp,'',u.MaterialProperty.MP_NORMAL)
 lib.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m);return m
solid=master('M_Surface');water=master('M_WaterSurface',True)
settings={'Stone':(.85,0,.15,.04,3,.45),'Paving':(.9,0,.18,.02,1,.55),'Steel':(.38,.85,.13,.04,3,.18),'Iron':(.65,.7,.18,.015,3,.22),'Leather':(.82,0,.18,.02,3,.45),'Wood':(.8,0,.15,.02,2,.45),'Cloth':(.95,0,.1,.01,5,.45),'Water':(.25,.15,.05,.02,3,.65)}
for name,values in settings.items():
 path='/Game/Visual/Materials/M_'+name
 mi=u.load_asset(path) if u.EditorAssetLibrary.does_asset_exist(path) else assets.create_asset('M_'+name,'/Game/Visual/Materials',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
 lib.set_material_instance_parent(mi,water if name=='Water' else solid)
 for key,value in zip(['Roughness','Metallic','DirtAmount','EdgeWear','TextureScale','NormalIntensity'],values):lib.set_material_instance_scalar_parameter_value(mi,key,value)
 u.EditorAssetLibrary.save_loaded_asset(mi)
u.log('TOURNAMENT MATERIAL LIBRARY COMPLETE')
