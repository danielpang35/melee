"""Unreal commandlet: import one immutable TP revision and write opt-in selection.

UnrealEditor-Cmd project.uproject -run=pythonscript -script=Tools/ImportThirdPersonSwing.py
The approved EX selector/assets and original CF skeleton are never modified.
"""
import hashlib
import json
import os
import shutil
from pathlib import Path
import unreal as u

ROOT = Path(u.Paths.project_dir()).resolve()
EXPORT = ROOT / os.environ.get('MCL_TP_EXPORT', 'ArtSource/CharacterReset/TP_v001/Export')
OUT = ROOT / os.environ.get('MCL_TP_IMPORT_OUT', 'Saved/TPProof')
OUT.mkdir(parents=True, exist_ok=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


# Use the reflected native name: Python type naming removes the underscore in
# some engine versions. PyCore::new_object explicitly accepts a loaded UClass.
codec_class = u.load_class(None, '/Script/Engine.AnimCompress_BitwiseCompressOnly')
assert codec_class, 'Native unreduced compression codec unavailable'
# Check the remaining new reflection surface before expensive asset import.
for method in ('get_anim_pose_at_time', 'get_bone_names', 'get_bone_pose'):
    assert callable(getattr(u.AnimPoseExtensions, method, None)), ('Missing pose API', method)
evaluation = u.AnimPoseEvaluationOptions()
evaluation.set_editor_property('evaluation_type', u.AnimDataEvalType.COMPRESSED)
evaluation.set_editor_property('should_retarget', False)
evaluation.set_editor_property('extract_root_motion', False)
world_pose_space = u.AnimPoseSpaces.WORLD
u.Transform().scale3d  # Verify the additional reflected field before importing.


manifest = json.loads((EXPORT / 'manifest.json').read_text())
assert manifest['profile'] in ('TP_native_60_v1', 'TP_native_attack_age_v1')
pilot = manifest['profile'] == 'TP_native_attack_age_v1'
duration = manifest['duration_s']
assert json.loads((EXPORT / 'export-verification.json').read_text())['passed']
assert sha(ROOT / manifest['source']) == manifest['source_sha256']
for name, expected in manifest['files'].items():
    assert sha(EXPORT / name) == expected, name
baseline = ROOT / 'Config/EXPreview.json'
baseline_hash = sha(baseline)
pipeline_identity = dict(profile='TP_native_import_v1', importer_sha256=sha(Path(__file__)),
                         manifest_sha256=sha(EXPORT / 'manifest.json'))
identity = hashlib.sha256(json.dumps(pipeline_identity, sort_keys=True).encode()).hexdigest()[:12]
base_dest = '/Game/TPPreview/TP_v001_' + identity
mesh_name = 'TPBody'
# An interrupted mesh+animation import may leave only a mesh or orphan skeleton.
# Preserve that evidence and retry into one fresh suffix; never delete/overwrite
# partially imported assets or silently reuse a mesh without its sequence.
skipped_attempts = []
for attempt in range(20):
    dest = base_dest if attempt == 0 else base_dest + '_retry' + str(attempt).zfill(2)
    if not u.EditorAssetLibrary.does_directory_exist(dest):
        break
    existing = [u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(dest, recursive=True)]
    if not existing:
        break
    existing_mesh = u.load_asset(dest + '/' + mesh_name)
    existing_animations = [a for a in existing if isinstance(a, u.AnimSequence)]
    complete = (isinstance(existing_mesh, u.SkeletalMesh) and len(existing_animations) == 1
                and existing_animations[0].get_editor_property('skeleton') == existing_mesh.get_editor_property('skeleton')
                and abs(existing_animations[0].get_play_length() - duration) < .0001)
    if complete:
        break
    skipped_attempts.append(dict(destination=dest, mesh_present=isinstance(existing_mesh, u.SkeletalMesh),
                                 animation_count=len(existing_animations)))
else:
    raise RuntimeError('Twenty incomplete TP native imports preserved; inspect their receipts before another attempt')
write(OUT / 'import-attempt.json', dict(pipeline_identity=pipeline_identity, destination=dest,
      attempt=attempt, preserved_incomplete_attempts=skipped_attempts))
mesh_path = dest + '/' + mesh_name
u.SystemLibrary.execute_console_command(None, 'Interchange.FeatureFlags.Import.FBX 0')
if not u.EditorAssetLibrary.does_asset_exist(mesh_path):
    options = u.FbxImportUI()
    options.automated_import_should_detect_type = False
    options.import_mesh = True
    options.import_as_skeletal = True
    options.mesh_type_to_import = u.FBXImportType.FBXIT_SKELETAL_MESH
    options.import_animations = True
    options.import_materials = False
    options.import_textures = False
    options.create_physics_asset = False
    options.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose', False)
    options.skeletal_mesh_import_data.set_editor_property('update_skeleton_reference_pose', False)
    anim_options = options.anim_sequence_import_data
    anim_options.set_editor_property('use_default_sample_rate', False)
    anim_options.set_editor_property('custom_sample_rate', 60)
    anim_options.set_editor_property('remove_redundant_keys', False)
    anim_options.set_editor_property('preserve_local_transform', True)
    anim_options.set_editor_property('import_bone_tracks', True)
    anim_options.set_editor_property('animation_length', u.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    task = u.AssetImportTask()
    task.filename = str(EXPORT / 'TP_v001_RightHorizontal.fbx')
    task.destination_path = dest
    task.destination_name = mesh_name
    task.options = options
    task.automated = True
    task.replace_existing = False
    task.save = True
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
mesh = u.load_asset(mesh_path)
assert isinstance(mesh, u.SkeletalMesh), 'Expected one complete skeletal body mesh'
weapon_path = dest + '/TPWeapon'
if not u.EditorAssetLibrary.does_asset_exist(weapon_path):
    options = u.FbxImportUI()
    options.automated_import_should_detect_type = False
    options.import_mesh = True
    options.import_as_skeletal = False
    options.mesh_type_to_import = u.FBXImportType.FBXIT_STATIC_MESH
    options.import_animations = False
    options.import_materials = False
    options.import_textures = False
    options.static_mesh_import_data.set_editor_property('combine_meshes', True)
    options.static_mesh_import_data.set_editor_property('auto_generate_collision', False)
    task = u.AssetImportTask()
    task.filename = str(EXPORT / 'TP_v001_Weapon.fbx')
    task.destination_path = dest
    task.destination_name = 'TPWeapon'
    task.options = options
    task.automated = True
    task.replace_existing = False
    task.save = True
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
weapon = u.load_asset(weapon_path)
assert isinstance(weapon, u.StaticMesh)
weapon_bounds = weapon.get_bounding_box()
assert abs(weapon_bounds.max.z - 103.5) < .10, ('Imported static blade tip/origin/scale mismatch', weapon_bounds.max.z)
for index, slot in enumerate(weapon.get_editor_property('static_materials')):
    slot_name = str(slot.get_editor_property('material_slot_name'))
    data = manifest['weapon_materials'].get(slot_name)
    assert data, ('Unrecognized source weapon material', slot_name)
    material = u.load_asset(dest + '/' + slot_name)
    if not material:
        material = u.AssetToolsHelpers.get_asset_tools().create_asset(slot_name, dest, u.Material, u.MaterialFactoryNew())
        color = u.MaterialEditingLibrary.create_material_expression(material, u.MaterialExpressionConstant3Vector)
        color.set_editor_property('constant', u.LinearColor(*data['color']))
        u.MaterialEditingLibrary.connect_material_property(color, '', u.MaterialProperty.MP_BASE_COLOR)
        for value, prop in ((data['metallic'], u.MaterialProperty.MP_METALLIC), (data['roughness'], u.MaterialProperty.MP_ROUGHNESS)):
            node = u.MaterialEditingLibrary.create_material_expression(material, u.MaterialExpressionConstant)
            node.set_editor_property('r', value)
            u.MaterialEditingLibrary.connect_material_property(node, '', prop)
        u.MaterialEditingLibrary.recompile_material(material)
        u.EditorAssetLibrary.save_loaded_asset(material)
    weapon.set_material(index, material)
u.EditorAssetLibrary.save_loaded_asset(weapon)
assets = [u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(dest, recursive=True)]
animations = [a for a in assets if isinstance(a, u.AnimSequence)]
assert len(animations) == 1, [a.get_path_name() for a in animations]
animation = animations[0]
assert animation.get_editor_property('skeleton') == mesh.get_editor_property('skeleton')
assert abs(animation.get_play_length() - duration) < .0001
settings_path = dest + '/TP_Unreduced'
settings = u.load_asset(settings_path)
if not settings:
    settings = u.AssetToolsHelpers.get_asset_tools().create_asset('TP_Unreduced', dest, u.AnimBoneCompressionSettings, u.AnimBoneCompressionSettingsFactory())
    codec = u.new_object(codec_class, outer=settings)
    settings.set_editor_property('codecs', [codec])
    u.EditorAssetLibrary.save_loaded_asset(settings)
animation.set_editor_property('bone_compression_settings', settings)
animation.set_editor_property('enable_root_motion', False)
animation.set_editor_property('force_root_lock', False)
u.EditorAssetLibrary.save_loaded_asset(animation)
u.EditorAssetLibrary.save_directory(dest, only_if_is_dirty=True, recursive=True)

# Native compressed component transforms at phase keys and diagnostic subframes.
# Runtime additionally compares all154 source frames with every102 deform bone.
source_data = json.loads((EXPORT / 'TP_v001_SkeletonMotion.json').read_text())
assert source_data['diagnostic_profile'] == ('TP_native_attack_age_v1' if pilot else 'TP_uniform_component_scale_carry_v1')
times = source_data['diagnostic_sample_times_s']
assert len(times) == len(set(times)) and times == sorted(times)
assert all(0 <= t <= duration for t in times)
assert len(times) == (6 if pilot else 25)
native = []
for time in times:
    pose = u.AnimPoseExtensions.get_anim_pose_at_time(animation, time, evaluation)
    bones = {}
    for name in u.AnimPoseExtensions.get_bone_names(pose):
        transform = u.AnimPoseExtensions.get_bone_pose(pose, name, world_pose_space)
        p, q, s = transform.translation, transform.rotation, transform.scale3d
        bones[str(name)] = dict(position_cm=[p.x, p.y, p.z], quaternion_xyzw=[q.x, q.y, q.z, q.w],
                                component_scale=[s.x, s.y, s.z])
    native.append(dict(time_s=time, bones=bones))
write(OUT / 'native-import-samples.json', dict(mesh=mesh.get_path_name(), animation=animation.get_path_name(),
      space='UE imported component (source reflectY, meters→cm); not gameplay world',
      diagnostic_profile=source_data['diagnostic_profile'], diagnostic_sample_times_s=times, samples=native))
assert sha(baseline) == baseline_hash
revision_dir = (EXPORT.parent / 'Runtime' if pilot else OUT / 'revisions') / identity
revision_dir.mkdir(parents=True, exist_ok=True)
for name in ('TP_v001_WeaponMotion.json', 'TP_v001_SkeletonMotion.json', 'manifest.json'):
    copied = revision_dir / name
    if copied.exists():
        assert sha(copied) == sha(EXPORT / name), 'Immutable revision metadata mismatch'
    else:
        shutil.copy2(EXPORT / name, copied)
selection = dict(revision='TP_v001-source-' + manifest['source_sha256'][:8] + '-FBX-' + identity,
                 mesh=mesh.get_path_name(), animation=animation.get_path_name(), weapon_mesh=weapon.get_path_name(),
                 weapon_motion=str((revision_dir / 'TP_v001_WeaponMotion.json').relative_to(ROOT)),
                 skeleton_motion=str((revision_dir / 'TP_v001_SkeletonMotion.json').relative_to(ROOT)),
                 source_sha256=manifest['source_sha256'], canonical_authority=False)
if pilot:
    selection.update(profile=manifest['profile'], fps=manifest['fps'], duration_s=duration,
                     idle_source_s=manifest['idle_source_s'])
write(OUT / 'selection.json', selection)
write(OUT / 'import-receipt.json', dict(selection=selection, pipeline_identity=pipeline_identity, imported_assets=[a.get_path_name() for a in assets if a],
      attempt_destination=dest, attempt=attempt, preserved_incomplete_attempts=skipped_attempts,
      static_weapon_tip_z_cm=weapon_bounds.max.z,
      baseline_selection_unchanged=sha(baseline) == baseline_hash, native_source_validation='Pending runtime all-frame gate',
      native_diagnostic_samples='Saved/TPProof/native-import-samples.json', artistic_acceptance=False))
u.log('TPPROOF_IMPORT ' + json.dumps(selection))
