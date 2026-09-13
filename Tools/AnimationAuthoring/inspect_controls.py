"""One bounded read-only native-control probe; no render or source save."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    sys.path[:0]=[str(root/'Saved/ArtRuntime'),str(root/'Tools')]
    import bpy
    from AnimationAuthoring.rig import match_support_to_fk
    folder=args.folder.resolve();source=folder/'TP_v001_RightHorizontal.blend'
    before=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene=bpy.context.scene;rig=bpy.data.objects['CF_CTRL']
    for obj in scene.objects:
        if obj.type=='MESH':obj.hide_viewport=True
    primary=bpy.data.objects['CF_PrimaryGrasp'];support=bpy.data.objects['CF_SupportGrasp']
    socket=bpy.data.objects['CF_SupportSocket'];weapon=bpy.data.objects['CF_Weapon']
    scene.frame_set(31);bpy.context.view_layer.update()
    blade_before=weapon.matrix_world.copy();wrist=rig.pose.bones['wrist.R']
    wrist.rotation_euler.x+=.1;bpy.context.view_layer.update()
    blade_delta=(weapon.matrix_world.translation-blade_before.translation).length
    primary_attached=(weapon.matrix_world-(primary.matrix_world@weapon.matrix_basis))
    attachment_error=max(abs(x) for row in primary_attached for x in row)
    scene.frame_set(1);bpy.context.view_layer.update()
    art=bpy.data.objects['CF_SupportArticulation']
    prior=support.matrix_world.to_quaternion()
    art.rotation_euler.x+=.1;bpy.context.view_layer.update()
    support_turn=prior.rotation_difference(support.matrix_world.to_quaternion()).angle
    articulation_gap=(support.matrix_world.translation-socket.matrix_world.translation).length
    scene.frame_set(30);bpy.context.view_layer.update()
    early=rig.pose.bones['wrist.L'].matrix.copy()
    scene.frame_set(44);bpy.context.view_layer.update()
    matched_before=rig.pose.bones['wrist.L'].matrix.copy()
    match_support_to_fk(rig);bpy.context.view_layer.update()
    matched_after=rig.pose.bones['wrist.L'].matrix.copy()
    match_delta=max(abs(x) for row in matched_after-matched_before for x in row)
    scene.frame_set(30);bpy.context.view_layer.update()
    early_delta=max(abs(x) for row in rig.pose.bones['wrist.L'].matrix-early for x in row)
    early_influence=rig['support_influence']
    scene.frame_set(44);bpy.context.view_layer.update()
    late_influence=rig['support_influence']
    channels={}
    for fc in rig.animation_data.action.fcurves:
        if fc.array_index==0 and any(n in fc.data_path for n in ['root','spine01','wrist.R','upperarm01.R']):
            channels[fc.data_path]=[int(k.co.x) for k in fc.keyframe_points]
    result=dict(source_sha256=before,source_preserved=hashlib.sha256(source.read_bytes()).hexdigest()==before,
        primary_wrist_edit_blade_base_delta_m=blade_delta,primary_attachment_matrix_error=attachment_error,
        support_articulation_response_radians=support_turn,support_articulation_grasp_error_m=articulation_gap,
        matched_fk_matrix_delta=match_delta,earlier_pose_matrix_delta_after_switch=early_delta,
        earlier_support_influence=early_influence,switched_support_influence=late_influence,independent_channel_frames=channels)
    (folder/'editable-control-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    assert result['source_preserved'] and blade_delta>1e-5 and attachment_error<1e-5
    assert support_turn>.05 and articulation_gap<.005
    assert match_delta<1e-4 and early_delta<1e-4 and early_influence==1 and late_influence==0


if __name__=='__main__':main()
