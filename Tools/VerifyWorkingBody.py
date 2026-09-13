"""Fresh-load asset and ordinary PIE body checks, including FP/TP visibility.

Run in the editor on /Engine/Maps/Entry, without -TPPreview.
"""
from pathlib import Path
import json, time, traceback, hashlib
import unreal as u

ROOT = Path(u.Paths.project_dir()).resolve()
OUT = ROOT/'Saved/WorkingBody'/(time.strftime('multi-angle-%Y%m%d-%H%M%S')+f'-{time.time_ns()}')
OUT.mkdir(parents=True, exist_ok=True)
PATH = '/Game/UserMaleBody/MB_v004_Project/SK_MB_Body.SK_MB_Body'
EDITOR = u.get_editor_subsystem(u.UnrealEditorSubsystem)
LEVEL = u.get_editor_subsystem(u.LevelEditorSubsystem)
ACTORS = u.get_editor_subsystem(u.EditorActorSubsystem)
MESH = u.get_editor_subsystem(u.SkeletalMeshEditorSubsystem)
skin = u.load_asset(PATH)
assert skin and MESH.get_lod_count(skin) == 4
for lod in range(4):
    assert MESH.get_num_sections(skin, lod) == 1
    assert MESH.get_lod_material_slot(skin, lod, 0) == lod
    assert skin.materials[lod].material_interface.get_path_name().endswith(f'MI_MB_Body_LOD{lod}.MI_MB_Body_LOD{lod}')
camera = ACTORS.spawn_actor_from_class(u.CameraActor, u.Vector(10, -250, 165))
camera.set_actor_rotation(u.MathLibrary.find_look_at_rotation(camera.get_actor_location(), u.Vector(350, 0, 94)), False)
camera.camera_component.set_field_of_view(43)
camera.tags = ['WorkingBodyReviewCamera']
VIEWS = [('front', (-340,0,0)), ('rear',(340,0,0)),
         ('left',(0,340,0)), ('right',(0,-340,0)),
         ('rear-left',(260,210,20)), ('rear-right',(260,-210,20))]
JOBS = [(lod,view,offset) for lod in range(4) for view,offset in VIEWS[:4]] + [(0,v,o) for v,o in VIEWS[4:]]
selection=json.loads((ROOT/'Config/WorkingCharacter.json').read_text(encoding='utf-8-sig'))
source=ROOT/selection['native_source']
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
import_path=ROOT/'Saved/WorkingBody/import.json'
import_receipt=json.loads(import_path.read_text(encoding='utf-8-sig'))
runtime_package=ROOT/'Content/UserMaleBody/MB_v004_Project/SK_MB_Body.uasset'
assert import_receipt.get('completed') and import_receipt['mesh']==PATH
assert (ROOT/import_receipt['source']).resolve()==source.resolve()
assert import_receipt['source_sha256']==sha(source), 'Selected source differs from imported source'
assert (ROOT/import_receipt['runtime_package']).resolve()==runtime_package.resolve()
assert import_receipt['runtime_package_sha256']==sha(runtime_package), 'Runtime mesh changed since import'
import_hash=sha(import_path)
state = dict(phase='start', ticks=0, started=time.monotonic(), job=0)
receipt = dict(policy='MCL-MULTI-ANGLE-2026-09-13', mesh=PATH,
    source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    import_receipt=str(import_path),import_receipt_sha256=import_hash,
    runtime_package=str(runtime_package),runtime_package_sha256=sha(runtime_package),
    fbx_inputs=import_receipt['fbx_inputs'],
    animation='independent rest pose; no TP retargeting', captures=[], views=[],
    visual_review='pending; capture completion alone is not a visual pass')

def prepare_capture():
    lod,view,offset=JOBS[state['job']]
    close=view.startswith('rear-')
    target=u.Vector(350,0,116 if close else 94)
    location=target+u.Vector(*offset)*(0.70 if close else 1)
    camera=state['camera']
    camera.set_actor_location(location,False,False)
    camera.set_actor_rotation(u.MathLibrary.find_look_at_rotation(location,target),False)
    for c in state['components']:
        c.set_forced_lod(lod+1)
    state.update(phase='capture',ticks=0,lod=lod,view=view,
        capture_name=f'body-lod{lod}-{view}',camera_location=[location.x,location.y,location.z],
        camera_target=[target.x,target.y,target.z])

def tick(delta):
    try:
        state['ticks'] += 1
        if state['phase'] != 'quit' and time.monotonic()-state['started'] > 600:
            raise RuntimeError('Working body verification timeout')
        if state['phase'] == 'start' and state['ticks'] >= 120:
            LEVEL.editor_request_begin_play()
            state.update(phase='begin', ticks=0)
        elif state['phase'] == 'begin':
            world = EDITOR.get_game_world()
            if not world or state['ticks'] < 120:
                return
            pc = u.GameplayStatics.get_player_controller(world, 0)
            pawn = u.GameplayStatics.get_player_pawn(world, 0)
            rigs = []
            components = []
            for actor in u.GameplayStatics.get_all_actors_of_class(world, u.Character):
                for component in actor.get_components_by_class(u.PoseableMeshComponent):
                    if component.get_name() != 'UserKnightSkin':
                        continue
                    assert component.get_skinned_asset().get_path_name() == PATH
                    assert component.get_num_bones() in (118, 119)
                    assert component.get_bone_index('pelvis') >= 0
                    assert component.get_bone_index('hand_r') >= 0
                    assert component.is_visible() == (actor != pawn)
                    rigs.append(dict(actor=actor.get_name(), bones=component.get_num_bones(),
                                     first_person_visible=component.is_visible()))
                    components.append(component)
            assert len(rigs) == 3, rigs
            cameras = u.GameplayStatics.get_all_actors_with_tag(world, 'WorkingBodyReviewCamera')
            floors = u.GameplayStatics.get_all_actors_with_tag(world, 'WhiteTestFloor')
            assert len(cameras) == len(floors) == 1
            origin, extent = floors[0].get_actor_bounds(False)
            assert abs(origin.z+extent.z) < .01
            pc.set_view_target_with_blend(cameras[0], 0)
            u.SystemLibrary.execute_console_command(world, 'ShowFlag.HUD 0', pc)
            u.SystemLibrary.execute_console_command(world, 'DisableAllScreenMessages', pc)
            receipt.update(rigs=rigs, floor_top_cm=origin.z+extent.z, first_person_hides_body=True)
            state.update(phase='third_person', ticks=0, switch_started=time.monotonic(),
                         pc=pc, world=world, pawn=pawn, components=components,camera=cameras[0])
        elif state['phase'] == 'third_person' and state['ticks'] >= 30:
            # Slate can continue ticking while a cold PIE world waits on assets.
            if not all(c.is_visible() for c in state['components']) and time.monotonic()-state['switch_started'] < 10:
                return
            assert all(c.is_visible() for c in state['components']), {
                'view_target': state['pc'].get_view_target().get_name(),
                'visible': [(c.get_owner().get_name(), c.is_visible()) for c in state['components']]}
            receipt['third_person_shows_body'] = True
            state['pawn'].set_actor_hidden_in_game(True)
            # Keep the second dummy from obscuring cardinal side views.
            for c in state['components']:
                if c.get_owner().get_actor_location().y > 300:
                    c.get_owner().set_actor_hidden_in_game(True)
            prepare_capture()
        elif state['phase'] == 'capture' and state['ticks'] >= 90:
            state['capture_time'] = time.time()
            path = OUT/(state['capture_name']+'.png')
            u.SystemLibrary.execute_console_command(state['world'], f'Shot filename="{path}"', state['pc'])
            state.update(phase='save', ticks=0, save_started=time.monotonic(), capture_signature=None)
        elif state['phase'] == 'save' and state['ticks'] >= 30:
            captures = [p for p in OUT.glob(state['capture_name']+'*.png') if p.stat().st_mtime >= state['capture_time']]
            assert len(captures) <= 1, 'Expected one fresh screenshot'
            assert time.monotonic()-state['save_started'] < 30, 'Screenshot save timeout'
            if not captures:
                return
            stat=captures[0].stat()
            signature=(stat.st_size,stat.st_mtime_ns)
            if state['capture_signature']!=signature:
                state.update(capture_signature=signature, stable_since=time.monotonic())
                return
            if stat.st_size<12 or time.monotonic()-state['stable_since'] < 0.5:
                return
            # IEND marks a completed PNG, rather than a temporarily stable partial write.
            with captures[0].open('rb') as image:
                image.seek(-12,2)
                if image.read()!=b'\x00\x00\x00\x00IEND\xaeB`\x82':
                    return
            receipt['captures'].append(str(captures[0]))
            receipt['views'].append(dict(lod=state['lod'],name=state['view'],pose='rest',
                camera=dict(location=state['camera_location'],target=state['camera_target'],fov=43),
                path=str(captures[0]),sha256=hashlib.sha256(captures[0].read_bytes()).hexdigest()))
            if state['job'] < len(JOBS)-1:
                state['job'] += 1
                prepare_capture()
            else:
                for lod in range(4):
                    assert {'front','rear','left','right'} <= {v['name'] for v in receipt['views'] if v['lod']==lod}
                assert receipt['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest(), 'Source changed during verification'
                assert sha(import_path)==import_hash, 'Import receipt changed during verification'
                assert sha(runtime_package)==receipt['runtime_package_sha256'], 'Runtime mesh changed during verification'
                receipt['completed'] = True
                (OUT/'verification.json').write_text(json.dumps(receipt, indent=2))
                LEVEL.editor_request_end_play()
                state.update(phase='quit', ticks=0)
        elif state['phase'] == 'quit' and state['ticks'] >= 90:
            u.unregister_slate_post_tick_callback(handle)
            u.EditorPythonScripting.set_keep_python_script_alive(False)
            u.SystemLibrary.quit_editor()
    except Exception:
        (OUT/'verification-error.txt').write_text(traceback.format_exc())
        u.log_error(traceback.format_exc())
        if LEVEL.is_in_play_in_editor():
            LEVEL.editor_request_end_play()
        state.update(phase='quit', ticks=0)

handle = u.register_slate_post_tick_callback(tick)
u.EditorPythonScripting.set_keep_python_script_alive(True)
