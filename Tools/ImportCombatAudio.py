"""Import only the MEL-7 audio bank; never reimport character assets."""
import json
from pathlib import Path
import unreal as u

root = Path(u.Paths.project_dir()).resolve()
manifest = json.loads((root / 'ArtSource/CombatAudio/manifest.json').read_text())
dest = '/Game/Visual/CombatAudio'
tasks = []
for sound in manifest['sounds']:
    task = u.AssetImportTask()
    task.filename = str(root / 'ArtSource/CombatAudio/Export' / (sound['name'] + '.wav'))
    task.destination_path = dest
    task.destination_name = sound['name']
    task.automated = True
    task.replace_existing = True
    task.save = True
    tasks.append(task)
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for sound in manifest['sounds']:
    asset = u.load_asset(dest + '/' + sound['name'])
    if not isinstance(asset, u.SoundWave):
        raise RuntimeError('SoundWave import failed: ' + sound['name'])
    asset.set_editor_property('loading_behavior', u.SoundWaveLoadingBehavior.FORCE_INLINE)
    asset.set_editor_property('sound_group', u.SoundGroup.SOUNDGROUP_EFFECTS)
    # Preserve the short cutting transients and quiet foley without a lossy
    # codec. This small bank prioritizes fidelity over compressed size.
    asset.set_sound_asset_compression_type(u.SoundAssetCompressionType.PCM)
    if not u.EditorAssetLibrary.save_loaded_asset(asset):
        raise RuntimeError('Failed to save ' + sound['name'])
    if asset.get_sound_asset_compression_type() != u.SoundAssetCompressionType.PCM:
        raise RuntimeError('PCM compression setting failed: ' + sound['name'])
u.log('COMBAT AUDIO IMPORT COMPLETE: ' + str(len(tasks)))
