"""Pin or check the accepted first-person and foundation identities for TP work."""
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Saved/TPProof'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
receipt=OUT/'preserved-baseline.json'
if args.check:
    saved=json.loads(receipt.read_text())
    changed=[name for name,digest in saved['files'].items() if not (ROOT/name).exists() or sha(ROOT/name)!=digest]
    assert not changed,changed
    print(json.dumps({'unchanged_files':len(saved['files']),'revision':saved['revision']}))
else:
    assert not receipt.exists(),'A baseline already exists; check it rather than overwrite it.'
    selection=json.loads((ROOT/'Config/EXPreview.json').read_text())
    names=['Config/EXPreview.json','Config/CombatDefaults.json',
       'ArtSource/CharacterReset/EX_v002/EX_v002_MordhauRight.blend',
       selection['weapon_motion'],'Content/EXPreview/EX_v002/EX_v002_Anim.uasset',
       'ArtSource/CharacterReset/CF_v001/CF_v001_Character.blend',
       'ArtSource/CharacterReset/CF_v001/CF_v001_Character.fbx',
       'Source/MeleeCombatLab/Combat/CombatSimulation.cpp',
       'Source/MeleeCombatLab/Combat/Attacks/EXWeaponMotion.h',
       'Source/MeleeCombatLab/Combat/Attacks/AttackStateMachine.cpp']
    files={name:sha(ROOT/name) for name in names}
    assert files[names[2]]==selection['source_sha256']
    assert files[names[4]]==selection['animation_package_sha256']
    OUT.mkdir(parents=True,exist_ok=True)
    receipt.write_text(json.dumps({'revision':selection['revision'],'files':files},indent=2))
    print(json.dumps({'pinned_files':len(files),'revision':selection['revision']}))
