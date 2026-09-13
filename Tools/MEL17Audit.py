"""Read-only source audit. Never rebuild or save the inspected character assets."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Saved/ArtRuntime'))
import bpy

OUT = ROOT / 'ArtSource/StyleReference/MEL17'
OUT.mkdir(parents=True, exist_ok=True)
report = {'bpy': bpy.app.version_string, 'python': sys.version.split()[0], 'sources': []}
for relative in ['ArtSource/CharacterReset/CF_v001/CF_v001_Character.blend',
                 'ArtSource/Citadel/Export/CitadelKnight_Rig.blend']:
    path = ROOT / relative
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(path))
    objects = []
    for obj in bpy.context.scene.objects:
        if obj.type not in ('MESH', 'ARMATURE'):
            continue
        entry = {'name': obj.name, 'type': obj.type}
        if obj.type == 'MESH':
            entry.update(vertices=len(obj.data.vertices), polygons=len(obj.data.polygons),
                         uv_layers=[u.name for u in obj.data.uv_layers],
                         materials=[m.name if m else None for m in obj.data.materials],
                         armatures=[m.object.name if m.object else None for m in obj.modifiers if m.type == 'ARMATURE'])
        else:
            entry['bones'] = len(obj.data.bones)
            entry['hand_bones'] = [b.name for b in obj.data.bones if any(s in b.name.lower() for s in ('finger', 'wrist', 'hand', 'metacarp'))]
        objects.append(entry)
    report['sources'].append({'path': relative, 'sha256': digest, 'objects': objects})
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, 'Audit altered source'
report['capabilities'] = {
    'cycles_registered': hasattr(bpy.context.scene, 'cycles'),
    'fbx_export_available': hasattr(bpy.ops.export_scene, 'fbx'),
    'unreal_commandlet': str(Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe')),
    'unreal_commandlet_exists': Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe').is_file(),
    'scope': 'Source reopen and inventory only; existing CF renders reviewed separately. No new style proof or engine import.'
}
(OUT / 'asset-audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'bpy': report['bpy'], 'source_count': len(report['sources']), 'report': str(OUT / 'asset-audit.json')}))
