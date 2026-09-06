"""Shared two-sided wind cloth and pooled emissive impact material."""
import unreal as u
L=u.MaterialEditingLibrary;A=u.AssetToolsHelpers.get_asset_tools();DEST='/Game/Visual/Citadel/Materials'
def mat(name):
    path=DEST+'/'+name
    m=u.load_asset(path) if u.EditorAssetLibrary.does_asset_exist(path) else A.create_asset(name,DEST,u.Material,u.MaterialFactoryNew())
    L.delete_all_material_expressions(m);m.set_editor_property('used_with_instanced_static_meshes',True);return m
def node(m,cls,**props):
    n=L.create_material_expression(m,cls,0,0)
    for k,v in props.items():n.set_editor_property(k,v)
    return n
def connect(a,b,pin='A',out=''):assert L.connect_material_expressions(a,out,b,pin)
def scalar(m,v):return node(m,u.MaterialExpressionConstant,r=v)

m=mat('M_CitadelCloth');m.set_editor_property('two_sided',True)
tint=node(m,u.MaterialExpressionVectorParameter,parameter_name='BaseColor',default_value=u.LinearColor(.2,.02,.015,1))
uv=node(m,u.MaterialExpressionTextureCoordinate)
mask=node(m,u.MaterialExpressionComponentMask,r=False,g=True,b=False,a=False);connect(uv,mask,'')
time=node(m,u.MaterialExpressionTime)
rate=node(m,u.MaterialExpressionMultiply);connect(time,rate);connect(scalar(m,1.3),rate,'B')
phase=node(m,u.MaterialExpressionMultiply);connect(mask,phase);connect(scalar(m,2.1),phase,'B')
add=node(m,u.MaterialExpressionAdd);connect(rate,add);connect(phase,add,'B')
sine=node(m,u.MaterialExpressionSine);connect(add,sine,'')
amount=node(m,u.MaterialExpressionMultiply);connect(sine,amount);connect(mask,amount,'B')
amplitude=node(m,u.MaterialExpressionMultiply);connect(amount,amplitude);connect(scalar(m,3.5),amplitude,'B')
normal=node(m,u.MaterialExpressionVertexNormalWS)
offset=node(m,u.MaterialExpressionMultiply);connect(normal,offset);connect(amplitude,offset,'B')
L.connect_material_property(offset,'',u.MaterialProperty.MP_WORLD_POSITION_OFFSET)
# Heraldic stitched cross and border, evaluated in the explicitly authored UVs.
uv_input=u.CustomInput();uv_input.set_editor_property('input_name','UV')
crest=node(m,u.MaterialExpressionCustom,code='float2 p=UV-float2(.5,.36); float cross=max(step(abs(p.x),.045)*step(abs(p.y),.18),step(abs(p.x),.18)*step(abs(p.y),.04)); float border=step(UV.x,.025)+step(.975,UV.x); return saturate(cross+border);',output_type=u.CustomMaterialOutputType.CMOT_FLOAT1,inputs=[uv_input])
connect(uv,crest,'UV')
gold=node(m,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(.64,.42,.13,1))
color=node(m,u.MaterialExpressionLinearInterpolate);connect(tint,color);connect(gold,color,'B');connect(crest,color,'Alpha')
L.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
L.connect_material_property(scalar(m,.93),'',u.MaterialProperty.MP_ROUGHNESS)
L.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)

m=mat('M_CitadelSparks');m.set_editor_property('blend_mode',u.BlendMode.BLEND_ADDITIVE);m.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
channels=[node(m,u.MaterialExpressionPerInstanceCustomData,data_index=i) for i in range(4)]
rg=node(m,u.MaterialExpressionAppendVector);connect(channels[0],rg);connect(channels[1],rg,'B')
rgb=node(m,u.MaterialExpressionAppendVector);connect(rg,rgb);connect(channels[2],rgb,'B')
bright=node(m,u.MaterialExpressionMultiply);connect(rgb,bright);connect(scalar(m,9.),bright,'B')
L.connect_material_property(bright,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
L.connect_material_property(channels[3],'',u.MaterialProperty.MP_OPACITY)
L.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
u.log('CITADEL EFFECT MATERIALS COMPLETE')
