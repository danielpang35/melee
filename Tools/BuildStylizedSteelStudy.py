"""Stylized forged steel: variation in surface response, not colored paint islands."""
import argparse, json, math, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'Saved/ArtRuntime'),str(ROOT/'Saved/VideoRuntime')]
import bpy
import numpy as np
from PIL import Image, ImageDraw
from mathutils import Vector
import BuildPaintedSteelStudy as base

parser=argparse.ArgumentParser()
parser.add_argument('--revision',default='026',help='New output revision; archived candidates are immutable.')
parser.add_argument('--samples',type=int,default=32)
args=parser.parse_args()
if not args.revision.isdigit() or int(args.revision)<25:parser.error('Use revision 025 or later; earlier generators are archived with their candidates.')
OUT=ROOT/f'ArtSource/StyleReference/MEL17/Steel_v{args.revision}'
if (OUT/'steel-study.png').exists():parser.error('This candidate already exists. Choose a new revision to preserve reviewed evidence.')
OUT.mkdir(parents=True,exist_ok=True)

def maps():
    size=1024
    yy,xx=np.mgrid[0:size,0:size]/(size-1)
    rng=np.random.default_rng(2026)
    # Continuous piecewise-planar tooling variation; subtle color is correlated
    # to broad rolling fields, while facets mostly affect reflected light.
    nx,ny=64,64
    points=np.zeros((ny+1,nx+1,3))
    for j in range(ny+1):
        for i in range(nx+1):
            points[j,i]=[(i+(rng.uniform(-.43,.43) if 0<i<nx else 0))/nx,
                         (j+(rng.uniform(-.43,.43) if 0<j<ny else 0))/ny,rng.normal(0,.12)]
    height=np.zeros((size,size))
    for j in range(ny):
        for i in range(nx):
            a,b,c,d=points[j,i],points[j,i+1],points[j+1,i],points[j+1,i+1]
            triangles=[(a,b,d),(a,d,c)] if rng.random()<.5 else [(a,b,c),(b,d,c)]
            for p,q,r in triangles:
                x0=max(0,int(min(p[0],q[0],r[0])*(size-1)));x1=min(size,int(max(p[0],q[0],r[0])*(size-1))+2)
                y0=max(0,int(min(p[1],q[1],r[1])*(size-1)));y1=min(size,int(max(p[1],q[1],r[1])*(size-1))+2)
                tx=xx[y0:y1,x0:x1];ty=yy[y0:y1,x0:x1]
                den=(q[1]-r[1])*(p[0]-r[0])+(r[0]-q[0])*(p[1]-r[1])
                u=((q[1]-r[1])*(tx-r[0])+(r[0]-q[0])*(ty-r[1]))/den
                v=((r[1]-p[1])*(tx-r[0])+(p[0]-r[0])*(ty-r[1]))/den
                w=1-u-v;mask=(u>=-1e-7)&(v>=-1e-7)&(w>=-1e-7)
                target=height[y0:y1,x0:x1];target[mask]=(u*p[2]+v*q[2]+w*r[2])[mask]
    broad=np.sin(xx*9+np.sin(yy*5))*np.cos(yy*7-xx*2)
    clusters=np.zeros_like(height)
    for cx,cy in rng.uniform(.05,.95,(38,2)):
        clusters=np.maximum(clusters,np.exp(-((xx-cx)**2+(yy-cy)**2)/(2*.036**2)))
    height*=.20+.80*clusters
    # Irregular five-to-seven-sided surface-response regions. Their boundaries
    # are value/roughness changes within steel, with no outline or relief edge.
    n=48;sites=rng.uniform(-.47,.47,(n+4,n+4,2));values=rng.normal(0,1,(n+4,n+4))
    gx=xx*(n-1);gy=yy*(n-1);ix=gx.astype(int);iy=gy.astype(int)
    nearest=np.full_like(xx,100.);facet=np.zeros_like(xx)
    for dy in range(-1,3):
        for dx in range(-1,3):
            sx=ix+dx;sy=iy+dy;site=sites[sy+1,sx+1]
            distance=(gx-sx-site[:,:,0])**2+(gy-sy-site[:,:,1])**2
            chosen=distance<nearest;nearest[chosen]=distance[chosen]
            facet[chosen]=values[sy+1,sx+1][chosen]
    facet=np.clip(facet,-1.8,1.8)
    tone=.025*facet*(.5+.5*clusters)
    color=np.stack([.52+.014*broad+tone,.525+.010*broad+tone,.51+.008*broad+tone],axis=-1)
    rough=.37+.025*broad+.070*facet
    for name,data in [('BaseColor',color),('Roughness',rough),('Forging',.5+height)]:
        if name=='Forging':
            Image.fromarray(np.uint16(np.clip(data,0,1)*65535)).save(OUT/f'T_Steel_{name}.png')
        else:
            Image.fromarray(np.uint8(np.clip(data,0,1)*255)).save(OUT/f'T_Steel_{name}.png')

def authored_maps():
    if int(args.revision)>=10:
        rng=np.random.default_rng(1010);size=2048
        normal=Image.new('RGB',(size,size),(128,128,128));draw=ImageDraw.Draw(normal)
        rough=Image.new('RGB',(size,size),(72,)*3);rd=ImageDraw.Draw(rough)
        # Overlapping, unequal steel planes, authored at a common physical scale.
        # Encoded world-normal offsets avoid the creases of a height derivative.
        for i in range(430):
            cx,cy=rng.uniform(-.05,1.05,2);radius=rng.uniform(.018,.060)
            angles=np.sort(rng.uniform(0,2*math.pi,rng.integers(4,8)))
            pts=[((cx+math.cos(a)*radius*rng.uniform(.65,1.2))*size,(cy+math.sin(a)*radius*rng.uniform(.65,1.2))*size) for a in angles]
            delta=rng.uniform(-.040,.040,3);delta[1]*=.3
            draw.polygon(pts,fill=tuple(int((.5+v)*255) for v in delta))
            rd.polygon(pts,fill=(int(rng.uniform(.26,.36)*255),)*3)
        if int(args.revision)>=12:
            normal=Image.new('RGB',(size,size),(128,128,128));draw=ImageDraw.Draw(normal)
            rough=Image.new('RGB',(size,size),(77,)*3);rd=ImageDraw.Draw(rough)
            for centerx,centerz in [(-.64,1.25),(-.56,1.08),(.38,1.07),(.51,.98),(.71,1.22)]:
                for i in range(18):
                    x=centerx+rng.normal(0,.06);z=centerz+rng.normal(0,.055)
                    radius=rng.uniform(.018,.038)
                    angles=np.sort(rng.uniform(0,2*math.pi,rng.integers(4,7)))
                    pts=[((.5+.33*(x+math.cos(a)*radius))*size,(.5-.33*(z+math.sin(a)*radius))*size) for a in angles]
                    delta=np.array([rng.uniform(-.12,.12),0,rng.uniform(-.12,.12)])
                    draw.polygon(pts,fill=tuple(int((.5+v)*255) for v in delta))
                    rd.polygon(pts,fill=(int(rng.uniform(.23,.33)*255),)*3)
        normal.save(OUT/'T_Steel_NormalOffset.png');rough.save(OUT/'T_Steel_Roughness.png')
        return
    regions=[
      ([(0,0),(.5,0),(.5,.58),(.36,.66),(.12,.53),(0,.57)],1.04,.41),
      ([(.5,0),(1,0),(1,.68),(.72,.59),(.5,.72)],.96,.36),
      ([(0,0),(.43,0),(.36,.15),(.20,.23),(0,.17)],1.09,.31),
      ([(.5,0),(.76,0),(.86,.18),(.69,.27),(.5,.16)],.92,.43),
      ([(.41,.14),(.5,.10),(.5,.49),(.44,.55),(.39,.35)],1.07,.29),
      ([(.5,.35),(.64,.43),(.86,.58),(1,.55),(1,.68),(.77,.67),(.5,.47)],1.04,.42),
      ([(0,.63),(.18,.59),(.37,.72),(.5,.79),(.5,1),(0,1)],.95,.43),
      ([(1,.70),(.85,.76),(.80,.90),(.66,1),(1,1)],1.05,.33)]
    for name,default,index in [('BaseColor',.24,1),('Roughness',.38,2)]:
        im=Image.new('RGB',(2048,2048),(round(default*255),)*3);draw=ImageDraw.Draw(im)
        for region in regions:
            value=round((.24*region[index] if name=='BaseColor' else region[index])*255)
            draw.polygon([(round(u*2047),round(y*2047)) for u,y in region[0]],fill=(value,)*3)
        im.resize((1024,1024),Image.Resampling.LANCZOS).save(OUT/f'T_Steel_{name}.png')
    (OUT/'regions.json').write_text(json.dumps(regions,indent=2))

def steel():
    m=base.mat('StylizedSteel',(.5,.53,.55),1,.36);tree=m.node_tree;p=tree.nodes.get('Principled BSDF')
    if int(args.revision)>=13:
        p.inputs['Base Color'].default_value=(.29,.285,.275,1);p.inputs['Roughness'].default_value=.30
        return m
    origin=bpy.data.objects.new('SteelTextureSpace',None);bpy.context.collection.objects.link(origin)
    texcoord=tree.nodes.new('ShaderNodeTexCoord');texcoord.object=origin
    scale=tree.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.33,.33,.33)
    offset=tree.nodes.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=(.5,.5,.5)
    tree.links.new(texcoord.outputs['Object'],scale.inputs[0]);tree.links.new(scale.outputs[0],offset.inputs[0])
    def mapping(n):
        n.projection='BOX';n.projection_blend=.24
        tree.links.new(offset.outputs[0],n.inputs['Vector'])
    if int(args.revision)>=10:
        split=tree.nodes.new('ShaderNodeSeparateXYZ');combine=tree.nodes.new('ShaderNodeCombineXYZ')
        tree.links.new(offset.outputs[0],split.inputs[0]);tree.links.new(split.outputs['X'],combine.inputs['X']);tree.links.new(split.outputs['Z'],combine.inputs['Y'])
        im=bpy.data.images.load(str(OUT/'T_Steel_NormalOffset.png'));im.colorspace_settings.name='Non-Color'
        n=tree.nodes.new('ShaderNodeTexImage');n.image=im;tree.links.new(combine.outputs[0],n.inputs['Vector'])
        sub=tree.nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(.5,.5,.5);tree.links.new(n.outputs[0],sub.inputs[0])
        geom=tree.nodes.new('ShaderNodeNewGeometry');add=tree.nodes.new('ShaderNodeVectorMath');add.operation='ADD'
        tree.links.new(geom.outputs['Normal'],add.inputs[0]);tree.links.new(sub.outputs[0],add.inputs[1])
        norm=tree.nodes.new('ShaderNodeVectorMath');norm.operation='NORMALIZE';tree.links.new(add.outputs[0],norm.inputs[0]);tree.links.new(norm.outputs[0],p.inputs['Normal'])
        im=bpy.data.images.load(str(OUT/'T_Steel_Roughness.png'));im.colorspace_settings.name='Non-Color'
        n=tree.nodes.new('ShaderNodeTexImage');n.image=im;tree.links.new(combine.outputs[0],n.inputs['Vector']);tree.links.new(n.outputs[0],p.inputs['Roughness'])
        p.inputs['Base Color'].default_value=(.24,.245,.25,1)
        return m
    if int(args.revision)>=9:
        for name,pin in [('BaseColor','Base Color'),('Roughness','Roughness')]:
            im=bpy.data.images.load(str(OUT/f'T_Steel_{name}.png'));im.colorspace_settings.name='Non-Color'
            n=tree.nodes.new('ShaderNodeTexImage');n.image=im
            tree.links.new(texcoord.outputs['UV'],n.inputs['Vector']);tree.links.new(n.outputs['Color'],p.inputs[pin])
        return m
    if int(args.revision)>=8:
        im=bpy.data.images.load(str(ROOT/'ArtSource/StyleReference/MEL17/AuthoredSteel/SteelResponse.png'))
        im.colorspace_settings.name='sRGB'
        image=tree.nodes.new('ShaderNodeTexImage');image.image=im;mapping(image)
        bw=tree.nodes.new('ShaderNodeRGBToBW');tree.links.new(image.outputs['Color'],bw.inputs[0])
        color=tree.nodes.new('ShaderNodeMapRange');color.inputs['From Min'].default_value=.1;color.inputs['From Max'].default_value=.4
        color.inputs['To Min'].default_value=.205;color.inputs['To Max'].default_value=.275
        tree.links.new(bw.outputs[0],color.inputs['Value']);tree.links.new(color.outputs[0],p.inputs['Base Color'])
        rough=tree.nodes.new('ShaderNodeMapRange');rough.inputs['From Min'].default_value=.1;rough.inputs['From Max'].default_value=.4
        rough.inputs['To Min'].default_value=.24;rough.inputs['To Max'].default_value=.52
        tree.links.new(bw.outputs[0],rough.inputs['Value']);tree.links.new(rough.outputs[0],p.inputs['Roughness'])
        bump=tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.003
        tree.links.new(bw.outputs[0],bump.inputs['Height']);tree.links.new(bump.outputs[0],p.inputs['Normal'])
        return m
    for name,pin in [('BaseColor','Base Color'),('Roughness','Roughness')]:
        im=bpy.data.images.load(str(OUT/f'T_Steel_{name}.png'));im.colorspace_settings.name='sRGB' if name=='BaseColor' else 'Non-Color'
        n=tree.nodes.new('ShaderNodeTexImage');n.image=im;mapping(n);tree.links.new(n.outputs['Color'],p.inputs[pin])
    im=bpy.data.images.load(str(OUT/'T_Steel_Forging.png'));im.colorspace_settings.name='Non-Color'
    n=tree.nodes.new('ShaderNodeTexImage');n.image=im;mapping(n)
    bump=tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.20;bump.inputs['Distance'].default_value=.023
    tree.links.new(n.outputs['Color'],bump.inputs['Height']);tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    return m

def shell(name,center,radii,angle0,angle1,material):
    # Upper hemisphere cap and overlapping lamellar bands, with proper thickness.
    rows,cols=(3 if angle0>10 else 18),48;verts=[];rng=np.random.default_rng(1300+int(angle0))
    ts=np.r_[0,np.cumsum(rng.uniform(.5,2,rows))];ts/=ts[-1]
    az=np.r_[0,np.cumsum(rng.uniform(.5,2,cols))];az/=az[-1]
    for j in range(rows+1):
        t=math.radians(angle0+(angle1-angle0)*(ts[j] if 17<=int(args.revision)<20 else j/rows))
        for i in range(cols+1):
            a=2*math.pi*(az[i] if 17<=int(args.revision)<20 else i/cols)
            tt=t
            if 13<=int(args.revision)<20 and 0<j<rows and 0<i<cols:
                a+=(rng.uniform(-.25,.25)+(.45 if j%2 else -.25))*2*math.pi/cols;tt+=rng.uniform(-.2,.2)*math.radians(angle1-angle0)/rows
            verts.append((center[0]+radii[0]*math.sin(tt)*math.cos(a),center[1]+radii[1]*math.sin(tt)*math.sin(a),center[2]+radii[2]*math.cos(tt)))
    faces=[]
    for j in range(rows):
        for i in range(cols):
            a=j*(cols+1)+i;q=(a,a+cols+1,a+cols+2,a+1)
            if 17<=int(args.revision)<20 and rng.random()<.28:
                faces.extend([(q[0],q[1],q[2]),(q[0],q[2],q[3])] if rng.random()<.5 else [(q[0],q[1],q[3]),(q[1],q[2],q[3])])
            else:faces.append(q)
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    uv=mesh.uv_layers.new(name='SteelUV')
    for poly in mesh.polygons:
        poly.use_smooth=int(args.revision)<13
        for li in poly.loop_indices:
            k=mesh.loops[li].vertex_index;uv.data[li].uv=(k%(cols+1)/cols,k//(cols+1)/rows)
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(material)
    if int(args.revision)>=14:group_normals(mesh,2.5)
    if int(args.revision)>=18:
        def pt(u,v):
            t=math.radians(angle0+(angle1-angle0)*v);a=2*math.pi*u
            return (center[0]+radii[0]*math.sin(t)*math.cos(a),center[1]+radii[1]*math.sin(t)*math.sin(a),center[2]+radii[2]*math.cos(t))
        def nm(u,v):
            co=pt(u,v);return Vector(tuple((co[i]-center[i])/radii[i]**2 for i in range(3))).normalized()
        organic_planes(o,32 if int(args.revision)>=22 else 48,(2 if angle0>10 else 10) if int(args.revision)>=22 else (3 if angle0>10 else 14),pt,nm,True)
    s=o.modifiers.new('Real plate thickness','SOLIDIFY');s.thickness=.016
    b=o.modifiers.new('Edge radius','BEVEL');b.width=.005;b.segments=3
    return o

def group_normals(mesh,group_size):
    rng=np.random.default_rng(1414+len(mesh.polygons))
    centers=np.array([list(p.center) for p in mesh.polygons]);normals=np.array([list(p.normal) for p in mesh.polygons])
    sites=centers if int(args.revision)>=16 else centers[rng.choice(len(centers),max(4,int(len(centers)/group_size)),replace=False)]
    group=np.argmin(((centers[:,None,:]-sites[None,:,:])**2).sum(axis=2),axis=1)
    means={int(g):Vector(normals[group==g].mean(axis=0)).normalized() for g in np.unique(group)}
    smooth=[v.normal.copy() for v in mesh.vertices]
    loops=[None]*len(mesh.loops)
    for p in mesh.polygons:
        p.use_smooth=True
        for li in p.loop_indices:
            n=means[int(group[p.index])]
            blend=.2 if int(args.revision)>=16 else .5
            loops[li]=(n*(1-blend)+smooth[mesh.loops[li].vertex_index]*blend).normalized() if int(args.revision)>=15 else n
    mesh.normals_split_custom_set(loops);mesh.update()

def planar_plate(plate,material):
    nx,ny=14,20;rng=np.random.default_rng(1313);verts=[]
    vs=np.r_[0,np.cumsum(rng.uniform(.5,2,ny))];vs/=vs[-1]
    us=np.r_[0,np.cumsum(rng.uniform(.5,2,nx//2))];us/=us[-1]*2
    us=np.r_[us,1-us[-2::-1]]
    for j in range(ny+1):
        for i in range(nx+1):
            u=us[i] if int(args.revision)>=17 else i/nx;v=vs[j] if int(args.revision)>=17 else j/ny
            if 0<i<nx and i!=nx//2:u+=(rng.uniform(-.20,.20)+(.30 if j%2 else -.20))/nx
            if 0<j<ny:v+=rng.uniform(-.2,.2)/ny
            verts.append(base.surface(u,v))
    faces=[]
    for j in range(ny):
        for i in range(nx):
            a=j*(nx+1)+i;q=(a,a+1,a+nx+2,a+nx+1)
            if int(args.revision)>=17 and rng.random()<.25:
                faces.extend([(q[0],q[1],q[2]),(q[0],q[2],q[3])] if rng.random()<.5 else [(q[0],q[1],q[3]),(q[1],q[2],q[3])])
            else:faces.append(q)
    mesh=bpy.data.meshes.new('ConnectedSteelPlanes');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(material);plate.data=mesh
    if int(args.revision)>=14:group_normals(mesh,3)

def organic_planes(obj,nu,nv,point,normal,reverse=False):
    """Connected convex regions; no merged staircases or staggered grid slivers."""
    rng=np.random.default_rng(1800+nu+nv)
    sites=np.array([((i+rng.uniform(.15,.85))/nu,(j+rng.uniform(.15,.85))/nv) for j in range(nv) for i in range(nu)])
    if int(args.revision)>=19:
        size=2048;im=Image.new('RGB',(size,size),(128,128,255));draw=ImageDraw.Draw(im)
        du=(Vector(point(.51,.5))-Vector(point(.49,.5))).length
        dv=(Vector(point(.5,.51))-Vector(point(.5,.49))).length
        weights=np.array([(du/dv)**2,1])
        for site in sites:
            left,right=(0,.5) if site[0]<.5 else (.5,1)
            if not obj.name.startswith('ControlledPlate'):left,right=0,1
            poly=[np.array(p,float) for p in [(left,0),(right,0),(right,1),(left,1)]]
            for idx in np.argsort((((sites-site)**2)*weights).sum(axis=1))[1:30]:
                other=sites[idx];axis=(other-site)*weights;limit=((other**2-site**2)*weights).sum()*.5;cut=[]
                for a,b in zip(poly,poly[1:]+poly[:1]):
                    da=a@axis-limit;db=b@axis-limit
                    if da<=1e-10:cut.append(a)
                    if (da<0)!=(db<0):cut.append(a+(b-a)*(da/(da-db)))
                poly=cut
                if not poly:break
            if len(poly)>=3:draw.polygon([(u*(size-1),(1-v)*(size-1)) for u,v in poly],fill=tuple(round((x*.5+.5)*255) for x in normal(*site)))
        if int(args.revision)>=20:
            alpha=Image.new('L',(size,size),255);ad=ImageDraw.Draw(alpha)
            if int(args.revision)>=21:
                yy,xx=np.mgrid[0:size,0:size]/(size-1);floor=.30 if int(args.revision)>=22 else .48;strength=np.full((size,size),floor)
                zones=[(.34,.22,.13,.20),(.65,.10,.09,.13)] if obj.name.startswith('ControlledPlate') else [(.66,.30,.07,.23),(.86,.46,.05,.17)]
                for cx,cy,rx,ry in zones:strength=np.maximum(strength,floor+(1-floor)*np.exp(-((xx-cx)/rx)**2-((yy-cy)/ry)**2))
                if int(args.revision)>=23:
                    if obj.name=='Pauldron_Cap':
                        for cx,cy,rx,ry in [(.716,.363,.035,.10),(.925,.437,.027,.08)]:strength*=1-.96*np.exp(-((xx-cx)/rx)**2-((yy-cy)/ry)**2)
                    elif obj.name.startswith('Pauldron_Lame'):strength*=.70
                if int(args.revision)>=25 and obj.name=='Pauldron_Cap':
                    strength=np.full((size,size),.075)
                    for cx,cy,rx,ry in [(.68,.18,.025,.09),(.884,.32,.025,.065)]:strength=np.maximum(strength,.075+.55*np.exp(-((xx-cx)/rx)**2-((yy-cy)/ry)**2))
                alpha=Image.fromarray(np.uint8(strength*255));ad=ImageDraw.Draw(alpha)
            border=round(size*.018);ad.rectangle((0,0,size-1,border),fill=0);ad.rectangle((0,size-1-border,size-1,size-1),fill=0)
            if obj.name.startswith('ControlledPlate'):
                ad.rectangle((size*.465,0,size*.535,size-1),fill=0)
                ad.rectangle((0,0,border,size-1),fill=0);ad.rectangle((size-1-border,0,size-1,size-1),fill=0)
            im.putalpha(alpha)
        path=OUT/(obj.name+'_ObjectNormal.png');im.save(path)
        mat=obj.data.materials[0].copy();mat.name=obj.name+'_Steel';obj.data.materials.clear();obj.data.materials.append(mat)
        tree=mat.node_tree;p=tree.nodes.get('Principled BSDF');n=tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(path));n.image.colorspace_settings.name='Non-Color'
        decode=tree.nodes.new('ShaderNodeVectorMath');decode.operation='MULTIPLY_ADD';decode.inputs[1].default_value=(2,2,2);decode.inputs[2].default_value=(-1,-1,-1);tree.links.new(n.outputs[0],decode.inputs[0])
        world=tree.nodes.new('ShaderNodeVectorTransform');world.vector_type='NORMAL';world.convert_from='OBJECT';world.convert_to='WORLD';tree.links.new(decode.outputs[0],world.inputs[0])
        mul=tree.nodes.new('ShaderNodeVectorMath');mul.operation='SCALE';mul.inputs[3].default_value=.8;tree.links.new(world.outputs[0],mul.inputs[0])
        geom=tree.nodes.new('ShaderNodeNewGeometry');blend=tree.nodes.new('ShaderNodeVectorMath');blend.operation='MULTIPLY_ADD';blend.inputs[1].default_value=(.2,.2,.2);tree.links.new(geom.outputs['Normal'],blend.inputs[0]);tree.links.new(mul.outputs[0],blend.inputs[2])
        norm=tree.nodes.new('ShaderNodeVectorMath');norm.operation='NORMALIZE';tree.links.new(blend.outputs[0],norm.inputs[0]);tree.links.new(norm.outputs[0],p.inputs['Normal'])
        if int(args.revision)>=20:
            factor=tree.nodes.new('ShaderNodeMath');factor.operation='MULTIPLY';factor.inputs[1].default_value=.4 if int(args.revision)>=22 else .65;tree.links.new(n.outputs['Alpha'],factor.inputs[0])
            mix=tree.nodes.new('ShaderNodeMixRGB');tree.links.new(factor.outputs[0],mix.inputs[0]);tree.links.new(geom.outputs['Normal'],mix.inputs[1]);tree.links.new(world.outputs[0],mix.inputs[2]);tree.links.new(mix.outputs[0],norm.inputs[0])
        if int(args.revision)>=22:
            old=obj.data;fresh=bpy.data.meshes.new(obj.name+'_SmoothSurface');fresh.from_pydata([v.co[:] for v in old.vertices],[],[list(p.vertices) for p in old.polygons]);fresh.update()
            uv=fresh.uv_layers.new(name='SteelUV')
            for li in range(len(fresh.loops)):uv.data[li].uv=old.uv_layers.active.data[li].uv
            for mat in old.materials:fresh.materials.append(mat)
            obj.data=fresh
        else:obj.data.normals_split_custom_set([(0,0,0)]*len(obj.data.loops))
        for poly in obj.data.polygons:poly.use_smooth=True
        obj.data.update()
        return
    verts=[];faces=[];normals=[];lookup={};uvs=[]
    for k,site in enumerate(sites):
        left,right=(0,.5) if site[0]<.5 else (.5,1)
        if not obj.name.startswith('ControlledPlate'):left,right=0,1
        poly=[np.array(p,float) for p in [(left,0),(right,0),(right,1),(left,1)]]
        neighbors=np.argsort(((sites-site)**2).sum(axis=1))[1:30]
        for idx in neighbors:
            other=sites[idx];axis=other-site;limit=(other@other-site@site)*.5;cut=[]
            for a,b in zip(poly,poly[1:]+poly[:1]):
                da=a@axis-limit;db=b@axis-limit
                if da<=1e-10:cut.append(a)
                if (da<0)!=(db<0):cut.append(a+(b-a)*(da/(da-db)))
            poly=cut
            if not poly:break
        if len(poly)<3:continue
        indices=[]
        for u,v in poly:
            co=point(u,v);key=tuple(round(float(x),7) for x in co)
            if key not in lookup:lookup[key]=len(verts);verts.append(co);uvs.append((u,v))
            indices.append(lookup[key])
        faces.append(indices[::-1] if reverse else indices);normals.append(normal(*site))
    mesh=bpy.data.meshes.new(obj.name+'_OrganicPlanes');mesh.from_pydata(verts,[],faces);mesh.update()
    materials=list(obj.data.materials);obj.data=mesh
    for mat in materials:mesh.materials.append(mat)
    custom=[None]*len(mesh.loops)
    for p in mesh.polygons:
        p.use_smooth=True
        for li in p.loop_indices:
            u,v=uvs[mesh.loops[li].vertex_index]
            custom[li]=(Vector(normals[p.index])*.8+Vector(normal(u,v))*.2).normalized()
    mesh.normals_split_custom_set(custom);mesh.update()

def plate_normal(u,v):
    du=Vector(base.surface(u+.0001,v))-Vector(base.surface(u-.0001,v))
    dv=Vector(base.surface(u,v+.0001))-Vector(base.surface(u,v-.0001))
    return du.cross(dv).normalized()

def rim_curve(name,center,radii,angle,material):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=.007;c.bevel_resolution=3
    s=c.splines.new('POLY');s.points.add(127);t=math.radians(angle)
    for i,p in enumerate(s.points):
        a=2*math.pi*i/128;p.co=(center[0]+radii[0]*math.sin(t)*math.cos(a),center[1]+radii[1]*math.sin(t)*math.sin(a),center[2]+radii[2]*math.cos(t),1)
    s.use_cyclic_u=True;o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);c.materials.append(material)

def build():
    if int(args.revision)<8:maps()
    if 9<=int(args.revision)<13:authored_maps()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    m=steel();edge=base.mat('EdgeSteel',(.40,.42,.42),1,.32)
    plate=base.coupon('ControlledPlate',-.60,0,m,edge)
    if 13<=int(args.revision)<19:planar_plate(plate,m)
    if int(args.revision)>=18:organic_planes(plate,10 if int(args.revision)>=22 else 14,14 if int(args.revision)>=22 else 20,base.surface,plate_normal)
    # Narrower physical rim, same steel family; light determines its brightness.
    rim=bpy.data.objects.get('ControlledPlate_rim');rim.data.bevel_depth=.004
    rim.data.materials.clear();rim.data.materials.append(m)
    shell('Pauldron_Cap',(.59,.05,.86),(.46,.40,.43),2,88,m)
    shell('Pauldron_Lame01',(.59,.05,.70),(.443,.385,.35),68,103,m)
    shell('Pauldron_Lame02',(.59,.05,.57),(.41,.36,.30),68,105,m)
    if int(args.revision)>=20:
        trim=base.mat('PolishedConstructionEdges',(.44,.44,.42),1,.23)
        rim_curve('CrownContinuousRim',(.59,.05,.86),(.461,.401,.43),88,trim)
        rim_curve('Lame01ContinuousRim',(.59,.05,.70),(.444,.386,.35),103,trim)
        rim_curve('Lame02ContinuousRim',(.59,.05,.57),(.411,.361,.30),105,trim)
    # Restrained fasteners make plate scale and overlap legible.
    for z,x in [(1.03,.35),(1.03,.83),(.75,.29),(.75,.89),(.60,.31),(.60,.87)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.013,location=(x,-.315,z))
        o=bpy.context.object;o.name='SteelRivet';o.scale.y=.45;o.data.materials.append(edge)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=args.samples;scene.cycles.use_denoising=True
    scene.render.threads_mode='FIXED';scene.render.threads=4
    scene.render.resolution_x=1440;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
    scene.world=bpy.data.worlds.new('CoolFill');scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.35,.45,.62,1);bg.inputs['Strength'].default_value=.3
    bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.data.materials.append(base.mat('WarmNeutral',(.20,.185,.16),0,.9))
    for name,loc,power,size,color in [('Key',(-2,-3,4),750,3,(1,.88,.72)),('Rim',(3,1,3),100,1,(.67,.81,1)),('Front',(-1,-4,1.5),15,3,(.8,.86,1))]:
        light=bpy.data.lights.new(name,'AREA');light.energy=power;light.size=size;light.color=color
        if name=='Key':light.shape='RECTANGLE';light.size_y=.18
        o=bpy.data.objects.new(name,light);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
    c=bpy.data.cameras.new('StudyCamera');o=bpy.data.objects.new('StudyCamera',c);bpy.context.collection.objects.link(o)
    o.location=(1.35,-5,2.5);o.rotation_euler=(Vector((0,0,.78))-o.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=2.6;scene.camera=o
    scene.render.filepath=str(OUT/'steel-study.png')
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'Steel_v{args.revision}.blend'))
    (OUT/'settings.json').write_text(json.dumps({'candidate':args.revision,'samples':args.samples,'material':{'metallic':1,'base_color_linear':list(p.inputs['Base Color'].default_value) if (p:=m.node_tree.nodes.get('Principled BSDF')) else None,'roughness':p.inputs['Roughness'].default_value,'normal_method':'Per-part object-space normal textures with influence and edge-exclusion alpha masks on fresh smooth geometry'},'camera_matrix':[list(r) for r in o.matrix_world],'orthographic_scale':c.ortho_scale,'lights':[{ 'name':l.name,'energy':l.energy,'size':l.size,'color':list(l.color)} for l in bpy.data.lights],'view_transform':scene.view_settings.view_transform,'scope':'material and pauldron proxies only; no runtime import'},indent=2))
    bpy.ops.render.render(write_still=True)
    (OUT/'generator.py').write_text(Path(__file__).read_text(encoding='utf-8'),encoding='utf-8')
    (OUT/'render.sha256').write_text(hashlib.sha256((OUT/'steel-study.png').read_bytes()).hexdigest())
    print('STEEL_STUDY_COMPLETE',args.revision)

if __name__=='__main__':build()
