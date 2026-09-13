"""Blender read-only check of a draft's native 500 ms release and preview binding.

Run with Blender --python-exit-code 1 --python this_file -- --source ...
--preview ... --output ... . Timeline markers must be ReleaseStart/ReleaseEnd.
Historical sources without that contract remain historical; this never edits them.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy

ROOT = Path(__file__).resolve().parents[1]


def check_native(scene, configured_seconds):
    fps = scene.render.fps / scene.render.fps_base
    required = scene.get('required_release_seconds')
    if required is None or not math.isclose(float(required), .5, abs_tol=1e-9):
        raise ValueError('Native source must explicitly declare required_release_seconds = 0.5')
    if not math.isclose(configured_seconds, .5, abs_tol=1e-9):
        raise ValueError('Project EX release differs from the required 500 ms authoring contract')
    markers = {name: scene.timeline_markers.get(name) for name in ['ReleaseStart', 'ReleaseEnd']}
    if any(marker is None for marker in markers.values()):
        raise ValueError('Native ReleaseStart and ReleaseEnd timeline markers are required')
    start, end = [markers[name].frame for name in ['ReleaseStart', 'ReleaseEnd']]
    if not scene.frame_start <= start < end <= scene.frame_end:
        raise ValueError('Release markers must be ordered within the complete source range')
    duration = (end - start) / fps
    if not math.isclose(duration, .5, abs_tol=1e-9):
        raise ValueError(f'Native release is {duration:.6f}s; required 0.500000s at source speed')
    return dict(fps=fps, frames=[scene.frame_start, scene.frame_end], release_frames=[start,end],
                release_frame_intervals=end-start, release_seconds=duration, required_release_seconds=required)


def main():
    parser = argparse.ArgumentParser()
    for name in ['source', 'preview', 'output']:
        parser.add_argument('--'+name, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    source, preview, output = [(ROOT / getattr(args, name)).resolve() for name in ['source', 'preview', 'output']]
    if not output.is_relative_to(ROOT) or output.exists():
        raise ValueError('Write a new receipt inside the project; preserve existing evidence')
    config = ROOT / 'Config/CombatDefaults.json'
    configured = json.loads(config.read_text(encoding='utf-8-sig'))['EXReleaseDuration']
    binding = json.loads(preview.read_text(encoding='utf-8-sig'))
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    if (ROOT / binding['source']).resolve() != source or binding['source_sha256'] != source_sha:
        raise ValueError('Preview is bound to a different native source')
    bpy.ops.wm.open_mainfile(filepath=str(source))
    result = check_native(bpy.context.scene, configured)
    if binding['fps'] != result['fps'] or binding['frames'] != result['frames'] or binding['playback_rate'] != 1:
        raise ValueError('Preview timing does not match the complete native source at 1x')
    output.write_text(json.dumps(dict(source=str(source.relative_to(ROOT)), source_sha256=source_sha,
        configured_release_seconds=configured, config_sha256=hashlib.sha256(config.read_bytes()).hexdigest(),
        **result, passed=True, evidence_limit='Native phase markers and preview binding; no runtime contact or artistic acceptance.'), indent=2))
    print('ATTACK_DRAFT_TIMING_PASS ' + json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
