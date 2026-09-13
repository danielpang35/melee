"""One isolated anatomical FK transfer for review; no runtime import/selection.

Run with background Blender. The retained native source is never regenerated.
This is a diagnostic transfer, not a production AnimationLab adapter.
"""
import bpy
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'ArtSource/UserMaleBody/MB_SwingReview_v001'
SOURCE = ROOT/'ArtSource/ReadabilityCorrection/TP/C_grounded_v01/C_grounded_v01.blend'
TARGET = ROOT/'ArtSource/UserMaleBody/MB_v004_Project/Male_Body_Project.blend'
OUT.mkdir(parents=True, exist_ok=True)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v): (OUT/n).write_text(json.dumps(v,indent=2)+'\n')
def frame(direction, reference):
    y=direction.normalized()
    x=(reference-y*reference.dot(y)).normalized()
    assert x.length>.9, 'Degenerate anatomical reference'
    return Matrix((x,y,x.cross(y))).transposed().to_quaternion()

def build():
    assert not (OUT/'MB_Grounded_Transfer.blend').exists(), 'Keep published source immutable'
    protected={str(p.relative_to(ROOT)):sha(p) for p in [SOURCE,TARGET,ROOT/'Config/EXPreview.json',ROOT/'Config/WorkingCharacter.json']}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene=bpy.context.scene
    source=bpy.data.objects['KN01_Rig']
    source_rest={b.name:b.matrix_local.copy() for b in source.data.bones}
    samples=[]
    for f in range(scene.frame_start,scene.frame_end+1):
        scene.frame_set(f)
        evaluated=source.evaluated_get(bpy.context.evaluated_depsgraph_get())
        samples.append({p.name:p.matrix.copy() for p in evaluated.pose.bones})
    markers=[(m.name,m.frame) for m in scene.timeline_markers]
    # Keep source camera and simple weapon geometry; no source controls in target.
    camera=bpy.data.objects['MEL37_Power_Fixed'].copy()
    camera.data=camera.data.copy()
    camera_matrix=camera.matrix_world.copy()
    weapon_meshes=[]
    for name in ['CF_Blade','CF_Guard','CF_Grip','CF_Pommel']:
        obj=bpy.data.objects[name]
        weapon_meshes.append((obj.name,obj.data.copy(),obj.matrix_basis.copy()))
    # Append target objects into this scene, then unlink the source scene objects.
    old=list(scene.objects)
    with bpy.data.libraries.load(str(TARGET),link=False) as (available,loaded):
        loaded.objects=['MB_AccuRig','MB_Rigged_LOD0']
    for o in loaded.objects: scene.collection.objects.link(o)
    rig=next(o for o in loaded.objects if o.type=='ARMATURE')
    body=next(o for o in loaded.objects if o.type=='MESH')
    for o in old: scene.collection.objects.unlink(o) if o.name in scene.collection.objects else None
    # Old objects may be in child collections: render only the explicitly retained objects.
    for o in old: o.hide_render=True
    rig.hide_render=False; body.hide_render=False; rig.hide_set(False);body.hide_set(False)
    rig.animation_data_clear()
    for p in rig.pose.bones:
        p.matrix_basis=Matrix.Identity(4);p.rotation_mode='QUATERNION'
        for c in list(p.constraints):p.constraints.remove(c)
    rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
    def tr(n): return rest[n].translation
    def sr(n): return source_rest[n].translation
    # Explicit anatomical endpoints collapse legacy split chains; never rename bones.
    mapping={'pelvis':('root','spine04','spine_02'),
             **{f'spine_{i:02}':(f'spine{6-i:02}',f'spine{5-i:02}' if i<5 else 'neck01',f'spine_{i+1:02}' if i<5 else 'neck_01') for i in range(1,6)},
             'neck_01':('neck01','neck03','neck_02'), 'neck_02':('neck03','head','head'),
             'head':('head',None,None)}
    for side in ['l','r']:
        S=side.upper()
        mapping.update({f'clavicle_{side}':(f'clavicle.{S}',f'upperarm01.{S}',f'upperarm_{side}'),
                        f'upperarm_{side}':(f'upperarm01.{S}',f'lowerarm01.{S}',f'lowerarm_{side}'),
                        f'lowerarm_{side}':(f'lowerarm01.{S}',f'wrist.{S}',f'hand_{side}'),
                        f'hand_{side}':(f'wrist.{S}',f'finger3-1.{S}',f'middle_01_{side}'),
                        f'thigh_{side}':(f'upperleg01.{S}',f'lowerleg01.{S}',f'calf_{side}'),
                        f'calf_{side}':(f'lowerleg01.{S}',f'foot.{S}',f'foot_{side}'),
                        f'foot_{side}':(f'foot.{S}',f'toe3-1.{S}',f'ball_{side}')})
        for j,digit in enumerate(['thumb','index','middle','ring','pinky'],1):
            if j>1: mapping[f'{digit}_metacarpal_{side}']=(f'metacarpal{j-1}.{S}',f'finger{j}-1.{S}',f'{digit}_01_{side}')
            for k in range(1,4):mapping[f'{digit}_{k:02}_{side}']=(f'finger{j}-{k}.{S}',f'finger{j}-{k+1}.{S}' if k<3 else None,f'{digit}_{k+1:02}_{side}' if k<3 else None)
    calibration={}
    for n,(s,se,te) in mapping.items():
        sv=(sr(se)-sr(s)) if se else source.data.bones[s].tail_local-sr(s)
        tv=(tr(te)-tr(n)) if te else rig.data.bones[n].tail_local-tr(n)
        # Across-knuckle direction resolves hand roll; forward resolves other chains.
        if n.startswith('hand_'):
            side=n[-1]; S=side.upper()
            sx=sr(f'finger2-1.{S}')-sr(f'finger5-1.{S}')
            tx=tr(f'index_01_{side}')-tr(f'pinky_01_{side}')
        else: sx=tx=Vector((0,-1,0))
        calibration[n]=(frame(sv,sx),frame(tv,tx),sx,sv)
    root_ratio=tr('pelvis').z*.01/sr('root').z
    scene.frame_start=1;scene.frame_end=len(samples);scene.render.fps=60;scene.render.fps_base=1
    previous={}
    for f,pose in enumerate(samples,1):
        scene.frame_set(f)
        matrices={}
        for p in rig.pose.bones:
            n=p.name; parent=p.parent
            base=matrices[parent.name]@rest[parent.name].inverted()@rest[n] if parent else rest[n].copy()
            if n in mapping:
                s,se,te=mapping[n]; sf,tf,ref,sv=calibration[n]
                deformation=pose[s].to_quaternion()@source_rest[s].to_quaternion().inverted()
                direction=pose[se].translation-pose[s].translation if se else deformation@sv
                if n.startswith('hand_'):
                    S=n[-1].upper();reference=pose[f'finger2-1.{S}'].translation-pose[f'finger5-1.{S}'].translation
                else:reference=deformation@ref
                q=frame(direction,reference)@tf.inverted()@rest[n].to_quaternion()
                base=Matrix.LocRotScale(base.translation,q,Vector((1,1,1)))
                if n=='pelvis':base.translation=tr(n)+(pose['root'].translation-sr('root'))*(100*root_ratio)
            matrices[n]=base
            p.matrix_basis=p.bone.convert_local_to_pose(base,rest[n],parent_matrix=matrices[parent.name] if parent else Matrix.Identity(4),parent_matrix_local=rest[parent.name] if parent else Matrix.Identity(4),invert=True)
            q=p.rotation_quaternion.copy()
            if n in previous and q.dot(previous[n])<0:q.negate()
            p.rotation_quaternion=q;previous[n]=q.copy()
            for ch in ['location','rotation_quaternion','scale']:p.keyframe_insert(ch,frame=f,group=n)
    rig.animation_data.action.name='MB_Grounded_AnatomicalTransfer_v001'
    # Native wrist-local grasp uses the same landmark construction as the legacy rig.
    grasps={}
    for side in ['r','l']:
        wrist=rig.data.bones[f'hand_{side}']
        palm=(tr(f'middle_01_{side}')-wrist.head_local).normalized()
        shaft=(tr(f'index_01_{side}')-tr(f'pinky_01_{side}')).normalized()
        normal=shaft.cross(palm).normalized();shaft=palm.cross(normal).normalized()
        x=palm if side=='r' else -palm
        g=Matrix((x,shaft.cross(x).normalized(),shaft)).transposed().to_4x4()
        g.translation=wrist.head_local+palm*7.7-normal*2.4
        follower=bpy.data.objects.new('MB_Wrist_'+side,None);scene.collection.objects.link(follower)
        c=follower.constraints.new('COPY_TRANSFORMS');c.target=rig;c.subtarget=wrist.name
        grasp=bpy.data.objects.new('MB_Grasp_'+side,None);scene.collection.objects.link(grasp)
        grasp.parent=follower;grasp.matrix_basis=wrist.matrix_local.inverted()@g
        grasps[side]=grasp
    weapon=bpy.data.objects.new('MB_Review_Weapon',None);scene.collection.objects.link(weapon)
    weapon.parent=grasps['r'];weapon.location=(0,0,7);weapon.scale=(100,100,100)
    for name,data,local in weapon_meshes:
        o=bpy.data.objects.new('MB_'+name,data);scene.collection.objects.link(o);o.parent=weapon;o.matrix_basis=local
    scene.collection.objects.link(camera);camera.name='MB_Review_Defender';camera.matrix_world=camera_matrix;camera.hide_render=False
    scene.camera=camera
    # A consistent wide review camera accommodates the new body's height and sword arc.
    camera.location=(3.1,-5.4,2.6)
    camera.rotation_euler=(Vector((0,0,1.0))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO';camera.data.ortho_scale=3.8
    scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.53,.60,.69)
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.background_type='WORLD';scene.world.color=(.045,.055,.07)
    scene.render.image_settings.file_format='PNG';scene.display.render_aa='FXAA'
    for m in list(scene.timeline_markers):scene.timeline_markers.remove(m)
    for name,f in markers:scene.timeline_markers.new(name,frame=f)
    errors=[]
    for f in range(1,len(samples)+1):
        scene.frame_set(f);bpy.context.view_layer.update()
        expected=grasps['r'].matrix_world@Vector((0,0,-12.5))
        errors.append((grasps['l'].matrix_world.translation-expected).length)
    scene.frame_set(1)
    scene['review_status']='Diagnostic FK retarget only; no runtime or artistic acceptance. Support grip uncorrected.'
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'MB_Grounded_Transfer.blend'),compress=True)
    write('transfer.json',dict(protected=protected,source=str(SOURCE.relative_to(ROOT)),target=str(TARGET.relative_to(ROOT)),source_frames=len(samples),fps=60,mapping=mapping,max_support_gap_m=max(errors),support_gap_m=errors,source_sha256=sha(OUT/'MB_Grounded_Transfer.blend'),method='anatomical-axis FK, target lengths/rest/weights preserved; no IK or runtime fitting'))
    assert all(sha(ROOT/p)==h for p,h in protected.items())

def render():
    # Retain this experiment's native Blender renderer beside its diagnostic receipts.
    # Blender 5.2 requires ImageFormatSettings.media_type='VIDEO' before FFMPEG.
    import runpy
    runpy.run_path(str(ROOT/'Saved/AccuRigSwingReview/native_render.py'),run_name='__main__')

if '--render' in sys.argv:render()
else:build()
