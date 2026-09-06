from pathlib import Path
import json
import unreal as u
report={}
for name in ('SK_CitadelKnight','SK_CitadelArms','SM_CitadelSword','SM_ArcadeArch','SM_SlateRoof'):
    mesh=u.load_asset('/Game/Visual/Citadel/Meshes/'+name)
    entry={'class':mesh.get_class().get_name()}
    if name.startswith('SK_'):
        comp=u.new_object(u.PoseableMeshComponent)
        comp.set_skinned_asset_and_update(mesh)
        entry['bones']=[]
        for i in range(comp.get_num_bones()):
            entry['bones'].append(str(comp.get_bone_name(i)))
        entry['skeleton']=str(mesh.get_editor_property('skeleton'))
        entry['materials']=[str(slot.material_interface) for slot in mesh.get_editor_property('materials')]
    report[name]=entry
(Path(u.Paths.project_saved_dir())/'citadel-import-inspection.json').write_text(json.dumps(report,indent=2))
u.log('CITADEL INSPECTION COMPLETE')
