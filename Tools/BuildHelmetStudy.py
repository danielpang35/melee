"""Isolated helmet proof. Accepted v025 steel values; no runtime asset edits."""
from pathlib import Path
import sys, math, argparse, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'Saved/ArtRuntime'),str(ROOT/'Saved/VideoRuntime')]
import bpy
from mathutils import Vector
import BuildPaintedSteelStudy as base

p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--samples',type=int,default=32)
args=p.parse_args();OUT=ROOT/f'ArtSource/StyleReference/MEL17/Helmet_v{args.revision}'
if OUT.exists():p.error('Choose a new revision; preserve reviewed candidates.')
OUT.mkdir(parents=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
SOURCE=ROOT/'ArtSource/StyleReference/MEL17/Steel_v025/Steel_v025.blend'
with bpy.data.libraries.load(str(SOURCE),link=False) as (available,loaded):
    loaded.materials=['StylizedSteel','PolishedConstructionEdges']
steel=bpy.data.materials['StylizedSteel'];edge=bpy.data.materials['PolishedConstructionEdges']
dark=base.mat('Dark quilted padding',(.018,.022,.026),0,.88)
inside=base.mat('Unlit visor interior',(.004,.005,.006),0,1)

def mesh(name,verts,faces,material,thickness=.008,bevel=.003,curved=False):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);data.materials.append(material)
    if curved:
        counts={tuple(sorted((p.vertices[i],p.vertices[(i+1)%len(p.vertices)]))):0 for p in data.polygons for i in range(len(p.vertices))}
        for p in data.polygons:
            for i in range(len(p.vertices)):counts[tuple(sorted((p.vertices[i],p.vertices[(i+1)%len(p.vertices)])))]+=1
        crease=data.attributes.new('crease_edge','FLOAT','EDGE')
        for e in data.edges:
            a,b=[data.vertices[k].co for k in e.vertices]
            boundary=counts[tuple(sorted(e.vertices))]==1
            central=abs(a.x)<1e-6 and abs(b.x)<1e-6
            lower='cranial' in name and a.z<.82 and b.z<.82
            transverse='cranial' in name and abs(a.z-b.z)<.06 and min(a.z,b.z)>.9
            cheek='faceplate' in name and .05<abs(a.x)<.26 and .05<abs(b.x)<.26 and abs(a.z-b.z)>.3
            temple='cranial' in name and tuple(sorted(e.vertices)) in [(6,7),(7,8),(16,17),(17,18)]
            crease.data[e.index].value=1 if boundary or lower else (.85 if central else (.65 if temple else (.2 if transverse else (.5 if cheek else (.4 if 'cranial' in name else .2)))))
        sub=o.modifiers.new('Shallow cranial and panel curvature','SUBSURF');sub.levels=2;sub.render_levels=2
        for poly in data.polygons:poly.use_smooth=True
    if thickness:
        s=o.modifiers.new('Physical steel thickness','SOLIDIFY');s.thickness=thickness;s.offset=-1
    if bevel:
        b=o.modifiers.new('Restrained construction bevel','BEVEL');b.width=bevel;b.segments=3
        if 'faceplate' in name or 'cheek return' in name:data.materials.append(edge);b.material=1
        if not curved:
            w=o.modifiers.new('Broad planar highlights','WEIGHTED_NORMAL');w.keep_sharp=True;w.weight=40
    return o

def line(name,points,material,radius=.002):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=2
    s=c.splines.new('POLY');s.points.add(len(points)-1)
    for p,co in zip(s.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);c.materials.append(material);return o

# Longitudinal cranial planes and a short fore-aft crest, not a radial cone.
axis=[(0,-.395,.804),(0,-.355,1.02),(0,-.12,1.16),(0,.13,1.145),(0,.285,.98),(0,.315,.74)]
sidepoints=[(.225,-.292,.804),(.235,-.225,1.015),(.215,-.055,1.10),(.23,.14,1.075),(.235,.26,.94),(.23,.24,.74),(.318,-.055,.779),(.315,-.08,.975),(.315,.125,.94),(.325,.03,.76)]
panels=[(0,6,7,1),(1,7,8,2),(2,8,9,3),(3,9,10,4),(4,10,11,5),(6,12,13,7),(7,13,14,9,8),(9,14,10),(10,14,15,11),(12,15,14,13),(11,15,12,6)]
verts=list(axis);faces=[]
for sign in [1,-1]:
    offset=len(verts)-6;verts.extend([(sign*x,y,z) for x,y,z in sidepoints])
    for panel in panels:
        ids=[i if i<6 else i+offset for i in panel]
        faces.append(tuple(ids if sign==1 else ids[::-1]))
crown=mesh('Shaped cranial vault and forehead',verts,faces,steel,curved=True)

# Front visor/bevor: two broad frontal planes and narrower temple turns.
front_angles=[math.radians(a) for a in [-90,-68,-42,0,42,68,90]]
upper=[(.325*math.sin(a),-.392*math.cos(a),.778) for a in front_angles]
lower=[(.23*math.sin(a),-.282*math.cos(a),.32+.065*abs(math.sin(a))) for a in front_angles]
front=mesh('Long tapered faceplate',lower+upper,[(i,i+1,i+8,i+7) for i in range(6)],steel,curved=True)
line('Eye slit lower lip',[(x,y-.001,z+.001) for x,y,z in upper[1:-1]],edge,.002)

# Narrow fitted cheek returns overlap the mask at a tapered construction seam.
bpy.context.view_layer.update()
surface=front.evaluated_get(bpy.context.evaluated_depsgraph_get())
for side in [-1,1]:
    guesses=[(.259,-.231,.774),(.308,-.115,.774),(.325,-.005,.774),
             (.196,-.15,.377),(.224,-.065,.384),(.23,-.005,.389)]
    cheek=[]
    for x,y,z in guesses:
        hit,point,normal,index=surface.closest_point_on_mesh(Vector((side*x,y,z)))
        if not hit:raise RuntimeError('Cheek projection failed')
        cheek.append(tuple(point+normal*.002))
    panels=[(0,1,4,3),(1,2,5,4)]
    mesh('Fitted cheek return',cheek,[q if side==1 else q[::-1] for q in panels],steel,.002,.0012)

# Rear and side enclosure; unseen construction is explicitly inferred.
rear_angles=[math.radians(a) for a in range(90,271,15)]
rv=[(.325*math.sin(a),-.32*math.cos(a),.779) for a in rear_angles]
rv += [((.23+.015*max(-math.cos(a),0))*math.sin(a),-.255*math.cos(a),.38+.005*abs(math.sin(a))) for a in rear_angles]
count=len(rear_angles)
mesh('Rear neck enclosure',rv,[(i,i+count,i+count+1,i+1) for i in range(count-1)],steel)
line('Rear lower rim',rv[count:],edge,.002)

# The dark opening is recessed; the eye slit remains an actual gap between shells.
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=(0,.005,.71))
o=bpy.context.object;o.name='Recessed dark helmet interior';o.scale=(.29,.29,.39);o.data.materials.append(inside)
for q in o.data.polygons:q.use_smooth=True

# Restrained six-sided visor pivots.
for side in [-1,1]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.025,depth=.011,location=(side*.328,-.02,.764),rotation=(0,math.pi/2,0))
    o=bpy.context.object;o.name='Visor hinge';o.data.materials.append(edge)
    bevel=o.modifiers.new('Hinge bevel','BEVEL');bevel.width=.002;bevel.segments=2
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.005,location=(side*.334,-.02,.764))
    bpy.context.object.data.materials.append(steel)

# One compact irregular folded collar, with a quiet recessed neck opening.
cv=[];cf=[];count=48
for j in range(4):
    for i in range(count):
        a=2*math.pi*i/count;r=.232+.018*math.sin(j*math.pi/3)+.009*math.sin(a*3+.5)
        cv.append((r*math.sin(a),r*.95*math.cos(a),.16+j*.037+.013*math.cos(a)+.007*math.sin(a*2+j*.6)))
for j in range(3):
    for i in range(count):a=j*count+i;b=j*count+(i+1)%count;cf.append((a,b,b+count,a+count))
collar=mesh('Folded padded neck wrap',cv,cf,dark,.018,.002)
for poly in collar.data.polygons:poly.use_smooth=True
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.21,depth=.13,location=(0,0,.285))
bpy.context.object.name='Dark neck support';bpy.context.object.data.materials.append(dark)

parts=list(bpy.context.scene.objects);assembly=bpy.data.objects.new('Helmet proof assembly',None);bpy.context.collection.objects.link(assembly)
for part in parts:part.parent=assembly
assembly.scale=(.90,.97,1)

scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=args.samples;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
scene.world=bpy.data.worlds.new('Cool daylight fill');scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.35,.45,.62,1);bg.inputs['Strength'].default_value=.3
bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.data.materials.append(base.mat('Warm neutral stage',(.20,.185,.16),0,.9))
for name,loc,power,size,color in [('Warm key',(-2,-3,4),750,3,(1,.88,.72)),('Cool rim',(3,1,3),100,1,(.67,.81,1)),('Soft front',(-1,-4,1.5),15,3,(.8,.86,1))]:
    l=bpy.data.lights.new(name,'AREA');l.energy=power;l.size=size;l.color=color
    if name=='Warm key':l.shape='RECTANGLE';l.size_y=.18
    o=bpy.data.objects.new(name,l);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.75))-o.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.cameras.new('Helmet review camera');camera=bpy.data.objects.new('Helmet review camera',c);bpy.context.collection.objects.link(camera);scene.camera=camera
c.type='ORTHO';c.ortho_scale=1.48
views=[('helmet',(1.45,-4,1.25),1200,1200),('front',(0,-4,.96),720,900)]
receipts=[]
for name,position,width,height in views:
    camera.location=position;camera.rotation_euler=(Vector((0,0,.68))-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.resolution_x=width;scene.render.resolution_y=height;scene.render.resolution_percentage=100
    scene.render.filepath=str(OUT/f'{name}.png');bpy.context.view_layer.update()
    if name=='helmet':bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'Helmet_v{args.revision}.blend'))
    bpy.ops.render.render(write_still=True)
    receipts.append({'view':name,'camera_matrix':[list(r) for r in camera.matrix_world],'sha256':hashlib.sha256((OUT/f'{name}.png').read_bytes()).hexdigest()})
(OUT/'settings.json').write_text(json.dumps({'revision':args.revision,'steel_source':str(SOURCE.relative_to(ROOT)),'samples':args.samples,'views':receipts,'scope':'static helmet proof; rear construction inferred; no runtime or animation changes'},indent=2))
(OUT/'generator.py').write_text(Path(__file__).read_text(encoding='utf-8'),encoding='utf-8')
print('HELMET_COMPLETE',args.revision)
