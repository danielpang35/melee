"""Publish a complete, immutable pilot bundle to an already running preview."""
import argparse,csv,hashlib,json,os,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('candidate');args=p.parse_args()
if not re.fullmatch(r'RC_v\d{3}',args.candidate):p.error('Expected RC_vNNN')
folder=ROOT/'ArtSource/Cascadeur/Candidates'/args.candidate
files=['RightCutWeapon.csv','RightCutView.csv','CascadeurPreview.csv','CascadeurFirstPerson.csv']
for name in files:
    rows=list(csv.reader((folder/name).open()))
    if rows[0][1:]!=['120','271']:raise ValueError('Wrong source clock: '+name)
    if name.startswith('Cascadeur'):
        if len(rows)!=5421:raise ValueError('Incomplete 20-bone skeleton: '+name)
    elif len(rows)!=272:raise ValueError('Incomplete weapon/view track: '+name)
    if name=='RightCutView.csv':
        for row in rows[100:161]:
            if any(abs(float(v))>1e-8 for v in row[1:]):raise ValueError('View offset during release')
if not list(folder.glob('*.casc')) or not list(folder.glob('*.fbx')):raise ValueError('Missing saved source/export')
manifest={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in files}
(folder/'bundle-hashes.json').write_text(json.dumps(manifest,indent=2)+'\n')
selector=ROOT/'Config/RightCutCandidate.txt';temporary=selector.with_suffix('.tmp')
temporary.write_text(args.candidate+'\n');os.replace(temporary,selector)
print(f'Published {args.candidate}. Keep this directory immutable; author the next edit in a new candidate.')
