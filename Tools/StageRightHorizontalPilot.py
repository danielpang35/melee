"""Create a fresh local runtime/source staging tree without Saved overrides.

Content is hardlinked on the same volume (read-only play inputs); configuration,
source and module files are copied. This is a local Editor-game pilot, not a cook.
"""
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/'Saved/RightHorizontalPilot/CleanStage'
assert not STAGE.exists(),'Use the existing receipt; do not overwrite a prior stage'
paths=[]
for folder in ('Source','Config','Content','ArtSource/Selected/D_arc_weight_v08','ArtSource/CharacterReset/EX_v002'):
    paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file())
paths += [ROOT/'MeleeCombatLab.uproject',ROOT/'AGENTS.md',ROOT/'Docs/DEVELOPMENT.md',ROOT/'Docs/ANIMATION_PROTOTYPE_PIPELINE.md']
paths += [ROOT/'Tools'/n for n in ('Build.ps1','PlayBenchmark.ps1','PlayRightHorizontalPilot.ps1','CaptureThirdPersonProof.ps1','AnalyzeRightHorizontalPilot.py')]
paths += [p for p in (ROOT/'Binaries/Win64').iterdir() if p.suffix in ('.dll','.modules')]
receipt={'format':'local Editor-game staging, not packaged/cooked','content_hardlinked':True,'files':{}}
for src in paths:
    rel=src.relative_to(ROOT);dest=STAGE/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    if rel.parts[0]=='Content':os.link(src,dest)
    else:shutil.copy2(src,dest)
    assert src.stat().st_size==dest.stat().st_size,rel
    if rel.parts[0]!='Content':
        digest=hashlib.sha256(src.read_bytes()).hexdigest()
        assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest,rel
        receipt['files'][rel.as_posix()]=digest
    else:receipt['files'][rel.as_posix()]={'bytes':src.stat().st_size,'same_file':os.path.samefile(src,dest)}
for name in ('EXPreview.json','RightHorizontalPilot.json'):
    selection=json.loads((STAGE/'Config'/name).read_text())
    for key in ('weapon_motion','skeleton_motion'):
        if key in selection:
            rel=Path(selection[key]);assert not rel.is_absolute() and rel.parts[0]!='Saved' and (STAGE/rel).is_file(),rel
assert not (STAGE/'Saved').exists()
receipt['stage']=str(STAGE);receipt['file_count']=len(paths)
(ROOT/'Saved/RightHorizontalPilot/staging.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(f'Staged {len(paths)} files: {STAGE}; no Saved inputs')
