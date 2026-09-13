"""Prepare an explicit native finishing guide from retained sparse pose controls.

Interpolates the authored primary grasp, not generated wrist noise. The Blender
finisher bakes both arms using existing nonstretch posing math; this is no runtime
or collision path. Run with Kimodo Python and one experiment candidate directory.
"""
import hashlib
import json
from pathlib import Path
import runpy
import sys
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.spatial.transform import Rotation,Slerp

ROOT=Path(__file__).resolve().parents[1]
folder=(ROOT/sys.argv[1]).resolve()
assert ROOT/'ArtSource/Kimodo/RH_20260913' in folder.parents
dest=folder/'grasp-targets.json'
assert not dest.exists(), 'Retain finishing guide with its source identity'
author=runpy.run_path(str(ROOT/'Tools/BuildKimodoConstraints.py'))
sk=author['sk'];rest=author['rest'];names=sk['names'];parents=sk['parents']
G,offset=author['hand_calibration']('r')
data=json.loads((folder/'constraints.json').read_text())
transfer=json.loads((folder/'transfer.json').read_text())
ratio=transfer['root_proportion_ratio']
targetpelvis=np.array(transfer['grasp_calibration']['target_rest_joints_cm']['pelvis'])*.01
targetoffset=np.array([targetpelvis[0],targetpelvis[1],0])
C=np.array([[1,0,0],[0,0,-1],[0,1,0]],float)
keys={}
for constraint in data:
    if constraint['type'] not in ('fullbody','end-effector','right-hand'):continue
    for f,rv,root in zip(constraint['frame_indices'],constraint['local_joints_rot'],constraint['root_positions']):
        local=Rotation.from_rotvec(rv).as_matrix();rot=[];pos=[]
        for i,p in enumerate(parents):
            rot.append(local[i] if p<0 else rot[p]@local[i])
            pos.append(np.array(root) if p<0 else pos[p]+rot[p]@(rest[i]-rest[p]))
        hand=names.index('RightHand')
        grasp=C@(pos[hand]+rot[hand]@offset)*ratio+targetoffset
        matrix=C@rot[hand]@G
        if f in keys:assert np.linalg.norm(keys[f][0]-grasp)<1e-5
        keys[f]=(grasp,matrix)
frames=sorted(keys);count=transfer['frames']
assert frames[0]==0 and frames[-1]==count-1
positions=PchipInterpolator(frames,np.array([keys[f][0] for f in frames]),axis=0)(np.arange(count))
rotations=Slerp(frames,Rotation.from_matrix([keys[f][1] for f in frames]))(np.arange(count)).as_quat()
payload=dict(coordinates='Blender world meters, +Z up, -Y forward; sword local +Z blade, +X primary palm',
    purpose='Authored native arm finishing guide. Not generated motion or accepted gameplay contact.',
    constraint_sha256=hashlib.sha256((folder/'constraints.json').read_bytes()).hexdigest(),
    transfer_sha256=hashlib.sha256((folder/'transfer.json').read_bytes()).hexdigest(),
    interpolation='PCHIP primary grasp translation; shortest-path quaternion SLERP orientation; original source clock',
    root_proportion_ratio=ratio,target_rest_horizontal_offset_m=targetoffset.tolist(),
    support_offset_m=[0,0,-.125],source_key_indices=frames,
    samples=[dict(frame=f+1,primary_grasp_position_m=p.tolist(),grasp_rotation_wxyz=q[[3,0,1,2]].tolist())
             for f,(p,q) in enumerate(zip(positions,rotations))])
dest.write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
print(dest)
