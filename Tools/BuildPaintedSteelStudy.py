"""MEL-17 material capability proof on original unrigged curved coupons.

Authors new UV paint maps and real Blender geometry; never modifies reference
images, character sources or runtime assets. No likeness/acceptance is implied.
"""
import hashlib
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'Saved/ArtRuntime'), str(ROOT / 'Saved/VideoRuntime')]
import bpy
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFilter

OUT = ROOT / 'ArtSource/StyleReference/MEL17/PaintedSteel_v002'
OUT.mkdir(parents=True, exist_ok=True)

# Deliberately composed UV shapes, in 0..1000 coordinates. These are editable
# paint masses, not random face colors or sampled pixels from the portrait.
PATCHES = [
    ([(60,70),(295,45),(330,100),(272,185),(175,156),(125,209),(70,161)], '#b7b5a8', .56),
    ([(305,25),(512,15),(532,107),(469,157),(398,126),(357,182)], '#d0cdbb', .62),
    ([(540,25),(787,59),(852,131),(770,170),(675,117),(618,186)], '#a1a9ac', .36),
    ([(89,224),(157,184),(262,226),(239,291),(300,328),(207,367),(131,309)], '#919a9e', .42),
    ([(267,177),(396,155),(476,217),(461,283),(387,257),(337,318),(274,278)], '#cac7b8', .58),
    ([(494,127),(540,169),(600,145),(653,226),(605,288),(555,257),(507,301)], '#b7b9b2', .48),
    ([(680,214),(791,179),(932,249),(894,318),(824,305),(799,373),(704,318)], '#858e91', .45),
    ([(197,378),(288,340),(342,392),(316,447),(359,481),(288,502),(215,451)], '#b0b2aa', .42),
    ([(368,307),(443,326),(464,389),(521,418),(470,471),(400,421),(354,436)], '#d0cabc', .53),
    ([(535,323),(632,310),(679,365),(658,443),(588,420),(558,462),(514,395)], '#878d88', .48),
    ([(742,408),(866,372),(927,428),(872,505),(797,486),(731,537),(701,466)], '#747d80', .40),
    ([(70,444),(137,393),(198,474),(168,533),(226,581),(151,618),(85,558)], '#6c7981', .38),
    ([(269,527),(367,475),(420,512),(397,588),(436,631),(339,645),(296,599)], '#9a9b91', .43),
    ([(449,481),(498,448),(539,510),(523,583),(580,622),(525,661),(463,598)], '#bab8aa', .34),
    ([(574,491),(662,471),(727,552),(685,595),(726,665),(641,675),(595,609)], '#656e70', .42),
    ([(167,657),(267,605),(309,662),(282,713),(330,754),(241,787),(192,747)], '#7c8587', .43),
    ([(358,678),(444,647),(484,699),(461,757),(504,795),(414,819),(357,774)], '#a5a598', .39),
    ([(516,719),(593,672),(641,723),(608,777),(678,824),(576,869),(529,809)], '#737970', .41),
    ([(734,625),(826,590),(881,651),(842,714),(865,765),(782,791),(711,718)], '#92978d', .33),
    ([(106,794),(200,779),(269,850),(218,905),(171,879),(127,921),(85,862)], '#616e75', .36),
    ([(280,842),(367,810),(421,858),(398,928),(320,958),(293,908)], '#8c9086', .36),
    ([(653,855),(740,808),(808,840),(835,921),(769,963),(703,925)], '#a3a497', .29),
]

def texture_maps():
    size = 1024
    image = Image.new('RGB', (size,size))
    pixels = []
    for y in range(size):
        v = y / (size-1)
        for x in range(size):
            u = x / (size-1)
            # Broad authored value drift, no cast shadow or photogrammetry grain.
            mass = 14 * math.cos((u-.44)*math.pi*1.5) + 16*(1-v)
            pixels.append((int(77+mass),int(86+mass),int(92+mass)))
    image.putdata(pixels)
    rough = Image.new('L',(size,size),128)
    rd = ImageDraw.Draw(rough)
    rng=random.Random(17)
    # Unequal overlapping paint masses with short, directed broken brush edges.
    # The underlying composition remains the explicit PATCHES layout above.
    scales=[1.9,1.6,1.4,.8,1.45,.85,1.8,1.5,.65,1.65,.9,1.7,1.35,.75,1.65,1.8,.9,1.45,1.25,1.5,.8,1.3]
    for i,(points,color,opacity) in enumerate(PATCHES):
        cx=sum(x for x,y in points)/len(points);cy=sum(y for x,y in points)/len(points)
        points=[(cx+(x-cx)*scales[i],cy+(y-cy)*scales[i]) for x,y in points]
        polygon=[]
        for a,b in zip(points,points[1:]+points[:1]):
            for t in (0,.18,.25,.43,.5,.71,.79):
                jitter=rng.uniform(-4,4) if t else 0
                polygon.append((round((a[0]+(b[0]-a[0])*t+jitter)*size/1000),round((a[1]+(b[1]-a[1])*t+jitter)*size/1000)))
        layer = Image.new('RGBA',(size,size),(0,0,0,0))
        rgb = tuple(int(color[j:j+2],16) for j in (1,3,5))
        ImageDraw.Draw(layer).polygon(polygon,fill=(*rgb,round(min(.82,opacity+.1)*255)))
        layer=layer.filter(ImageFilter.GaussianBlur(.55))
        image = Image.alpha_composite(image.convert('RGBA'),layer).convert('RGB')
        rd.polygon(polygon,fill=93+(i%4)*9)
    # Smaller directional scumbles inside selected highlight masses break the
    # sticker-like uniform fill while preserving low-frequency value grouping.
    draw=ImageDraw.Draw(image,'RGBA')
    for cx,cy,w,h in [(190,175,130,75),(380,220,100,100),(445,378,85,68),(325,542,115,78),(550,216,85,70),(702,781,95,74)]:
        for k in range(22):
            px=cx+rng.uniform(-w/2,w/2);py=cy+rng.uniform(-h/2,h/2)
            length=rng.uniform(12,42);thick=rng.uniform(3,9)
            draw.polygon([(px,py),(px+length*.65,py-thick),(px+length,py+thick*.3),(px+length*.2,py+thick)],fill=(207,204,187,rng.randrange(15,45)))
    # Sparse broken pale accents inside the trim. Large patches dominate.
    draw=ImageDraw.Draw(image)
    for pts in [[(40,105),(43,224)],[(65,314),(70,372)],[(94,635),(104,699)],
                [(957,128),(951,220)],[(908,666),(897,749)],[(443,33),(496,25),(545,38)]]:
        draw.line(pts,fill=(178,182,174),width=3)
    image.save(OUT/'T_PaintedSteel_BaseColor.png')
    rough.save(OUT/'T_PaintedSteel_Roughness.png')
    (OUT/'paint-layout.json').write_text(json.dumps({'size':size,'patches':PATCHES,'description':'Original authored UV polygons; y=0 is top. No reference-image pixels copied.'},indent=2))

def mat(name,color,metal=0,rough=.6):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m

def painted():
    m=mat('M_PaintedSteel',(.4,.42,.42),.90,.42)
    tree=m.node_tree;p=tree.nodes.get('Principled BSDF')
    for suffix,pin,srgb in [('BaseColor','Base Color',True),('Roughness','Roughness',False)]:
        im=bpy.data.images.load(str(OUT/f'T_PaintedSteel_{suffix}.png'))
        im.colorspace_settings.name='sRGB' if srgb else 'Non-Color'
        n=tree.nodes.new('ShaderNodeTexImage');n.image=im;n.interpolation='Linear'
        tree.links.new(n.outputs['Color'],p.inputs[pin])
    return m

def surface(u,v):
    z=.15+1.25*v
    width=.34+.105*math.sin(v*math.pi*.87)
    x=(u*2-1)*width
    y=-.08-.24*math.sin(math.pi*u)*(.5+.5*math.sin(math.pi*v))-.025*math.exp(-abs(u-.5)*35)
    z-=.11*(abs(u-.5)*2)**2*v**6
    return (x,y,z)

def coupon(name,x,yaw,material,edge):
    n=40;verts=[surface(i/n,j/n) for j in range(n+1) for i in range(n+1)]
    faces=[]
    for j in range(n):
        for i in range(n):
            a=j*(n+1)+i;faces.append((a,a+1,a+n+2,a+n+1))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    uv=mesh.uv_layers.new(name='PaintUV')
    for p in mesh.polygons:
        p.use_smooth=True
        for li in p.loop_indices:
            index=mesh.loops[li].vertex_index
            uv.data[li].uv=((index%(n+1))/n,(index//(n+1))/n)
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    obj.location.x=x;obj.rotation_euler.z=math.radians(yaw);mesh.materials.append(material)
    sol=obj.modifiers.new('Plate thickness','SOLIDIFY');sol.thickness=.025
    bevel=obj.modifiers.new('Physical edge bevel','BEVEL');bevel.width=.008;bevel.segments=3
    # Narrow continuous rim geometry; the fine texture accents remain selective.
    curve=bpy.data.curves.new(name+'_rim','CURVE');curve.dimensions='3D';curve.bevel_depth=.006;curve.bevel_resolution=2
    points=[surface(i/n,0) for i in range(n+1)]+[surface(1,j/n) for j in range(1,n+1)]+[surface(i/n,1) for i in range(n-1,-1,-1)]+[surface(0,j/n) for j in range(n-1,0,-1)]
    spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points):p.co=(*co,1)
    spline.use_cyclic_u=True
    rim=bpy.data.objects.new(name+'_rim',curve);bpy.context.collection.objects.link(rim);rim.parent=obj;curve.materials.append(edge)
    return obj

def build():
    texture_maps();bpy.ops.wm.read_factory_settings(use_empty=True)
    steel=painted();edge=mat('M_EdgeSteel',(.48,.50,.47),.9,.3)
    coupon('PaintedSteel_Front',-.64,0,steel,edge)
    coupon('PaintedSteel_Turned',.64,-32,steel,edge)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
    scene.render.threads_mode='FIXED';scene.render.threads=4
    scene.render.resolution_x=1440;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
    scene.world=bpy.data.worlds.new('CoolStudioFill');scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.23,.30,.40,1);bg.inputs['Strength'].default_value=.35
    bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.name='QuietWarmGround'
    floor.data.materials.append(mat('M_QuietGround',(.09,.105,.115),0,.88))
    for name,loc,power,size,color in [('WarmKey',(-2,-3,4),650,3.0,(1,.88,.70)),('CoolEdge',(3,1,3),850,2,(.67,.80,1))]:
        light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;light.color=color
        o=bpy.data.objects.new(name,light);bpy.context.collection.objects.link(o);o.location=loc
        o.rotation_euler=(Vector((0,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
    camera=bpy.data.cameras.new('MaterialStudyCamera');o=bpy.data.objects.new('MaterialStudyCamera',camera);bpy.context.collection.objects.link(o)
    o.location=(1.8,-5,2.3);o.rotation_euler=(Vector((0,0,.73))-o.location).to_track_quat('-Z','Y').to_euler()
    camera.type='ORTHO';camera.ortho_scale=2.7;scene.camera=o
    scene.render.filepath=str(OUT/'painted-steel-study.png')
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'PaintedSteel_v002.blend'))
    settings={'candidate':'PaintedSteel_v002','scope':'Original unrigged material coupons, not knight geometry or style acceptance',
              'bpy':bpy.app.version_string,'camera_matrix':[list(r) for r in o.matrix_world],
              'ortho_scale':camera.ortho_scale,'samples':32,'view_transform':'AgX','metallic':.90,
              'lighting':'Warm area key + cool area edge + cool world fill',
              'source_reference':'../06-riot-inspired.png','patch_count':len(PATCHES)}
    (OUT/'settings.json').write_text(json.dumps(settings,indent=2))
    bpy.ops.render.render(write_still=True)
    settings['render_sha256']=hashlib.sha256((OUT/'painted-steel-study.png').read_bytes()).hexdigest()
    (OUT/'settings.json').write_text(json.dumps(settings,indent=2))
    print('MEL17_PAINTED_STEEL_RENDER_COMPLETE')

if __name__=='__main__':
    build()

