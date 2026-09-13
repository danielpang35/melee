"""Explicit pipeline operations executed in Cascadeur's UI thread."""
import csc,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ArtSource/Cascadeur'
def run(action,request,view):
    scene=view.domain_scene();mv=scene.model_viewer()
    if action=='pilot_review_frame':
        frame=int(request['frame'])
        if not 0<=frame<=270:raise ValueError('Frame outside pilot')
        def select_frame(model,update,updater,session):session.set_current_frame(frame)
        scene.modify_update_with_session('Review right cut frame',select_frame)
        return {'frame':frame}
    if action=='author_right_cut_pilot':
        import AuthorRightCutPilot,importlib
        importlib.reload(AuthorRightCutPilot)
        return AuthorRightCutPilot.run(view,request['candidate'])
    if action=='pilot_inspect':
        bv=mv.behaviour_viewer();dv=mv.data_viewer();out={}
        for obj in mv.get_objects():
            name=mv.get_object_name(obj)
            if not ('Point' in name and not name.startswith('EdgeView')) and name not in ('ReferenceHilt','ReferenceTip','RightGripGuide','LeftGripGuide','hand_r','hand_l'):continue
            transform=bv.get_behaviour_by_name(obj,'Transform')
            if transform.is_null():continue
            data=bv.get_behaviour_data(transform,'global_position')
            if data.is_null():continue
            out[name]=[float(v) for v in dv.get_data_value(data,0)]
        return {'positions':out}
    if action=='guide_info':
        bv=mv.behaviour_viewer();dv=mv.data_viewer();out={}
        for obj in mv.get_objects():
            name=mv.get_object_name(obj)
            if name not in ('ReferenceHilt','ReferenceTip'):continue
            data=bv.get_behaviour_data(bv.get_behaviour_by_name(obj,'Transform'),'global_position')
            out[name]={str(f):[float(v) for v in dv.get_data_value(data,f)] for f in (0,25,50,100,200,270)}
        return {'guides':out}
    if action=='setup':
        import runpy
        runpy.run_path(str(ROOT/'Tools/SetupCascadeur.py'))
        return json.loads((ROOT/'Saved/Cascadeur/setup-result.json').read_text())
    if action=='export_performance':
        import runpy
        runpy.run_path(str(ROOT/'Tools/ExportCascadeur.py'))
        return {'exported':str(KIT/'RightCut_Performance.fbx')}
    if action=='open_ready':
        return {'loaded':csc.app.get_application().get_data_source_manager().load_scene(str(KIT/'Knight_Ready.casc'))}
    if action=='open_authoring':
        return {'loaded':csc.app.get_application().get_data_source_manager().load_scene(str(KIT/'RightCut_120.casc'))}
    if action=='export_authoring':
        csc.fbx.FbxLoader(120.,scene.get_event_log_or_null(),view).export_all_objects(csc.Path(str(KIT/'RightCut_Authoring_Check.fbx')))
        return {'exported':True}
    if action=='reference_120':
        csc.fbx.FbxLoader(120.,scene.get_event_log_or_null(),view).import_scene(csc.Path(str(KIT/'RightCut_WeaponReference.fbx')))
        return {'imported':True,'fps':120}
    if action=='save_authoring':
        view.save(str(KIT/'RightCut_120.casc'))
        return {'save_requested':str(KIT/'RightCut_120.casc')}
    if action=='settings_info':
        handler=view.get_setting_handler()
        return {'type':str(type(handler)),'methods':dir(handler),'doc':str(handler.__doc__)}
    if action=='probe':
        import numpy as np,math
        bv=mv.behaviour_viewer();dv=mv.data_viewer()
        points=[]
        for o in mv.get_objects():
            name=mv.get_object_name(o)
            if 'Point' not in name:continue
            transform=bv.get_behaviour_by_name(o,'Transform')
            if transform.is_null():continue
            data=bv.get_behaviour_data(transform,'global_position')
            if data.is_null():continue
            points.append((data,np.array(dv.get_data_value(data,0),dtype=float),name))
        if len(points)<20:raise RuntimeError('No complete point control rig')
        amplitude=float(request.get('amplitude',6.))
        if not 0<amplitude<=20:raise ValueError('Probe amplitude out of range')
        shoulder=next(base for _,base,name in points if name=='upperarm_MainPoint_r')
        def edit(model,update,updater):
            layers=scene.layers_viewer();le=model.layers_editor();de=model.data_editor()
            for layer in layers.all_layer_ids():
                if not layer.is_null():le.set_section(csc.layers.layer.Section(),61,layer)
            model.fit_animation_size_by_layers();updater.generate_update()
            for frame in range(61):
                shift=np.array([amplitude*math.sin(2*math.pi*frame/60),0.,0.])
                actual=set()
                angle=math.radians(amplitude*3)*math.sin(math.pi*frame/60)**2
                rotation=np.array([[math.cos(angle),-math.sin(angle),0.],[math.sin(angle),math.cos(angle),0.],[0.,0.,1.]])
                for data,base,name in points:
                    position=base
                    if name.endswith('_r') and name.startswith(('upperarm_','lowerarm_','hand_')):
                        position=shoulder+rotation@(base-shoulder)
                    de.set_data_value(data,frame,position+shift);actual.add(data)
                for layer in layers.all_layer_ids():
                    if not layer.is_null():le.set_fixed_interpolation_or_key_if_need(layer,frame,True)
                model.set_fixed_interpolation_if_need(actual,frame)
                updater.run_update(actual,frame)
        if not scene.modify_update('Pipeline translation probe',edit):raise RuntimeError('Probe modification rejected')
        return {'points':len(points),'frames':61,'amplitude_cm':amplitude,'purpose':'technical playback test, not an attack'}
    if action=='reopen':
        return {'loaded':csc.app.get_application().get_data_source_manager().load_scene(str(KIT/'Knight_Pipeline.casc'))}
    if action=='direct_rig':
        import pycsc
        from prototypes.rigs.qrt.biped import Biped,BipedData,BipedSettings
        from prototypes.qrt_prototypes.create import _process_qrt
        ps=pycsc.wrap(scene)
        objects={mv.get_object_name(o):o for o in mv.get_objects()}
        template=json.loads((KIT/'Knight_resolved.qrigcasc').read_text())
        mapped={e['Bone name']:pycsc.wrap(objects[e['Joint name']],ps)
                for s in template['Document'][0]['Sections'] for e in s['Names']}
        data=BipedData(settings=BipedSettings(),node_joints=mapped)
        rig=Biped(json.dumps(template),ps,data,5.,5.,[.25,.65,.95])
        rig.run_rig_process(_process_qrt)
        return {'mapped':list(mapped)}
    raise ValueError('Unsupported operation '+action)
