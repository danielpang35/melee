"""Create a separate editable exchange stage from CF_v001; no motion authored."""
import sys, math, json, argparse
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Saved/ArtRuntime'))
import bpy
from mathutils import Vector, Matrix

OUT = ROOT / 'ArtSource/CharacterReset/EX_v001'
PHASES = [(1, 'Idle'), (13, 'Parry'), (21, 'RightRiposte_Start'),
          (29, 'RightRiposte_Contact'), (37, 'Carry'), (49, 'Return'), (61, 'Idle_Loop')]

def empty(name, location, parent=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    obj.location = location
    obj.empty_display_type = 'ARROWS'
    obj.empty_display_size = .06
    return obj

def material(name, color, metal=0):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metal
    bsdf.inputs['Roughness'].default_value = .38 if metal else .7
    return mat

def box(name, location, dimensions, mat, parent):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object; obj.name = name; obj.parent = parent
    obj.location = location; obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('SmallEdgeBevel', 'BEVEL'); bevel.width = .002; bevel.segments = 2
    obj.modifiers.new('WeightedNormals', 'WEIGHTED_NORMAL')
    return obj

def camera(name, location, target, lens):
    data = bpy.data.cameras.new(name); data.lens = lens
    obj = bpy.data.objects.new(name, data); bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z', 'Y').to_euler()
    data.clip_start = .025
    obj['contract'] = 'Fixed world transform; do not track weapon or animate camera'
    return obj

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'ArtSource/CharacterReset/CF_v001/CF_v001_Character.blend'))
    scene = bpy.context.scene; rig = bpy.data.objects['CF01_CharacterRig']
    rig.animation_data_clear()
    for pb in rig.pose.bones: pb.matrix_basis = Matrix.Identity(4)
    scene.timeline_markers.clear()
    scene.render.fps = 30; scene.frame_start = 1; scene.frame_end = 61
    for frame, name in PHASES: scene.timeline_markers.new(name, frame=frame)
    scene.frame_set(1)
    root = empty('EX01_WeaponRoot', (0, -.43, 1.30))
    root['contract'] = 'Canonical sword transform. Origin blade base; +Z to tip; +X guard; meters.'
    empty('EX01_BladeBase', (0,0,0), root)
    empty('EX01_BladeTip', (0,0,.90), root)
    steel = material('EX01_Steel', (.40,.45,.50), .8)
    leather = material('EX01_Leather', (.055,.027,.014))
    # Diamond cross-section taper and pointed tip, not a full-thickness box.
    vertices = []
    for z, width in [(0,.042),(.72,.032),(.84,.019)]:
        vertices += [(-width/2,0,z),(0,-.004,z),(width/2,0,z),(0,.004,z)]
    vertices.append((0,0,.90))
    faces = [(3,2,1,0)]
    for ring in range(2):
        for i in range(4): faces.append((ring*4+i,ring*4+(i+1)%4,(ring+1)*4+(i+1)%4,(ring+1)*4+i))
    for i in range(4): faces.append((8+i,8+(i+1)%4,12))
    mesh = bpy.data.meshes.new('EX01_BladeMesh'); mesh.from_pydata(vertices,[],faces); mesh.update()
    blade = bpy.data.objects.new('EX01_Blade',mesh); bpy.context.collection.objects.link(blade)
    blade.parent = root; blade.data.materials.append(steel)
    box('EX01_Guard',(0,0,-.012),(.23,.022,.021),steel,root)
    box('EX01_Handle',(0,0,-.14),(.027,.030,.235),leather,root)
    box('EX01_Pommel',(0,0,-.277),(.048,.040,.035),steel,root)
    bpy.context.view_layer.update()
    for side, sign, height in [('R',-1,-.075),('L',1,-.18)]:
        target = empty('EX01_Grip.'+side,(sign*.095,.0,height),root)
        # Palm longitudinal axis across the handle; thumb side points up blade.
        y = Vector((-sign,0,0)); x = Vector((0,0,1)); z = x.cross(y)
        target.rotation_mode = 'QUATERNION'
        target.rotation_quaternion = Matrix((x,y,z)).transposed().to_quaternion()
        target['role'] = 'Wrist control, coupled to sword; editable local placement/rotation for grip polish'
        pole = empty('EX01_Elbow.'+side,(sign*.48,-.10,1.02))
        pole['role'] = 'Editable elbow pole; shoulder and clavicle remain direct pose controls'
        # Keep twist segments rigid for IK so only anatomical upper/lower arm bend.
        for prefix in ['upperarm02.','lowerarm02.']:
            pb = rig.pose.bones[prefix+side]
            pb.lock_ik_x = pb.lock_ik_y = pb.lock_ik_z = True
        ik = rig.pose.bones['lowerarm02.'+side].constraints.new('IK')
        ik.name = 'EX01_TwoHandCoupling'; ik.target = target
        ik.chain_count = 4; ik.use_stretch = False; ik.iterations = 128
        # A freely editable pole is supplied, but disabled initially: twist-rest
        # axes need animator calibration before enabling its angle.
        pole['activation'] = 'Assign to lowerarm02 IK pole_target after calibrating pole_angle'
        rot = rig.pose.bones['wrist.'+side].constraints.new('COPY_ROTATION')
        rot.name = 'EX01_GripOrientation'; rot.target = target
        rot.target_space = rot.owner_space = 'WORLD'
        for pb in rig.pose.bones:
            if pb.name.startswith('finger') and pb.name.endswith('.'+side):
                pb.rotation_mode = 'XYZ'
                pb.rotation_euler.x = math.radians(50 if not pb.name.startswith('finger1') else 20)
                pb['role'] = 'Editable finger curl; initial contact is a staging approximation'
    external = camera('EX01_Camera_External',(2.7,-4.8,2.35),(0,-.15,1.08),55)
    camera('EX01_Camera_FP',(0,-.115,1.68),(0,-2,1.38),24)
    scene.camera = external
    scene.render.resolution_x = 1100; scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100; scene.cycles.samples = 16
    scene['EX01_status'] = 'STATIC STAGING ONLY; phase markers are an authoring contract, not keyed motion'
    bpy.context.view_layer.update()
    residuals = {s:(rig.pose.bones['wrist.'+s].head-bpy.data.objects['EX01_Grip.'+s].matrix_world.translation).length for s in ['R','L']}
    (OUT/'staging-report.json').write_text(json.dumps({'fps':30,'phase_markers':PHASES,'wrist_target_error_m':residuals,'animation_authored':False},indent=2))
    bpy.ops.object.select_all(action='DESELECT'); root.select_set(True); bpy.context.view_layer.objects.active=root
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'EX_v001_Staging.blend'))
    print(json.dumps(residuals), flush=True)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--render',action='store_true'); args=parser.parse_args()
    build()
    if args.render:
        bpy.context.scene.render.filepath=str(OUT/'staging.png')
        bpy.ops.render.render(write_still=True)
