"""Build editable CF blocking source; derive samples and cheap source-speed preview."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,data):
    Path(path).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def sample(keys, frame):
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if a <= frame <= b:
            t=(frame-a)/(b-a);t=t*t*(3-2*t)
            return [x+(y-x)*t for x,y in zip(va,vb)]
    raise ValueError('Channel frame outside source')


def build(snapshot, folder, native_input=None):
    import bpy
    from mathutils import Euler, Matrix, Vector
    from AnimationAuthoring import rig as control
    from AnimationAuthoring.performance import validate_score, CHARACTER
    score=json.loads((folder/'pose-controls.json').read_text())
    validate_score(score)
    if native_input:
        bpy.ops.wm.open_mainfile(filepath=str(native_input))
        rig=bpy.data.objects['CF_CTRL']
        grasps={s:bpy.data.objects['CF_'+n+'Grasp'] for s,n in [('R','Primary'),('L','Support')]}
        weapon=bpy.data.objects['CF_Weapon']
        assist_errors=[]
    else:
        rig,grasps,target,poles=control.setup(snapshot/CHARACTER)
        meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
        for obj in meshes:obj.hide_viewport=True
        scene=bpy.context.scene
        scene.frame_start=1;scene.frame_end=score['frame_end'];scene.render.fps=score['fps'];scene.render.fps_base=1
        scene.timeline_markers.clear()
        for event in score['events']:
            scene.timeline_markers.new(event['name'],frame=event['frame'])
        channels=score['channels'];previous={}
        def key(p,frame):
            if p.name in previous:
                p.rotation_euler.make_compatible(previous[p.name])
            previous[p.name]=p.rotation_euler.copy()
            p.keyframe_insert('rotation_euler',frame=frame,group=p.name)
        # Body/clavicles are separately timed native channels.
        for channel,bones in [('body',[('root',1)]),('chest',[('spine03',.22),('spine02',.35),('spine01',.43)]),
                              ('clavicle.R',[('clavicle.R',1)]),('clavicle.L',[('clavicle.L',1)])]:
            for frame,angles in channels[channel]:
                scene.frame_set(frame)
                for name,share in bones:
                    p=rig.pose.bones[name];p.matrix_basis=Matrix.Identity(4)
                    bpy.context.view_layer.update()
                    control.rotate_global(rig,name,Euler([math.radians(x*share) for x in angles],'XYZ'))
                    key(p,frame)
        arm_frames=sorted({f for c in ['primary_position','elbow.R'] for f,_ in channels[c]})
        assist_errors=[]
        for frame in arm_frames:
            scene.frame_set(frame)
            for side in ['R','L']:
                for name in ['upperarm01','upperarm02','lowerarm01','lowerarm02','wrist']:
                    rig.pose.bones[name+'.'+side].matrix_basis=Matrix.Identity(4)
            bpy.context.view_layer.update()
            orient=Euler([math.radians(x) for x in sample(channels['primary_orientation'],frame)],'XYZ').to_matrix().to_4x4()
            orient.translation=Vector(sample(channels['primary_position'],frame))
            wrist_matrix=orient@grasps['R'].matrix_basis.inverted()
            err=control.pose_arm(rig,'R',wrist_matrix.translation,sample(channels['elbow.R'],frame))
            p=rig.pose.bones['wrist.R']
            wrist_matrix.translation=p.head
            p.matrix=wrist_matrix
            bpy.context.view_layer.update()
            for name in ['upperarm01.R','lowerarm01.R']:
                key(rig.pose.bones[name],frame)
            assist_errors.append(dict(frame=frame,unreachable_distance_m=err))
        # Parent curves must be final before decomposing world wrist intentions.
        # Sparse independently timed local wrist keys previously introduced full
        # carry turns and pushed the support target beyond anatomical reach.
        for fc in rig.animation_data.action.fcurves:
            for point in fc.keyframe_points:
                point.interpolation='BEZIER'
                point.handle_left_type=point.handle_right_type='AUTO_CLAMPED'
        control.key_world_grasp_orientations(rig, grasps['R'], [
            (frame, Euler([math.radians(x) for x in sample(channels['primary_orientation'],frame)], 'XYZ').to_matrix().to_4x4())
            for frame in range(scene.frame_start,scene.frame_end+1)])
        for side in ['R','L']:
            for frame,value in channels['elbow.'+side]:
                scene.frame_set(frame)
                shoulder=rig.pose.bones['upperarm01.'+side].head
                poles[side].location=shoulder+Vector(value)
                poles[side].keyframe_insert('location',frame=frame)
        scene.frame_set(1)
        bpy.context.view_layer.update()
        # One initial support FK pose establishes a stable branch for native IK.
        control.pose_arm(rig,'L',target.matrix_world.translation,sample(channels['elbow.L'],1))
        rig.pose.bones['wrist.L'].matrix=target.matrix_world
        bpy.context.view_layer.update()
        ik=control.support_constraint(rig,target,poles['L'])
        # Calibrate the native IK pole axis to the actual CF bend at ready.
        desired=(poles['L'].location-rig.pose.bones['upperarm01.L'].head).normalized()
        choices=[]
        for angle in [i*math.pi/8 for i in range(-8,8)]:
            ik.pole_angle=angle;bpy.context.view_layer.update()
            a=rig.pose.bones['upperarm01.L'].head;b=rig.pose.bones['lowerarm01.L'].head;c=rig.pose.bones['wrist.L'].head
            axis=(c-a).normalized();plane=b-a-axis*(b-a).dot(axis)
            choices.append((plane.normalized().dot(desired),angle))
        ik.pole_angle=max(choices)[1]
        articulation=bpy.data.objects['CF_SupportArticulation']
        for frame,angles in [(1,(0,0,0)),(9,(0,0,0)),(29,(0,0,-6)),(45,(3,4,3)),(60,(-3,5,6)),(81,(0,2,2)),(97,(0,0,0))]:
            articulation.rotation_euler=[math.radians(x) for x in angles]
            articulation.keyframe_insert('rotation_euler',frame=frame)
        scene.frame_set(1)
        bpy.context.view_layer.update()
        for side in ['R','L']:
            control.calibrate_fingers(rig,side,grasps[side])
        weapon=control.weapon(grasps['R'])
        for obj in meshes:obj.hide_viewport=False
        rig.animation_data.action.name='CF_ControlProof_IndependentTiming_v1'
        for action in bpy.data.actions:
            for fc in action.fcurves:
                for point in fc.keyframe_points:
                    point.interpolation='BEZIER'
                    point.handle_left_type=point.handle_right_type='AUTO_CLAMPED'
        scene['source_authority']='Native CF_CTRL curves, editable grasp frames, support IK influence/pole. JSON regenerates initial blocking only.'
        scene['integration']='Exploration only; timing/reach diverges from accepted EX. No runtime binding or human acceptance.'
    scene=bpy.context.scene
    camera_path=snapshot/'ArtSource/AnimationLab/MEL36_reference/camera_setup.py'
    spec=importlib.util.spec_from_file_location('proof_camera',camera_path)
    camera_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(camera_module)
    camera_module.configure_camera(scene,snapshot/'ArtSource/AnimationLab/MEL36_reference/camera-spec.json')
    scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD'
    scene.world.color=(.055,.065,.08)
    scene.render.resolution_percentage=60
    scene.render.threads_mode='FIXED';scene.render.threads=2
    scene.display.render_aa='FXAA'
    scene.render.image_settings.file_format='PNG'
    scene.frame_set(scene.frame_start)
    bpy.ops.object.select_all(action='DESELECT')
    rig.hide_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig
    source=folder/'TP_v001_RightHorizontal.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
    rows=[];support_errors=[];projections=[]
    from bpy_extras.object_utils import world_to_camera_view
    for f in range(scene.frame_start,scene.frame_end+1):
        scene.frame_set(f);bpy.context.view_layer.update()
        base=weapon.matrix_world.translation;tip=weapon.matrix_world@Vector((0,0,1.035))
        support_socket=bpy.data.objects['CF_SupportSocket'].matrix_world.translation
        support_errors.append((grasps['L'].matrix_world.translation-support_socket).length)
        rows.append(dict(frame=f,time_s=(f-scene.frame_start)*scene.render.fps_base/scene.render.fps,
            blade_base_m=list(base),blade_tip_m=list(tip),primary_grasp_m=list(grasps['R'].matrix_world.translation),
            support_grasp_m=list(grasps['L'].matrix_world.translation)))
        projections.append(dict(frame=f,**{name:list(world_to_camera_view(scene,scene.camera,p)) for name,p in [
            ('primary',grasps['R'].matrix_world.translation),('support',grasps['L'].matrix_world.translation),('tip',tip)]}))
    fps=scene.render.fps/scene.render.fps_base
    events=[dict(name=m.name,frame=m.frame,time_s=(m.frame-scene.frame_start)/fps,confidence='authored',authority='descriptive only') for m in scene.timeline_markers]
    write(folder/'weapon-samples.json',dict(derived_from=digest(source),units='meters',fps=fps,samples=rows,events=events,runtime_binding=None))
    write(folder/'control-report.json',dict(source_sha256=digest(source),source_fps=fps,frame_start=scene.frame_start,frame_end=scene.frame_end,
        primary_pose_assistance=assist_errors,max_support_grasp_error_m=max(support_errors),
        control_rig=rig.name,source_action=rig.animation_data.action.name,native_curves=len(rig.animation_data.action.fcurves),
        primary_grasp_wrist_local=[list(row) for row in grasps['R'].matrix_basis],support_grasp_wrist_local=[list(row) for row in grasps['L'].matrix_basis],
        projection_samples=projections,human_acceptance=False))
    return source


def preview(folder, source, manifest, runner_hash):
    import bpy
    import imageio_ffmpeg
    from PIL import Image, ImageDraw
    scene=bpy.context.scene
    fps=scene.render.fps/scene.render.fps_base
    frames=range(scene.frame_start,scene.frame_end+1)
    w=int(scene.render.resolution_x*scene.render.resolution_percentage/100)
    h=int(scene.render.resolution_y*scene.render.resolution_percentage/100)
    pending=folder/'preview.pending.mp4'
    cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-threads','2',
         '-preset','veryfast','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(pending)]
    still_frames={1,20,31,37,44,49,52,57,64,76,88,97}
    stills=[]
    with open(folder/'encode.log','wb') as error_log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=error_log)
        try:
            for frame in frames:
                scene.frame_set(frame);scene.render.filepath=str(folder/'preview-frame.png')
                bpy.ops.render.render(write_still=True)
                with Image.open(scene.render.filepath) as im:
                    rgb=im.convert('RGB');proc.stdin.write(rgb.tobytes())
                    if frame in still_frames:
                        rgb.save(folder/f'frame-{frame:03d}.png');stills.append((frame,rgb.copy()))
            proc.stdin.close()
            if proc.wait()!=0:raise RuntimeError('Preview encoder failed; see encode.log')
        finally:
            if proc.poll() is None:proc.kill();proc.wait()
    pending.replace(folder/'preview.mp4')
    if stills:
        sheet=Image.new('RGB',(w*4,(h+24)*math.ceil(len(stills)/4)),(22,28,36))
        draw=ImageDraw.Draw(sheet)
        for index,(f,im) in enumerate(stills):
            x=(index%4)*w;y=(index//4)*(h+24);sheet.paste(im,(x,y));draw.text((x+8,y+h+4),f'Frame {f} | {(f-1)/fps:.3f}s',fill='white')
        sheet.save(folder/'whole-action-sheet.jpg')
    write(folder/'preview.json',dict(source_sha256=digest(source),controls_sha256=digest(folder/'pose-controls.json'),
        preview_sha256=digest(folder/'preview.mp4'),camera=scene.camera.name,fps=fps,source_fps=fps,
        first_source_frame=scene.frame_start,last_source_frame=scene.frame_end,source_stride=1,frames=len(frames),
        duration_s=len(frames)/fps,last_source_time_s=(len(frames)-1)/fps,terminal_display_duration_s=1/fps,
        playback_rate=1,human_acceptance=False,author_inputs=manifest['inputs'],runner_sha256=runner_hash,
        python_version=sys.version,blender_version=bpy.app.version_string,
        native_input_sha256=manifest.get('native_input_sha256'),derived_samples_sha256=digest(folder/'weapon-samples.json')))
