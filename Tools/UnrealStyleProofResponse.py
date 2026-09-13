"""Isolated Unlit response diagnostic; not a production lighting model."""
import unreal as u

CODE='''float3 N = normalize(NWorld);
float3 L = normalize(KeyDirection);
float3 V = normalize(ViewDirection);
float d = dot(N,L);
float3 low = float3(0.30,0.38,0.48);
float3 mid = float3(0.90,0.83,0.70);
float3 high = float3(1.50,1.48,1.40);
float3 ramp = lerp(low,mid,smoothstep(0.40,0.60,d));
ramp = lerp(ramp,high,smoothstep(0.60,0.95,d));
float3 H = normalize(L+V);
float spec = 0.06*pow(saturate(dot(N,H)),32.0)*smoothstep(0.0,0.2,d);
return float3(0.29,0.285,0.275)*ramp + float3(1.0,0.95,0.85)*spec;'''

def build_response(destination,import_receipt):
    lib=u.MaterialEditingLibrary;assets=u.AssetToolsHelpers.get_asset_tools();folder=destination+'/Materials/ResponseDiagnostic'
    u.EditorAssetLibrary.make_directory(folder)
    path=folder+'/M_ResponseDiagnostic_v001'
    material=u.load_asset(path) or assets.create_asset('M_ResponseDiagnostic_v001',folder,u.Material,u.MaterialFactoryNew())
    lib.delete_all_material_expressions(material)
    material.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
    material.set_editor_property('two_sided',False)
    def node(cls,x,y):return lib.create_material_expression(material,cls,x,y)
    def link(source,output,target,input_name):assert lib.connect_material_expressions(source,output,target,input_name),(type(source).__name__,input_name)
    sample=node(u.MaterialExpressionTextureSample,-1000,0);sample.set_editor_property('texture',u.load_asset(destination+'/Textures/T_Helmet_Normal'));sample.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    flat=node(u.MaterialExpressionConstant3Vector,-1000,200);flat.set_editor_property('constant',u.LinearColor(0,0,1,1))
    strength=node(u.MaterialExpressionScalarParameter,-1000,400);strength.set_editor_property('parameter_name','NormalStrength');strength.set_editor_property('default_value',1)
    blend=node(u.MaterialExpressionLinearInterpolate,-750,0)
    for src,out,pin in [(flat,'','A'),(sample,'RGB','B'),(strength,'','Alpha')]:link(src,out,blend,pin)
    norm=node(u.MaterialExpressionNormalize,-550,0);link(blend,'',norm,'VectorInput')
    transform=node(u.MaterialExpressionTransform,-350,0)
    assert 'TANGENT' in str(transform.get_editor_property('transform_source_type')).upper()
    assert 'WORLD' in str(transform.get_editor_property('transform_type')).upper()
    # UE exposes a display pin name that differs from the UPROPERTY; empty selects input0.
    link(norm,'',transform,'')
    view=node(u.MaterialExpressionCameraVectorWS,-350,200)
    key=node(u.MaterialExpressionVectorParameter,-350,400);key.set_editor_property('parameter_name','KeyDirection');key.set_editor_property('default_value',u.LinearColor(-.54167522,.54167522,.64278761,0))
    custom=node(u.MaterialExpressionCustom,0,0);custom.set_editor_property('code',CODE);custom.set_editor_property('description','DIAGNOSTIC ONLY: continuous key response, no scene shadows/reflections')
    enum_name=next(k for k in dir(u.CustomMaterialOutputType) if k.replace('_','').upper()=='CMOTFLOAT3')
    custom.set_editor_property('output_type',getattr(u.CustomMaterialOutputType,enum_name))
    inputs=[]
    for name in ['NWorld','KeyDirection','ViewDirection']:
        entry=u.CustomInput();entry.set_editor_property('input_name',name);inputs.append(entry)
    custom.set_editor_property('inputs',inputs)
    pin_names=lib.get_material_expression_input_names(custom)
    assert len(pin_names)==3,list(pin_names)
    for (source,out),pin in zip([(transform,''),(key,'RGB'),(view,'')],pin_names):link(source,out,custom,pin)
    assert lib.connect_material_property(custom,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
    assert lib.get_material_property_input_node(material,u.MaterialProperty.MP_EMISSIVE_COLOR)==custom
    lib.recompile_material(material);u.EditorAssetLibrary.save_loaded_asset(material)
    variants={}
    for name,value in [('response_control',0.0),('response_normals',1.0)]:
        instance_path=folder+'/MI_'+name
        instance=u.load_asset(instance_path) or assets.create_asset('MI_'+name,folder,u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
        lib.set_material_instance_parent(instance,material);lib.set_material_instance_scalar_parameter_value(instance,'NormalStrength',value);lib.update_material_instance(instance)
        assert abs(lib.get_material_instance_scalar_parameter_value(instance,'NormalStrength')-value)<1e-6
        u.EditorAssetLibrary.save_loaded_asset(instance)
        variants[name]=[instance.get_path_name(),instance.get_path_name()]+import_receipt['variants']['control'][2:]
    definition={'diagnostic_only':True,'shading_model':str(material.get_editor_property('shading_model')),'material':material.get_path_name(),'normal_pipeline':'Normal sampler decodes existing DX tangent map; normalize(lerp((0,0,1),decodedNormal,NormalStrength)); Transform(Tangent,World); normalize. Strength0 transforms flat tangent normal through the actual mesh TBN, recovering mesh normal. PixelNormalWS is not used.','transform_source':str(transform.get_editor_property('transform_source_type')),'transform_destination':str(transform.get_editor_property('transform_type')),'hlsl':CODE,'ramp_ndotl_anchors':[.40,.60,.95],'uniform_steel_tint':[.29,.285,.275],'key_direction_contract':'Surface-to-light world vector = negative actual directional light actor forward, supplied every capture through dynamic instances.','fit_evidence':'response_normal_ranges.json: source BVH-visible projected active cheek quartiles .458/.507/.539, roof median .842; mean active authored delta .027.','limitations':['No automatic scene shadows or environment reflections on diagnostic steel.','Padding/interior keep source standard-lit materials.','Manual exposure and camera remain unchanged.','Not production accepted.'],'variants':variants}
    return variants,definition

def supply_actual_key(helmet,key,paths):
    forward=key.get_actor_forward_vector();direction=u.LinearColor(-forward.x,-forward.y,-forward.z,0)
    actual=[]
    for i in range(2):
        instance=helmet.static_mesh_component.create_dynamic_material_instance(i)
        instance.set_vector_parameter_value('KeyDirection',direction)
        value=instance.get_vector_parameter_value('KeyDirection')
        assert max(abs(a-b) for a,b in zip((value.r,value.g,value.b),(direction.r,direction.g,direction.b)))<1e-6
        actual.append(instance.get_scalar_parameter_value('NormalStrength'))
    return {'surface_to_light_world':[direction.r,direction.g,direction.b],'actual_steel_normal_strengths':actual,'material_assets':paths[:2]}
