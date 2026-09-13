"""One ordinary PIE rest-pose screenshot and floor/rig checks; no animation test."""
from pathlib import Path
import json,time,traceback
import unreal as u
ROOT=Path(u.Paths.project_dir()).resolve();OUT=ROOT/'Saved/UserKnight'
BODY_REVIEW='-KnightBodyReview' in u.SystemLibrary.get_command_line()
if BODY_REVIEW:
    OUT=OUT/'body-engine';OUT.mkdir(parents=True,exist_ok=True)
EDITOR=u.get_editor_subsystem(u.UnrealEditorSubsystem)
LEVEL=u.get_editor_subsystem(u.LevelEditorSubsystem)
ACTORS=u.get_editor_subsystem(u.EditorActorSubsystem)
camera=ACTORS.spawn_actor_from_class(u.CameraActor,u.Vector(10,-250,165))
camera.set_actor_rotation(u.MathLibrary.find_look_at_rotation(camera.get_actor_location(),u.Vector(350,0,94)),False)
camera.camera_component.set_field_of_view(43)
camera.tags=['UserKnightReviewCamera']
state={'phase':'start','ticks':0,'started':time.monotonic()}
receipt={}
def tick(delta):
    try:
        state['ticks']+=1
        if state['phase']!='quit' and time.monotonic()-state['started']>240:raise RuntimeError('Rest-pose verification timeout')
        if state['phase']=='start' and state['ticks']>=120:
            LEVEL.editor_request_begin_play();state.update(phase='begin',ticks=0)
        elif state['phase']=='begin':
            world=EDITOR.get_game_world()
            if not world or state['ticks']<120:return
            pc=u.GameplayStatics.get_player_controller(world,0)
            cameras=u.GameplayStatics.get_all_actors_with_tag(world,'UserKnightReviewCamera')
            floors=u.GameplayStatics.get_all_actors_with_tag(world,'WhiteTestFloor')
            assert len(cameras)==1 and len(floors)==1
            pc.set_view_target_with_blend(cameras[0],0)
            u.GameplayStatics.get_player_pawn(world,0).set_actor_hidden_in_game(True)
            u.SystemLibrary.execute_console_command(world,'ShowFlag.HUD 0',pc)
            u.SystemLibrary.execute_console_command(world,'DisableAllScreenMessages',pc)
            origin,extent=floors[0].get_actor_bounds(False)
            assert abs(origin.z+extent.z)<.01
            actors=u.GameplayStatics.get_all_actors_of_class(world,u.Character)
            rigs=[]
            for actor in actors:
                for component in actor.get_components_by_class(u.PoseableMeshComponent):
                    if component.get_name()!='UserKnightSkin':continue
                    assert component.get_num_bones()>=102
                    mesh=component.get_skinned_asset()
                    if BODY_REVIEW:
                        assert mesh.get_path_name()=='/Game/UserKnight/KN_v002/SK_KnightBody.SK_KnightBody'
                    rigs.append(dict(actor=actor.get_name(),bones=component.get_num_bones(),
                        mesh=mesh.get_path_name(),
                        location=[actor.get_actor_location().x,actor.get_actor_location().y,actor.get_actor_location().z]))
            assert len(rigs)==3,rigs
            receipt.update(floor_top_cm=origin.z+extent.z,rigs=rigs,animation='independent rest pose',
                screenshot=str(OUT/'rest-engine.png'))
            state.update(phase='capture',ticks=0,world=world,pc=pc)
        elif state['phase']=='capture' and state['ticks']>=120:
            state['capture_time']=time.time()
            u.SystemLibrary.execute_console_command(state['world'],'Shot filename="'+str(OUT/'rest-engine.png')+'"',state['pc'])
            state.update(phase='save',ticks=0)
        elif state['phase']=='save' and state['ticks']>=30:
            captures=[p for p in OUT.glob('rest-engine*.png') if p.stat().st_mtime>=state['capture_time']]
            assert len(captures)==1,'Expected one fresh engine screenshot'
            receipt['screenshot']=str(captures[0])
            receipt['completed']=True
            (OUT/'verification.json').write_text(json.dumps(receipt,indent=2))
            LEVEL.editor_request_end_play();state.update(phase='quit',ticks=0)
        elif state['phase']=='quit' and state['ticks']>=120:
            u.unregister_slate_post_tick_callback(handle)
            u.EditorPythonScripting.set_keep_python_script_alive(False)
            u.SystemLibrary.quit_editor()
    except Exception:
        (OUT/'verification-error.txt').write_text(traceback.format_exc())
        u.log_error(traceback.format_exc())
        if LEVEL.is_in_play_in_editor():LEVEL.editor_request_end_play()
        state.update(phase='quit',ticks=0)
handle=u.register_slate_post_tick_callback(tick)
u.EditorPythonScripting.set_keep_python_script_alive(True)
