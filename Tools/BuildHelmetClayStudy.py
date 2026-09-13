"""Reproducible, isolated MEL17 geometry-only study; no accepted asset imports."""
from pathlib import Path
import sys, math, argparse, json, hashlib
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'Saved/ArtRuntime')]
import bpy
from mathutils import Vector

p=argparse.ArgumentParser()
p.add_argument('--revision',default='001')
p.add_argument('--samples',type=int,default=32)
args=p.parse_args()
OUT=ROOT/'ArtSource/StyleReference/MEL17/GeometryReview'/f'Clay_v{args.revision}'
if OUT.exists(): p.error('Revision exists; choose a new revision to preserve evidence.')
OUT.mkdir(parents=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name,color,roughness):
    m=bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1)
    b.inputs['Roughness'].default_value=roughness;b.inputs['Metallic'].default_value=0
    b.inputs['Specular IOR Level'].default_value=.22
    return m
clay=material('Uniform neutral clay — geometry only',(.39,.39,.39),.88)
recess=material('Recessed cavity',(.016,.016,.016),1)
stage=material('Neutral stage',(.105,.105,.105),1)
parts=[]

def surface(name,fn,nu,nv,thickness=.009,bevel=.0015,mat=clay):
    verts=[];faces=[];lookup={};grid=[]
    for j in range(nv+1):
        row=[]
        for i in range(nu+1):
            v=tuple(fn(i/nu,j/nv));k=tuple(round(q,7) for q in v)
            if k not in lookup:lookup[k]=len(verts);verts.append(v)
            row.append(lookup[k])
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            f=list(dict.fromkeys([grid[j][i],grid[j][i+1],grid[j+1][i+1],grid[j+1][i]]))
            if len(f)>2:faces.append(f)
    return mesh(name,verts,faces,thickness,bevel,mat)

def mesh(name,verts,faces,thickness=.009,bevel=.0015,mat=clay):
    d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update()
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mat)
    # Face winding is made coherent before thickness; loose pole duplicates are absent.
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
    for f in d.polygons:f.use_smooth=True
    if thickness:
        s=o.modifiers.new('Editable physical shell thickness','SOLIDIFY');s.thickness=thickness;s.offset=-1
        s.use_even_offset=True
    if bevel:
        b=o.modifiers.new('Restrained physical edge radius','BEVEL');b.width=bevel;b.segments=3
        b.limit_method='ANGLE';b.angle_limit=math.radians(35)
    parts.append(o);return o

def lerp(a,b,t):return a+(b-a)*t
def interp(points,t):
    for (a,x),(b,y) in zip(points,points[1:]):
        if t<=b:return lerp(x,y,max(0,(t-a)/(b-a)))
    return points[-1][1]

# Two shallow convex forged crown panels meet on a longitudinal ridge.
# The roof/brow boundary remains a real construction break, independent of shading.
def roof_edge_height(theta):
    lateral=abs(math.sin(theta))
    # Front runs have a deliberate center cusp and a shallow bow toward each
    # temple. Preserve the already-reviewed rear boundary and endpoint heights.
    run=lateral if math.cos(theta)>=0 else lateral*lateral
    return 1.10-.101*run-.097*(1-math.cos(theta))/2

def crown(theta,t,side):
    y=-.31*math.cos(theta)
    edgez=roof_edge_height(theta)
    ridge=interp([(-.31,1.10),(-.075,1.205),(.025,1.193),(.16,1.145),(.24,1.085),(.31,1.003)],y)
    x=.299*math.sin(theta)*(1-t)
    # A steep short shoulder rolls into a shallower peaked roof panel.
    def profile(q):return 2.15*q-1.60*.022*math.log1p(math.exp((q-.28)/.022))
    roof=(profile(t)-profile(0))/(profile(1)-profile(0))
    z=lerp(edgez,ridge,roof)+.006*math.sin(math.pi*t)*math.sin(theta)
    return side*x,y,z
for side in [-1,1]:
    surface(('Left' if side<0 else 'Right')+' convex peaked crown',
            lambda u,v,s=side:crown(math.pi*u,v,s),56,20,.009,.0022)
    def roof_return(u,v,s=side):
        a=math.pi*u;x,y,z=crown(a,.075*v,s)
        return x+s*.004*math.sin(a)*(1-v),y-.004*math.cos(a)*(1-v),z+lerp(-.004,.002,v)
    surface(('Left' if side<0 else 'Right')+' folded crown perimeter ledge',roof_return,56,5,.004,.001)

# A broad forged brow sweeps out toward the face; upper edge tucks under the roof.
def brow(theta,t,side):
    r=lerp(.314,.296,t)+.008*math.sin(math.pi*t)
    depth=lerp(.394,.307,t)+.018*math.sin(math.pi*t)
    z0=.806+.018*math.sin(theta)
    z1=roof_edge_height(theta)+.006
    sf=math.sin(theta)
    yf=math.cos(theta)-.38*sf*(1-sf)*(1-.65*t)
    tuck=max(0,(theta/math.radians(70)-.78)/.22)**2
    return side*(r*sf-.016*tuck*(1-.5*t)),-depth*yf,lerp(z0,z1,t)
for side in [-1,1]:
    surface(('Left' if side<0 else 'Right')+' wrapping brow',
            lambda u,v,s=side:brow(u*math.radians(70),v,s),36,24,.012,.0022)

# Separate cheek halves preserve a crisp center keel while longitudinal and
# transverse curvature provide a compound surface, turning into the temple.
def cheek(u,v,side):
    width=.225+.089*(2*v-v*v)
    depth=.277+.112*(2*v-v*v)
    # Continuous first derivative away from the intentional center and temple break.
    a=u*math.radians(70);s=math.sin(a)
    yf=math.cos(a)-.32*s*(1-s)
    tuck=max(0,(u-.78)/.22)**2
    x=width*s-(.008+.008*v)*tuck
    y=-depth*yf-.014*math.sin(math.pi*v)*math.sin(math.pi*u)
    z=lerp(.357+.049*s,.778+.019*s,v)
    return side*x,y,z
for side in [-1,1]:
    surface(('Left' if side<0 else 'Right')+' compound cheek and chin',
            lambda u,v,s=side:cheek(u,v,s),40,36,.012,.0022)
    # A narrow returned lower flange is modeled in depth, not an added bright line.
    surface(('Left' if side<0 else 'Right')+' inward chin return',
            lambda u,v,s=side:(lerp(cheek(u,0,s)[0],cheek(u,0,s)[0]*.91,v),
                               lerp(cheek(u,0,s)[1],cheek(u,0,s)[1]+.034,v),
                               cheek(u,0,s)[2]+.012*v),40,3,.007,.001)

# Rear and side closure: inferred from the visible temple construction.
def rear(u,v):
    a=math.radians(65)+math.radians(230)*u
    width=.216+.087*(1-(1-v)**4);depth=.21+.10*(1-(1-v)**3)
    z0=.412+.013*(-math.cos(a));z1=roof_edge_height(a)
    return width*math.sin(a),-depth*math.cos(a),lerp(z0,z1,v)
surface('Continuous inferred rear and temple shell',rear,64,32,.009,.0015)

# Angular flush hinge covers sit over the temple shell and overlap the slit ends.
for side in [-1,1]:
    x=side*.291
    outline=[(y-.055,z) for y,z in [(-.061,.867),(-.090,.835),(-.067,.781),(-.025,.758),(.008,.804),(-.011,.847)]]
    baseoutline=[(-.093+(y+.093)*1.12,.813+(z-.813)*1.10) for y,z in outline]
    baseverts=[(side*.279,y,z) for y,z in baseoutline]+[(side*.292,y,z) for y,z in baseoutline]
    n=len(outline);basefaces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh(('Left' if side<0 else 'Right')+' recessed hinge seat',baseverts,basefaces,0,.0015)
    verts=[(x,y,z) for y,z in outline]+[(x+side*.009,y,z) for y,z in outline]
    n=len(outline);faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    hinge=mesh(('Left' if side<0 else 'Right')+' seated angular hinge cover',verts,faces,0,.002)
    for f in hinge.data.polygons:f.use_smooth=False

# Recess is smaller than the outer shell, so the slit is a genuine open gap.
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,location=(0,.015,.75))
o=bpy.context.object;o.name='Recessed dark interior';o.scale=(.265,.235,.32);o.data.materials.append(recess)
for f in o.data.polygons:f.use_smooth=True
parts.append(o)
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.205,depth=.16,location=(0,.015,.30))
o=bpy.context.object;o.name='Neutral recessed neck support';o.data.materials.append(recess);parts.append(o)
o.hide_render=True

assembly=bpy.data.objects.new('Helmet clay assembly',None);bpy.context.collection.objects.link(assembly)
for o in parts:o.parent=assembly
assembly.scale=(.93,1,1)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=args.samples
scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=6
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene.world=bpy.data.worlds.new('Neutral gray world');scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.35,.35,.35,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.35
lights=[]
for name,loc,power,size in [('Broad neutral key',(-2.6,-4,4),600,3),('Soft neutral fill',(3,-2,2.3),110,3),('Neutral separation',(1.5,2,3),220,2)]:
    l=bpy.data.lights.new(name,'AREA');l.energy=power;l.size=size;l.color=(1,1,1)
    o=bpy.data.objects.new(name,l);bpy.context.collection.objects.link(o);o.location=loc
    o.rotation_euler=(Vector((0,0,.75))-o.location).to_track_quat('-Z','Y').to_euler()
    lights.append({'name':name,'location':loc,'power':power,'size':size})
c=bpy.data.cameras.new('Matched clay review camera');camera=bpy.data.objects.new(c.name,c);bpy.context.collection.objects.link(camera)
scene.camera=camera;c.type='ORTHO';c.ortho_scale=1.32;c.lens=85
target=Vector((0,-.01,.75));views=[]
for name,position in [('three_quarter',(-1.45,-4,1.22)),('front',(0,-4,.98)),('side',(-4,-.05,1.02)),('rear_three_quarter',(-2.8,3,1.22)),('rear',(0,4,.98))]:
    camera.location=position;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    diagnostic=name not in ('three_quarter','front')
    scene.render.resolution_x=450 if diagnostic else 900;scene.render.resolution_y=550 if diagnostic else 1100;scene.render.resolution_percentage=100
    scene.cycles.samples=16 if diagnostic else args.samples
    scene.render.filepath=str(OUT/f'{name}.png');bpy.context.view_layer.update()
    if name=='three_quarter':bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'Helmet_Clay_v{args.revision}.blend'))
    bpy.ops.render.render(write_still=True)
    views.append({'name':name,'location':list(position),'target':list(target),'resolution':[scene.render.resolution_x,scene.render.resolution_y],
                  'samples':scene.cycles.samples,'camera_matrix':[list(row) for row in camera.matrix_world],
                  'sha256':hashlib.sha256((OUT/f'{name}.png').read_bytes()).hexdigest()})
audit=[];deps=bpy.context.evaluated_depsgraph_get()
for obj in parts:
    if obj.type!='MESH' or not any(m==clay for m in obj.data.materials):continue
    obj.data.calc_loop_triangles();evaluated=obj.evaluated_get(deps);d=evaluated.to_mesh();d.calc_loop_triangles()
    used=set(v for face in d.polygons for v in face.vertices)
    audit.append({'name':obj.name,'base_triangles':len(obj.data.loop_triangles),'evaluated_triangles':len(d.loop_triangles),
                  'degenerate_faces':sum(f.area<1e-12 for f in d.polygons),'loose_vertices':len(d.vertices)-len(used)})
    evaluated.to_mesh_clear()
receipt={'revision':args.revision,'source':'06-riot-inspired.png','assembly':'Helmet clay assembly','bpy':bpy.app.version_string,
         'render':{'engine':'Cycles CPU','samples':args.samples,'resolution':[900,1100],'ortho_scale':c.ortho_scale,'view_transform':'AgX','look':scene.view_settings.look},
         'views':views,'lights':lights,'materials':'Uniform matte gray, no image textures or normal fields; dark cavity/support only',
         'editable_mesh_objects':len(parts),'base_vertices':sum(len(o.data.vertices) for o in parts if o.type=='MESH'),
         'metal_audit':audit,'base_metal_triangles':sum(a['base_triangles'] for a in audit),'evaluated_metal_triangles':sum(a['evaluated_triangles'] for a in audit),
         'min_shell_thickness':min(m.thickness for o in parts for m in o.modifiers if m.type=='SOLIDIFY'),
         'joint':'Brow top rises 0.006 above crown boundary and tucks 0.003 radially beneath it; modeled overlap. Slit return is solidified brow/cheek edge.',
         'scope':'Geometry review only. Rear is inferred. Reference projection is estimated, not camera-solved. No runtime or steel changes.'}
(OUT/'settings.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
(OUT/'generator.py').write_text(Path(__file__).read_text(encoding='utf-8'),encoding='utf-8')
print('CLAY_COMPLETE',str(OUT))
