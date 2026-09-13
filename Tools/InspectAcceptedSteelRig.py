"""Read only the accepted packed studio rig, without rerendering or editing it."""
from pathlib import Path
import sys,json,hashlib
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'Saved/ArtRuntime'))
import bpy
from mathutils import Vector
source=root/'ArtSource/StyleReference/MEL17/Steel_v025/Steel_v025.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
def bounds(obj):
    points=[obj.matrix_world@Vector(p) for p in obj.bound_box]
    return [[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
result={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'engine':scene.render.engine,'cycles_samples':scene.cycles.samples,'world':{node.name:{p.name:list(p.default_value) if hasattr(p.default_value,'__len__') else p.default_value for p in node.inputs if hasattr(p,'default_value')} for node in scene.world.node_tree.nodes if node.type=='BACKGROUND'},'camera':{'type':scene.camera.data.type,'ortho_scale':scene.camera.data.ortho_scale,'matrix_world':[list(row) for row in scene.camera.matrix_world]},'display':{'view_transform':scene.view_settings.view_transform,'look':scene.view_settings.look,'exposure':scene.view_settings.exposure,'gamma':scene.view_settings.gamma,'view_settings_curve_mapping':scene.view_settings.use_curve_mapping,'display_device':scene.display_settings.display_device},'resolution':[scene.render.resolution_x,scene.render.resolution_y],'lights':[],'objects':[]}
for obj in scene.objects:
    if obj.type=='LIGHT':
        light=obj.data;forward=obj.matrix_world.to_3x3()@Vector((0,0,-1))
        result['lights'].append({'name':obj.name,'type':light.type,'shape':light.shape,'power_watts':light.energy,'size':light.size,'size_y':light.size_y,'color_linear':list(light.color),'matrix_world':[list(row) for row in obj.matrix_world],'emission_forward_blender':list(forward),'diffuse_factor':light.diffuse_factor,'specular_factor':light.specular_factor,'use_shadow':light.use_shadow})
    elif obj.type in ['MESH','CURVE']:
        result['objects'].append({'name':obj.name,'type':obj.type,'matrix_world':[list(row) for row in obj.matrix_world],'bounds_world':bounds(obj),'materials':[slot.material.name if slot.material else None for slot in obj.material_slots]})
out=root/'Saved/ArtReview/UnrealStyle/AcceptedSteelTransfer';out.mkdir(exist_ok=True,parents=True);(out/'rig_audit.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['objects','camera']},indent=2))
