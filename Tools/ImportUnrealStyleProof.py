"""Revision-scoped UE5.8 material/import/stage builder. Execute in full Unreal Editor."""
from pathlib import Path
import json, math, hashlib, re,sys,traceback,gzip,subprocess,shutil
import unreal as u
ROOT=Path(u.Paths.project_dir()).resolve()
sys.path.insert(0,str(ROOT/'Tools'))
from UnrealStyleTransferContract import load_manifest
CMD=u.SystemLibrary.get_command_line()
match=re.search(r'(?:^|\s)-StyleProofRevision=(\S+)',CMD)
REV=match.group(1) if match else 'USP_v001'
assert re.fullmatch(r'USP_v[0-9]{3}',REV),'Invalid style proof revision'
match=re.search(r'(?:^|\s)-StyleProofEnvironmentRevision=(\S+)',CMD);ENV_REV=match.group(1) if match else 'Environment_v001'
assert re.fullmatch(r'Environment_v[0-9]{3}',ENV_REV),'Invalid environment revision'
match=re.search(r'(?:^|\s)-StyleProofCaptureSet=(\S+)',CMD);CAPTURE_SET=match.group(1) if match else 'default'
assert CAPTURE_SET in ['default','environment_compare','environment_step','environment_response','orientation_camera','maps_environment','material_compare','native','stage','geometry','amplitude','worldnormal','response','transfer'],'Invalid capture set'
SRC=ROOT/'ArtSource/StyleReference/MEL17/UnrealProof'/REV
DEST='/Game/Visual/StyleProof/'+REV
OUT=ROOT/'Saved/ArtReview/UnrealStyle'/REV
A=u.AssetToolsHelpers.get_asset_tools(); L=u.MaterialEditingLibrary
E=u.get_editor_subsystem(u.EditorActorSubsystem)
LEVEL=u.get_editor_subsystem(u.LevelEditorSubsystem)

def asset(name,sub,cls,factory):
    return u.load_asset(DEST+'/'+sub+'/'+name) or A.create_asset(name,DEST+'/'+sub,cls,factory)

def texture(path,name,normal=False):
    t=u.AssetImportTask(); t.filename=str(path);t.destination_path=DEST+'/Textures';t.destination_name=name
    t.automated=True;t.replace_existing=True;t.save=True;A.import_asset_tasks([t])
    tex=u.load_asset(DEST+'/Textures/'+name)
    assert tex,path
    tex.set_editor_property('srgb',False)
    tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP if normal else u.TextureCompressionSettings.TC_MASKS)
    tex.set_editor_property('flip_green_channel',False)
    assert tex.get_editor_property('srgb') is False
    assert tex.get_editor_property('compression_settings')==(u.TextureCompressionSettings.TC_NORMALMAP if normal else u.TextureCompressionSettings.TC_MASKS)
    assert tex.get_editor_property('flip_green_channel') is False
    u.EditorAssetLibrary.save_loaded_asset(tex)
    return tex

def master(normal,masks,normal_base=None):
    m=asset('M_SteelAuthored','Materials',u.Material,u.MaterialFactoryNew()); L.delete_all_material_expressions(m)
    m.set_editor_property('two_sided',False);m.set_editor_property('tangent_space_normal',True)
    m.set_editor_property('blend_mode',u.BlendMode.BLEND_OPAQUE)
    m.set_editor_property('shading_model',u.MaterialShadingModel.MSM_DEFAULT_LIT)
    assert m.get_editor_property('blend_mode')==u.BlendMode.BLEND_OPAQUE
    assert m.get_editor_property('shading_model')==u.MaterialShadingModel.MSM_DEFAULT_LIT
    def node(cls,x,y):return L.create_material_expression(m,cls,x,y)
    def scalar(name,value,y):
        n=node(u.MaterialExpressionScalarParameter,-700,y);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',value);return n
    tint=node(u.MaterialExpressionVectorParameter,-500,-600);tint.set_editor_property('parameter_name','BaseColor');tint.set_editor_property('default_value',u.LinearColor(.38,.40,.42,1))
    L.connect_material_property(tint,'RGB',u.MaterialProperty.MP_BASE_COLOR)
    metal=scalar('Metallic',1,-440);L.connect_material_property(metal,'',u.MaterialProperty.MP_METALLIC)
    rough=scalar('Roughness',.30,-280);strength=scalar('RoughnessVariation',0,-120)
    sample=node(u.MaterialExpressionTextureSample,-900,100);sample.set_editor_property('texture',masks);sample.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_MASKS)
    mix=node(u.MaterialExpressionLinearInterpolate,-150,-130)
    for src,pin,dst in [(rough,'','A'),(sample,'R','B'),(strength,'','Alpha')]:assert L.connect_material_expressions(src,pin,mix,dst)
    L.connect_material_property(mix,'',u.MaterialProperty.MP_ROUGHNESS)
    norm=node(u.MaterialExpressionTextureSample,-900,400);norm.set_editor_property('texture',normal);norm.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    flat=node(u.MaterialExpressionConstant3Vector,-700,650);flat.set_editor_property('constant',u.LinearColor(0,0,1,1))
    power=scalar('NormalStrength',0,850);blend=node(u.MaterialExpressionLinearInterpolate,-200,480)
    foundation=flat
    if normal_base:
        base=node(u.MaterialExpressionTextureSample,-900,680);base.set_editor_property('texture',normal_base);base.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        foundation=node(u.MaterialExpressionLinearInterpolate,-430,680)
        enable=scalar('UseConstructionFoundation',0,1080)
        for src,pin,dst in [(flat,'','A'),(base,'RGB','B'),(enable,'','Alpha')]:assert L.connect_material_expressions(src,pin,foundation,dst)
    for src,pin,dst in [(foundation,'','A'),(norm,'RGB','B'),(power,'','Alpha')]:assert L.connect_material_expressions(src,pin,blend,dst)
    normalize=node(u.MaterialExpressionNormalize,0,480);assert L.connect_material_expressions(blend,'',normalize,'VectorInput'),'Normal blend connection failed';assert L.connect_material_property(normalize,'',u.MaterialProperty.MP_NORMAL),'Normal output connection failed'
    assert L.get_material_property_input_node(m,u.MaterialProperty.MP_NORMAL)==normalize,'Normal input not bound to Normalize'
    L.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m);return m

def instance(name,parent,color,metal,rough,normal=0,variation=0,foundation=0):
    m=asset(name,'Materials',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
    L.set_material_instance_parent(m,parent)
    L.set_material_instance_vector_parameter_value(m,'BaseColor',u.LinearColor(*color[:3],1))
    for key,value in [('Metallic',metal),('Roughness',rough),('NormalStrength',normal),('RoughnessVariation',variation)]:L.set_material_instance_scalar_parameter_value(m,key,value)
    L.set_material_instance_scalar_parameter_value(m,'UseConstructionFoundation',foundation)
    L.update_material_instance(m)
    assert abs(L.get_material_instance_scalar_parameter_value(m,'NormalStrength')-normal)<1e-6,'NormalStrength override mismatch'
    assert abs(L.get_material_instance_scalar_parameter_value(m,'UseConstructionFoundation')-foundation)<1e-6,'Construction foundation override mismatch'
    u.EditorAssetLibrary.save_loaded_asset(m);return m

def actor(cls,name,location=(0,0,0),rotation=(0,0,0)):
    a=E.spawn_actor_from_class(cls,u.Vector(*location),u.Rotator(pitch=rotation[0],yaw=rotation[1],roll=rotation[2]));a.set_actor_label(name);a.tags=[name];return a

def install_review_game_mode(world,camera):
    factory=u.BlueprintFactory();factory.set_editor_property('parent_class',u.GameModeBase)
    blueprint=asset('BP_StyleProofGameMode','Blueprints',u.Blueprint,factory)
    assert u.BlueprintEditorLibrary.compile_blueprint(blueprint),'GameMode blueprint compile failed'
    generated=u.BlueprintEditorLibrary.generated_class(blueprint)
    assert generated.get_path_name().startswith(DEST+'/Blueprints/'),'Refusing native/global class edits'
    defaults=u.get_default_object(generated);defaults.set_editor_property('default_pawn_class',None)
    assert defaults.get_editor_property('default_pawn_class') is None
    u.EditorAssetLibrary.save_loaded_asset(blueprint,only_if_is_dirty=False)
    world.get_world_settings().set_editor_property('default_game_mode',generated)
    enum_name=next(name for name in dir(u.AutoReceiveInput) if name.replace('_','')=='PLAYER0')
    camera.set_editor_property('auto_activate_for_player',getattr(u.AutoReceiveInput,enum_name))
    assert camera.get_auto_activate_player_index()==0
    return generated.get_path_name()


def fit_transfer_cameras(manifest):
    """Fit the new bounds in perspective, retaining the source view direction."""
    lo,hi=manifest['assembly']['bounds_blender_cm']
    center=[(lo[0]+hi[0])/2,-(lo[1]+hi[1])/2,(lo[2]+hi[2])/2]
    corners=[[x,-y,z] for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]
    matrix=manifest['review']['source_camera']['matrix_world']
    source_direction=[matrix[0][2],-matrix[1][2],matrix[2][2]]
    def unit(v):
        length=math.sqrt(sum(x*x for x in v));assert length>1e-8
        return [x/length for x in v]
    def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    def dot(a,b):return sum(x*y for x,y in zip(a,b))
    cameras={}
    for view,direction,fraction in [('front',[0,1,.06],.78),('matched',source_direction,.78),('threequarter',source_direction,.78),('gameplay',source_direction,.22)]:
        direction=unit(direction);right=unit(cross([0,0,1],direction));up=unit(cross(direction,right))
        distance=0
        for corner in corners:
            delta=[a-b for a,b in zip(corner,center)]
            distance=max(distance,dot(delta,direction)+max(abs(dot(delta,right)),abs(dot(delta,up)))/(math.tan(math.radians(15))*fraction))
        cameras[view]={'location_cm':[c+d*distance for c,d in zip(center,direction)],'target_cm':center,'horizontal_fov_deg':30,'projection':'perspective','bounds_fit_fraction':fraction,'source_view_direction_blender':[matrix[i][2] for i in range(3)],'note':'New bounds fitted at fixed 30-degree FOV; gameplay is a declared proof screen-size scenario, human gameplay-distance acceptance pending.'}
    return cameras

def run():
    package=load_manifest(SRC/'manifest.json',ROOT,expected_revision=REV,allow_legacy=True)
    manifest=package.manifest;transfer=package.schema_version==2
    if CAPTURE_SET=='transfer':assert transfer,'transfer requires schema v2'
    if transfer:
        assert 'render_contract' in package.files,'Missing actual imported geometry/UV/tangent verification contract'
        assert not (OUT/'import_receipt.json').exists(),'Immutable imported revision exists; use a fresh revision'
        if u.EditorAssetLibrary.does_asset_exist(DEST+'/Meshes/SM_Helmet'):
            assert (OUT/'import_started.json').exists(),'Refusing to overwrite an unowned existing asset'
            assert json.loads((OUT/'import_started.json').read_text())['manifest_sha256']==package.manifest_sha256,'Partial import belongs to another source identity'
    OUT.mkdir(parents=True,exist_ok=True)
    if transfer:(OUT/'import_started.json').write_text(json.dumps({'manifest_sha256':package.manifest_sha256,'revision':REV},indent=2))
    for folder in ('Meshes','Materials','Textures','Blueprints'):u.EditorAssetLibrary.make_directory(DEST+'/'+folder)
    n=texture(package.files['normal_final' if transfer else 'normal'],'T_Helmet_Normal',True)
    n0=texture(package.files['normal_base'],'T_Helmet_NormalBase',True) if transfer else None
    masks=texture(package.files['masks'],'T_Helmet_Masks')
    m=master(n,masks,n0)
    u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
    opts=u.FbxImportUI();opts.automated_import_should_detect_type=False;opts.import_mesh=True;opts.import_as_skeletal=False;opts.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH
    opts.import_materials=False;opts.import_textures=False;opts.import_animations=False
    data=opts.static_mesh_import_data;data.combine_meshes=True;data.auto_generate_collision=False
    if transfer:
        data.set_editor_property('remove_degenerates',False)
        data.set_editor_property('generate_lightmap_u_vs',False)
        data.set_editor_property('build_nanite',False)
    data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
    data.convert_scene=True;data.force_front_x_axis=False;data.convert_scene_unit=True
    reuse_mesh=transfer and u.EditorAssetLibrary.does_asset_exist(DEST+'/Meshes/SM_Helmet')
    if not reuse_mesh:
        t=u.AssetImportTask();t.filename=str(package.files['fbx']);t.destination_path=DEST+'/Meshes';t.destination_name='SM_Helmet';t.options=opts;t.automated=True;t.replace_existing=True;t.save=True;A.import_asset_tasks([t])
    mesh=u.load_asset(DEST+'/Meshes/SM_Helmet');assert mesh,'mesh missing'
    slots=manifest['material_slots']; by_name={s['name']:s for s in slots}
    variants={key:[] for key in ('control','normals','combined','matte')};actual=[]
    for i,slot in enumerate(mesh.static_materials):
        name=str(slot.material_slot_name); source=by_name.get(name)
        if source is None:source=next((s for s in slots if s['name'].replace(' ','_')==name),None)
        assert source,('unmapped material slot',name,list(by_name))
        actual.append(name)
        steel=source['kind']=='steel' if transfer else source['metallic']>.5
        for variant in variants:
            mat=instance('MI_Helmet_'+variant+'_'+str(i),m,([.3,.3,.3] if steel and variant=='matte' else source['base_color_linear']),(0 if variant=='matte' else source['metallic']),(1 if variant=='matte' else source['roughness']),int(steel and variant in ('normals','combined')),int(steel and variant=='combined'),int(transfer))
            variants[variant].append(mat.get_path_name())
            if variant=='control':mesh.set_material(i,mat)
    assert len(actual)==len(slots) and {n.replace(' ','_') for n in actual}=={s['name'].replace(' ','_') for s in slots},'Imported material slot set mismatch'
    mesh_settings={};landmark_checks={};capture_cameras={}
    if transfer:
        sm=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
        build=sm.get_lod_build_settings(mesh,0)
        build.set_editor_property('recompute_normals',False);build.set_editor_property('recompute_tangents',False)
        build.set_editor_property('use_full_precision_u_vs',True)
        build.set_editor_property('use_high_precision_tangent_basis',True)
        build.set_editor_property('generate_lightmap_u_vs',False);build.set_editor_property('remove_degenerates',False)
        sm.set_lod_build_settings(mesh,0,build)
        build=sm.get_lod_build_settings(mesh,0)
        for key in ['recompute_normals','recompute_tangents','generate_lightmap_u_vs','remove_degenerates']:
            mesh_settings[key]=build.get_editor_property(key);assert mesh_settings[key] is False
        mesh_settings['use_full_precision_u_vs']=build.get_editor_property('use_full_precision_u_vs');assert mesh_settings['use_full_precision_u_vs'] is True
        mesh_settings['use_high_precision_tangent_basis']=build.get_editor_property('use_high_precision_tangent_basis');assert mesh_settings['use_high_precision_tangent_basis'] is True
        nanite=sm.get_nanite_settings(mesh);nanite.set_editor_property('enabled',False);sm.set_nanite_settings(mesh,nanite,True)
        assert not sm.get_nanite_settings(mesh).get_editor_property('enabled')
        sm.remove_collisions(mesh)
        assert sm.get_simple_collision_count(mesh)==0
        mesh_settings.update(nanite=False,simple_collision_count=0)
        mesh.set_editor_property('allow_cpu_access',True)
        # Export render buffers, not source MeshDescription. UE 5.8's procedural
        # mesh Python helper reads sign from TangentX.W; the stored sign is Z.W.
        index=1
        while (OUT/f'imported_render_{index:03d}.fbx').exists():index+=1
        render_fbx=OUT/f'imported_render_{index:03d}.fbx'
        render_json=OUT/f'imported_render_{index:03d}.json.gz'
        export_options=u.FbxExportOption()
        for key,value in [('export_source_mesh',False),('level_of_detail',False),('collision',False),('ascii',False),('force_front_x_axis',False)]:export_options.set_editor_property(key,value)
        export_task=u.AssetExportTask();export_task.object=mesh;export_task.exporter=u.StaticMeshExporterFBX()
        export_task.options=export_options;export_task.automated=True;export_task.prompt=False;export_task.filename=str(render_fbx)
        assert u.Exporter.run_asset_export_task(export_task),'Built render FBX export failed'
        python=shutil.which('python')
        assert python,'External Python 3.11 runtime unavailable'
        parsed=subprocess.run([python,str(ROOT/'Tools/ReadUnrealRenderFBX.py'),'--fbx',str(render_fbx),'--output',str(render_json)],capture_output=True,text=True,timeout=180)
        assert parsed.returncode==0,('Render FBX reader failed',parsed.stdout,parsed.stderr)
        with gzip.open(render_json,'rt',encoding='utf-8') as stream:render_data=json.load(stream)
        render_triangles=render_data['triangles']
        for triangle in render_triangles:
            material_name=render_data['material_slot_names'][triangle['slot']]
            material_match=re.fullmatch(r'MI_Helmet_control_(\d+)',material_name)
            assert material_match,('Unexpected exported render material',material_name)
            slot_name=str(mesh.static_materials[int(material_match.group(1))].material_slot_name)
            triangle['slot']=next(s['index'] for s in slots if s['name'].replace(' ','_')==slot_name.replace(' ','_'))
        vertices=[u.Vector(*corner[:3]) for triangle in render_triangles for corner in triangle['corners']]
        imported_triangles=len(render_triangles)
        assert imported_triangles==manifest['validation']['triangles'],('Imported triangle count mismatch',imported_triangles,manifest['validation']['triangles'])
        mesh_settings.update(triangles=imported_triangles,render_inspection='StaticMeshExporterFBX export_source_mesh=False; actual LOD0 buffers',render_fbx_sha256=hashlib.sha256(render_fbx.read_bytes()).hexdigest(),reused_partial_mesh=reuse_mesh)
        if 'render_contract' in package.files:
            from UnrealStyleTransferContract import verify_imported_triangles
            with gzip.open(package.files['render_contract'],'rt',encoding='utf-8') as stream:expected_render=json.load(stream)
            try:mesh_settings['render_contract']=verify_imported_triangles(expected_render,render_triangles)
            except Exception:
                index=1
                while (OUT/f'imported_render_failure_{index:03d}.json.gz').exists():index+=1
                with gzip.open(OUT/f'imported_render_failure_{index:03d}.json.gz','wt',encoding='utf-8') as stream:json.dump({'schema_version':1,'triangles':render_triangles},stream,separators=(',',':'))
                raise
        for name,landmark in manifest['assembly']['landmarks'].items():
            expected=landmark['unreal_cm']
            nearest=min(vertices,key=lambda v:sum((a-b)**2 for a,b in zip([v.x,v.y,v.z],expected)))
            actual_pos=[nearest.x,nearest.y,nearest.z]
            distance=math.sqrt(sum((a-b)**2 for a,b in zip(actual_pos,expected)))
            assert distance<.05,('Imported landmark mismatch',name,distance)
            landmark_checks[name]={'expected_cm':expected,'actual_cm':actual_pos,'error_cm':distance}
        capture_cameras=fit_transfer_cameras(manifest)
    u.EditorAssetLibrary.save_loaded_asset(mesh)
    assert LEVEL.new_level(DEST+'/L_HelmetStyleProof')
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    world.get_world_settings().set_editor_property('default_game_mode',u.GameModeBase)
    helmet=actor(u.StaticMeshActor,'ProofHelmet');helmet.static_mesh_component.set_static_mesh(mesh);helmet.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE)
    cam=actor(u.CameraActor,'ProofCamera',(-27,160,29))
    cam.set_actor_rotation(u.MathLibrary.find_look_at_rotation(cam.get_actor_location(),u.Vector(0,0,19)),False)
    game_mode_path=install_review_game_mode(world,cam)
    cam.camera_component.set_field_of_view(30);cam.camera_component.set_editor_property('constrain_aspect_ratio',True);cam.camera_component.set_editor_property('aspect_ratio',1.0)
    if transfer:
        fit=capture_cameras['matched'];cam.set_actor_location(u.Vector(*fit['location_cm']),False,False)
        cam.set_actor_rotation(u.MathLibrary.find_look_at_rotation(cam.get_actor_location(),u.Vector(*fit['target_cm'])),False)
        cam.camera_component.set_field_of_view(fit['horizontal_fov_deg'])
    u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(cam.get_actor_location(),cam.get_actor_rotation())
    LEVEL.set_level_viewport_fov(30,LEVEL.get_active_viewport_config_key())
    LEVEL.editor_set_game_view(True)
    pp=actor(u.PostProcessVolume,'ProofExposure');pp.set_editor_property('unbound',True)
    settings=pp.get_editor_property('settings')
    for key,value in [('auto_exposure_method',u.AutoExposureMethod.AEM_MANUAL),('auto_exposure_bias',0.0),('white_temp',6500.0),('motion_blur_amount',0.0),('depth_of_field_focal_distance',0.0),('bloom_intensity',0.0)]:
        settings.set_editor_property('override_'+key,True);settings.set_editor_property(key,value)
    settings.set_editor_property('override_auto_exposure_apply_physical_camera_exposure',True);settings.set_editor_property('auto_exposure_apply_physical_camera_exposure',False)
    pp.set_editor_property('settings',settings)
    key=actor(u.DirectionalLight,'ProofKey',(0,0,100),(-40,-45,0));key.light_component.set_mobility(u.ComponentMobility.MOVABLE);key.light_component.set_intensity(3.0);key.light_component.set_light_color(u.LinearColor(1,.86,.68,1))
    sky=actor(u.SkyLight,'ProofSky',(0,0,80));sky.light_component.set_mobility(u.ComponentMobility.MOVABLE);sky.light_component.set_intensity(1.0);sky.light_component.set_light_color(u.LinearColor(.65,.78,1,1))
    sky.light_component.set_editor_property('source_type',u.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
    cubemap=u.load_asset('/Engine/MapTemplates/Sky/DaylightAmbientCubemap.DaylightAmbientCubemap')
    assert cubemap,'engine daylight cubemap unavailable';sky.light_component.set_cubemap(cubemap)
    stage=instance('MI_StageWarm',m,[.24,.19,.13],0,.85)
    instance('MI_StageNeutral',m,[.2,.2,.2],0,.85)
    cube=u.load_asset('/Engine/BasicShapes/Cube.Cube')
    if transfer:
        occluder=actor(u.StaticMeshActor,'ProofShadeOccluder',(0,0,200))
        occluder.static_mesh_component.set_static_mesh(cube);occluder.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE)
        occluder.set_actor_scale3d(u.Vector(.8,.8,.02));occluder.static_mesh_component.set_material(0,stage)
        occluder.set_actor_hidden_in_game(True);occluder.set_actor_enable_collision(False)
    for name,loc,scale in [('ProofGround',(0,0,-4),(6,6,.08)),('ProofWall',(0,-100,70),(6,.1,1.5)),('ProofOpening',(60,-93,50),(.6,.04,.9))]:
        a=actor(u.StaticMeshActor,name,loc);a.static_mesh_component.set_static_mesh(cube);a.set_actor_scale3d(u.Vector(*scale));a.static_mesh_component.set_material(0,stage)
    dark=instance('MI_Opening',m,[.005,.007,.011],0,1)
    a.static_mesh_component.set_material(0,dark)
    assert LEVEL.save_current_level()
    u.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=True,recursive=True)
    b=helmet.get_actor_bounds(False)
    expected_height=manifest['assembly']['height_cm'] if transfer else manifest['height_cm']
    assert abs(2*b[1].z-expected_height)<.05,('Unexpected imported height_cm',2*b[1].z)
    receipt={'schema_version':package.schema_version,'revision':REV,'map':DEST+'/L_HelmetStyleProof','manifest':str(SRC/'manifest.json'),'variants':variants,'material_slots':actual,'source_hashes':{str(p.relative_to(SRC)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [SRC/'manifest.json',*package.files.values()]},'normal_import_method':'IMPORT_NORMALS_AND_TANGENTS','no_pawn_game_mode':game_mode_path,'camera_auto_activate_player':0,'normal_graph_verified':True,'instance_normal_strengths':{k:[L.get_material_instance_scalar_parameter_value(u.load_asset(p),'NormalStrength') for p in paths] for k,paths in variants.items()},'height_cm':2*b[1].z,'bounds':[[v.x,v.y,v.z] for v in b],'camera':capture_cameras.get('matched',{'location_cm':[-27,160,29],'target_cm':[0,0,19],'horizontal_fov_deg':30}),'engine':u.SystemLibrary.get_engine_version(),'capture_cameras':capture_cameras,'mesh_settings':mesh_settings,'landmarks':landmark_checks}
    if transfer:
        lo,hi=manifest['assembly']['bounds_blender_cm'];expected_lo=[lo[0],-hi[1],lo[2]];expected_hi=[hi[0],-lo[1],hi[2]]
        actual_lo=[b[0].x-b[1].x,b[0].y-b[1].y,b[0].z-b[1].z];actual_hi=[b[0].x+b[1].x,b[0].y+b[1].y,b[0].z+b[1].z]
        assert max(abs(a-e) for a,e in zip(actual_lo+actual_hi,expected_lo+expected_hi))<.05,'Imported bounds mismatch'
        receipt['normal_contract']=manifest['bake']['runtime'];receipt['manifest_sha256']=package.manifest_sha256
        receipt['instance_construction_foundations']={key:[L.get_material_instance_scalar_parameter_value(u.load_asset(path),'UseConstructionFoundation') for path in paths] for key,paths in variants.items()}
        receipt['shade_occluder']='ProofShadeOccluder'
    (OUT/'import_receipt.json').write_text(json.dumps(receipt,indent=2))

def import_environment(environment_revision=None):
    environment_revision=environment_revision or ENV_REV
    folder=ROOT/'ArtSource/StyleReference/MEL17/UnrealProof'/environment_revision
    for name in ['T_AuthoredDaylight','T_AuthoredNeutral']:
        assert (folder/(name+'.hdr')).is_file(),'Missing authored environment source'
    OUT.mkdir(parents=True,exist_ok=True)
    receipt={'revision':REV,'environment_revision':environment_revision,'textures':{}}
    for name in ['T_AuthoredDaylight','T_AuthoredNeutral']:
        file=folder/(name+'.hdr')
        asset_name=name+'_'+environment_revision
        task=u.AssetImportTask();task.filename=str(file);task.destination_path=DEST+'/Textures';task.destination_name=asset_name;task.automated=True;task.replace_existing=True;task.save=True
        A.import_asset_tasks([task]);tex=u.load_asset(DEST+'/Textures/'+asset_name)
        assert isinstance(tex,u.TextureCube),('HDR did not import as TextureCube',name,type(tex))
        tex.set_editor_property('srgb',False);u.EditorAssetLibrary.save_loaded_asset(tex)
        receipt['textures'][name]={'source':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'asset':tex.get_path_name(),'type':type(tex).__name__}
    (OUT/('environment_import_'+environment_revision+'.json')).write_text(json.dumps(receipt,indent=2))

if __name__=='__main__':
    try:
        if '-StyleProofImportEnvironment' in CMD:
            if CAPTURE_SET=='environment_compare':import_environment('Environment_v001')
            import_environment()
        else:
            run()
            if '-StyleProofEnvironment=authored' in CMD:
                if CAPTURE_SET=='maps_environment':import_environment('Environment_v'+str(int(ENV_REV[-3:])-1).zfill(3))
                import_environment()
        u.log('USP_IMPORT_SUCCESS')
    except Exception:
        OUT.mkdir(parents=True,exist_ok=True)
        failure=json.dumps({'completed':False,'error':traceback.format_exc()},indent=2)
        index=1
        while (OUT/f'import_failure_{index:03d}.json').exists():index+=1
        (OUT/f'import_failure_{index:03d}.json').write_text(failure)
        (OUT/'import_failure.json').write_text(failure)
        u.log_error('USP_IMPORT_FAILED '+traceback.format_exc())
        raise
    finally:
        # ExecutePythonScript runs during startup. Let editor mode/tool contexts
        # finish initialization before shutdown, avoiding UE 5.8 teardown crashes.
        shutdown_ticks=0
        def deferred_shutdown(delta):
            global shutdown_ticks
            shutdown_ticks+=1
            if shutdown_ticks>=120:
                u.unregister_slate_post_tick_callback(shutdown_handle)
                u.EditorPythonScripting.set_keep_python_script_alive(False)
                u.SystemLibrary.quit_editor()
        shutdown_handle=u.register_slate_post_tick_callback(deferred_shutdown)
        u.EditorPythonScripting.set_keep_python_script_alive(True)


