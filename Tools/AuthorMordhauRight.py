"""EX_v002: reference-seconds FP reconstruction; no runtime or EX_v001 edits.

Run with Python 3.11 and Saved/ArtRuntime bpy. Named camera-space pose keys
are stored beside the blend; depth/FOV/roll remain explicit reconstruction choices.
"""
import argparse, json, math, sys, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy
from mathutils import Vector, Matrix, Quaternion
from AuthorFreshExchange import swing

OUT=ROOT/'ArtSource/CharacterReset/EX_v002'
SOURCE=OUT/'EX_v002_MordhauRight.blend'
FPS=60

def lerp_pose(keys,t):
    if t<=keys[0]['time']:return keys[0]
    if t>=keys[-1]['time']:return keys[-1]
    for i,(a,b) in enumerate(zip(keys,keys[1:])):
        if a['time']<=t<=b['time']:
            x=(t-a['time'])/(b['time']-a['time'])
            # Linear local intervals retain measured passage acceleration; dense
            # reference keys control curvature rather than uniform easing.
            out={'time':t}
            for k in ('hilt','tip','roll','arm_scale','shoulder_follow','elbow_drop','face_blade'):
                av,bv=a[k],b[k]
                out[k]=[u+(v-u)*x for u,v in zip(av,bv)] if isinstance(av,list) else av+(bv-av)*x
            return out

def screen_point(camera,uvd):
    u,v,d=uvd
    half=math.tan(camera.data.angle_x/2)
    return camera.matrix_world@Vector(((2*u-1)*d*half,(1-2*v)*d*half*9/16,-d))

def move_head(p,point):
    m=p.matrix.copy();m.translation=point;p.matrix=m
    bpy.context.view_layer.update()

def build():
    contract=json.loads((OUT/'pose-controls.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'ArtSource/CharacterReset/EX_v001/EX_v001_Staging.blend'))
    scene=bpy.context.scene;rig=bpy.data.objects['CF01_CharacterRig'];weapon=bpy.data.objects['EX01_WeaponRoot']
    for o in (rig,weapon):o.animation_data_clear()
    for p in rig.pose.bones:
        for c in list(p.constraints):p.constraints.remove(c)
        p.matrix_basis=Matrix.Identity(4)
    camera=bpy.data.objects['EX01_Camera_FP'];camera.name='EX02_Camera_FP'
    camera.animation_data_clear();camera.location=(0,-.115,1.68)
    camera.rotation_euler=(math.pi/2,0,math.pi)
    # Camera looks horizontally down world -Y; screen-right is anatomical R (-X).
    camera.rotation_euler=(Vector((0,-1,0))).to_track_quat('-Z','Y').to_euler()
    camera.data.lens=contract['lens_mm'];camera.data.sensor_width=36;camera.data.sensor_fit='HORIZONTAL';camera.data.clip_start=.025
    camera['projection']='Static horizontal camera; FOV is a reconstruction choice, fitted over several phases.'
    bpy.context.view_layer.update()
    # Dedicated FP mesh: keep actual foundation arms/hands, omit hidden body/head.
    body=bpy.data.objects['CF01_Body'];body.data=body.data.copy();body.name='EX02_FP_Arms'
    # A restrained FP sleeve envelope widens the foreground arm silhouette.
    # Original foundation vertices are untouched; hands retain their source shape.
    for v in body.data.vertices:
        if not v.groups:continue
        vg=max(v.groups,key=lambda g:g.weight);name=body.vertex_groups[vg.group].name
        if not name.startswith(('upperarm','lowerarm')):continue
        side=name[-1];upper_region=name.startswith('upperarm')
        a=rig.data.bones[('upperarm01.' if upper_region else 'lowerarm01.')+side].head_local
        b=rig.data.bones[('lowerarm01.' if upper_region else 'wrist.')+side].head_local
        axis=b-a;u=max(0,min(1,(v.co-a).dot(axis)/axis.length_squared));radial=v.co-(a+axis*u)
        if radial.length>.001:v.co+=radial.normalized()*.025*(1 if upper_region else max(.20,1-u*.8))
    groups={g.index for g in body.vertex_groups if g.name.startswith(('upperarm','lowerarm','wrist','finger'))}
    maskgroup=body.vertex_groups.new(name='EX02_FP_VisibleArms')
    indices=[v.index for v in body.data.vertices if sum(g.weight for g in v.groups if g.group in groups)>.45]
    maskgroup.add(indices,1,'REPLACE')
    mod=body.modifiers.new('Dedicated FP arm visibility','MASK');mod.vertex_group=maskgroup.name
    for o in scene.objects:
        if o.name.startswith(('CF01_Eye','EX01_Grip','EX01_Elbow')):o.hide_render=True;o.hide_viewport=True
    # Blade silhouette: explicit art dimensions, never derived from gameplay range.
    blade=bpy.data.objects['EX01_Blade'];blade.data=blade.data.copy()
    for v in blade.data.vertices:v.co.x*=contract['blade_width_factor'];v.co.z*=contract['blade_length_factor']
    bpy.data.objects['EX01_BladeTip'].location.z=.9*contract['blade_length_factor']
    # Compact fittings preserve the paired grip rather than filling the passage
    # with the staging block pommel when the blade is strongly foreshortened.
    pommel=bpy.data.objects['EX01_Pommel'];pommel.scale=(.55,.65,.70);pommel.location.z=-.235
    handle=bpy.data.objects['EX01_Handle'];handle.scale.z=.84;handle.location.z=-.12
    rest={p.name:p.bone.matrix_local.copy() for p in rig.pose.bones}
    wrist_rest={s:rig.data.bones['wrist.'+s].head_local.copy() for s in ('R','L')}
    first,last=contract['start_time'],contract['end_time']
    count=round((last-first)*FPS)+1
    scene.frame_start=1;scene.frame_end=count;scene.render.fps=FPS;scene.render.fps_base=1
    scene.timeline_markers.clear()
    for name,t in contract['events'].items():scene.timeline_markers.new(name,frame=1+round((t-first)*FPS))
    errors=[];translations=[];scales=[];previous_weapon=None;previous_bones={}
    hidden=[o for o in scene.objects if o.type=='MESH' and not o.hide_viewport]
    for o in hidden:o.hide_viewport=True
    for f in range(1,count+1):
        scene.frame_set(f);t=first+(f-1)/FPS;pose=lerp_pose(contract['poses'],t)
        for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4);p.rotation_mode='QUATERNION'
        hilt=screen_point(camera,pose['hilt']);tip=screen_point(camera,pose['tip'])
        base=(tip-hilt).normalized().to_track_quat('Z','Y');roll=math.radians(pose['roll'])
        toward_camera=base.inverted()@(camera.location-hilt)
        broadside=math.atan2(-toward_camera.x,toward_camera.y)
        while broadside-roll>math.pi/2:broadside-=math.pi
        while broadside-roll<-math.pi/2:broadside+=math.pi
        roll+=(broadside-roll)*pose['face_blade']
        rot=base@Quaternion((0,0,1),roll)
        if previous_weapon is not None and rot.dot(previous_weapon)<0:rot.negate()
        previous_weapon=rot.copy();weapon.location=hilt;weapon.rotation_mode='QUATERNION';weapon.rotation_quaternion=rot
        weapon.keyframe_insert('location',frame=f);weapon.keyframe_insert('rotation_quaternion',frame=f)
        for side,sign,depth in [('R',-1,-.075),('L',1,-.155)]:
            rest_y=(rig.data.bones['finger3-1.'+side].head_local-wrist_rest[side]).normalized()
            rest_x=(rig.data.bones['finger2-1.'+side].head_local-rig.data.bones['finger5-1.'+side].head_local).normalized()
            rest_z=rest_x.cross(rest_y).normalized();rest_x=rest_y.cross(rest_z).normalized()
            dst_x=rot@Vector((0,0,1));dst_y=rot@Vector((-sign,0,0));dst_z=dst_x.cross(dst_y).normalized()
            basis=Matrix((dst_x,dst_y,dst_z)).transposed()@Matrix((rest_x,rest_y,rest_z)).transposed().inverted()
            target=hilt+rot@Vector((0,0,depth))-dst_y*.082+dst_z*(-.026 if side=='R' else .026)
            bpy.context.view_layer.update()
            upper=rig.pose.bones['upperarm01.'+side];lower=rig.pose.bones['lowerarm01.'+side]
            original_sh=upper.head.copy()
            # FP shoulder translation follows the offscreen load/carry while a
            # low shoulder origin maintains a broad converging arm silhouette.
            neutral=screen_point(camera,[.5,.88,.60])
            sh=Vector((sign*.24,.015,1.19))+(hilt-neutral)*pose['shoulder_follow']
            l1=(rig.data.bones['lowerarm01.'+side].head_local-rig.data.bones['upperarm01.'+side].head_local).length*pose['arm_scale']
            l2=(wrist_rest[side]-rig.data.bones['lowerarm01.'+side].head_local).length*pose['arm_scale']
            # Translate the shoulder for residual reach instead of flattening hilt.
            delta=target-sh
            if delta.length>l1+l2-.025:sh+=delta.normalized()*(delta.length-(l1+l2-.025))
            delta=target-sh;dist=max(.03,delta.length);axis=delta.normalized()
            pole=Vector((sign*.30,.03,-pose['elbow_drop']));pole=(pole-axis*pole.dot(axis)).normalized()
            along=(l1*l1-l2*l2+dist*dist)/(2*dist);height=math.sqrt(max(0,l1*l1-along*along));elbow=sh+axis*along+pole*height
            move_head(upper,sh);swing(rig,upper.name,elbow-sh)
            # Direct authored joint translations make segment deformation explicit
            # editable FK; not a runtime constraint or a physically limited solve.
            move_head(lower,elbow);swing(rig,lower.name,target-elbow)
            p=rig.pose.bones['wrist.'+side]
            p.matrix=Matrix.Translation(target)@basis.to_4x4()@rest[p.name].to_3x3().to_4x4()
            bpy.context.view_layer.update();errors.append((p.head-target).length)
            translations.append((sh-original_sh).length);scales.append(pose['arm_scale'])
            for digit in range(1,6):
                for segment in range(1,4):
                    p=rig.pose.bones.get(f'finger{digit}-{segment}.{side}')
                    if p:p.rotation_quaternion=Quaternion((1,0,0),.68 if digit==1 else 1.16)
        for p in rig.pose.bones:
            if p.name in previous_bones and p.rotation_quaternion.dot(previous_bones[p.name])<0:p.rotation_quaternion.negate()
            previous_bones[p.name]=p.rotation_quaternion.copy()
            for channel in ('rotation_quaternion','location','scale'):p.keyframe_insert(channel,frame=f,group=p.name)
    rig.animation_data.action.name='EX02_FP_NeutralRight_ReferenceSeconds';weapon.animation_data.action.name='EX02_Greatsword_FullRotation'
    for o in (rig,weapon):
        for fc in o.animation_data.action.fcurves:
            for k in fc.keyframe_points:k.interpolation='LINEAR'
    for o in hidden:o.hide_viewport=False
    scene.camera=camera;scene['EX02_status']='REFERENCE RECONSTRUCTION CANDIDATE; user artistic acceptance pending'
    configure(scene);scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    receipt={'source':str(SOURCE),'camera':camera.name,'fps':FPS,'source_capture_start_time':first,'source_capture_end_time':last,'frames':count,'duration_seconds':count/FPS,'events_seconds_in_clip':{k:v-first for k,v in contract['events'].items()},'max_wrist_alignment_error_m':max(errors),'max_shoulder_translation_m':max(translations),'authored_segment_length_multiplier_range':[min(scales),max(scales)],'deformation_method':'Explicit FK joint translations; scale channels retained; dedicated FP arms','projection':'static horizontal, no camera aim animation','normal_speed_viewed':False,'acceptance':'pending visual comparison and user judgment'}
    (OUT/'motion-report.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)

def configure(scene):
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD';scene.world.color=(.13,.17,.21)
    scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False

def render(inspect):
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;configure(scene)
    contract=json.loads((OUT/'pose-controls.json').read_text());folder=OUT/'Preview'/'FP';folder.mkdir(parents=True,exist_ok=True)
    frames=sorted(set(1+round((t-contract['start_time'])*FPS) for t in contract['inspect_times'])) if inspect else range(1,scene.frame_end+1)
    for f in frames:
        scene.frame_set(f);scene.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
    print('RENDER_DONE',len(frames),flush=True)

def encode():
    sys.path.insert(0,str(ROOT/'Saved/VideoRuntime'))
    import imageio_ffmpeg
    report=json.loads((OUT/'motion-report.json').read_text())
    folder=OUT/'Preview'/'FP'
    missing=[f for f in range(1,report['frames']+1) if not (folder/f'{f:04d}.png').is_file()]
    if missing:raise RuntimeError(f'Missing rendered frames: {missing}')
    result=OUT/'Preview'/'EX_v002_FP.mp4'
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-hide_banner','-loglevel','error','-framerate',str(FPS),'-start_number','1','-i',str(folder/'%04d.png'),'-frames:v',str(report['frames']),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(result)],check=True)
    report['preview']=str(result);report['preview_bytes']=result.stat().st_size
    (OUT/'motion-report.json').write_text(json.dumps(report,indent=2));print('PREVIEW_READY',result,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--render',action='store_true');p.add_argument('--inspect',action='store_true');p.add_argument('--encode',action='store_true');a=p.parse_args()
    if a.encode:encode()
    elif a.render or a.inspect:render(a.inspect)
    else:build()
