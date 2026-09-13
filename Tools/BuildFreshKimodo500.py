"""Fresh rest-based SOMA constraints and explicitly authored pose-proof input.

No old animation, pose arrays or trajectories are read. No diffusion runs here.
Run with the installed Kimodo Python; root separately runs the reviewed job.
"""
import ast
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.spatial.transform import Rotation
import torch
from kimodo.skeleton import SOMASkeleton30
from kimodo.exports.motion_io import complete_motion_dict, save_kimodo_npz

ROOT=Path(__file__).resolve().parents[1]
EXPERIMENT=ROOT/'ArtSource/Kimodo/RH_20260913'
JOB=EXPERIMENT/'fresh_restposed_500_v003'
PROOF=EXPERIMENT/'fresh_restposed_500_v003_poseproof'
# Reuse only the small proven vector/frame/nonstretch link operations.
HELPER=ROOT/'ArtSource/Cascadeur/MB_FreshRH_20260913/author_mb_rh.py'
tree=ast.parse(HELPER.read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('unit','axisrot','yaw','frame','link')],type_ignores=[]),str(HELPER),'exec'))
SKELETONS=json.loads((EXPERIMENT/'skeletons.json').read_text())
S30=SKELETONS['somaskel30'];NAMES=S30['names'];PARENTS=S30['parents'];REST=np.array(S30['neutral']);INDEX={n:i for i,n in enumerate(NAMES)}
HREST=dict(zip(SKELETONS['somaskel77']['names'],np.array(SKELETONS['somaskel77']['neutral'])))
FPS,COUNT,START,END=30,96,39,54
assert (END-START)/FPS==.5

# Entirely new shared performance landmarks: all coordinates SOMA meters/Y-up.
KEYS=[0,9,23,39,44,49,54,68,95]
HIPS=[[0,.965,0],[0,.950,.015],[-.045,.925,-.035],[-.070,.930,-.030],
      [-.035,.935,.010],[.025,.920,.085],[.060,.920,.090],[.070,.925,.040],[0,.965,0]]
HIP_YAW=[0,-5,-12,-18,-7,10,18,16,0]
CHEST_YAW=[0,-6,-22,-30,-13,10,28,26,0]
# x=anatomical left/right, y=height, z=forward relative to upper chest.
GRIPS=[[0,.015,.230],[-.015,.020,.260],[-.120,.065,.180],[-.220,.105,.100],
       [-.180,.090,.230],[0,.055,.275],[.025,.025,.230],[.080,-.035,.170],[0,.015,.230]]
BLADES=[[-.48,.80,.35],[-.78,.38,.45],[-.96,.16,-.21],[-.98,.08,-.17],
        [-.78,.03,.62],[0,-.06,1],[.75,-.12,.65],[.70,-.50,.50],[-.48,.80,.35]]
FEET={'l':np.array([.145,.070,.145]),'r':np.array([-.165,.070,-.125])}


def hand_calibration(side):
    prefix='Right' if side=='r' else 'Left';head=HREST[prefix+'Hand']
    palm=unit(HREST[prefix+'HandMiddle2']-head)
    shaft=unit(HREST[prefix+'HandIndex2']-HREST[prefix+'HandPinky2'])
    normal=unit(np.cross(shaft,palm));shaft=unit(np.cross(palm,normal));x=palm if side=='r' else -palm
    return np.column_stack((x,np.cross(shaft,x),shaft)),palm*.077-normal*.024


def pose(hip,hipyaw,chestyaw,grip_local,blade_local):
    R={};P={};body=yaw(chestyaw);pelvis=yaw(hipyaw)
    for i,n in enumerate(NAMES):
        parent=PARENTS[i]
        R[n]=R[NAMES[parent]].copy() if parent>=0 else pelvis.copy()
        if n=='Spine1':R[n]=yaw((hipyaw+chestyaw)*.5)
        if n in ['Spine2','Chest']:R[n]=body.copy()
        if n in ['Neck1','Neck2','Head']:R[n]=yaw(chestyaw*.10)
        if n in ['LeftShoulder','RightShoulder']:
            R[n]=body@axisrot([0,0,1],math.radians(-13 if n.startswith('Left') else 13))
        P[n]=np.array(hip,float) if parent<0 else P[NAMES[parent]]+R[NAMES[parent]]@(REST[i]-REST[parent])
    upper_chest=(P['LeftShoulder']+P['RightShoulder'])*.5+np.array([0,-.055,0])
    primary=upper_chest+body@np.array(grip_local)
    blade=unit(body@unit(np.array(blade_local)))
    x=unit(np.cross([0,1,0],blade));G=np.column_stack((x,np.cross(blade,x),blade))
    reaches={}
    for side,prefix in [('r','Right'),('l','Left')]:
        calibration,offset=hand_calibration(side);handrot=G@calibration.T
        grasp=primary-(G[:,2]*.125 if side=='l' else 0)
        wrist=grasp-handrot@offset
        a,b,c=[prefix+n for n in ['Arm','ForeArm','Hand']]
        l1=np.linalg.norm(REST[INDEX[b]]-REST[INDEX[a]]);l2=np.linalg.norm(REST[INDEX[c]]-REST[INDEX[b]])
        reaches['arm_'+side]=np.linalg.norm(wrist-P[a])/(l1+l2)
        pole=body@np.array([-1.7,-.55,-.45] if side=='r' else [1.5,-.55,1.1])
        elbow=link(P[a],wrist,l1,l2,pole)
        for n,end,target in [(a,b,elbow),(b,c,wrist)]:
            reference=body@np.array([0,0,1.])
            R[n]=frame(target-P[n],reference)@frame(REST[INDEX[end]]-REST[INDEX[n]],[0,0,1.]).T
            P[end]=target
        R[c]=handrot
        a,b,c=[prefix+n for n in ['Leg','Shin','Foot']]
        ankle=FEET[side]
        l1=np.linalg.norm(REST[INDEX[b]]-REST[INDEX[a]]);l2=np.linalg.norm(REST[INDEX[c]]-REST[INDEX[b]])
        reaches['leg_'+side]=np.linalg.norm(ankle-P[a])/(l1+l2)
        knee=link(P[a],ankle,l1,l2,np.array([-.10 if side=='r' else .10,0,1]))
        for n,end,target in [(a,b,knee),(b,c,ankle)]:
            R[n]=frame(target-P[n],[1,0,0])@frame(REST[INDEX[end]]-REST[INDEX[n]],[1,0,0]).T
            P[end]=target
        R[c]=np.eye(3);R[prefix+'ToeBase']=np.eye(3)
    for n in NAMES:
        if 'Hand' in n and n not in ['RightHand','LeftHand']:
            R[n]=R[NAMES[PARENTS[INDEX[n]]]].copy()
    local_m=[]
    for i,n in enumerate(NAMES):
        parent=PARENTS[i]
        local_m.append(R[n] if parent<0 else R[NAMES[parent]].T@R[n])
    return np.array(local_m),primary,G,reaches,upper_chest


def main():
    assert not JOB.exists() and not PROOF.exists(),'Retain prior fresh inputs; use a distinct revision'
    values=[PchipInterpolator(KEYS,np.array(v,float),axis=0) for v in [HIPS,HIP_YAW,CHEST_YAW,GRIPS,BLADES]]
    local=[];roots=[];grasps=[];checks=[]
    for f in range(COUNT):
        hip,hy,cy,g,b=[v(f) for v in values]
        try:m,P,G,reach,chest=pose(hip,float(hy),float(cy),g,b)
        except ValueError as e:raise ValueError(f'Fresh frame{f}: {e}') from e
        local.append(m);roots.append(hip);checks.append(dict(index=f,reach_fraction=reach,grip_chest_local_m=list(g)))
        grasps.append(dict(index=f,primary_grasp_soma_m=P.tolist(),grasp_rotation_soma_matrix=G.tolist(),upper_chest_soma_m=chest.tolist()))
    local=np.array(local);roots=np.array(roots)
    def constraint(kind,indices,**kwargs):
        return dict(type=kind,frame_indices=indices,local_joints_rot=Rotation.from_matrix(local[indices].reshape(-1,3,3)).as_rotvec().reshape(len(indices),30,3).tolist(),root_positions=roots[indices].tolist(),**kwargs)
    handframes=[5,16,31,42,47,52,61,80,89]
    constraints=[constraint('fullbody',KEYS),constraint('end-effector',handframes,joint_names=['LeftHand','RightHand'])]
    JOB.mkdir();PROOF.mkdir()
    (JOB/'author_fresh_constraints.py').write_bytes(Path(__file__).read_bytes())
    def write(path,v):path.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
    write(JOB/'constraints.json',constraints)
    write(JOB/'job.json',dict(candidate=JOB.name,purpose='attack',
        prompt='A person performs one weighty two-handed sword cut from their right to their left. Standing upright with relaxed shoulders, they first open their hands lower in front, then visibly draw both hands up and back alongside their right shoulder with their right elbow pulling back. They drive a connected sweeping cut with supported weight transfer, let it carry through, then recover to the same ready stance.',
        duration_seconds=COUNT/FPS,frame_count=COUNT,seed=91341,constraints='constraints.json',
        attack_timing=dict(fps=FPS,release_start_index=START,release_end_index=END,required_release_seconds=.5)))
    write(JOB/'fresh-authoring.json',dict(author_script=str(Path(__file__).relative_to(ROOT)),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source='Fresh SOMA rest posing; no prior animation, constraint pose arrays or trajectory loaded',
        reused_calibration='SOMA rest/hands and existing vector/frame/nonstretch two-link math only',
        reference=['Docs/MordhauAnimationAtlas/review/neutral-RH/003.jpg','Docs/MordhauAnimationAtlas/review/neutral-RH/008.jpg'],
        key_indices=KEYS,hip_m=HIPS,hip_yaw=HIP_YAW,chest_yaw=CHEST_YAW,
        primary_grasp_upper_chest_local_m=GRIPS,blade_body_local=BLADES,feet_soma_m={s:v.tolist() for s,v in FEET.items()},
        upright='Yaw-only torso, supported hip translation and fresh leg poses;13degree relaxed shoulder depression',
        phase=dict(fps=FPS,release_start_index=START,release_end_index=END,release_seconds=.5),
        poseproof_status='Authored calibration/feasibility preview, NOT Kimodo-generated motion; review before generation',checks=checks))
    write(JOB/'fresh-grasp-route.json',dict(coordinates='SOMA meters Y-up; +Z forward; localgraspZ blade/guardward',fps=FPS,samples=grasps))
    sk=SOMASkeleton30();m30=torch.tensor(local,dtype=torch.float32);m77=sk.to_SOMASkeleton77(m30)
    authored=complete_motion_dict(m77,torch.tensor(roots,dtype=torch.float32),sk.somaskel77,FPS)
    save_kimodo_npz(str(PROOF/'authored-constraint-preview.npz'),authored)
    write(PROOF/'provenance.json',dict(operation='Fresh authored constraint feasibility preview from rest; no diffusion or inherited motion',job=str((JOB/'job.json').relative_to(ROOT)),source_joint_count=77,fps=FPS,frames=COUNT,human_acceptance=False))
    print('FRESH_CONSTRAINTS_READY',JOB, 'maximum source arm reach',max(r['reach_fraction'][s] for r in checks for s in ['arm_r','arm_l']),flush=True)


if __name__=='__main__':main()
