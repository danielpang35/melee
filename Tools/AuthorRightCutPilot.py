"""One bounded Cascadeur point-rig blocking pass, using the verified sword guides.

Run through CascadeurOperations. Original starter and gameplay remain untouched.
"""
import json, math, time
from pathlib import Path
import numpy as np
import csc

ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ArtSource/Cascadeur'

def unit(v):
    return v/max(np.linalg.norm(v),1.e-10)

def frame(axis, radial):
    z=unit(axis);x=unit(radial-z*np.dot(radial,z))
    return np.column_stack((x,np.cross(z,x),z))

def yaw(deg):
    a=math.radians(deg);c=math.cos(a);s=math.sin(a)
    return np.array([[c,0,-s],[0,1,0],[s,0,c]])

def lean(deg):
    a=math.radians(deg);c=math.cos(a);s=math.sin(a)
    return np.array([[c,s,0],[-s,c,0],[0,0,1]])

def link(start,end,a,b,rail):
    axis=unit(end-start);distance=np.linalg.norm(end-start)
    if distance>a+b-.05:raise RuntimeError(f'Unreachable arm/leg: {distance:.3f} > {a+b:.3f} cm')
    d=max(distance,abs(a-b)+.01)
    along=(a*a-b*b+d*d)/(2*d)
    pole=unit(rail-axis*np.dot(rail,axis))
    return start+axis*along+pole*math.sqrt(max(0,a*a-along*along))

# Frame, pelvis yaw, chest yaw, forward lean, pelvis X, pelvis Y,
# right elbow outward, left elbow outward. Cubic tangents preserve travel.
KEYS=np.array([
 [0,0,0,1,0,-1, .62,-.65],
 [30,0,0,1,0,-1,.62,-.65],
 [65,4,13,2,-1,-2,.80,-.55],
 [99,7,23,3,-1.3,-2.5,.92,-.40],
 [125,-2,-4,5,1.8,-1.6,.68,-.55],
 [159,-8,-25,3.5,2,-1.2,.45,-.80],
 [181,-7,-22,2.4,1.5,-1.3,.44,-.83],
 [211,-3,-9,1.4,.5,-1.1,.55,-.73],
 [240,0,0,1,0,-1,.62,-.65],
 [270,0,0,1,0,-1,.62,-.65]],dtype=float)

def performance(f):
    i=min(len(KEYS)-2,max(0,np.searchsorted(KEYS[:,0],f,side='right')-1))
    t0,t1=KEYS[i,0],KEYS[i+1,0];t=(f-t0)/(t1-t0)
    def tangent(j):
        if j in (0,1,len(KEYS)-2,len(KEYS)-1):return np.zeros(KEYS.shape[1]-1)
        return (KEYS[j+1,1:]-KEYS[j-1,1:])/(KEYS[j+1,0]-KEYS[j-1,0])
    return ((2*t**3-3*t*t+1)*KEYS[i,1:]+(t**3-2*t*t+t)*(t1-t0)*tangent(i)
        +(-2*t**3+3*t*t)*KEYS[i+1,1:]+(t**3-t*t)*(t1-t0)*tangent(i+1))

def run(view, candidate):
    global KEYS
    if candidate not in ('RC_v001','RC_v002','RC_v003','RC_v004','RC_v005','RC_v006','RC_v006_FP','RC_v007','RC_v007_FP','RC_v008','RC_v008_FP'):raise ValueError('Unknown pilot candidate')
    strong=candidate in ('RC_v004','RC_v005','RC_v006','RC_v006_FP','RC_v007','RC_v007_FP','RC_v008','RC_v008_FP')
    if strong:
        KEYS=np.array([
            [0,0,0,1,0,-1,.62,-.65],[30,0,0,1,0,-1,.62,-.65],
            [65,7,25,1,-1.5,-2,.95,-.45],
            [99,14,46,2,-2,-3,1.05,-.35],
            [125,-2,-2,5,2,-2,.68,-.55],
            [159,-10,-34,3.5,2.5,-1.5,.45,-.80],
            [181,-8,-27,2.4,1.8,-1.4,.44,-.83],
            [211,-3,-10,1.4,.5,-1.1,.55,-.73],
            [240,0,0,1,0,-1,.62,-.65],[270,0,0,1,0,-1,.62,-.65]],dtype=float)
    if candidate in ('RC_v006','RC_v006_FP','RC_v007','RC_v007_FP','RC_v008','RC_v008_FP'):
        KEYS=np.array([
            [0,0,0,1,0,-1,.62,-.65],[30,0,0,1,0,-1,.62,-.65],
            [65,8,24,1,-1.5,-2,.80,-.48],
            [90,14,40,1,-2,-3,.88,-.38],
            [99,10,34,2,-1,-3,.90,-.42],
            [110,2,18,4,1,-2.8,.75,-.55],
            [124,-6,-9,5,2,-2.5,.54,-.67],
            [137,-10,-27,4,2.5,-2,.42,-.76],
            [159,-12,-38,3,2,-1.5,.36,-.86],
            [181,-9,-29,2,1.5,-1.4,.44,-.83],
            [211,-3,-10,1.4,.5,-1.1,.55,-.73],
            [240,0,0,1,0,-1,.62,-.65],[270,0,0,1,0,-1,.62,-.65]],dtype=float)
        if candidate.endswith('_FP'):
            KEYS[:,2]*=.65
            KEYS[:,6]*=.72
            KEYS[:,7]*=.76
    started=time.monotonic()
    directory=KIT/'Candidates'/candidate
    if directory.exists():raise FileExistsError(str(directory))
    base={n:np.array(v) for n,v in json.loads((ROOT/'Saved/Cascadeur/pilot-rest.json').read_text())['positions'].items()}
    calibration=json.loads((ROOT/'Saved/Cascadeur/pilot-hand-calibration.json').read_text()) if candidate in ('RC_v003','RC_v004','RC_v005','RC_v006','RC_v006_FP','RC_v007','RC_v007_FP','RC_v008','RC_v008_FP') else None
    scene=view.domain_scene();mv=scene.model_viewer();bv=mv.behaviour_viewer();dv=mv.data_viewer()
    ids={}
    for obj in mv.get_objects():
        name=mv.get_object_name(obj)
        if name not in base:continue
        transform=bv.get_behaviour_by_name(obj,'Transform')
        if not transform.is_null():ids[name]=bv.get_behaviour_data(transform,'global_position')
    controls={n:d for n,d in ids.items() if 'Point' in n}
    guides=[{n:np.array(dv.get_data_value(ids[n],f),dtype=float) for n in ('ReferenceHilt','ReferenceTip','RightGripGuide','LeftGripGuide')} for f in range(271)]
    if strong:
        import csv
        rows=list(csv.DictReader((ROOT/('Saved/AstraRightCut/reference.csv' if candidate in ('RC_v006','RC_v006_FP','RC_v007','RC_v007_FP','RC_v008','RC_v008_FP') else 'Saved/Cascadeur/StrongLoad/reference.csv')).open()))
        guides=[{n:np.array([float(row[p+'_x']),float(row[p+'_z']),float(row[p+'_y'])])
                 for n,p in [('ReferenceHilt','hilt'),('ReferenceTip','tip'),('RightGripGuide','right'),('LeftGripGuide','left')]} for row in rows]
        if len(guides)!=271:raise ValueError('Unexpected source duration')
    if candidate=='RC_v008_FP':
        import csv
        offsets=list(csv.reader((ROOT/'Config/RightCutView.csv').open()))[1:]
        for f,row in enumerate(offsets):
            shift=np.array([float(row[1]),float(row[3]),float(row[2])])
            for name in guides[f]:guides[f][name]+=shift
    poses=[];max_wrist=0.;previous_twist={}
    for f in range(271):
        py,cy,pitch,px,drop,re,le=performance(f)
        p={n:v.copy() for n,v in base.items() if n in controls}
        pelvis=base['pelvis_MainPoint'];hips=pelvis+np.array([px,drop,0])
        rp=yaw(py);r1=yaw(py*.55+cy*.45)@lean(pitch*.45);rc=yaw(cy)@lean(pitch)
        def rigid(prefix,origin,target,rotation):
            for n in p:
                if n.startswith(prefix):p[n]=target+rotation@(base[n]-origin)
        rigid('pelvis_',pelvis,hips,rp)
        s1=hips+rp@(base['spine_01_MainPoint']-pelvis)
        rigid('spine_01_',base['spine_01_MainPoint'],s1,r1)
        s2=s1+r1@(base['spine_02_MainPoint']-base['spine_01_MainPoint'])
        rigid('spine_02_',base['spine_02_MainPoint'],s2,rc)
        neck=s2+rc@(base['neck_MainPoint']-base['spine_02_MainPoint'])
        # Head keeps the target while the torso winds away underneath it.
        rh=yaw(cy*(.04 if strong else .25))@lean(pitch*.35)
        rigid('neck_',base['neck_MainPoint'],neck,rh)
        head=neck+rh@(base['head_MainPoint']-base['neck_MainPoint'])
        rigid('head_',base['head_MainPoint'],head,rh)
        for side,sign,spread in [('r',1,re),('l',-1,le)]:
            names={part:part+'_MainPoint_'+side for part in ('clavicle','upperarm','lowerarm','hand','thigh','calf','foot')}
            cl=s2+rc@(base[names['clavicle']]-base['spine_02_MainPoint'])
            shoulder=cl+rc@(base[names['upperarm']]-base[names['clavicle']])
            for n in p:
                if n.startswith('clavicle_') and n.endswith('_'+side):p[n]=cl+rc@(base[n]-base[names['clavicle']])
            p[names['upperarm']]=shoulder
            grip=guides[f]['RightGripGuide' if side=='r' else 'LeftGripGuide']
            shaft=unit(guides[f]['ReferenceTip']-guides[f]['ReferenceHilt'])
            rest_upper=base[names['lowerarm']]-base[names['upperarm']]
            rest_lower=base[names['hand']]-base[names['lowerarm']]
            finger=unit(np.array([.03,-.24,sign*.22]))
            palm=unit(np.array([-1.,0,0])+finger*finger[0])
            # Cascadeur Y-up swaps UE Y/Z: cross-product chirality reverses.
            rest_grip=unit(np.cross(finger,palm)*sign+finger*.8)
            if calibration:
                finger=unit(np.array(calibration[side]['finger']))
                palm=unit(np.array(calibration[side]['palm']))
                rest_grip=unit(np.array(calibration[side]['grip']))
            rail=rc@np.array([.20,-.85,spread])
            if candidate in ('RC_v007','RC_v007_FP','RC_v008','RC_v008_FP'):
                # Let the upper arm follow the crossed-body carry instead of
                # forcing the support elbow down behind an over-turned blade.
                carry=max(0.,math.sin(math.pi*max(0.,min(1.,(f-125)/86))))
                rail=unit(rail*(1.-.65*carry)+np.array([-.30,-.28,sign*.65])*.65*carry)
            elbow_hint=shoulder+unit(rail)*np.linalg.norm(rest_upper)
            target_frame=frame(shaft,grip-elbow_hint)
            source_frame=frame(rest_grip,rest_lower)
            best=None
            for angle in np.linspace(-math.pi,math.pi,145):
                radial=target_frame[:,0]*math.cos(angle)+target_frame[:,1]*math.sin(angle)
                rotation=frame(shaft,radial)@source_frame.T
                target=grip-rotation@(finger*4.5+palm*2.)
                try:middle=link(shoulder,target,np.linalg.norm(rest_upper),np.linalg.norm(rest_lower),rail)
                except RuntimeError:continue
                bend=math.acos(np.clip(np.dot(unit(target-middle),unit(rotation@rest_lower)),-1,1))
                continuity=math.atan2(math.sin(angle-previous_twist.get(side,angle)),math.cos(angle-previous_twist.get(side,angle)))
                score=bend*bend+.10*continuity*continuity
                if best is None or score<best[0]:best=(score,angle,rotation,target,middle)
            if best is None:raise RuntimeError(f'No reachable wrist: {candidate} frame {f} side {side}')
            _,previous_twist[side],hand_rotation,wrist,elbow=best
            p[names['lowerarm']]=elbow
            # The lowerarm additional point also defines the upper/lower hinge
            # plane. Using palm pronation here drove the elbow onto the other
            # side of the arm. Preserve its signed bend-plane offset instead.
            rest_add=base['lowerarm_AdditionalPoint_'+side]-base[names['lowerarm']]
            rest_normal=unit(np.cross(rest_lower,-rest_upper))
            target_normal=unit(np.cross(wrist-elbow,shoulder-elbow))
            if np.dot(rest_normal,rest_add)<0:rest_normal=-rest_normal;target_normal=-target_normal
            lower_rotation=frame(wrist-elbow,target_normal)@frame(rest_lower,rest_normal).T
            for n in p:
                if n.startswith('lowerarm_') and n.endswith('_'+side) and n!=names['lowerarm']:
                    p[n]=elbow+lower_rotation@(base[n]-base[names['lowerarm']])
                if n.startswith('hand_') and n.endswith('_'+side):p[n]=wrist+hand_rotation@(base[n]-base[names['hand']])
            max_wrist=max(max_wrist,math.degrees(math.acos(np.clip(np.dot(unit(wrist-elbow),unit(hand_rotation@rest_lower)),-1,1))))
            hip=hips+rp@(base[names['thigh']]-pelvis)
            ankle=base[names['foot']]
            upper_leg=base[names['calf']]-base[names['thigh']];lower_leg=ankle-base[names['calf']]
            knee=link(hip,ankle,np.linalg.norm(upper_leg),np.linalg.norm(lower_leg),np.array([1.,0,sign*.07]))
            p[names['thigh']]=hip;p[names['calf']]=knee
            lr=frame(ankle-knee,np.array([0,0,sign]))@frame(lower_leg,np.array([0,0,sign])).T
            n='calf_AdditionalPoint_'+side;p[n]=knee+lr@(base[n]-base[names['calf']])
        poses.append(p)
    if strong:
        # Preserve an exact resting endpoint; distribute the small wrist-twist
        # residual over the final return rather than snapping after recovery.
        for f in range(211,241):
            u=(f-211)/29.;weight=u*u*(3-2*u)
            for n in poses[f]:
                if n.startswith('hand_'):
                    poses[f][n]+=weight*(poses[0][n]-poses[240][n])
        for f in range(240,271):poses[f]={n:v.copy() for n,v in poses[0].items()}
    directory.mkdir(parents=True)
    def edit(model,update,updater):
        editor=model.data_editor();layers=scene.layers_viewer();le=model.layers_editor()
        for f,p in enumerate(poses):
            actual=set()
            if strong:
                for n,pos in guides[f].items():editor.set_data_value(ids[n],f,pos);actual.add(ids[n])
            for n,d in controls.items():editor.set_data_value(d,f,p[n]);actual.add(d)
            for layer in layers.all_layer_ids():
                if not layer.is_null():le.set_fixed_interpolation_or_key_if_need(layer,f,True)
            model.set_fixed_interpolation_if_need(actual,f);updater.run_update(actual,f)
    if not scene.modify_update('Right cut compact torso-led blocking '+candidate,edit):raise RuntimeError('Rig edit rejected')
    source=directory/(candidate+'.casc');view.save(str(source))
    # Export the solved Cascadeur skeleton, never an offline reconstruction.
    loader=csc.fbx.FbxLoader(120.,scene.get_event_log_or_null(),view)
    settings=csc.fbx.FbxSettings();settings.bake_animation=True;loader.set_settings(settings)
    loader.export_all_objects(csc.Path(str(directory/(candidate+'.fbx'))))
    errors={}
    for f in (0,30,65,99,125,159,181,211,240,270):
        errors[str(f)]={n:float(np.linalg.norm(np.array(dv.get_data_value(controls[n],f))-poses[f][n])) for n in controls}
    report={'candidate':candidate,'source':str(source),'source_exists':source.exists(),'frames':271,
        'hypothesis':('Curved hand drive, delayed blade turn, shortened carry; separate non-damaging FP framing' if candidate in ('RC_v008','RC_v008_FP') else 'Rearward hilt draw, stronger chest/shoulder coil, target-facing head' if strong else 'Compact torso-led blocking'),
        'max_planned_wrist_bend_degrees':max_wrist,'max_solved_control_error_cm':max(v for row in errors.values() for v in row.values()),
        'seconds':time.monotonic()-started,'review':'pending'}
    (directory/'blocking.json').write_text(json.dumps(report,indent=2))
    (directory/'control-errors.json').write_text(json.dumps(errors,indent=2))
    return report
