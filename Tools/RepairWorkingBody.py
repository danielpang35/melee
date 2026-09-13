"""Isolated MB surface repair and repeatable multi-angle source verification.

Run with Blender --background --python Tools/RepairWorkingBody.py -- <stage>.
Never changes working selection or imports/promotes assets automatically.
"""
import bpy, bmesh, json, math, hashlib, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'ArtSource/UserMaleBody/MB_v004_Project/Male_Body_Project.blend'
OUT = ROOT / 'ArtSource/UserMaleBody/MB_v005_SurfaceRepair'
EVIDENCE = ROOT / 'Saved/WorkingBodyRepair'
OUT.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def intersections(mesh):
    faces = [tuple(p.vertices) for p in mesh.polygons]
    tree = BVHTree.FromPolygons([v.co for v in mesh.vertices], faces, all_triangles=True)
    return [(a, b) for a, b in tree.overlap(tree)
            if a < b and not set(faces[a]).intersection(faces[b])]

def audit(obj):
    mesh = obj.data
    bm = bmesh.new(); bm.from_mesh(mesh)
    pairs = intersections(mesh)
    result = dict(vertices=len(mesh.vertices), triangles=len(mesh.polygons),
        boundary_edges=sum(e.is_boundary for e in bm.edges),
        nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),
        inconsistent_winding_edges=sum(e.is_manifold and not e.is_contiguous for e in bm.edges),
        loose_vertices=sum(not v.link_edges for v in bm.verts),
        degenerate_faces=sum(f.calc_area() < 1e-12 for f in bm.faces),
        duplicate_faces=len(mesh.polygons)-len({tuple(sorted(p.vertices)) for p in mesh.polygons}),
        nonadjacent_intersections=len(pairs),
        opposed_custom_normal_faces=sum(any(mesh.corner_normals[i].vector.dot(p.normal) < -.1
                                          for i in p.loop_indices) for p in mesh.polygons),
        unweighted_vertices=sum(not any(g.weight > 0 for g in v.groups) for v in mesh.vertices))
    bm.free()
    return result

def open_source(path=SOURCE):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    bpy.context.window.scene = bpy.data.scenes['Rigged body - working']
    scene = bpy.context.scene
    scene.frame_set(1)
    return scene

def setup_camera(scene, view, target=(0, 0, .91), scale=2.05):
    obj = bpy.data.objects.get('MB_ValidationCamera')
    if obj is None:
        obj = bpy.data.objects.new('MB_ValidationCamera', bpy.data.cameras.new('MB_ValidationCamera'))
        scene.collection.objects.link(obj)
    offsets = {'front':(0,-4,0), 'rear':(0,4,0), 'left':(4,0,0), 'right':(-4,0,0),
               'rear-left':(3,4,.3), 'rear-right':(-3,4,.3)}
    obj.location = Vector(target) + Vector(offsets[view])
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    obj.data.type = 'ORTHO'; obj.data.ortho_scale = scale; scene.camera = obj
    return dict(name=view, location=list(obj.location), rotation=list(obj.rotation_euler),
                target=list(target), orthographic_scale=scale)

def render(scene, folder, views=('front','rear','left','right'), target=(0,0,.91), scale=2.05, textured=False):
    folder.mkdir(parents=True, exist_ok=True)
    scene.render.engine = 'BLENDER_EEVEE' if textured else 'BLENDER_WORKBENCH'
    if textured:
        if scene.world is None:scene.world=bpy.data.worlds.new('MB_ReviewWorld')
        scene.world.use_nodes=True
        background=scene.world.node_tree.nodes.get('Background')
        background.inputs['Color'].default_value=(.12,.12,.12,1)
        background.inputs['Strength'].default_value=.45
        for name,loc,power in [('Front',(-3,-4,4),650),('Rear',(3,4,3),600),('Top',(0,0,4),350)]:
            light=bpy.data.objects.get('MB_Review'+name)
            if light is None:
                light=bpy.data.objects.new('MB_Review'+name,bpy.data.lights.new('MB_Review'+name,'AREA'))
                scene.collection.objects.link(light)
            light.location=loc; light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
            light.data.energy=power; light.data.shape='DISK'; light.data.size=4
    scene.render.resolution_x = scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.threads_mode='FIXED'; scene.render.threads=4
    scene.display.shading.light='STUDIO'; scene.display.shading.studiolight_rotate_z=.5
    scene.display.shading.color_type='SINGLE'; scene.display.shading.single_color=(.55,.55,.55)
    scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True
    scene.display.shading.cavity_type='BOTH'; scene.display.shading.show_specular_highlight=True
    scene.display.shading.background_type='VIEWPORT'; scene.display.shading.background_color=(.08,.08,.08)
    scene.render.image_settings.file_format='PNG'
    captures=[]
    for view in views:
        camera=setup_camera(scene,view,target,scale)
        path=folder/(view+'.png'); scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
        captures.append(dict(path=str(path.relative_to(ROOT)),camera=camera,frame=scene.frame_current))
    return captures

def select_lod(scene,lod):
    for layer in scene.view_layers:
        def enable(c):
            c.exclude=False; c.hide_viewport=False
            for child in c.children:enable(child)
        enable(layer.layer_collection)
    for c in bpy.data.collections:
        c.hide_render=False; c.hide_viewport=False
    for o in scene.objects:
        if o.type=='MESH':
            show=o.name==f'MB_Rigged_LOD{lod}'
            o.hide_render=not show; o.hide_set(not show); o.hide_viewport=False

def repair_surface(obj):
    """Relax only intersecting patches and two edge rings, retaining topology/UVs."""
    mesh=obj.data
    original=[v.co.copy() for v in mesh.vertices]
    # Store keys before editing. Blender's Basis can share vertex storage; adding
    # a delta in place afterwards may apply the correction twice.
    key_data=[]
    if mesh.shape_keys:
        for key in mesh.shape_keys.key_blocks:
            key_data.append((key.name,key.value,[v.co.copy() for v in key.data]))
        obj.shape_key_clear()
    for name in ('custom_normal','sharp_edge','sharp_face'):
        if name in mesh.attributes:mesh.attributes.remove(mesh.attributes[name])
    for p in mesh.polygons:p.use_smooth=True
    mesh.update()
    adjacency=[set() for v in mesh.vertices]
    for e in mesh.edges:
        a,b=e.vertices; adjacency[a].add(b); adjacency[b].add(a)
    history=[]
    for iteration in range(100):
        pairs=intersections(mesh)
        opposed={p.index for p in mesh.polygons if any(mesh.corner_normals[i].vector.dot(p.normal)<-.05 for i in p.loop_indices)}
        history.append([len(pairs),len(opposed)])
        if not pairs and not opposed:break
        core={v for pair in pairs for f in pair for v in mesh.polygons[f].vertices}
        core.update(v for f in opposed for v in mesh.polygons[f].vertices)
        ring1={n for v in core for n in adjacency[v]}-core
        ring2={n for v in ring1 for n in adjacency[v]}-core-ring1
        ring3={n for v in ring2 for n in adjacency[v]}-core-ring1-ring2
        strength={**{v:.08 for v in ring3},**{v:.18 for v in ring2},**{v:.30 for v in ring1},**{v:.48 for v in core}}
        positions={i:mesh.vertices[i].co.lerp(sum((mesh.vertices[j].co for j in adjacency[i]),Vector())/len(adjacency[i]),s)
                   for i,s in strength.items() if adjacency[i]}
        for i,co in positions.items():mesh.vertices[i].co=co
        mesh.update()
    deltas=[v.co-original[i] for i,v in enumerate(mesh.vertices)]
    for name,value,coords in key_data:
        key=obj.shape_key_add(name=name,from_mix=False)
        key.data.foreach_set('co',[x for i,co in enumerate(coords) for x in co+deltas[i]])
        key.value=value
    mesh.update()
    return dict(intersection_history=history,modified_vertices=sum(d.length>1e-7 for d in deltas),
                maximum_displacement_cm=max(d.length for d in deltas),after=audit(obj))

def main():
    stage=sys.argv[sys.argv.index('--')+1]
    scene=open_source()
    if stage=='diagnose':
        before={f'LOD{i}':audit(bpy.data.objects[f'MB_Rigged_LOD{i}']) for i in range(4)}
        select_lod(scene,0)
        captures=render(scene,EVIDENCE/'before')
        captures+=render(scene,EVIDENCE/'before-arms',('rear','rear-left','rear-right'),(0,0,1.19),1.35)
        (EVIDENCE/'before.json').write_text(json.dumps(dict(source=str(SOURCE),source_sha256=digest(SOURCE),audit=before,captures=captures),indent=2))
    elif stage=='repair':
        assert not (OUT/'Male_Body_SurfaceRepair.blend').exists(), 'Retain prior repair before another attempt'
        repaired={}
        for i in range(4):
            obj=bpy.data.objects[f'MB_Rigged_LOD{i}']
            obj.data=obj.data.copy()
            repaired[f'LOD{i}']=repair_surface(obj)
            print('REPAIR',i,json.dumps({k:v for k,v in repaired[f'LOD{i}'].items() if k!='intersection_history'}),flush=True)
        select_lod(scene,0)
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Male_Body_SurfaceRepair.blend'))
        captures=render(scene,EVIDENCE/'repaired')
        captures+=render(scene,EVIDENCE/'repaired-arms',('rear','rear-left','rear-right'),(0,0,1.19),1.35)
        (EVIDENCE/'repair.json').write_text(json.dumps(dict(source_sha256=digest(SOURCE),repaired=repaired,captures=captures),indent=2))
    elif stage=='inspect':
        open_source(OUT/'Male_Body_SurfaceRepair.blend')
        results={}
        for i in range(4):
            o=bpy.data.objects[f'MB_Rigged_LOD{i}']; me=o.data
            ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
            results[i]=dict(audit=audit(o),eval_max_delta=max((a.co-b.co).length for a,b in zip(me.vertices,ev.vertices)),
                basis_max_delta=max((a.co-b.co).length for a,b in zip(me.vertices,me.shape_keys.key_blocks[0].data)),
                attributes=[a.name for a in me.attributes])
        print('INSPECT',json.dumps(results))
    elif stage=='normal-test':
        scene=open_source(OUT/'SurfaceRepair_trial01.blend')
        for i in range(4):
            o=bpy.data.objects[f'MB_Rigged_LOD{i}']; me=o.data
            for name in ('custom_normal','sharp_edge','sharp_face'):
                if name in me.attributes:me.attributes.remove(me.attributes[name])
            for p in me.polygons:p.use_smooth=True
            me.update()
            print('NORMAL_AUDIT',i,json.dumps(audit(o)),flush=True)
        select_lod(scene,0)
        render(scene,EVIDENCE/'normal-test',('rear','rear-left','rear-right'),(0,0,1.19),1.35)
    elif stage=='lod3':
        scene=open_source(OUT/'Male_Body_SurfaceRepair.blend')
        select_lod(scene,0)
        old=bpy.data.objects['MB_Rigged_LOD3']
        # The isolated trial retains this coarse mesh; rebuild from repaired LOD0.
        old.name='MB_Rigged_LOD3_PreRebuild'; old.hide_render=True; old.hide_set(True)
        obj=bpy.data.objects['MB_Rigged_LOD0'].copy(); obj.data=obj.data.copy()
        scene.collection.objects.link(obj); obj.name='MB_Rigged_LOD3'
        obj.shape_key_clear()
        obj.data.materials.clear(); obj.data.materials.append(old.data.materials[0])
        for o in scene.objects:o.select_set(False)
        obj.hide_set(False); obj.select_set(True); bpy.context.view_layer.objects.active=obj
        mod=obj.modifiers.new('Rebuilt coarse surface','DECIMATE'); mod.ratio=3998/len(obj.data.polygons)
        # Apply decimation in rest geometry, before the armature modifier.
        bpy.ops.object.modifier_move_up(modifier=mod.name)
        bpy.ops.object.modifier_apply(modifier=mod.name)
        result=repair_surface(obj)
        print('LOD3_REBUILT',json.dumps({k:v for k,v in result.items() if k!='intersection_history'}),flush=True)
        select_lod(scene,3)
        captures=render(scene,EVIDENCE/'lod3-rebuilt')
        select_lod(scene,0)
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Male_Body_SurfaceRepair.blend'))
        (EVIDENCE/'lod3-rebuilt.json').write_text(json.dumps(dict(result=result,captures=captures),indent=2))
    else:
        raise ValueError(stage)

if __name__=='__main__':main()
