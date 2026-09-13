"""Pose-first SOMA30 landmarks for the isolated RH experiment; no generation.

Run with the installed Kimodo Python. This reuses the existing two-link posing
math for sparse authoring only. It does not add a runtime or continuous solver.
"""
import ast
import hashlib
import json
import math
import sys
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'ArtSource/Kimodo/RH_20260913'
helper = ROOT/'ArtSource/Cascadeur/MB_FreshRH_20260913/author_mb_rh.py'
# Reuse the already-established small posing helpers without importing Cascadeur.
tree = ast.parse(helper.read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
     and n.name in ('unit', 'axisrot', 'yaw', 'frame', 'link')], type_ignores=[]), str(helper), 'exec'))
SKELS = json.loads((OUT/'skeletons.json').read_text())
sk = SKELS['somaskel30']; names = sk['names']; parents = sk['parents']
rest = np.array(sk['neutral']); index = {n:i for i,n in enumerate(names)}
handrest = dict(zip(SKELS['somaskel77']['names'], np.array(SKELS['somaskel77']['neutral'])))


def hand_calibration(side):
    prefix = 'Right' if side == 'r' else 'Left'
    head = handrest[prefix+'Hand']
    palm = unit(handrest[prefix+'HandMiddle2']-head)
    shaft = unit(handrest[prefix+'HandIndex2']-handrest[prefix+'HandPinky2'])
    normal = unit(np.cross(shaft, palm)); shaft = unit(np.cross(palm, normal))
    x = palm if side == 'r' else -palm
    return np.column_stack((x, np.cross(shaft, x), shaft)), palm*.077-normal*.024


def weapon_rotation(direction):
    z = unit(np.array(direction, float))
    # Horizontal sword has the grip-frame palm axis sideways in its blade plane.
    x = unit(np.cross([0,1,0], z))
    return np.column_stack((x, np.cross(z,x), z))


def pose(hip, hipyaw, chestyaw, lean, hilt, blade, feet):
    rotations = {}; positions = {}; hip = np.array(hip, float)
    chest = yaw(chestyaw)@axisrot([1,0,0], math.radians(lean))
    pelvis = yaw(hipyaw)
    for n in names:
        i=index[n]; p=parents[i]
        rotations[n] = rotations[names[p]].copy() if p>=0 else pelvis.copy()
        if n=='Spine1': rotations[n]=yaw((hipyaw+chestyaw)*.5)@axisrot([1,0,0],math.radians(lean*.5))
        if n in ('Spine2','Chest'): rotations[n]=chest.copy()
        if n in ('Neck1','Neck2','Head'): rotations[n]=yaw(chestyaw*.12)
        positions[n] = hip.copy() if p<0 else positions[names[p]]+rotations[names[p]]@(rest[i]-rest[p])
    W=weapon_rotation(blade); grip=np.array(hilt,float)-W[:,2]*.07
    reach=[]
    for side,prefix in [('r','Right'),('l','Left')]:
        G,offset=hand_calibration(side); handrot=W@G.T
        grasp=grip-(W[:,2]*.125 if side=='l' else 0)
        wrist=grasp-handrot@offset
        a,b,c=[prefix+n for n in ('Arm','ForeArm','Hand')]
        l1=np.linalg.norm(rest[index[b]]-rest[index[a]])
        l2=np.linalg.norm(rest[index[c]]-rest[index[b]])
        distance=np.linalg.norm(wrist-positions[a]);reach.append(distance/(l1+l2))
        elbow=link(positions[a],wrist,l1,l2,np.array([-1 if side=='r' else 1,-.6,-.1]))
        for n,end,new in [(a,b,elbow),(b,c,wrist)]:
            direction=new-positions[n]
            reference=np.array([0,0,1.])
            rotations[n]=frame(direction,reference)@frame(rest[index[end]]-rest[index[n]],reference).T
            positions[end]=new
        rotations[c]=handrot
        a,b,c=[prefix+n for n in ('Leg','Shin','Foot')]
        ankle=np.array(feet[side],float)
        l1=np.linalg.norm(rest[index[b]]-rest[index[a]])
        l2=np.linalg.norm(rest[index[c]]-rest[index[b]])
        knee=link(positions[a],ankle,l1,l2,np.array([-.08 if side=='r' else .08,0,1.]))
        for n,end,new in [(a,b,knee),(b,c,ankle)]:
            rotations[n]=frame(new-positions[n],np.array([1,0,0.]))@frame(rest[index[end]]-rest[index[n]],np.array([1,0,0.])).T
            positions[end]=new
        rotations[c]=np.eye(3);rotations[prefix+'ToeBase']=np.eye(3)
    # Descendant orientation defaults must follow the newly posed parent.
    for n in names:
        if 'Hand' in n and n not in ('RightHand','LeftHand'):
            rotations[n]=rotations[names[parents[index[n]]]].copy()
    local=[]
    for i,n in enumerate(names):
        p=parents[i]; r=rotations[n] if p<0 else rotations[names[p]].T@rotations[n]
        local.append(Rotation.from_matrix(r).as_rotvec().tolist())
    return local, reach


def main():
    # Native 69 samples at 30Hz. Guide release .7333–1.0333s is represented by
    # indices 22–31. These are exploratory feasible hand routes, not EX contact.
    frames=[0,12,22,31,43,68]
    basic_hilts=[[0,1.27,.32],[-.31,1.40,.19],[-.33,1.39,.43],[.43,1.27,.37],[.30,1.13,.23],[0,1.27,.32]]
    blades=[[-.45,.80,.39],[-.99,.08,-.10],[-.983,.068,.170],[.605,-.146,.783],[.55,-.60,.58],[-.45,.80,.39]]
    variants={
        'A_gathering_v001':dict(hipyaw=[-8,-22,-12,18,16,-8],chestyaw=[-12,-46,-18,40,25,-12],
            hips=[[0,.94,0],[-.06,.93,.015],[-.09,.93,.15],[.08,.91,.13],[.045,.92,.02],[0,.94,0]],
            lean=[0,2,12,10,2,0],prompt='gathers both hands conspicuously back to the right, then launches them decisively'),
        'B_rotational_v001':dict(hipyaw=[-8,-36,-16,24,20,-8],chestyaw=[-12,-70,-24,49,34,-12],
            hips=[[0,.94,0],[-.045,.94,0],[-.09,.93,.15],[.08,.91,.13],[.045,.93,.02],[0,.94,0]],
            lean=[0,1,12,10,2,0],prompt='counterturns the torso into the preparation, then sweeps through with coordinated rotational power and controlled torso braking'),
        'C_grounded_v001':dict(hipyaw=[-8,-22,-12,18,16,-8],chestyaw=[-12,-42,-18,39,23,-12],
            hips=[[0,.94,0],[-.065,.86,.015],[-.09,.90,.15],[.085,.88,.13],[.055,.85,.02],[0,.94,0]],
            lean=[0,2,12,10,3,0],prompt='compresses into an asymmetric supported stance, drives through the strike and absorbs the follow-through with bent knees')}
    plans=[]
    for candidate,v in variants.items():
        folder=OUT/candidate
        assert not folder.exists(), 'Retain any existing candidate; revise into a new take'
        hilts=np.array(basic_hilts,float)
        if candidate.startswith('A_gathering'):hilts[1]+=[-.025,.015,-.03]
        if candidate.startswith('B_rotational'):hilts[1]+=[-.015,0,-.04];hilts[4]+=[.035,.025,-.02]
        if candidate.startswith('C_grounded'):hilts[1]+=[0,-.025,0];hilts[4]+=[-.02,-.02,.02]
        feet={'l':[.16,.062,.12],'r':[-.16,.062,-.13]}
        poses=[];reaches=[]
        for i,f in enumerate(frames):
            try:
                local,reach=pose(v['hips'][i],v['hipyaw'][i],v['chestyaw'][i],v['lean'][i],hilts[i],blades[i],feet)
            except ValueError as e:raise ValueError(f'{candidate} frame {f}: {e}') from e
            poses.append(local);reaches.append(reach)
        constraints=[dict(type='fullbody',frame_indices=frames,local_joints_rot=poses,root_positions=v['hips'])]
        handframes=[6,18,26,37,51,60];handposes=[];handroots=[]
        for f in handframes:
            k=next(i for i in range(len(frames)-1) if frames[i]<f<frames[i+1])
            u=(f-frames[k])/(frames[k+1]-frames[k]);u=u*u*(3-2*u)
            def mix(values):return np.array(values[k])*(1-u)+np.array(values[k+1])*u
            hip=mix(v['hips'])
            local,reach=pose(hip,mix(v['hipyaw']),mix(v['chestyaw']),mix(v['lean']),mix(hilts),mix(blades),feet)
            handposes.append(local);handroots.append(hip.tolist())
        constraints.append(dict(type='end-effector',joint_names=['LeftHand','RightHand'],frame_indices=handframes,
                                local_joints_rot=handposes,root_positions=handroots))
        plans.append((folder,v,hilts.tolist(),constraints,reaches))
    for folder,v,hilts,constraints,reaches in plans:
        folder.mkdir()
        def write(name,value):(folder/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
        write('constraints.json',constraints)
        write('job.json',dict(candidate=folder.name,prompt='A person performs one powerful two-handed sword slash from their right to their left. The person '+v['prompt']+', keeps both hands together on the sword handle, follows through, then returns to the same ready stance.',duration_seconds=2.3,seed=91310+len([p for p in plans if p[0].name<folder.name]),constraints='constraints.json'))
        write('landmarks.json',dict(frames=frames,fps=30,hilt_m=hilts,blade_directions=blades,hip_m=v['hips'],chest_yaw_degrees=v['chestyaw'],arm_reach_fraction=reaches,pose_math_source=str(helper.relative_to(ROOT)),pose_math_sha256=hashlib.sha256(helper.read_bytes()).hexdigest(),author_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),contact_status='Exploratory feasible hilt route, NOT authoritative EX path; evaluate discrepancy before runtime selection',human_acceptance=False))
        print(folder.name, 'maximum arm reach fraction', max(max(r) for r in reaches))


def constrained_diagnostic():
    source=OUT/'diagnostic_constrained'
    folder=OUT/'diagnostic_hand_targets'
    assert not folder.exists(), 'Retain earlier constrained diagnostic'
    constraints=json.loads((source/'constraints.json').read_text())
    landmarks=json.loads((OUT/'A_gathering/landmarks.json').read_text())
    keys=[0,44,89]; ids=[0,1,5]
    hips=[landmarks['hip_m'][i] for i in ids]
    hilts=[landmarks['hilt_m'][i] for i in ids]
    blades=[landmarks['blade_directions'][i] for i in ids]
    hipyaws=[-8,-22,-8]; chestyaws=[-12,-46,-12]; leans=[0,2,0]
    frames=[10,20,30,40,50,60,70,80]; poses=[]; roots=[]
    for f in frames:
        k=0 if f<44 else 1
        u=(f-keys[k])/(keys[k+1]-keys[k]);u=u*u*(3-2*u)
        def mix(values):return np.array(values[k])*(1-u)+np.array(values[k+1])*u
        hip=mix(hips)
        local,reach=pose(hip,mix(hipyaws),mix(chestyaws),mix(leans),mix(hilts),mix(blades),
                         {'l':[.16,.062,.12],'r':[-.16,.062,-.13]})
        poses.append(local);roots.append(hip.tolist())
    constraints.append(dict(type='end-effector',joint_names=['LeftHand','RightHand'],frame_indices=frames,
                            local_joints_rot=poses,root_positions=roots))
    job=json.loads((source/'job.json').read_text())
    job['candidate']=folder.name
    job['purpose']='Same-seed bounded correction: eight sparse paired-hand targets between the three fullbody keys; no continuous prop solver or runtime change'
    folder.mkdir()
    for name,value in [('constraints.json',constraints),('job.json',job)]:
        (folder/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    print(folder.name, '3 fullbody keys, 8 paired-hand frames; unchanged seed and prompt')


if __name__=='__main__':
    if '--diagnostic-hand-targets' in sys.argv:constrained_diagnostic()
    else:main()
