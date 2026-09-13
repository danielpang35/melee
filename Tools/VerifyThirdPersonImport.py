"""Independent source-vs-compressed Unreal pose comparison at keys/subframes."""
import hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Saved/TPProof'
selection=json.loads((OUT/'selection.json').read_text())
source=json.loads((ROOT/selection['skeleton_motion']).read_text())
native=json.loads((OUT/'native-import-samples.json').read_text())
assert native['mesh']==selection['mesh'] and native['animation']==selection['animation'],'Native sample asset identity differs from selection'
assert source['source_sha256']==selection['source_sha256'],'Source identity differs from selection'
profile='TP_uniform_component_scale_carry_v1'
assert source['diagnostic_profile']==native['diagnostic_profile']==profile
# Independent explicit coverage: retain the original16, add three carry keys
# (Blender88/94/100) and their six bracketing half-frames. Time0 is Blender1.
key_offsets=[0,18,62,68,80,118,153,87,93,99]
subframe_offsets=[18.5,61.5,62.5,67.5,72.5,79.5,80.5,118.5,152.5,86.5,87.5,92.5,93.5,98.5,99.5]
expected_times={round(t/60,8) for t in key_offsets+subframe_offsets}
declared_times=[round(t,8) for t in source['diagnostic_sample_times_s']]
native_declared=[round(t,8) for t in native['diagnostic_sample_times_s']]
actual_times=[round(s['time_s'],8) for s in native['samples']]
assert len(expected_times)==len(actual_times)==len(set(actual_times))==25 and set(actual_times)==expected_times,'Expected all25 phase/carry keys and subframes'
assert len(declared_times)==len(set(declared_times))==len(native_declared)==len(set(native_declared))==25
assert set(declared_times)==set(native_declared)==expected_times,'Declared sample coverage differs'
for sample in native['samples']:
    for bone in sample['bones'].values():
        assert len(bone['position_cm'])==len(bone['component_scale'])==3 and len(bone['quaternion_xyzw'])==4
        assert all(math.isfinite(v) for v in bone['position_cm']+bone['quaternion_xyzw']+bone['component_scale']),'Nonfinite native pose'
def normalize(q):
    n=math.sqrt(sum(v*v for v in q));assert n>0;return [v/n for v in q]
def convert(q):
    w,x,y,z=q;return normalize([-x,y,-z,w])
def multiply(a,b):
    x,y,z,w=a;X,Y,Z,W=b
    return normalize([w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z])
def inverse(q):
    x,y,z,w=normalize(q);return [-x,-y,-z,w]
def angle(a,b):return math.degrees(2*math.acos(min(1,abs(sum(x*y for x,y in zip(normalize(a),normalize(b)))))))
def key(name):return name.lower().replace('.','_').replace('-','_')
lookup={round(s['time_s'],8):s for s in source['samples']+source['diagnostic_subframes']}
zero_source=lookup[0.]['bones']
zero_native={key(k):v for k,v in next(s for s in native['samples'] if s['time_s']==0)['bones'].items()}
positions=[];rotations=[];scales=[];source_spreads=[];native_spreads=[];scale_samples=[]
for frame in native['samples']:
    expected=lookup[round(frame['time_s'],8)]
    actual={key(k):v for k,v in frame['bones'].items()}
    assert len(expected['bones'])==102
    for name,bone in expected['bones'].items():
        got=actual[key(name)]
        x,y,z=bone['head_world_m'];position=[100*x,-100*y,100*z]
        positions.append((math.dist(position,got['position_cm']),frame['time_s'],name))
        source_delta=multiply(convert(bone['deformation_quaternion_wxyz']),inverse(convert(zero_source[name]['deformation_quaternion_wxyz'])))
        native_delta=multiply(got['quaternion_xyzw'],inverse(zero_native[key(name)]['quaternion_xyzw']))
        rotations.append((angle(source_delta,native_delta),frame['time_s'],name))
        source_scale=bone['component_scale'];source_zero=zero_source[name]['component_scale']
        native_scale=got['component_scale'];native_zero=zero_native[key(name)]['component_scale']
        assert len(source_scale)==len(source_zero)==3 and all(math.isfinite(v) for v in source_scale+source_zero)
        assert all(abs(v)>1e-8 for v in source_zero+native_zero),'Scale ratio requires nonzero reference components'
        sr=[a/b for a,b in zip(source_scale,source_zero)];nr=[a/b for a,b in zip(native_scale,native_zero)]
        scales.append((max(abs(a-b) for a,b in zip(sr,nr)),frame['time_s'],name))
        source_spreads.append(max(sr)-min(sr));native_spreads.append(max(nr)-min(nr))
        if name in ('upperarm01.R','lowerarm01.R','wrist.R'):
            scale_samples.append(dict(time_s=frame['time_s'],bone=name,source_component_scale=source_scale,
                                      native_component_scale=native_scale,source_ratio_from_t0=sr,native_ratio_from_t0=nr))
worst_position=max(positions);worst_rotation=max(rotations);worst_scale=max(scales)
uniform=max(source_spreads)<1e-4 and max(native_spreads)<1e-4
receipt={'revision':selection['revision'],'source_sha256':source['source_sha256'],
    'native_samples_sha256':hashlib.sha256((OUT/'native-import-samples.json').read_bytes()).hexdigest(),
    'sample_times_s':[s['time_s'] for s in native['samples']], 'bones_per_sample':102,
    'max_position_error_cm':worst_position[0],'position_worst_time_bone':worst_position[1:],
    'max_relative_rotation_error_degrees':worst_rotation[0],'rotation_worst_time_bone':worst_rotation[1:],
    'max_component_scale_ratio_error':worst_scale[0],'scale_worst_time_bone':worst_scale[1:],
    'max_source_ratio_nonuniformity':max(source_spreads),'max_native_ratio_nonuniformity':max(native_spreads),
    'uniform_deformation_assumption_satisfied':uniform,'right_arm_scale_samples':scale_samples,
    'scale_method':'Compare per-axis component scale ratios relative to explicit t0, cancelling fixed imported rest/unit scale. This focused proof assumes uniform temporal deformation; inverse wrist scaling may return hand component scale to1. No deformation-magnitude or reach ceiling.',
    'method':'Compare reflected source heads to compressed UE component heads; compare per-bone rotations relative to t0 to cancel native rest-bone axis conversion.',
    'passed':worst_position[0]<.1 and worst_rotation[0]<.15 and worst_scale[0]<1e-4 and uniform,
    'scope':'Source/native pose and uniform component-scale fidelity at10keys+15subframes (including Blender88/94/100 carry). Nonuniform temporal component scales are flagged; shear and vertex-level skinning parity are outside this focused proof. No artistic acceptance claim.'}
(OUT/'source-native-verification.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt));assert receipt['passed']
