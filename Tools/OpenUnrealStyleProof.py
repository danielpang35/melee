"""Open the saved proof map at its camera; session-only view/material/environment controls."""
from pathlib import Path
import configparser,json,re,sys,hashlib
import unreal as u
root=Path(u.Paths.project_dir()).resolve();cmd=u.SystemLibrary.get_command_line()
sys.path.insert(0,str(root/'Tools'))
from UnrealStyleProofStage import configure_stage
match=re.search(r'(?:^|\s)-StyleProofStageRevision=(\S+)',cmd);stage_revision=match.group(1) if match else 'Stage_v001'
assert stage_revision in ['Stage_v001','Stage_v002','Stage_v003']
match=re.search(r'(?:^|\s)-StyleProofRevision=(\S+)',cmd);revision=match.group(1) if match else 'USP_v001'
assert re.fullmatch(r'USP_v[0-9]{3}',revision)
match=re.search(r'(?:^|\s)-StyleProofEnvironmentRevision=(\S+)',cmd);environment_revision=match.group(1) if match else 'Environment_v001'
assert re.fullmatch(r'Environment_v[0-9]{3}',environment_revision)
match=re.search(r'(?:^|\s)-StyleProofCubemapAngle=(\S+)',cmd);cube_angle=float(match.group(1)) if match else 0.0
assert -360<=cube_angle<=360
match=re.search(r'(?:^|\s)-StyleProofCameraProfile=(\S+)',cmd);camera_profile=match.group(1) if match else 'baseline'
assert camera_profile in ['baseline','reference18']
match=re.search(r'(?:^|\s)-StyleProofVariant=(\S+)',cmd);variant=match.group(1) if match else 'combined'
assert variant in ['control','normals','combined']
receipt=json.loads((root/'Saved/ArtReview/UnrealStyle'/revision/'import_receipt.json').read_text())
if receipt.get('schema_version')==2:
    manifest=root/'ArtSource/StyleReference/MEL17/UnrealProof'/revision/'manifest.json'
    assert hashlib.sha256(manifest.read_bytes()).hexdigest()==receipt['manifest_sha256'],'Imported source manifest changed'
level=u.get_editor_subsystem(u.LevelEditorSubsystem);assert level.load_level(receipt['map'])
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors();by_tag={str(tag):a for a in actors for tag in a.tags}
cam=by_tag['ProofCamera'];cam.camera_component.set_editor_property('constrain_aspect_ratio',True);cam.camera_component.set_editor_property('aspect_ratio',1.0)
match=re.search(r'(?:^|\s)-StyleProofKeySpecular=(\S+)',cmd);specular=float(match.group(1)) if match else 1.0
assert 0<=specular<=1
by_tag['ProofKey'].light_component.set_specular_scale(specular)
stage_info=configure_stage(lambda name:by_tag[name],'/Game/Visual/StyleProof/'+revision,stage_revision,read_only='-StyleProofRestoreWinning' in cmd)
offset=stage_info['helmet_and_camera_elevation_cm']
location=(-50.14,154.32,29+offset) if camera_profile=='reference18' else (-27,160,29+offset)
cam.set_actor_location(u.Vector(*location),False,False);cam.set_actor_rotation(u.MathLibrary.find_look_at_rotation(cam.get_actor_location(),u.Vector(0,0,19+offset)),False)
if receipt.get('schema_version')==2:
    fit=receipt['capture_cameras']['matched'];pos=fit['location_cm'];target=fit['target_cm']
    location=[pos[0],pos[1],pos[2]+offset]
    cam.set_actor_location(u.Vector(*location),False,False)
    cam.set_actor_rotation(u.MathLibrary.find_look_at_rotation(cam.get_actor_location(),u.Vector(target[0],target[1],target[2]+offset)),False)
    cam.camera_component.set_field_of_view(fit['horizontal_fov_deg'])
by_tag['ProofKey'].set_actor_rotation(u.Rotator(pitch=-40,yaw=-45,roll=0),False)
sky=by_tag['ProofSky'].light_component;sky.set_editor_property('lower_hemisphere_is_black',False)
if '-StyleProofEnvironment=authored' in cmd:
    cube=u.load_asset('/Game/Visual/StyleProof/'+revision+'/Textures/T_AuthoredDaylight_'+environment_revision)
    if not cube and environment_revision=='Environment_v001':cube=u.load_asset('/Game/Visual/StyleProof/'+revision+'/Textures/T_AuthoredDaylight')
    assert cube,'Run environment import first'
    sky.set_cubemap(cube);sky.set_light_color(u.LinearColor(1,1,1,1));sky.set_intensity(3)
sky.set_source_cubemap_angle(cube_angle);sky.recapture_sky()
for i,path in enumerate(receipt['variants'][variant]):
    material=u.load_asset(path);assert material,('Missing winning material',path)
    by_tag['ProofHelmet'].static_mesh_component.set_material(i,material)
profile=configparser.ConfigParser();profile.optionxform=str;profile.read(root/'Config/GraphicsProfiles.ini')
for k,v in profile['Competitive'].items():u.SystemLibrary.execute_console_command(None,k+' '+v)
level.editor_set_game_view(True);level.pilot_level_actor(cam)
if '-StyleProofSaveWinning' in cmd or '-StyleProofRestoreWinning' in cmd:
    assert receipt.get('no_pawn_game_mode'),'Saved winning proof requires isolated no-pawn GameMode'
    assert cam.get_auto_activate_player_index()==0
    restoring='-StyleProofRestoreWinning' in cmd
    if not restoring:assert level.save_current_level(),'Failed to save winning proof map'
    winning={'revision':revision,'stage':stage_info,'map':receipt['map'],'variant':variant,'environment_revision':environment_revision,'cubemap_asset':sky.get_editor_property('cubemap').get_path_name(),'cubemap_angle_deg':sky.get_editor_property('source_cubemap_angle'),'key_specular_scale':by_tag['ProofKey'].light_component.get_editor_property('specular_scale'),'camera_profile':camera_profile,'camera_location_cm':list(location),'horizontal_fov_deg':cam.camera_component.field_of_view,'settings':{k:u.SystemLibrary.get_console_variable_string_value(k) for k in profile['Competitive']},'material_assets':receipt['variants'][variant]}
    state_path=root/'Saved/ArtReview/UnrealStyle'/revision/'winning_state.json'
    actual_location=cam.get_actor_location()
    winning['camera_location_cm']=[actual_location.x,actual_location.y,actual_location.z]
    winning['material_assets']=[by_tag['ProofHelmet'].static_mesh_component.get_material(i).get_path_name() for i in range(len(receipt['variants'][variant]))]
    if restoring:
        expected=json.loads(state_path.read_text())
        assert json.loads(json.dumps(winning))==expected,'Restored proof differs from saved winning state'
        restore_path=state_path.with_name('restore_receipt.json')
        restore_index=2
        while restore_path.exists():
            restore_path=state_path.with_name('restore_receipt_'+str(restore_index).zfill(3)+'.json');restore_index+=1
        restore_path.write_text(json.dumps({'completed':True,'revision':revision,'winning_state':str(state_path),'actual':winning,'mechanism':'Reload preserved baseline map and select its recorded material/environment/camera settings; no assets or winning state saved.'},indent=2))
        u.log('USP_RESTORE_SUCCESS')
    else:
        state_path.write_text(json.dumps(winning,indent=2))
        u.log('USP_SAVE_SUCCESS')
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
else:
    u.EditorPythonScripting.set_keep_python_script_alive(True);u.log('USP_OPEN_READY')
