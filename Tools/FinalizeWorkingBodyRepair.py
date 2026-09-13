"""Bake/export/verify an explicitly repaired MB source; no runtime promotion."""
import sys, json, math, shutil
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector, Quaternion
sys.path.insert(0,str(Path(__file__).resolve().parent))
from RepairWorkingBody import ROOT, OUT, EVIDENCE, SOURCE, digest, open_source, select_lod, render, audit, repair_surface

REPAIRED=OUT/'Male_Body_SurfaceRepair.blend'

def select(objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.hide_set(False); obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[-1]

def copy_for_bake(obj):
    tmp=obj.copy(); tmp.data=obj.data.copy(); bpy.context.scene.collection.objects.link(tmp)
    tmp.shape_key_clear()
    tmp.modifiers.clear()
    tmp.hide_viewport=False; tmp.hide_render=False; tmp.hide_set(False)
    select([tmp]); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return tmp

def bake():
    scene=open_source(REPAIRED)
    tex=OUT/'Textures'; tex.mkdir(exist_ok=True)
    (tex/'Unreal_DirectX').mkdir(exist_ok=True)
    for name in ['T_MB_BaseColor_2K.png','T_MB_ORM_2K.png']:
        shutil.copy2(ROOT/'ArtSource/UserMaleBody/MB_v002_GameReady/Textures'/name,tex/name)
    select_lod(scene,0)
    high=copy_for_bake(bpy.data.objects['MB_Rigged_LOD0'])
    # Use the repaired geometric surface as authority. Recursively baking the
    # imported normal map carries its inverted arm patches into coarse LODs.
    for slot in high.material_slots:
        slot.material=slot.material.copy()
        for node in slot.material.node_tree.nodes:
            if node.type=='BSDF_PRINCIPLED':
                for link in list(node.inputs['Normal'].links):slot.material.node_tree.links.remove(link)
    scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=1
    scene.render.threads_mode='FIXED'; scene.render.threads=4
    scene.render.bake.use_selected_to_active=True; scene.render.bake.use_clear=True
    scene.render.bake.margin=12
    records=[]
    for lod,size in enumerate([4096,2048,1024,512]):
        original=bpy.data.objects[f'MB_Rigged_LOD{lod}']
        low=copy_for_bake(original)
        for o in scene.objects:
            if o.type=='MESH':o.hide_render=o not in (high,low)
        low.data.materials.clear()
        material=bpy.data.materials.new(f'MB_BakeTarget{lod}'); material.use_nodes=True
        low.data.materials.append(material)
        image=bpy.data.images.new(f'MB_RepairedNormal{lod}',width=size,height=size,alpha=False)
        image.colorspace_settings.name='Non-Color'
        node=material.node_tree.nodes.new('ShaderNodeTexImage'); node.image=image
        material.node_tree.nodes.active=node
        select([high,low])
        bpy.ops.object.bake(type='NORMAL',normal_space='TANGENT',use_selected_to_active=True,
                            cage_extrusion=.005 if lod else .002,max_ray_distance=.05,margin=12)
        pixels=np.empty(size*size*4,dtype=np.float32); image.pixels.foreach_get(pixels)
        # Thin toes can project onto the opposite surface. Reject back-facing
        # samples and fade grazing hits to the target's geometric normal.
        rgb=pixels.reshape((-1,4))[:,:3]
        vector=rgb*2-1
        confidence=np.clip((vector[:,2]-.1)/.4,0,1)
        confidence=confidence*confidence*(3-2*confidence)
        rejected=int(np.sum(confidence<1))
        vector*=confidence[:,None];vector[:,2]+=1-confidence
        vector/=np.maximum(np.linalg.norm(vector,axis=1)[:,None],1e-8)
        rgb[:]=(vector+1)/2
        image.pixels.foreach_set(pixels)
        path=tex/f'T_MB_Normal_LOD{lod}.png'; image.filepath_raw=str(path); image.file_format='PNG'; image.save()
        pixels[1::4]=1-pixels[1::4]
        dx=bpy.data.images.new(f'MB_RepairedNormalDX{lod}',width=size,height=size,alpha=False)
        dx.colorspace_settings.name='Non-Color'; dx.pixels.foreach_set(pixels)
        dx.filepath_raw=str(tex/'Unreal_DirectX'/f'T_MB_Normal_LOD{lod}_DX.png'); dx.file_format='PNG'; dx.save()
        records.append(dict(lod=lod,size=size,rejected_or_faded_projection_samples=rejected,
                            opengl_sha256=digest(path),directx_sha256=digest(dx.filepath_raw)))
        # Keep a distinct corrected material; originals remain in the archive scene.
        mat=original.data.materials[0].copy(); mat.name=f'M_MB_Repaired_LOD{lod}'
        original.data.materials[0]=mat
        normal_node=next(n for n in mat.node_tree.nodes if n.type=='NORMAL_MAP')
        normal_texture=normal_node.inputs['Color'].links[0].from_node
        normal_texture.image=image
        image.pack()
        bpy.data.objects.remove(low,do_unlink=True)
        print('BAKED',lod,size,flush=True)
    bpy.data.objects.remove(high,do_unlink=True)
    select_lod(scene,0)
    bpy.ops.wm.save_as_mainfile(filepath=str(REPAIRED))
    (EVIDENCE/'bake.json').write_text(json.dumps(dict(source_sha256=digest(REPAIRED),maps=records,
        reference='Repaired LOD0 geometric surface; imported normal map excluded to avoid retaining inverted arm patches'),indent=2))

def export():
    scene=open_source(REPAIRED)
    rig=bpy.data.objects['MB_AccuRig']; rig.animation_data_clear(); rig.data.pose_position='REST'
    lods=[]
    for lod in range(4):
        select_lod(scene,lod)
        obj=bpy.data.objects[f'MB_Rigged_LOD{lod}']; obj.shape_key_clear()
        select([rig,obj])
        path=OUT/f'SK_MB_Body_LOD{lod}.fbx'
        bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'ARMATURE','MESH'},
            add_leaf_bones=False,use_armature_deform_only=False,bake_anim=False,
            axis_forward='-Y',axis_up='Z',global_scale=1,apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_NONE',path_mode='STRIP',use_mesh_modifiers=True,
            mesh_smooth_type='FACE')
        lods.append(dict(lod=lod,file=path.name,sha256=digest(path),bones=len(rig.data.bones),triangles=len(obj.data.polygons)))
    (OUT/'export_receipt.json').write_text(json.dumps(dict(source_sha256=digest(REPAIRED),lods=lods),indent=2))

def verify():
    scene=open_source(REPAIRED)
    checks={}; captures=[]
    for lod in range(4):
        obj=bpy.data.objects[f'MB_Rigged_LOD{lod}']; checks[lod]=audit(obj)
        assert all(v==0 for k,v in checks[lod].items() if k not in ('vertices','triangles')),checks[lod]
        select_lod(scene,lod)
        captures+= [dict(lod=lod,**c) for c in render(scene,EVIDENCE/'source-current'/f'LOD{lod}')]
    select_lod(scene,0)
    captures += [dict(lod=0,**c) for c in render(scene,EVIDENCE/'source-current'/'arms',('rear-left','rear-right'),(0,0,1.18),1.30)]
    # Compare preserved rig/weights/UVs by loading the protected source separately.
    before={}
    with bpy.data.libraries.load(str(SOURCE),link=False) as (src,dst):
        dst.objects=['MB_AccuRig','MB_Rigged_LOD0','MB_Rigged_LOD1','MB_Rigged_LOD2']
    oldrig=next(o for o in dst.objects if o.type=='ARMATURE')
    rig=bpy.data.objects['MB_AccuRig']
    assert len(rig.data.bones)==len(oldrig.data.bones)==118
    for b in rig.data.bones:
        old=oldrig.data.bones[b.name]
        assert (b.parent.name if b.parent else None)==(old.parent.name if old.parent else None)
        assert max(abs(x-y) for r,s in zip(b.matrix_local,old.matrix_local) for x,y in zip(r,s))<1e-7
    for lod in range(3):
        new=bpy.data.objects[f'MB_Rigged_LOD{lod}']; old=next(o for o in dst.objects if o.type=='MESH' and o.name.startswith(f'MB_Rigged_LOD{lod}'))
        assert len(new.data.vertices)==len(old.data.vertices)
        assert [tuple(p.vertices) for p in new.data.polygons]==[tuple(p.vertices) for p in old.data.polygons]
        before[lod]=sum([(g.group,g.weight) for g in a.groups]!=[(g.group,g.weight) for g in b.groups]
                        for a,b in zip(new.data.vertices,old.data.vertices))
        assert all(abs(sum(g.weight for g in v.groups)-1)<1e-4 for v in new.data.vertices)
        assert max(sum(g.weight>1e-5 for g in v.groups) for v in new.data.vertices)<=8
        assert max((a.uv-b.uv).length for a,b in zip(new.data.uv_layers.active.data,old.data.uv_layers.active.data))<1e-7
    (EVIDENCE/'source-verification.json').write_text(json.dumps(dict(source_sha256=digest(REPAIRED),
        audit=checks,captures=captures,bones_unchanged=118,lod012_topology_uvs_unchanged=True,
        changed_skin_weight_vertices=before,
        lod3='Regenerated from repaired LOD0; interpolated original skin weights',visual_review='pending'),indent=2))

def textured():
    scene=open_source(REPAIRED); captures=[]
    for lod in range(4):
        select_lod(scene,lod)
        captures += [dict(lod=lod,**c) for c in render(scene,EVIDENCE/'textured-current'/f'LOD{lod}',textured=True)]
    select_lod(scene,0)
    captures += render(scene,EVIDENCE/'textured-current'/'arms',('rear-left','rear-right'),(0,0,1.18),1.30,textured=True)
    (EVIDENCE/'textured.json').write_text(json.dumps(dict(source_sha256=digest(REPAIRED),captures=captures,visual_review='pending'),indent=2))

def weights():
    scene=open_source(OUT/'SurfaceRepair_before_joint_weights.blend'); rig=bpy.data.objects['MB_AccuRig']; results=[]
    joints=[(rig.data.bones[n].head_local.copy(),r) for n,r in
            [('lowerarm_l',9),('lowerarm_r',9),('hand_l',7),('hand_r',7),
             ('calf_l',9),('calf_r',9),('thigh_l',11),('thigh_r',11)]]
    for lod in range(4):
        obj=bpy.data.objects[f'MB_Rigged_LOD{lod}']; mesh=obj.data
        for name in ('upperarm_l','upperarm_r','lowerarm_l','lowerarm_r','hand_l','hand_r','thigh_l','thigh_r','calf_l','calf_r'):
            if name not in obj.vertex_groups:obj.vertex_groups.new(name=name)
        w=np.zeros((len(mesh.vertices),len(obj.vertex_groups)),dtype=np.float64)
        for v in mesh.vertices:
            for g in v.groups:w[v.index,g.group]=g.weight
        old=w.copy()
        adjacency=[set() for v in mesh.vertices]
        for e in mesh.edges:
            a,b=e.vertices; adjacency[a].add(b); adjacency[b].add(a)
        selected={v.index:max(max(0,1-(v.co-center).length/r) for center,r in joints) for v in mesh.vertices}
        selected={i:s for i,s in selected.items() if s>0}
        for iteration in range(12):
            updates={i:(1-.65*s)*w[i]+.65*s*np.mean(w[list(adjacency[i])],axis=0)
                     for i,s in selected.items() if adjacency[i]}
            for i,value in updates.items():w[i]=value
        # Smooth anatomical hinges explicitly. Imported helper weights can retain
        # a sharp crease even after graph smoothing on the densely triangulated skin.
        hinges=[('upperarm_l','lowerarm_l','hand_l',10,6),('upperarm_r','lowerarm_r','hand_r',10,6),
                ('lowerarm_l','hand_l','middle_01_l',6,4),('lowerarm_r','hand_r','middle_01_r',6,4),
                ('thigh_l','calf_l','foot_l',11,7),('thigh_r','calf_r','foot_r',11,7)]
        for parent,child,end,radius,width in hinges:
            center=rig.data.bones[child].head_local
            axis=(rig.data.bones[end].head_local-rig.data.bones[parent].head_local).normalized()
            pi=obj.vertex_groups[parent].index; ci=obj.vertex_groups[child].index
            for v in mesh.vertices:
                d=(v.co-center).length
                if d>=radius:continue
                t=max(0,min(1,.5+(v.co-center).dot(axis)/(2*width)))
                t=t*t*(3-2*t)
                influence=max(0,min(1,(radius-d)/(radius*.3)))
                target=np.zeros(w.shape[1]); target[pi]=1-t; target[ci]=t
                w[v.index]=(1-influence)*w[v.index]+influence*target
                selected[v.index]=1
        for i in selected:
            # Keep a compact eight-influence engine-compatible result.
            order=np.argsort(w[i]); w[i,order[:-8]]=0; w[i,w[i]<1e-5]=0
            w[i]/=w[i].sum()
            for g in obj.vertex_groups:g.remove([i])
            for g in np.flatnonzero(w[i]):obj.vertex_groups[int(g)].add([i],float(w[i,g]),'REPLACE')
        results.append(dict(lod=lod,changed_vertices=int(sum(np.max(abs(w-old),axis=1)>1e-7)),
                            joint_radius_cm=[r for _,r in joints],iterations=12,max_influences=8))
    select_lod(scene,0)
    bpy.ops.wm.save_as_mainfile(filepath=str(REPAIRED))
    (EVIDENCE/'weight-repair.json').write_text(json.dumps(dict(source_sha256=digest(REPAIRED),results=results),indent=2))

def roundtrip():
    from mathutils.kdtree import KDTree
    scene=open_source(REPAIRED); rig=bpy.data.objects['MB_AccuRig']
    bones={b.name:dict(parent=b.parent.name if b.parent else None,head=rig.matrix_world@b.head_local) for b in rig.data.bones}
    references={}
    for lod in range(4):
        obj=bpy.data.objects[f'MB_Rigged_LOD{lod}']
        references[lod]=[obj.matrix_world@v.co for v in obj.data.vertices]
    receipt=[]
    for lod in range(4):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(OUT/f'SK_MB_Body_LOD{lod}.fbx'),use_anim=False,automatic_bone_orientation=False)
        objs=list(bpy.context.scene.objects); obj=next(o for o in objs if o.type=='MESH'); rig=next(o for o in objs if o.type=='ARMATURE')
        assert set(rig.data.bones.keys())==set(bones)
        bone_error=0
        for b in rig.data.bones:
            assert (b.parent.name if b.parent else None)==bones[b.name]['parent']
            bone_error=max(bone_error,100*(rig.matrix_world@b.head_local-bones[b.name]['head']).length)
        tree=KDTree(len(references[lod]))
        for i,co in enumerate(references[lod]):tree.insert(co,i)
        tree.balance()
        error=max(tree.find(obj.matrix_world@v.co)[2]*100 for v in obj.data.vertices)
        assert error<.01 and bone_error<.01,(error,bone_error)
        receipt.append(dict(lod=lod,vertices=len(obj.data.vertices),triangles=len(obj.data.polygons),
            mesh_position_error_cm=error,bone_position_error_cm=bone_error,bones=len(rig.data.bones),
            fbx_sha256=digest(OUT/f'SK_MB_Body_LOD{lod}.fbx')))
    (EVIDENCE/'roundtrip.json').write_text(json.dumps(dict(source_sha256=digest(REPAIRED),lods=receipt,completed=True),indent=2))

def finish_joints():
    scene=open_source(REPAIRED); rig=bpy.data.objects['MB_AccuRig']; records=[]
    centers=[(rig.data.bones[n].head_local.copy(),r) for n,r in
             [('hand_l',10),('hand_r',10),('lowerarm_l',9),('lowerarm_r',9)]]
    for lod in range(4):
        obj=bpy.data.objects[f'MB_Rigged_LOD{lod}']; mesh=obj.data
        original=[v.co.copy() for v in mesh.vertices]
        keys=[(k,[v.co.copy() for v in k.data]) for k in mesh.shape_keys.key_blocks] if mesh.shape_keys else []
        adjacency=[set() for v in mesh.vertices]
        for e in mesh.edges:
            a,b=e.vertices; adjacency[a].add(b); adjacency[b].add(a)
        mask={v.index:max(max(0,1-(v.co-center).length/r)**.5 for center,r in centers) for v in mesh.vertices}
        mask={i:w for i,w in mask.items() if w>0}
        # Alternating positive/negative Laplacian steps remove local ridges with
        # much less volume loss than repeated ordinary smoothing.
        for iteration in range(32):
            for factor in (.48,-.50):
                positions={i:mesh.vertices[i].co.lerp(sum((mesh.vertices[j].co for j in adjacency[i]),Vector())/len(adjacency[i]),factor*w)
                           for i,w in mask.items() if adjacency[i]}
                for i,co in positions.items():mesh.vertices[i].co=co
        delta=[v.co-original[i] for i,v in enumerate(mesh.vertices)]
        for key,coords in keys:key.data.foreach_set('co',[x for i,co in enumerate(coords) for x in co+delta[i]])
        mesh.update()
        result=audit(obj)
        records.append(dict(lod=lod,modified_vertices=sum(d.length>1e-7 for d in delta),maximum_displacement_cm=max(d.length for d in delta),audit=result))
    select_lod(scene,0)
    bpy.ops.wm.save_as_mainfile(filepath=str(REPAIRED))
    (EVIDENCE/'joint-surface-finish.json').write_text(json.dumps(dict(source_sha256=digest(REPAIRED),records=records),indent=2))

def forearm_weights():
    scene=open_source(REPAIRED);rig=bpy.data.objects['MB_AccuRig'];records=[]
    def smooth(t):
        t=max(0,min(1,t));return t*t*(3-2*t)
    for lod in range(4):
        obj=bpy.data.objects[f'MB_Rigged_LOD{lod}']; changed=0
        for side in 'lr':
            elbow=rig.data.bones['lowerarm_'+side].head_local
            wrist=rig.data.bones['hand_'+side].head_local
            axis=wrist-elbow; length=axis.length; axis.normalize()
            group_names=['upperarm_'+side,'lowerarm_'+side,'hand_'+side]
            for n in group_names:
                if n not in obj.vertex_groups:obj.vertex_groups.new(name=n)
            groups=[obj.vertex_groups[n].index for n in group_names]
            for v in obj.data.vertices:
                t=(v.co-elbow).dot(axis)/length
                radial=((v.co-elbow)-axis*((v.co-elbow).dot(axis))).length
                if not -.3<t<1.2 or radial>=10:continue
                strength=smooth((t+.3)/.18)*smooth((1.2-t)/.15)*smooth((10-radial)/2)
                if strength<1e-6:continue
                upper=1-smooth((t+.12)/.34)
                hand=smooth((t-.72)/.43)
                lower=max(0,1-upper-hand)
                values={g.group:g.weight*(1-strength) for g in v.groups}
                for g,w in zip(groups,[upper,lower,hand]):values[g]=values.get(g,0)+strength*w
                keep=sorted(values.items(),key=lambda item:item[1],reverse=True)[:8]
                keep=[(g,w) for g,w in keep if w>1e-5]; total=sum(w for _,w in keep)
                for group_index in [int(g.group) for g in v.groups]:obj.vertex_groups[group_index].remove([v.index])
                for g,w in keep:obj.vertex_groups[g].add([v.index],w/total,'REPLACE')
                changed+=1
        records.append(dict(lod=lod,changed_vertices=changed))
    select_lod(scene,0);bpy.ops.wm.save_as_mainfile(filepath=str(REPAIRED))
    (EVIDENCE/'forearm-weights.json').write_text(json.dumps(dict(source_sha256=digest(REPAIRED),records=records),indent=2))

def cleanup():
    shutil.copy2(REPAIRED,OUT/'SurfaceRepair_before_final_cleanup.blend')
    scene=open_source(REPAIRED);records={}
    for lod in range(4):
        obj=bpy.data.objects[f'MB_Rigged_LOD{lod}']
        records[lod]=repair_surface(obj)
    select_lod(scene,0);bpy.ops.wm.save_as_mainfile(filepath=str(REPAIRED))
    (EVIDENCE/'final-cleanup.json').write_text(json.dumps(records,indent=2))
    print('CLEANUP',json.dumps({k:v['after'] for k,v in records.items()}))

if __name__=='__main__':
    {'bake':bake,'export':export,'verify':verify,'textured':textured,'weights':weights,'roundtrip':roundtrip,'finish-joints':finish_joints,'forearm-weights':forearm_weights,'cleanup':cleanup}[sys.argv[sys.argv.index('--')+1]]()
