"""Assemble the three verified, unchanged-clock review views."""
import argparse,hashlib,json,subprocess,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--revision',default='Block04');p.add_argument('--take',default='v001');args=p.parse_args()
assert all(re.fullmatch(r'[A-Za-z0-9_-]+',v) for v in [args.revision,args.take])
tags=[f'TP_{args.revision.lower()}_{view}_{args.take}' for view in ['fp','external','defender']]
receipts=[json.loads((ROOT/'Saved/MEL15'/t/'verification.json').read_text()) for t in tags]
assert all(r['comparison']['combat_control_fields_identical'] and r['comparison']['events_identical'] for r in receipts)
assert len({r['launch']['module_sha256'] for r in receipts})==1
assert len({r['launch']['tp_selection']['revision'] for r in receipts})==1
assert len({r['launch']['tp_selection_sha256'].lower() for r in receipts})==1
assert len({json.dumps(r['launch']['tp_selection'],sort_keys=True) for r in receipts})==1
assert len({json.dumps(r['launch']['fp_selection'],sort_keys=True) for r in receipts})==1
assert len({r['comparison']['tag'] for r in receipts})==1
for r in receipts:
    assert hashlib.sha256(Path(r['video']).read_bytes()).hexdigest()==r['video_sha256'],'Input video changed after verification'
ff=next((ROOT/'Saved/VideoRuntime').rglob('ffmpeg*.exe'))
out=ROOT/f'Saved/TPProof/TP_{args.revision}_{args.take}_synchronized_views.mp4'
assert not out.exists() and not out.with_suffix('.json').exists(),'Review take already exists'
filters=[]
for i,label in enumerate(['FIRST PERSON - EX_v002 SOURCE',f'EXTERNAL - TP {args.revision.upper()}',f'DEFENDER - TP {args.revision.upper()}']):
    filters.append(f"[{i}:v]scale=640:480,pad=640:516:0:36:color=0x171b20,drawtext=text='{label}':fontcolor=white:fontsize=17:x=12:y=10[v{i}]")
filters.append('[v0][v1][v2]hstack=inputs=3[out]')
cmd=[str(ff),'-hide_banner','-loglevel','error','-n']
for r in receipts:cmd+=['-i',r['video']]
subprocess.run(cmd+['-filter_complex',';'.join(filters),'-map','[out]','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
receipt={'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'inputs':[{k:r[k] for k in ['tag','video_sha256','frames','fps','comparison']} for r in receipts],'alignment':'Same deterministic replay frame; no retiming. Two hits and one miss under preserved canonical weapon. TP cosmetic contact divergence remains under review.'}
(out.with_suffix('.json')).write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
