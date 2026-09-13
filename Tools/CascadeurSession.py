"""Bounded, local Cascadeur staging commands on its Qt UI thread.

The command file selects an explicit operation; it never contains executable
code. Quit automatically after one hour or an explicit stop command.
"""
import json,time,traceback
from pathlib import Path
import csc
from PySide6.QtCore import QTimer
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ArtSource/Cascadeur'
COMMAND=ROOT/'Saved/Cascadeur/session-command.json'
RESULT=ROOT/'Saved/Cascadeur/session-result.json'
last=None
started=time.monotonic()
def poll():
    global last
    if time.monotonic()-started>3600:timer.stop();return
    if not COMMAND.exists():return
    request=json.loads(COMMAND.read_text())
    if request['id']==last:return
    last=request['id']
    try:
        app=csc.app.get_application();view=app.get_scene_manager().current_scene()
        scene=view.domain_scene();quick=app.get_tools_manager().get_tool('RiggingToolWindowTool').editor(view)
        action=request['action'];extra={}
        if action=='stop':timer.stop()
        elif action=='rig_on':
            import rig_mode.on
            rig_mode.on.run_raw(scene,[.25,.65,.95],with_dialogs=False)
        elif action=='load_mapping':
            quick.load_template_by_content((KIT/'Knight_resolved.qrigcasc').read_text())
            quick.set_is_create_autoposing(True)
        elif action=='inspect':
            mv=scene.model_viewer()
            extra={'objects':[mv.get_object_name(o) for o in mv.get_objects()], 'qrt':quick.get_template_from_qrt()}
        elif action=='generate':quick.generate_rig_elements()
        elif action=='finish':
            import rig_mode.off
            rig_mode.off.run(scene,True,change_view_mode=True)
        elif action=='save_export':
            view.save(str(KIT/'Knight_Pipeline.casc'))
            app.get_tools_manager().get_tool('FbxSceneLoader').get_fbx_loader(view).export_all_objects(csc.Path(str(KIT/'Knight_Pipeline.fbx')))
        elif action=='reference':
            app.get_tools_manager().get_tool('FbxSceneLoader').get_fbx_loader(view).import_scene(csc.Path(str(KIT/'RightCut_WeaponReference.fbx')))
        else:
            import CascadeurOperations,importlib
            importlib.reload(CascadeurOperations)
            extra=CascadeurOperations.run(action,request,view) or {}
        RESULT.write_text(json.dumps({'id':last,'status':'executed','action':action,**extra},indent=2))
    except Exception:RESULT.write_text(json.dumps({'id':last,'status':'error','error':traceback.format_exc()},indent=2))
timer=QTimer();timer.timeout.connect(poll);timer.start(1000)
print('Cascadeur local staging session started; one-hour maximum.')
