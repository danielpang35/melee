"""Actual PIE viewport captures; invoke with -ExecutePythonScript, never a commandlet."""
from pathlib import Path
import json,time,traceback,math,configparser,re,sys,hashlib
import unreal as u
ROOT=Path(u.Paths.project_dir()).resolve();CMD=u.SystemLibrary.get_command_line()
sys.path.insert(0,str(ROOT/'Tools'))
from UnrealStyleProofStage import configure_stage
from UnrealStyleCaptureValidation import validate_png, validate_motion
match=re.search(r'(?:^|\s)-StyleProofStageRevision=(\S+)',CMD);STAGE_REV=match.group(1) if match else 'Stage_v001'
assert STAGE_REV in ['Stage_v001','Stage_v002','Stage_v003']
match=re.search(r'(?:^|\s)-StyleProofRevision=(\S+)',CMD);REV=match.group(1) if match else 'USP_v001'
assert re.fullmatch(r'USP_v[0-9]{3}',REV),'Invalid style proof revision'
match=re.search(r'(?:^|\s)-StyleProofEnvironmentRevision=(\S+)',CMD);ENV_REV=match.group(1) if match else 'Environment_v001'
assert re.fullmatch(r'Environment_v[0-9]{3}',ENV_REV),'Invalid environment revision'
match=re.search(r'(?:^|\s)-StyleProofCaptureSet=(\S+)',CMD);CAPTURE_SET=match.group(1) if match else 'default'
assert CAPTURE_SET in ['default','environment_compare','environment_step','environment_response','orientation_camera','maps_environment','material_compare','native','stage','geometry','amplitude','worldnormal','response','transfer'],'Invalid capture set'
DEST='/Game/Visual/StyleProof/'+REV
AUTHORED='-StyleProofEnvironment=authored' in CMD
match=re.search(r'(?:^|\s)-StyleProofKeySpecular=(\S+)',CMD);KEY_SPECULAR=float(match.group(1)) if match else 1.0
assert 0<=KEY_SPECULAR<=1,'Key specular scale outside 0..1'
match=re.search(r'(?:^|\s)-StyleProofCubemapAngle=(\S+)',CMD);CUBE_ANGLE=float(match.group(1)) if match else 0.0
assert -360<=CUBE_ANGLE<=360
match=re.search(r'(?:^|\s)-StyleProofCameraProfile=(\S+)',CMD);CAMERA_PROFILE=match.group(1) if match else 'baseline'
assert CAMERA_PROFILE in ['baseline','reference18']
OUT=ROOT/'Saved/ArtReview/UnrealStyle'/REV
BASE_OUT=OUT
R=json.loads((OUT/'import_receipt.json').read_text())
manifest_path=ROOT/'ArtSource/StyleReference/MEL17/UnrealProof'/REV/'manifest.json'
manifest_hash=hashlib.sha256(manifest_path.read_bytes()).hexdigest()
if CAPTURE_SET=='transfer':
    assert R.get('schema_version')==2,'Transfer captures require a schema v2 imported asset'
if R.get('schema_version')==2:
    assert R['source_hashes']['manifest.json']==manifest_hash,'Imported manifest identity changed'
run_index=1
while (BASE_OUT/('run_'+str(run_index).zfill(3))).exists():run_index+=1
OUT=BASE_OUT/('run_'+str(run_index).zfill(3));OUT.mkdir(parents=True)
FULL='-USPFull' in u.SystemLibrary.get_command_line()
LEVEL=u.get_editor_subsystem(u.LevelEditorSubsystem);EDITOR=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert LEVEL.load_level(R['map'])
if CAPTURE_SET=='response':
    try:
        from UnrealStyleProofResponse import build_response,supply_actual_key
        response_variants,response_definition=build_response(DEST,R);R['variants'].update(response_variants)
        (BASE_OUT/'response_diagnostic_definition.json').write_text(json.dumps(response_definition,indent=2))
    except Exception:
        (OUT/'capture_receipt.json').write_text(json.dumps({'completed':False,'revision':REV,'error':traceback.format_exc(),'phase':'response_material_initialization'},indent=2))
        u.EditorPythonScripting.set_keep_python_script_alive(False)
        raise
# Persist camera-fit changes in the isolated map only; runtime settings remain session-local.
settings=configparser.ConfigParser();settings.optionxform=str;settings.read(ROOT/'Config/GraphicsProfiles.ini')
CVARS=dict(settings['Competitive']);CVARS.update({'r.SetRes':'960x960w','r.EyeAdaptationQuality':'0','r.DepthOfFieldQuality':'0','r.Tonemapper.Sharpen':'0','r.VSync':'0','t.MaxFPS':'30'})
if CAPTURE_SET=='worldnormal':CVARS.update({'ShowFlag.VisualizeBuffer':'1','r.BufferVisualizationTarget':'WorldNormal'})
RECEIPT={'schema_version':1,'revision':REV,'environment':'authored' if AUTHORED else 'builtin','engine':R['engine'],'map':R['map'],'source_manifest':R['manifest'],'renderer':'PIE','settings':{},'command_line':u.SystemLibrary.get_command_line(),'slate_delta_seconds':[],'camera':R['camera'],'captures':[],'motion':[],'notes':['PIE game viewport via Shot; no tiled high-resolution screenshot.','DefaultLit material mechanism proof; geometry fidelity is judged separately.']}
queue=[]
for rig in (['daylight'] if (AUTHORED and not FULL) or (FULL and R.get('schema_version')==2) else ['daylight','neutral']):
    for variant in ['control','normals','combined']:
        queue.append({'name':rig+'_'+variant+'_matched','rig':rig,'variant':variant,'view':'matched','angle':0,'key_yaw':-45,'warmup':50})
# One enlarged front and three-quarter diagnostic of combined material.
for view in ([] if AUTHORED and not FULL else ['front','threequarter','gameplay']):
    queue.append({'name':'daylight_combined_'+view,'rig':'daylight','variant':'combined','view':view,'angle':0,'key_yaw':-45,'warmup':40})
# Smooth small increments between screenshots; tick callback advances every rendered frame.
for seq in (['helmet_rotation','key_sweep'] if FULL else []):
    for i in range(60):
        queue.append({'name':seq+'_'+str(i).zfill(3),'rig':'daylight','variant':'combined','view':'matched','angle':-25+50*i/59 if seq=='helmet_rotation' else 0,'key_yaw':-100+160*i/59 if seq=='key_sweep' else -45,'warmup':40 if i==0 else 0,'motion':seq,'sequence_frame':i})
for item in queue:item['environment']='authored' if AUTHORED else 'builtin'
if FULL and R.get('schema_version')==2:
    queue += [{'name':'shade_transition_'+str(i).zfill(3),'rig':'daylight','variant':'combined','view':'matched','angle':0,'key_yaw':-45,'warmup':40 if i==0 else 0,'motion':'shade_transition','sequence_frame':i,'shade_progress':i/59,'environment':'authored' if AUTHORED else 'builtin'} for i in range(60)]
if AUTHORED and not FULL and REV=='USP_v001':queue.insert(0,{'name':'daylight_control_corrected_key_builtin','rig':'daylight','variant':'control','view':'matched','angle':0,'key_yaw':-45,'warmup':60,'environment':'builtin'})
if 'matte' in R['variants'] and not FULL:queue.append({'name':'daylight_matte_matched','rig':'daylight','variant':'matte','view':'matched','angle':0,'key_yaw':-45,'warmup':50,'environment':'authored' if AUTHORED else 'builtin'})
if REV!='USP_v001' and not FULL:queue.append({'name':'daylight_normals_key_specular_zero','rig':'daylight','variant':'normals','view':'matched','angle':0,'key_yaw':-45,'warmup':50,'environment':'authored' if AUTHORED else 'builtin','key_specular_scale':0.0})
if CAPTURE_SET in ['environment_compare','geometry']:
    queue=[]
    cases=([('environment1_normals','normals','matched','Environment_v001'),('environment2_control','control','matched',ENV_REV),('environment2_normals','normals','matched',ENV_REV)] if CAPTURE_SET=='environment_compare' else [('geometry_normals','normals','matched',ENV_REV),('geometry_matte','matte','matched',ENV_REV),('geometry_normals_native','normals','gameplay',ENV_REV)])
    for name,variant,view,environment_revision in cases:
        queue.append({'name':name,'rig':'daylight','variant':variant,'view':view,'angle':0,'key_yaw':-45,'warmup':60,'environment':'authored','environment_revision':environment_revision})
if CAPTURE_SET=='environment_step':
    previous='Environment_v'+str(int(ENV_REV[-3:])-1).zfill(3)
    queue=[{'name':environment_revision+'_'+variant,'rig':'daylight','variant':variant,'view':'matched','angle':0,'key_yaw':-45,'warmup':60,'environment':'authored','environment_revision':environment_revision} for environment_revision,variant in [(previous,'control'),(ENV_REV,'control'),(ENV_REV,'normals')]]
if CAPTURE_SET=='environment_response':
    previous='Environment_v'+str(int(ENV_REV[-3:])-1).zfill(3)
    queue=[{'name':environment_revision+'_'+variant+'_'+view,'rig':'daylight','variant':variant,'view':view,'angle':0,'key_yaw':-45,'warmup':60,'environment':'authored','environment_revision':environment_revision} for environment_revision,variant,view in [(previous,'normals','matched'),(ENV_REV,'control','matched'),(ENV_REV,'normals','matched'),(ENV_REV,'normals','gameplay')]]
if CAPTURE_SET=='orientation_camera':
    cases=[('orientation_control','control','matched','baseline'),('orientation_normals','normals','matched','baseline'),('camera18_normals','normals','matched','reference18'),('camera18_matte','matte','matched','reference18'),('camera18_normals_native','normals','gameplay','reference18')]
    queue=[{'name':name,'rig':'daylight','variant':variant,'view':view,'angle':0,'key_yaw':-45,'warmup':60,'environment':'authored','environment_revision':ENV_REV,'camera_profile':profile} for name,variant,view,profile in cases]
if CAPTURE_SET=='maps_environment':
    previous='Environment_v'+str(int(ENV_REV[-3:])-1).zfill(3)
    queue=[{'name':environment_revision+'_'+variant,'rig':'daylight','variant':variant,'view':'matched','angle':0,'key_yaw':-45,'warmup':60,'environment':'authored','environment_revision':environment_revision} for environment_revision,variant in [(previous,'control'),(previous,'normals'),(ENV_REV,'normals')]]
if CAPTURE_SET=='native':
    queue=[{'name':ENV_REV+'_normals_native','rig':'daylight','variant':'normals','view':'gameplay','angle':0,'key_yaw':-45,'warmup':60,'environment':'authored','environment_revision':ENV_REV}]
if CAPTURE_SET=='stage':
    queue=[{'name':STAGE_REV+'_normals_'+view,'rig':'daylight','variant':'normals','view':view,'angle':0,'key_yaw':-45,'warmup':60,'environment':'authored','environment_revision':ENV_REV} for view in ['matched','gameplay']]
if CAPTURE_SET=='material_compare':
    queue=[{'name':variant+'_'+view,'rig':'daylight','variant':variant,'view':view,'angle':0,'key_yaw':-45,'warmup':60,'environment':'authored','environment_revision':ENV_REV} for view in ['matched','gameplay'] for variant in ['control','normals']]
if CAPTURE_SET=='amplitude':
    queue=[{'name':'normal_strength_2_matched','rig':'daylight','variant':'normals','view':'matched','angle':0,'key_yaw':-45,'warmup':60,'environment':'authored','environment_revision':ENV_REV,'normal_strength':2.0}]
if CAPTURE_SET=='worldnormal':
    queue=[{'name':'WorldNormal_'+variant,'rig':'daylight','variant':variant,'view':'matched','angle':0,'key_yaw':-45,'warmup':60,'environment':'authored','environment_revision':ENV_REV} for variant in ['control','normals']]
    RECEIPT['buffer_visualization']={'target':'WorldNormal','material_asset':'/Engine/BufferVisualization/WorldNormal.WorldNormal','mechanism':'ShowFlag.VisualizeBuffer=1 and r.BufferVisualizationTarget=WorldNormal, ordinary PIE Shot','purpose':'Actual rendered world-normal buffer control/authored diagnostic; lighting excluded by stock buffer visualization material.'}
if CAPTURE_SET=='response':
    queue=[{'name':'standard_lit_normals_matched','rig':'daylight','variant':'normals','view':'matched','angle':0,'key_yaw':-45,'warmup':60,'environment':'authored','environment_revision':ENV_REV}]
    queue += [{'name':variant+'_'+view,'rig':'daylight','variant':variant,'view':view,'angle':0,'key_yaw':-45,'warmup':60,'environment':'authored','environment_revision':ENV_REV} for view in ['matched','gameplay'] for variant in ['response_control','response_normals']]
    RECEIPT['response_diagnostic']=response_definition
state={'phase':'start','ticks':0,'started':time.monotonic(),'active':None,'index':0,'last_size':None}
if CAPTURE_SET=='transfer':
    assert not FULL,'Transfer stills must pass before full motion capture'
    cases=[('matte','matched')]+[(variant,view) for view in ['front','threequarter'] for variant in ['control','normals']]
    queue=[{'name':'transfer_'+variant+'_'+view,'rig':'neutral','variant':variant,'view':view,'angle':0,'key_yaw':-45,'warmup':60,'environment':'authored' if AUTHORED else 'builtin','environment_revision':ENV_REV} for variant,view in cases]
RECEIPT.update(capture_set=CAPTURE_SET,source_manifest_sha256=manifest_hash,material_variants=R['variants'])
RECEIPT['motion_requirements']={name:60 for name in ['helmet_rotation','key_sweep']} if FULL else {}
if FULL and R.get('schema_version')==2:RECEIPT['motion_requirements']['shade_transition']=60

def finish(error=None):
    if state.get('finished'):return
    state['finished']=True
    try:
        if error:RECEIPT['error']=error
        RECEIPT['completed']=not error
        (OUT/'capture_receipt.json').write_text(json.dumps(RECEIPT,indent=2))
        (BASE_OUT/'capture_receipt.json').write_text(json.dumps(RECEIPT,indent=2))
    except Exception:
        error=traceback.format_exc()
    finally:
        try:
            u.unregister_slate_post_tick_callback(handle)
        finally:
            try:
                if LEVEL.is_in_play_in_editor():LEVEL.editor_request_end_play()
            finally:
                u.log('USP_CAPTURE_SUCCESS' if not error else 'USP_CAPTURE_FAILED '+error)
                # End PIE is queued. Allow its world/render resources to finish
                # teardown before requesting editor shutdown.
                state['shutdown_ticks']=0
                def shutdown_tick(delta):
                    state['shutdown_ticks']+=1
                    if state['shutdown_ticks']<60:return
                    if LEVEL.is_in_play_in_editor() and state['shutdown_ticks']<180:return
                    u.unregister_slate_post_tick_callback(state['shutdown_handle'])
                    u.EditorPythonScripting.set_keep_python_script_alive(False)
                    u.SystemLibrary.quit_editor()
                state['shutdown_handle']=u.register_slate_post_tick_callback(shutdown_tick)
                u.EditorPythonScripting.set_keep_python_script_alive(True)

def actor(tag):
    for a in u.GameplayStatics.get_all_actors_of_class(state['world'],u.Actor):
        if a.actor_has_tag(tag):return a
    raise RuntimeError('Missing PIE actor '+tag)

def vec(v):return [v.x,v.y,v.z]
def rot(v):return [v.pitch,v.yaw,v.roll]

def projected_helmet_bounds(width,height):
    camera=state['camera'];center,extent=state['helmet'].get_actor_bounds(False)
    position=camera.get_actor_location();forward=camera.get_actor_forward_vector();right=camera.get_actor_right_vector();up=camera.get_actor_up_vector()
    points=[];factor=min(width,height)/2/math.tan(math.radians(camera.camera_component.field_of_view/2))
    for x in (-1,1):
        for y in (-1,1):
            for z in (-1,1):
                delta=u.Vector(center.x+x*extent.x-position.x,center.y+y*extent.y-position.y,center.z+z*extent.z-position.z)
                depth=delta.x*forward.x+delta.y*forward.y+delta.z*forward.z
                assert depth>0,'Helmet bounds behind capture camera'
                points.append([width/2+factor*(delta.x*right.x+delta.y*right.y+delta.z*right.z)/depth,height/2-factor*(delta.x*up.x+delta.y*up.y+delta.z*up.z)/depth])
    lo=[min(p[i] for p in points) for i in (0,1)];hi=[max(p[i] for p in points) for i in (0,1)]
    return {'min_px':lo,'max_px':hi,'height_px':hi[1]-lo[1],'measurement':'Projected world bounding-box envelope; actual silhouette pixel height requires image review'}

def prepare(item):
    authored=item['environment']=='authored'
    helmet=state['helmet'];cam=state['camera'];key=state['key'];sky=state['sky']
    cam.camera_component.set_editor_property('constrain_aspect_ratio',True);cam.camera_component.set_editor_property('aspect_ratio',1.0)
    for i,path in enumerate(R['variants'][item['variant']]):helmet.static_mesh_component.set_material(i,u.load_asset(path))
    if 'normal_strength' in item:
        strengths=[]
        for i,path in enumerate(R['variants'][item['variant']]):
            baseline=u.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(u.load_asset(path),'NormalStrength')
            value=item['normal_strength'] if baseline>0 else 0.0
            dynamic=helmet.static_mesh_component.create_dynamic_material_instance(i)
            dynamic.set_scalar_parameter_value('NormalStrength',value)
            actual=dynamic.get_scalar_parameter_value('NormalStrength')
            assert abs(actual-value)<1e-5;strengths.append(actual)
        validation=json.loads((ROOT/'ArtSource/StyleReference/MEL17/UnrealProof'/REV/'validation.json').read_text())
        peak=validation['max_occupied_deviation_deg'];theta=math.radians(peak);strength=item['normal_strength']
        RECEIPT['normal_amplitude_diagnostic']={'formula':'normalize(lerp(float3(0,0,1), decoded_tangent_normal, NormalStrength))','actual_slot_strengths':strengths,'source_peak_deviation_deg':peak,'estimated_peak_after_strength_deg':math.degrees(math.atan2(strength*math.sin(theta),1+strength*(math.cos(theta)-1))),'peak_note':'Analytic estimate before UE normal compression and filtering; source sampled peak from validation.json. Runtime dynamic instances only; saved source material instances unchanged.'}
    helmet.set_actor_rotation(u.Rotator(pitch=0,yaw=item['angle'],roll=0),False)
    key.set_actor_rotation(u.Rotator(pitch=-40,yaw=item['key_yaw'],roll=0),False)
    key.light_component.set_specular_scale(item.get('key_specular_scale',KEY_SPECULAR))
    state['response']=supply_actual_key(helmet,key,R['variants'][item['variant']]) if item['variant'].startswith('response_') else None
    neutral=item['rig']=='neutral'
    state['stage']=configure_stage(actor,DEST,STAGE_REV,neutral)
    if authored:
        environment_revision=item.get('environment_revision',ENV_REV)
        cube=u.load_asset(DEST+'/Textures/'+('T_AuthoredNeutral' if neutral else 'T_AuthoredDaylight')+'_'+environment_revision)
        if not cube and environment_revision=='Environment_v001':cube=u.load_asset(DEST+'/Textures/'+('T_AuthoredNeutral' if neutral else 'T_AuthoredDaylight'))
        assert cube,'Import authored environment before capture'
        sky.light_component.set_cubemap(cube)
        sky.light_component.set_editor_property('lower_hemisphere_is_black',False)
    else:
        sky.light_component.set_cubemap(u.load_asset('/Engine/MapTemplates/Sky/DaylightAmbientCubemap.DaylightAmbientCubemap'))
        sky.light_component.set_editor_property('lower_hemisphere_is_black',False)
    key.light_component.set_light_color(u.LinearColor(1,1,1,1) if neutral else u.LinearColor(1,.86,.68,1))
    sky.light_component.set_light_color(u.LinearColor(1,1,1,1) if (neutral or authored) else u.LinearColor(.65,.78,1,1))
    sky.light_component.set_intensity(3.0 if authored else 1.0)
    sky.light_component.set_source_cubemap_angle(CUBE_ANGLE)
    sky_setup=(item['environment'],item['rig'],item.get('environment_revision',ENV_REV),CUBE_ANGLE)
    if state.get('sky_setup')!=sky_setup:
        sky.light_component.recapture_sky();state['sky_setup']=sky_setup
    loc={'matched':(-27,160,29),'front':(0,110,24),'threequarter':(-64,110,33),'gameplay':(-43,255,35)}[item['view']]
    if item.get('camera_profile',CAMERA_PROFILE)=='reference18':
        if item['view']=='matched':loc=(-50.14,154.32,29)
        elif item['view']=='gameplay':loc=(-50.14*290/182,154.32*290/182,19+10*290/182)
    offset=state['stage']['helmet_and_camera_elevation_cm'];loc=(loc[0],loc[1],loc[2]+offset)
    cam.set_actor_location(u.Vector(*loc),False,False);cam.set_actor_rotation(u.MathLibrary.find_look_at_rotation(cam.get_actor_location(),u.Vector(0,0,19+offset)),False)
    if R.get('schema_version')==2:
        fit=R['capture_cameras'][item['view']]
        loc=fit['location_cm'];target=fit['target_cm']
        cam.set_actor_location(u.Vector(loc[0],loc[1],loc[2]+offset),False,False)
        cam.set_actor_rotation(u.MathLibrary.find_look_at_rotation(cam.get_actor_location(),u.Vector(target[0],target[1],target[2]+offset)),False)
        cam.camera_component.set_field_of_view(fit['horizontal_fov_deg'])
    state['controller'].set_view_target_with_blend(cam,0)
    if R.get('schema_version')==2:
        occluder=actor('ProofShadeOccluder');active='shade_progress' in item
        occluder.set_actor_hidden_in_game(not active)
        if active:
            direction=key.get_actor_forward_vector();assert direction.z<-.1,'Shade key must point down'
            center=helmet.get_actor_bounds(False)[0];height=85.0
            target_location=u.Vector(center.x-direction.x*height/(-direction.z)-100*(1-item['shade_progress']),center.y-direction.y*height/(-direction.z),center.z+height)
            occluder.set_actor_location(target_location,False,False)
    if not RECEIPT['captures']:
        RECEIPT['camera']={'location_cm':vec(cam.get_actor_location()),'rotation_deg':rot(cam.get_actor_rotation()),'target_cm':[0,0,19+offset],'horizontal_fov_deg':cam.camera_component.field_of_view,'camera_profile':item.get('camera_profile',CAMERA_PROFILE),'constrained_aspect_ratio':1.0,'note':'Primary capture camera; each capture records its actual transform.'}
        if R.get('schema_version')==2:RECEIPT['camera']['target_cm']=[target[0],target[1],target[2]+offset]
    state['ticks']=0;state['active']=item;state['phase']='warmup'

def tick(delta):
    try:
        state['ticks']+=1
        if delta and len(RECEIPT['slate_delta_seconds'])<300:RECEIPT['slate_delta_seconds'].append(delta)
        if time.monotonic()-state['started']>900:raise RuntimeError('Capture exceeded 15 minute bound')
        if state['phase']=='start':
            if state['ticks']<10:return
            LEVEL.editor_request_begin_play();state['phase']='begin';state['ticks']=0;return
        if state['phase']=='begin':
            world=EDITOR.get_game_world()
            if not world:return
            controller=u.GameplayStatics.get_player_controller(world,0)
            if not controller:return
            pawn=u.GameplayStatics.get_player_pawn(world,0)
            if R.get('no_pawn_game_mode'):
                assert pawn is None,'Saved proof GameMode unexpectedly spawned a pawn'
                RECEIPT['no_pawn_game_mode_verified']=True
            elif pawn:
                pawn.set_actor_hidden_in_game(True);pawn.set_actor_enable_collision(False)
            state.update(world=world,controller=controller)
            for k,t in [('helmet','ProofHelmet'),('camera','ProofCamera'),('key','ProofKey'),('sky','ProofSky')]:state[k]=actor(t)
            if R.get('no_pawn_game_mode'):
                RECEIPT['camera_auto_activation_verified']=controller.get_view_target()==state['camera']
                assert RECEIPT['camera_auto_activation_verified'],'Saved camera did not auto-activate for player 0'
            for k,v in CVARS.items():u.SystemLibrary.execute_console_command(world,k+' '+v,controller)
            RECEIPT['settings']={k:u.SystemLibrary.get_console_variable_string_value(k) for k in CVARS if k!='r.SetRes'}
            for key,value in CVARS.items():
                if key=='r.SetRes':continue
                actual=RECEIPT['settings'][key]
                try:matches=abs(float(actual)-float(value))<1e-5
                except ValueError:matches=actual==value
                assert matches,('Effective setting mismatch',key,actual,value)
            if CAPTURE_SET=='worldnormal':
                assert RECEIPT['settings']['ShowFlag.VisualizeBuffer']=='1'
                assert RECEIPT['settings']['r.BufferVisualizationTarget']=='WorldNormal'
            controller.set_view_target_with_blend(state['camera'],0)
            state['phase']='settle';state['ticks']=0;return
        if state['phase']=='settle':
            if state['ticks']<120:return
            prepare(queue[0]);return
        if state['phase']=='warmup':
            item=state['active']
            if state['ticks']<item['warmup']:return
            file=(OUT/'motion'/item['motion']/(item['name']+'.png')) if 'motion' in item else OUT/(item['name']+'.png')
            file.parent.mkdir(parents=True,exist_ok=True)
            if file.exists():raise RuntimeError('Refusing to overwrite capture '+str(file))
            state['file']=file
            state['viewport_size']=tuple(state['controller'].get_viewport_size())
            assert min(state['viewport_size'])>=720,('PIE viewport too small',state['viewport_size'])
            state['request_engine_frame']=u.SystemLibrary.get_frame_count()
            u.SystemLibrary.execute_console_command(state['world'],'Shot filename="'+str(file)+'" -nosuffix',state['controller'])
            state['phase']='waiting';state['ticks']=0;return
        if state['phase']=='waiting':
            file=state['file']
            if not file.exists():
                if state['ticks']>120:raise RuntimeError('Screenshot missing '+str(file))
                return
            try:
                image_validation=validate_png(file,state['viewport_size'])
            except ValueError:
                if state['ticks']>120:raise
                return
            w,h=image_validation['width'],image_validation['height'];item=state['active']
            entry={'file':str(file),'request_engine_frame':state['request_engine_frame'],'completion_engine_frame':u.SystemLibrary.get_frame_count(),'world_delta_seconds':u.GameplayStatics.get_world_delta_seconds(state['world']),'rig':item['rig'],'variant':item['variant'],'view':item['view'],'width':w,'height':h,'frame':state['index'],'helmet_rotation_deg':rot(state['helmet'].get_actor_rotation()),'key_rotation_deg':rot(state['key'].get_actor_rotation()),'camera_location_cm':vec(state['camera'].get_actor_location()),'camera_rotation_deg':rot(state['camera'].get_actor_rotation()),'horizontal_fov_deg':state['camera'].camera_component.field_of_view,'constrained_aspect_ratio':1.0,'environment':item['environment'],'stage':state['stage'],'environment_revision':item.get('environment_revision',ENV_REV),'camera_profile':item.get('camera_profile',CAMERA_PROFILE),'cubemap_angle_deg':state['sky'].light_component.get_editor_property('source_cubemap_angle'),'cubemap_asset':state['sky'].light_component.get_editor_property('cubemap').get_path_name(),'lower_hemisphere_is_black':state['sky'].light_component.get_editor_property('lower_hemisphere_is_black'),'sky_intensity':state['sky'].light_component.intensity,'sky_light_color':[1,1,1] if (item['rig']=='neutral' or item['environment']=='authored') else [.65,.78,1],'key_specular_scale':state['key'].light_component.get_editor_property('specular_scale'),'key_intensity':3.0,'key_light_color':[1,1,1] if item['rig']=='neutral' else [1,.86,.68]}
            entry.update(image_validation)
            entry['actual_viewport_size']=list(state['viewport_size'])
            entry['requested_window_size']=[960,960]
            entry['projected_helmet_bounds']=projected_helmet_bounds(w,h)
            if 'shade_progress' in item:
                entry['shade_occluder_location_cm']=vec(actor('ProofShadeOccluder').get_actor_location())
                entry['shade_mechanism']='Moving opaque geometry across fixed directional light; fixed helmet, camera and light intensity'
            if 'motion' in item:entry.update(motion=item['motion'],sequence_frame=item['sequence_frame'],capture_wait_ticks=state['ticks'])
            if state.get('response'):entry['response_diagnostic_actual']=state['response']
            RECEIPT['captures'].append(entry);state['index']+=1
            if state['index']==len(queue):
                RECEIPT['motion']=validate_motion(RECEIPT['captures'],RECEIPT['motion_requirements'])
                finish();return
            prepare(queue[state['index']])
            if state['active']['warmup']==0:tick(0)
    except Exception:
        finish(traceback.format_exc())
handle=u.register_slate_post_tick_callback(tick)
u.EditorPythonScripting.set_keep_python_script_alive(True)


