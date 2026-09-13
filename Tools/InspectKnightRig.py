import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'ArtSource/CharacterReset/CF_v001/CF_v001_Character.blend'))
rig=bpy.data.objects['CF01_CharacterRig']
record=dict(objects=[dict(name=o.name,type=o.type) for o in bpy.data.objects],bones=[dict(name=b.name,head=list(b.head_local),tail=list(b.tail_local),parent=b.parent.name if b.parent else None) for b in rig.data.bones])
(ROOT/'Saved/UserKnight/rig-inspection.json').write_text(json.dumps(record,indent=2))
for b in record['bones']:
    if not any(x in b['name'] for x in ['finger','toe','face','eye','jaw','tongue']):print(b)
