"""Photo-directed fresh rest poses. Kimodo Python: prepare | proof.

Only calibrated skeleton/grasp math is reused; no prior motion is loaded.
"""
import json
import sys
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools'))
import BuildKimodoConstraints as posing
from KimodoWorkflow import environment, sha, validate_attack_job, write
BASE=ROOT/'ArtSource/Kimodo/RH_20260913'
KEYS=[0,12,29,39,54,66,91]
VARIANTS={
 'A_reference_upright_v003':dict(load=[-.32,1.46,-.025],lean=0,turn=-44,
    prompt='raises both hands beside the right shoulder and visibly pulls both arms backward, keeping the torso upright'),
 'B_reference_extended_v003':dict(load=[-.38,1.45,-.035],lean=0,turn=-49,
    prompt='makes an exaggerated wide arm-led windup, extending both arms farther to the right and backward while keeping the torso upright'),
 'C_reference_bent_v003':dict(load=[-.34,1.44,-.025],lean=9,turn=-46,
    prompt='loads both arms conspicuously beside the right shoulder with a modest forward torso bend, then drives upright through the swing')}

def controls(name):
    v=VARIANTS[name]; load=np.array(v['load'])
    return dict(hilts=[[0,1.27,.19],[-.27,1.43,.24],load.tolist(),(load+[-.005,-.01,-.025]).tolist(),
                      [.30,1.29,.29],[.25,1.21,.16],[0,1.27,.19]],
      blades=[[-.38,.82,.43],[-.75,.56,.35],[-.66,.42,-.62],[-.91,.10,-.40],
              [.78,-.08,.62],[.90,-.35,.22],[-.38,.82,.43]],
      hips=[[0,.95,0],[-.025,.94,0],[-.045,.925,-.025],[-.04,.93,-.02],
            [.045,.925,.04],[.05,.91,.025],[0,.95,0]],
      hipyaw=[-6,-13,-24,-21,22,26,-6],chestyaw=[-8,-22,v['turn'],v['turn']+3,38,43,-8],
      lean=[0,v['lean']*.4,v['lean'],v['lean']*.7,0,2,0],
      feet={'l':[.175,.062,.14],'r':[-.18,.062,-.16]})

def sample(c,f):
    def at(k):return PchipInterpolator(KEYS,c[k],axis=0)(f)
    hip=at('hips')
    local,reach=posing.pose(hip,at('hipyaw'),at('chestyaw'),at('lean'),at('hilts'),at('blades'),c['feet'])
    return local,hip.tolist(),reach

def prepare():
    # Validate every complete rest-authored route before creating any destination.
    plans=[]
    for name,v in VARIANTS.items():
        c=controls(name);samples=[sample(c,f) for f in range(92)]
        constraints=[]
        for kind,frames in [('fullbody',KEYS),('end-effector',[6,21,35,46,60,77,85])]:
            constraint=dict(type=kind,frame_indices=frames,
                local_joints_rot=[samples[f][0] for f in frames],root_positions=[samples[f][1] for f in frames])
            if kind=='end-effector':constraint['joint_names']=['LeftHand','RightHand']
            constraints.append(constraint)
        job=dict(candidate=name,purpose='attack',frame_count=92,duration_seconds=92/30,seed=91361+len(plans),
            attack_timing=dict(fps=30,release_start_index=39,release_end_index=54,required_release_seconds=.5),
            constraints='constraints.json',prompt='A standing person performs one powerful two-handed sword slash from right to left. The person '+v['prompt']+', drives a weighty horizontal strike across the front, absorbs the follow-through through the hips and bent knees, and returns to the same ready stance. Both hands hold one sword handle together.')
        validate_attack_job(job,constraints)
        folder=BASE/name
        assert not folder.exists(),'Retain every earlier take'
        plans.append((folder,c,samples,constraints,job))
    protected=json.loads((ROOT/'Saved/Kimodo/protected-baseline-verification.json').read_text(encoding='utf-8-sig'))['protected_files']
    before={p:sha(ROOT/p) for p in protected}
    for folder,c,samples,constraints,job in plans:
        folder.mkdir()
        (folder/'author-used.py').write_bytes(Path(__file__).read_bytes())
        for filename,data in [('job.json',job),('constraints.json',constraints),('protected-before.json',before)]:write(folder/filename,data)
        write(folder/'landmarks.json',dict(keys=KEYS,controls=c,author_sha256=sha(__file__),
            reference='Saved/reference.jpg',reference_sha256=sha(ROOT/'Saved/reference.jpg'),
            lineage='Fresh SOMA rest-based poses; prior C animation, poses and trajectories not loaded.',
            max_soma_reach_fraction=max(max(s[2]) for s in samples),
            reference_limit='Single photograph directs raised hands, visible rearward arm load and elbow separation; it does not establish sword path or timing.',
            timing='92 samples at30fps; zero-based release39-54=500ms; full source1x',
            contact_status='Exploratory weapon route, not accepted EX contact',human_acceptance=False))
        print(folder.name,'max SOMA reach',max(max(s[2]) for s in samples),flush=True)

def proof():
    import torch
    from kimodo.skeleton import SOMASkeleton30
    from kimodo.exports.motion_io import complete_motion_dict,save_kimodo_npz
    from kimodo.scripts.motion_convert import main as convert
    # Widest planned extension tests the common target-proportion/grasp premise.
    folder=BASE/'reference_extended_poseproof_v003'
    assert not folder.exists()
    samples=[sample(controls('B_reference_extended_v003'),f) for f in range(92)]
    matrices=Rotation.from_rotvec(np.array([s[0] for s in samples]).reshape(-1,3)).as_matrix().reshape(92,30,3,3)
    motion=complete_motion_dict(torch.tensor(matrices,dtype=torch.float32),torch.tensor([s[1] for s in samples],dtype=torch.float32),SOMASkeleton30(),30.)
    folder.mkdir()
    save_kimodo_npz(str(folder/'authored-poseproof.npz'),motion)
    assert convert([str(folder/'authored-poseproof.npz'),str(folder/'transfer-standard-tpose.bvh'),
        '--from','kimodo','--to','soma-bvh','--source-fps','30','--bvh_standard_tpose'])==0
    (folder/'constraints.json').write_bytes((BASE/'B_reference_extended_v003/constraints.json').read_bytes())
    (folder/'author-used.py').write_bytes(Path(__file__).read_bytes())
    write(folder/'proof.json',dict(purpose='Fresh authored FK grasp/pose diagnostic, NOT Kimodo generation',
        author_sha256=sha(__file__),source_sha256=sha(folder/'authored-poseproof.npz'),frames=92,fps=30))
    print('POSE_PROOF_READY',folder,flush=True)

if __name__=='__main__':
    environment()
    {'prepare':prepare,'proof':proof}[sys.argv[1]]()
