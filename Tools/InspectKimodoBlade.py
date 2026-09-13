"""Compare one selected draft's native blade with the retained source guide.

Blender -b --python Tools/InspectKimodoBlade.py -- <native.blend> <receipt.json>
This is an aligned source-space diagnostic, not an Unreal contact acceptance test.
"""
import bpy
import hashlib
import json
from pathlib import Path
import sys
from mathutils import Matrix,Vector

ROOT=Path(__file__).resolve().parents[1]
source,out=[(ROOT/p).resolve() for p in sys.argv[sys.argv.index('--')+1:]]
assert ROOT in source.parents and ROOT in out.parents and not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
guidefile=ROOT/'ArtSource/CharacterReset/EX_v002/Export/EX_v002_WeaponMotion.json'
guide=json.loads(guidefile.read_text())
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
assert abs(scene.render.fps/scene.render.fps_base-30)<.0001
weapon=bpy.data.objects['Kimodo_Weapon_PrimaryOwned']
rows=[]
for index in range(22,32):
    scene.frame_set(index+1);bpy.context.view_layer.update()
    actual=weapon.matrix_world.copy()
    expected=Matrix(guide['samples'][18+2*index]['weapon_world']['matrix_row_major'])
    expected.translation+=Vector((0,.115,.020))
    hilt=actual.translation;tip=actual@Vector((0,0,1.035))
    refhilt=expected.translation;reftip=expected@Vector((0,0,1.035))
    rows.append(dict(source_index=index,source_relative_seconds=index/30,
        hilt_discrepancy_cm=(hilt-refhilt).length*100,tip_discrepancy_cm=(tip-reftip).length*100,
        blade_length_m=(tip-hilt).length))
receipt=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),guide_sha256=sha(guidefile),
    alignment='Retained EX weapon_world plus existing Cascadeur source-guide actor alignment (0,.115,.020)m',
    scope='All ten native30Hz release samples; no runtime timing remap or engine capture',samples=rows,
    maximum_hilt_cm=max(r['hilt_discrepancy_cm'] for r in rows),maximum_tip_cm=max(r['tip_discrepancy_cm'] for r in rows),
    limitation='Exploratory hand route; discrepancy is unresolved. Source-space numbers do not establish engine contact or human/play acceptance.')
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(receipt,indent=2)+'\n')
print('SOURCE_GUIDE',receipt['maximum_hilt_cm'],receipt['maximum_tip_cm'])
