"""Verify the scoped TP replay and encode source-clock footage; no art acceptance."""
import argparse, csv, hashlib, json, math, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('tag');p.add_argument('--compare');args=p.parse_args()
assert args.tag and all(c.isalnum() or c in '_-' for c in args.tag)
folder=ROOT/'Saved/MEL15'/args.tag
launch=json.loads(folder.with_name(args.tag+'-launch.json').read_text(encoding='utf-8-sig'))
def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
rows=read_csv(folder/'frames.csv');events=read_csv(folder/'events.csv')
assert len(rows)==len(list((folder/'frames').glob('*.png')))==480
assert [int(r['frame']) for r in rows]==list(range(480))
assert all(math.isfinite(float(v)) for r in rows for k,v in r.items() if k!='phase')
assert all(float(r['blade_error'])<.001 and float(r['pose_error'])<.001 for r in rows),'FP native fidelity changed'
assert {int(r['serial']) for r in rows}=={0,1,2,3},'Expected exactly three ordinary attacks'
for serial in (1,2,3):
    start=next(r for r in rows if int(r['serial'])==serial and r['phase']=='WINDUP')
    start_time=float(start['time'])-float(start['elapsed'])
    active=[r for r in rows if int(r['serial'])==serial and r['ex_active']=='1' and r['phase'] in ('WINDUP','RELEASE','RECOVERY')]
    assert active
    assert all(abs(float(r['source'])-(.3+float(r['time'])-start_time))<1e-5 for r in active),'Source clock drift'
    if serial==3:
        assert len({r['hits'] for r in active})==1,'Range miss unexpectedly contacts'
if not launch['composition']:
    for serial in (1,2):
        attack=[r for r in rows if int(r['serial'])==serial]
        assert any(e['result']=='HIT' and e['attacker']=='1' and int(attack[0]['frame'])<=int(e['frame'])<=int(attack[-1]['frame']) for e in events),f'Expected hit for attack {serial}'
if not launch['baseline']:
    assert all(r['tp_selected']=='1' for r in rows),'TP selection failed'
    authored=[r for r in rows if r['tp_authored']=='1' and float(r['tp_blend'])>.999999]
    if launch['view']=='firstperson':
        assert all(r['tp_active']=='0' for r in rows),'External TP output leaked into owner FP view'
    else:
        assert authored,'No unblended authored output'
        expected=[r for r in rows if r['ex_active']=='1' and r['phase'] in ('WINDUP','RELEASE','RECOVERY')]
        assert all(r['tp_authored']=='1' and r['tp_active']=='1' for r in expected),'Expected TP performance is hidden or absent'
        assert all(float(r['tp_blend'])>.999999 for r in expected if r['phase']=='RELEASE'),'Release cannot evade native fidelity checks through blending'
        assert max(float(r['tp_pose_error']) for r in authored)<.01,'Native skeletal commit mismatch'
        assert max(float(r['tp_weapon_error']) for r in authored)<.01,'Authored visible blade mismatch'
        assert all(abs(float(r['tp_source'])-float(r['source']))<1e-6 for r in authored if r['ex_active']=='1'),'TP source clock differs'
else:
    assert all(r['tp_selected']=='0' and r['tp_active']=='0' for r in rows),'Baseline accidentally opted into TP'
release=[r for r in rows if r['phase']=='RELEASE' and r['tp_authored']=='1']
compare=None
if args.compare:
    other=ROOT/'Saved/MEL15'/args.compare
    control=read_csv(other/'frames.csv')
    keys=('frame','time','serial','phase','elapsed','source','ex_active','hits','player_hits','x','y','yaw','pitch')
    assert len(control)==len(rows)
    assert all([r[k] for k in keys]==[c[k] for k in keys] for r,c in zip(rows,control)),'Combat/control replay differs'
    assert events==read_csv(other/'events.csv'),'Contact events differ'
    compare={'tag':args.compare,'combat_control_fields_identical':True,'events_identical':True}
ff=next((ROOT/'Saved/VideoRuntime').rglob('ffmpeg*.exe'))
video=folder.with_suffix('.mp4')
subprocess.run([str(ff),'-hide_banner','-loglevel','error','-y','-framerate','60','-i',str(folder/'frames/%04d.png'),
    '-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
def maximum(key,selection=rows):return max((float(r[key]) for r in selection),default=None)
receipt={'tag':args.tag,'frames':480,'fps':60,'duration_s':8,'video':str(video),
    'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'launch':launch,
    'max_fp_blade_error_cm':maximum('blade_error'),'max_fp_pose_error_cm':maximum('pose_error'),
    'max_tp_pose_commit_error_cm':maximum('tp_pose_error'),'max_tp_visible_authored_weapon_error_cm':maximum('tp_weapon_error'),
    'max_release_canonical_base_error_cm':maximum('tp_canonical_base_error',release),
    'max_release_canonical_tip_error_cm':maximum('tp_canonical_tip_error',release),
    'comparison':compare,'events':events,
    'scope':'Technical neutral replay proof; native commit errors do not alone verify source FBX parity. Canonical endpoint differences are diagnostics, not contact-order or artistic acceptance.'}
(folder/'verification.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({k:v for k,v in receipt.items() if k!='launch'}))
