"""Inspect user supplied FBX files without modifying them."""
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'Saved/ArtRuntime'))
import bpy
from mathutils import Vector
out = ROOT/'Saved/UserKnight'
out.mkdir(parents=True, exist_ok=True)
results = []
for source in ['D:/fHHDATOQt9zB6wsFpnZJw.fbx', 'D:/20260909174448_72c77e03.fbx']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=source)
    meshes = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH': continue
        bounds = [obj.matrix_world@Vector(v) for v in obj.bound_box]
        meshes.append(dict(name=obj.name, vertices=len(obj.data.vertices), polygons=len(obj.data.polygons),
            minimum=[min(v[i] for v in bounds) for i in range(3)], maximum=[max(v[i] for v in bounds) for i in range(3)],
            materials=[m.name if m else None for m in obj.data.materials], groups=len(obj.vertex_groups)))
    record = dict(source=source, meshes=meshes,
        armatures=[dict(name=o.name,bones=len(o.data.bones)) for o in bpy.data.objects if o.type=='ARMATURE'],
        images=[dict(name=i.name,size=list(i.size),packed=bool(i.packed_file),path=i.filepath) for i in bpy.data.images])
    results.append(record)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/(Path(source).stem+'.blend')))
(out/'inspection.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
