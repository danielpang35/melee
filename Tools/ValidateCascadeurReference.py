"""Check the weapon guide after a real Cascadeur save/reopen/export."""
import sys,csv,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'ArtSource/Cascadeur/RightCut_Authoring_Check.fbx'),anim_offset=0.)
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE' and 'ReferenceHilt' in o.pose.bones)
fps=bpy.context.scene.render.fps/bpy.context.scene.render.fps_base
assert fps==120,fps
rows=list(csv.DictReader(open(ROOT/'ArtSource/Cascadeur/right_cut_reference.csv')))
start=rig.animation_data.action.frame_range[0]
maximum=0.
for index,row in enumerate(rows):
    bpy.context.scene.frame_set(int(start+index));bpy.context.view_layer.update()
    for name,prefix in [('ReferenceHilt','hilt'),('ReferenceTip','tip'),('RightGripGuide','right'),('LeftGripGuide','left')]:
        expected=Vector((float(row[prefix+'_x']),-float(row[prefix+'_y']),float(row[prefix+'_z'])))/100
        observed=rig.matrix_world@rig.pose.bones[name].head
        maximum=max(maximum,(observed-expected).length*100)
report={'fps':fps,'frames':len(rows),'max_cascadeur_roundtrip_error_cm':maximum,'passed':maximum<.05}
(ROOT/'Saved/Cascadeur/reference-roundtrip.json').write_text(json.dumps(report,indent=2))
print(report,flush=True)
os._exit(0 if report['passed'] else 1)
