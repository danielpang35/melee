"""Inspect bounded production input replay and encode its unretimed 60 fps footage."""
import csv,json,sys,subprocess,hashlib,math
from pathlib import Path
root=Path(__file__).resolve().parents[1]
tag=sys.argv[1]
assert tag and all(c.isalnum() or c in "_-" for c in tag)
directory=root/'Saved/MEL15'/tag
runtime_log=directory.with_suffix('.log').read_text(encoding='utf-8-sig',errors='replace')
assert 'Failed to compile Material' not in runtime_log,'runtime shader compilation must succeed'
assert runtime_log.count('FRESHBODY mesh=/Game/CharacterReset/CF_v001/CF_GameplayBody.')==3,'all characters use the fresh body'
with (directory/'frames.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
with (directory/'events.csv').open(encoding='utf-8-sig',newline='') as f:events=list(csv.DictReader(f))
assert len(rows)==len(list((directory/'frames').glob('*.png')))==840
assert [int(r['frame']) for r in rows]==list(range(840))
blade=max(float(r['blade_error']) for r in rows);pose=max(float(r['pose_error']) for r in rows)
assert blade<.001 and pose<.001,(blade,pose)
branch_grip=max(float(r['branch_grip_error']) for r in rows)
branch_anchor=max(float(r['branch_anchor_error']) for r in rows)
branch_reach=max(float(r['branch_reach_scale']) for r in rows)
assert all(math.isfinite(float(r[k])) for r in rows for k in ('branch_grip_error','branch_anchor_error','branch_reach_scale'))
assert branch_grip<.001 and branch_anchor<.001,(branch_grip,branch_anchor)
assert max(int(r['serial']) for r in rows)>=4,'repeated input must enter actual attacks'
assert max(float(r['x']) for r in rows)-min(float(r['x']) for r in rows)>5,'forward movement'
assert max(float(r['y']) for r in rows)-min(float(r['y']) for r in rows)>5,'lateral movement'
assert max(float(r['yaw']) for r in rows)-min(float(r['yaw']) for r in rows)>1,'yaw manipulation'
assert max(float(r['pitch']) for r in rows)-min(float(r['pitch']) for r in rows)>1,'pitch manipulation'
assert any(r['phase']=='PARRY' for r in rows),'legal defense must render'
assert any(e['result']=='PARRY' for e in events),'successful parry contact'
assert any(r['phase']=='FLINCH' for r in rows),'hit interruption'
for serial in (1,2):
 cut=[r for r in rows if int(r['serial'])==serial]
 assert any(e['result']=='HIT' and e['attacker']=='1' and int(cut[0]['frame'])<=int(e['frame'])<=int(cut[-1]['frame']) for e in events),f'cut {serial} hits'
miss=[r for r in rows if int(r['serial'])==3]
assert len(set(r['hits'] for r in miss))==1,'third repeated cut misses at range'
assert any(r['serial']=='5' and r['phase']=='WINDUP' and r['ex_active']=='0' for r in rows),'riposte uses explicit fallback'
# The first three ordinary input transactions retain the source interval at 1x.
for serial in (1,2,3):
 windup=next(r for r in rows if int(r['serial'])==serial and r['phase']=='WINDUP')
 start=float(windup['time'])-float(windup['elapsed'])
 for r in rows:
  if int(r['serial'])==serial and r['ex_active']=='1' and r['phase'] in ('WINDUP','RELEASE','RECOVERY'):
   assert abs(float(r['source'])-(.3+float(r['time'])-start))<1e-5,(serial,r)
ffmpeg=next((root/'Saved/VideoRuntime').rglob('ffmpeg*.exe'))
video=directory.with_suffix('.mp4')
subprocess.run([str(ffmpeg),'-hide_banner','-loglevel','error','-y','-framerate','60','-i',str(directory/'frames/%04d.png'),'-c:v','libx264','-crf','19','-pix_fmt','yuv420p',str(video)],check=True)
receipt=dict(tag=tag,frames=len(rows),fps=60,duration=14,video=str(video),video_sha256=hashlib.sha256(video.read_bytes()).hexdigest(),max_blade_error_cm=blade,max_pose_error_cm=pose,max_branch_grip_error_cm=branch_grip,max_branch_anchor_error_cm=branch_anchor,max_branch_reach_scale=branch_reach,events=events,scope='production input replay; phase mapping and provisional first-person branch poses await human acceptance; third-person design deferred')
(directory/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
