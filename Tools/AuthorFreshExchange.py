"""MEL-27: co-authored exchange poses, editable FK bake and fixed-camera previews.
Run with PYTHONPATH=Saved/ArtRuntime. No legacy action or runtime correction.
"""
import argparse, json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector, Matrix, Quaternion
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'ArtSource/CharacterReset/EX_v001'
# Frame, hilt, blade direction, torso yaw, torso lean, shoulder reach, elbow spread.
# The load and delivery are authored as whole upper-body poses; the arm solve below
# only closes the fixed paired grip and is baked to ordinary editable FK channels.
BEATS=[
(1,(-.06,-.25,1.22),(-.28,-.48,.83),0,0,.04,.28),
(7,(-.08,-.29,1.25),(-.25,-.48,.84),-.02,.01,.07,.29),
(13,(-.10,-.38,1.39),(.48,-.30,.82),-.08,.035,.16,.34),
(17,(-.10,-.24,1.42),(-.28,.22,.94),-.15,.025,.10,.38),
(21,(-.19,-.27,1.39),(-.80,.35,.48),-.22,.02,.06,.40),
(24,(-.19,-.32,1.39),(-.85,-.16,.50),-.16,.035,.12,.38),
(27,(-.12,-.47,1.36),(-.51,-.82,.26),-.03,.06,.20,.31),
(29,(.01,-.50,1.32),(.04,-.99,.10),.07,.07,.22,.27),
(33,(.20,-.42,1.22),(.84,-.51,-.17),.16,.05,.16,.31),
(37,(.17,-.27,1.17),(.89,-.18,-.42),.18,.035,.10,.34),
(43,(.10,-.25,1.21),(.58,-.32,.75),.09,.015,.05,.30),
(49,(-.02,-.25,1.20),(.02,-.46,.89),.025,0,.04,.28),
(61,(-.06,-.25,1.22),(-.28,-.48,.83),0,0,.04,.28)]
MARKERS={1:'Idle',13:'Parry',21:'RiposteStart',29:'Contact',37:'Carry',49:'Return',61:'IdleEnd'}
def swing(rig,name,direction):
    bpy.context.view_layer.update(); p=rig.pose.bones[name]; origin=p.head.copy()
    end=p.tail
    if name.startswith('upperarm01.'):end=rig.pose.bones['lowerarm01.'+name[-1]].head
    elif name.startswith('lowerarm01.'):end=rig.pose.bones['wrist.'+name[-1]].head
    q=(end-p.head).normalized().rotation_difference(Vector(direction).normalized())
    p.matrix=Matrix.Translation(origin)@q.to_matrix().to_4x4()@Matrix.Translation(-origin)@p.matrix
    bpy.context.view_layer.update()
def beat_at(f):
    for idx,(a,b) in enumerate(zip(BEATS,BEATS[1:])):
        if a[0]<=f<=b[0]:
            t=(f-a[0])/(b[0]-a[0]); prev=BEATS[max(0,idx-1)]; nxt=BEATS[min(len(BEATS)-1,idx+2)]
            values=[]
            for i in range(1,7):
                p0,p1,p2,p3=[Vector(v[i]) if i in (1,2) else v[i] for v in (prev,a,b,nxt)]
                m1=(p2-p0)*(b[0]-a[0])/max(1,b[0]-prev[0]);m2=(p3-p1)*(b[0]-a[0])/max(1,nxt[0]-a[0])
                if idx==0:m1*=0
                if idx==len(BEATS)-2:m2*=0
                values.append((2*t**3-3*t*t+1)*p1+(t**3-2*t*t+t)*m1+(-2*t**3+3*t*t)*p2+(t**3-t*t)*m2)
            return values
    raise ValueError(f)
def build():
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'EX_v001_Staging.blend'))
    scene=bpy.context.scene; rig=bpy.data.objects['CF01_CharacterRig']; weapon=bpy.data.objects['EX01_WeaponRoot']
    for o in (rig,weapon):o.animation_data_clear()
    for p in rig.pose.bones:
        for c in list(p.constraints):p.constraints.remove(c)
    scene['EX01_status']='AUTHORED EXCHANGE: editable FK and coupled hilt transform action'
    for o in scene.objects:
        if o.name.startswith(('EX01_Grip','EX01_Elbow')):o.hide_viewport=True
    scene.timeline_markers.clear();scene.frame_start=1;scene.frame_end=61;scene.render.fps=30
    for f,n in MARKERS.items():scene.timeline_markers.new(n,frame=f)
    rest={p.name:p.bone.matrix_local.copy() for p in rig.pose.bones}
    wrist_rest={s:rig.data.bones['wrist.'+s].head_local.copy() for s in ('R','L')}
    max_error=0
    hidden=[o for o in scene.objects if o.type=='MESH' and not o.hide_viewport]
    for o in hidden:o.hide_viewport=True
    for f in range(1,62):
        scene.frame_set(f)
        for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4);p.rotation_mode='QUATERNION'
        hilt,blade,yaw,lean,reach,spread=beat_at(f)
        torso=rig.pose.bones['spine01'];torso.rotation_quaternion=Quaternion((0,0,1),yaw)@Quaternion((1,0,0),lean)
        bpy.context.view_layer.update()
        rot=blade.normalized().to_track_quat('Z','Y');weapon.location=hilt;weapon.rotation_mode='QUATERNION';weapon.rotation_quaternion=rot
        weapon.keyframe_insert('location',frame=f);weapon.keyframe_insert('rotation_quaternion',frame=f)
        for side,sign,depth in [('R',-1,-.085),('L',1,-.215)]:
            swing(rig,'clavicle.'+side,(sign,.0-reach,.13+lean))
            swing(rig,'shoulder01.'+side,(sign,-reach,-.30))
            # Hand frame: palm length traverses handle, fingers close around it.
            rest_y=(rig.data.bones['finger3-1.'+side].head_local-wrist_rest[side]).normalized()
            rest_x=(rig.data.bones['finger2-1.'+side].head_local-rig.data.bones['finger5-1.'+side].head_local).normalized()
            rest_z=rest_x.cross(rest_y).normalized();rest_x=rest_y.cross(rest_z).normalized()
            dst_x=rot@Vector((0,0,1));dst_y=rot@Vector((-sign,0,0));dst_z=dst_x.cross(dst_y).normalized()
            basis=Matrix((dst_x,dst_y,dst_z)).transposed()@Matrix((rest_x,rest_y,rest_z)).transposed().inverted()
            grip=hilt+rot@Vector((0,0,depth))
            target=grip-dst_y*.082+dst_z*.026
            sh=rig.pose.bones['upperarm01.'+side].head.copy()
            l1=(rig.data.bones['lowerarm01.'+side].head_local-rig.data.bones['upperarm01.'+side].head_local).length
            l2=(wrist_rest[side]-rig.data.bones['lowerarm01.'+side].head_local).length
            delta=target-sh;dist=min(delta.length,l1+l2-.002);axis=delta.normalized()
            pole=Vector((sign*spread,.10,-.35));pole=(pole-axis*pole.dot(axis)).normalized()
            along=(l1*l1-l2*l2+dist*dist)/(2*dist);height=math.sqrt(max(0,l1*l1-along*along));elbow=sh+axis*along+pole*height
            swing(rig,'upperarm01.'+side,elbow-sh)
            elbow_actual=rig.pose.bones['lowerarm01.'+side].head.copy()
            swing(rig,'lowerarm01.'+side,target-elbow_actual)
            p=rig.pose.bones['wrist.'+side];loc=p.head.copy();p.matrix=Matrix.Translation(loc)@basis.to_4x4()@rest[p.name].to_3x3().to_4x4()
            bpy.context.view_layer.update();max_error=max(max_error,(p.head-target).length)
            if (p.head-target).length>.01:print("GRIP_ERROR",f,side,round((p.head-target).length,3),"REACH",round(delta.length,3),flush=True)
            for digit in range(1,6):
                for segment in range(1,4):
                    p=rig.pose.bones.get(f'finger{digit}-{segment}.{side}')
                    if p:
                        # Local flexion remains individually editable on all digits.
                        curl=(.65 if digit==1 else 1.10)+(.08 if 24<=f<=33 else 0)
                        p.rotation_quaternion=Quaternion((1,0,0),curl)
        for p in rig.pose.bones:
            p.keyframe_insert('rotation_quaternion',frame=f,group=p.name);p.keyframe_insert('location',frame=f,group=p.name)
    rig.animation_data.action.name='EX01_WholeBody_ParryRightRiposte';weapon.animation_data.action.name='EX01_CoupledHilt_ParryRightRiposte'
    for o in (rig,weapon):
        for fc in o.animation_data.action.fcurves:
            for k in fc.keyframe_points:k.interpolation='LINEAR'
    for o in hidden:o.hide_viewport=False
    fp=bpy.data.objects['EX01_Camera_FP'];fp.data.clip_start=.14;fp.data.lens=16
    fp.rotation_euler=(Vector((0,-2,.65))-fp.location).to_track_quat('-Z','Y').to_euler()
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'EX_v001_Exchange.blend'))
    (OUT/'motion-report.json').write_text(json.dumps({'frames':61,'fps':30,'markers':MARKERS,'max_wrist_solve_error_m':max_error,'method':'Whole-body pose beats, paired-grip closure baked to editable FK. Fixed cameras. No runtime correction.','normal_speed_viewed':False},indent=2))
    print('SOURCE_READY',flush=True)
def render(inspect=False):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'EX_v001_Exchange.blend'))
    s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True
    s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
    cameras=[o for o in s.objects if o.type=='CAMERA' and o.name.startswith('EX01_Camera')];print('CAMERAS',[(c.name) for c in cameras],flush=True)
    for camera in cameras:
        label='FP' if any(t in camera.name.lower() for t in ['first','fp']) else 'External'
        s.camera=camera
        if label=='FP':camera.data.clip_start=.14
        folder=OUT/'Preview'/label;folder.mkdir(parents=True,exist_ok=True)
        for f in ([1,21,29,37] if inspect else range(1,62)):
            s.frame_set(f);s.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
        print('RENDER_DONE',label,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--render',action='store_true');p.add_argument('--inspect',action='store_true');a=p.parse_args()
    if a.render or a.inspect:render(a.inspect)
    else:build()
