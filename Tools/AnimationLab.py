"""Cheap isolated TP exploration: new -> render -> select -> refine. No Unreal work."""
from __future__ import annotations
import argparse
import copy
import hashlib
import html
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / 'ArtSource/AnimationLab'
POLICY = 'MCL-DEV-2026-09-08'
INPUTS = ['Tools/AuthorThirdPersonSwing.py', 'Tools/AuthorFreshExchange.py',
          'ArtSource/CharacterReset/CF_v001/CF_v001_Character.blend',
          'ArtSource/CharacterReset/EX_v002/Export/EX_v002_WeaponMotion.json']
VARIANTS = [
    ('A_control', 'Control: preserve the seed whole performance'),
    ('B_deeper_load', 'Stronger backward/lateral hand draw and shoulder coil'),
    ('C_rounder_sweep', 'Broader curved hand route with earlier opening'),
    ('D_longer_carry', 'More sustained opposite-side carry and body follow-through'),
]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def slug(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', value):
        raise ValueError('Use a short name containing only letters, digits, _ and -')
    return value


def batch_path(name):
    path = (LAB / slug(name)).resolve()
    if not path.is_relative_to(LAB.resolve()):
        raise ValueError('Batch must stay inside AnimationLab')
    return path


def candidate_folder(batch, candidate):
    path = (batch/candidate['folder']).resolve()
    if not path.is_relative_to((batch/'source/Candidates').resolve()) or path.name != 'TP_v001':
        raise ValueError('Candidate output must stay in its isolated batch')
    return path


def checked_preview(folder):
    receipt = read(folder/'preview.json')
    if receipt.get('native_input_sha256') and receipt['native_input_sha256'] != digest(folder/'native-input.blend'):
        raise ValueError('Editable native input changed since preview; create a new take')
    if receipt.get('derived_samples_sha256') and receipt['derived_samples_sha256'] != digest(folder/'weapon-samples.json'):
        raise ValueError('Derived weapon samples changed since preview; preserve the recorded evidence')
    for field, filename in [('controls_sha256', 'pose-controls.json'),
                            ('source_sha256', 'TP_v001_RightHorizontal.blend'),
                            ('preview_sha256', 'preview.mp4')]:
        if receipt[field] != digest(folder/filename):
            raise ValueError('Candidate changed since its preview; preserve it and create a new take')
    return receipt


VIEW_POLICY = 'MCL-MULTI-ANGLE-2026-09-13'


def checked_views(folder, primary, expected_cameras=None):
    """New checks require supplementary evidence; old primary receipts stay readable."""
    path = folder/'preview-views.json'
    if not path.exists():
        raise ValueError('Historical/single-view preview retained; new validation requires primary and rear-quarter evidence in a new take')
    evidence = read(path)
    if evidence.get('policy') != VIEW_POLICY:
        raise ValueError('Missing current multi-angle evidence policy')
    cameras = {}
    timing = {k: primary.get(k) for k in ('fps', 'source_fps', 'first_source_frame', 'source_stride', 'frames', 'playback_rate')}
    if timing['playback_rate'] != 1:
        raise ValueError('Comparison must use source-speed playback')
    for name in ('primary', 'rear-quarter'):
        view = evidence.get('views', {}).get(name)
        if not view:
            raise ValueError(f'Missing required view: {name}')
        if view['source_sha256'] != primary['source_sha256']:
            raise ValueError('View source identity is stale')
        if view['timing'] != timing:
            raise ValueError('Views must use identical source timing')
        media = (folder/view['file']).resolve()
        if not media.is_relative_to(folder.resolve()) or not media.is_file() or digest(media) != view['sha256']:
            raise ValueError('Missing or changed camera evidence')
        cameras[name] = view['camera']
    if expected_cameras is not None and cameras != expected_cameras:
        raise ValueError('Use the same camera definitions across candidates')
    return cameras


def render_required_views(folder):
    """Supplement the compatible primary receipt, without saving or rebuilding source."""
    import bpy
    import imageio_ffmpeg
    from PIL import Image
    from mathutils import Vector
    primary = checked_preview(folder)
    scene = bpy.context.scene
    original = scene.camera
    def camera_identity(camera):
        return dict(matrix_world=[list(row) for row in camera.matrix_world],
                    type=camera.data.type, lens=camera.data.lens,
                    ortho_scale=camera.data.ortho_scale)
    timing = {k: primary.get(k) for k in ('fps', 'source_fps', 'first_source_frame', 'source_stride', 'frames', 'playback_rate')}
    views = {'primary': dict(file='preview.mp4', sha256=primary['preview_sha256'],
              source_sha256=primary['source_sha256'], timing=timing, camera=camera_identity(original))}
    rear = original.copy(); rear.data = original.data.copy()
    scene.collection.objects.link(rear)
    rear.name = 'AnimationLab_RearQuarter_v1'
    rear.location = (-original.location.x, -original.location.y, original.location.z)
    rear.rotation_euler = (Vector((0, 0, 1.0))-rear.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = rear
    bpy.context.view_layer.update()
    w = int(scene.render.resolution_x*scene.render.resolution_percentage/100)
    h = int(scene.render.resolution_y*scene.render.resolution_percentage/100)
    pending = folder/'preview-rear-quarter.pending.mp4'
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error', '-f', 'rawvideo',
           '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(primary['fps']), '-i', '-', '-an',
           '-c:v', 'libx264', '-threads', '2', '-preset', 'veryfast', '-crf', '24',
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(pending)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(primary['frames']):
            scene.frame_set(primary['first_source_frame']+i*primary['source_stride'])
            scene.render.filepath = str(folder/'preview-rear-quarter-frame.png')
            bpy.ops.render.render(write_still=True)
            with Image.open(scene.render.filepath) as im:
                proc.stdin.write(im.convert('RGB').tobytes())
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError('Rear-quarter encoder failed')
    finally:
        if proc.poll() is None:
            proc.kill(); proc.wait()
        scene.camera = original
    pending.replace(folder/'preview-rear-quarter.mp4')
    views['rear-quarter'] = dict(file='preview-rear-quarter.mp4', sha256=digest(folder/'preview-rear-quarter.mp4'),
        source_sha256=primary['source_sha256'], timing=timing, camera=camera_identity(rear))
    checked_preview(folder)
    write(folder/'preview-views.json', dict(policy=VIEW_POLICY, views=views, human_acceptance=False,
                                          continuous_playback_review=False))
    checked_views(folder, primary)


# Historical frame/weapon-input contract lives only in its adapter.
from AnimationAuthoring.legacy import validate_score


def envelope(frame, start, peak, end):
    if frame <= start or frame >= end:
        return 0.
    return (frame-start)/(peak-start) if frame <= peak else (end-frame)/(end-peak)


def variation(seed, index):
    score = copy.deepcopy(seed)
    score['revision'] = VARIANTS[index][0]
    score['status'] = 'Exploration only; no human or gameplay acceptance'
    score['hypothesis'] = VARIANTS[index][1]
    for b in score['beats']:
        f = b['f']
        if index == 1:
            w = envelope(f, 19, 46, 63)
            b['h'][0] -= .10*w
            b['h'][1] += .10*w
            b['cy'] -= 12*w
            b['py'] -= 4*w
        elif index == 2:
            w = envelope(f, 36, 57, 81)
            b['h'][0] -= .09*w
            b['h'][1] -= .055*w
            b['cy'] -= 7*w
            if 52 < f < 63:
                b['f'] -= 2
        elif index == 3:
            w = envelope(f, 73, 94, 139)
            b['h'][0] += .13*w
            b['h'][1] -= .045*w
            b['cy'] += 10*w
            b['py'] += 3*w
    validate_score(score)
    return score


def make_batch(args):
    if args.adapter is None:
        working = read(ROOT/'Config/WorkingCharacter.json')
        args.adapter = working.get('animation_adapter')
        if not args.adapter:
            raise ValueError('Working AccuRig body has no AnimationLab control adapter yet. '
                             f"Author in {working['native_source']}; "
                             'use --adapter cf-controls-v1 only for archived Knight/CF drafts.')
    destination = batch_path(args.batch)
    is_controls = args.adapter == 'cf-controls-v1'
    from AnimationAuthoring import performance
    seed_path = Path(args.seed).resolve() if args.seed else None
    if seed_path is None and not is_controls:
        seed_path = ROOT/'ArtSource/CharacterReset/TP_v001/pose-controls.json'
    seed = read(seed_path) if seed_path else (performance.seed_score() if is_controls else read(ROOT/'ArtSource/CharacterReset/TP_v001/pose-controls.json'))
    (performance.validate_score if is_controls else validate_score)(seed)
    inputs = performance.INPUTS if is_controls else INPUTS
    if destination.exists():
        raise ValueError('Batch already exists; use a new name to retain prior takes')
    # Snapshot the small authoring closure once; live source remains untouched.
    for path in inputs:
        if not (ROOT/path).is_file():
            raise ValueError(f'Missing authoring dependency: {path}')
    destination.mkdir(parents=True)
    identities = {}
    for relative in inputs:
        target = destination/'source'/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/relative, target)
        identities[relative] = digest(target)
    manifest = dict(policy=POLICY, batch=args.batch, created=time.time(),
                    adapter=args.adapter, seed=str(seed_path) if seed_path else 'adapter default',
                    seed_sha256=digest(seed_path) if seed_path else None, inputs=identities,
                    selected=None, human_acceptance=False, candidates=[])
    for index in range(1 if is_controls else args.count):
        name, hypothesis = (('A_control_proof', seed['hypothesis']) if is_controls else VARIANTS[index])
        folder = destination/'source/Candidates'/name/'TP_v001'
        folder.mkdir(parents=True)
        write(folder/'pose-controls.json', seed if is_controls else variation(seed, index))
        manifest['candidates'].append(dict(id=name, hypothesis=hypothesis,
                                          folder=folder.relative_to(destination).as_posix(), state='draft'))
    write(destination/'batch.json', manifest)
    gallery(destination, manifest)
    print(f'Created {len(manifest["candidates"])} independent drafts: {destination / "index.html"}')


def gallery(batch, manifest):
    cards = []
    for c in manifest['candidates']:
        preview = batch/c['folder']/'preview.mp4'
        media = (f'<video controls loop muted preload="metadata" src="{html.escape(preview.relative_to(batch).as_posix())}"></video>'
                 if preview.exists() else '<p>Preview not rendered yet.</p>')
        rear = batch/c['folder']/'preview-rear-quarter.mp4'
        if rear.exists():
            media += f'<p>Rear-quarter</p><video controls loop muted preload="metadata" src="{html.escape(rear.relative_to(batch).as_posix())}"></video>'
        cards.append(f'<article><h2>{html.escape(c["id"])}</h2><p>{html.escape(c["hypothesis"])}</p>{media}<p>{html.escape(c["state"])}</p></article>')
    selection = manifest.get('selected')
    selected_text = ('<p><strong>Provisional selection: ' + html.escape(selection['id']) + '</strong> — ' + html.escape(selection['reason']) + '</p>') if selection else '<p>No candidate selected yet.</p>'
    page = '''<!doctype html><meta charset="utf-8"><title>Animation candidates</title>
<style>body{background:#161c24;color:#eef1f5;font:16px system-ui;margin:24px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}article{background:#222b36;padding:14px;border-radius:8px}video{width:100%}button{padding:10px;margin:0 8px 16px 0}h2{font-size:18px}</style>
<h1>''' + html.escape(manifest['batch']) + '</h1>' + selected_text + '''<p>Source-speed drafts. Compare load, hand arc, delivery, coordination and recovery. Agent selection is provisional.</p>
<button onclick="document.querySelectorAll('video').forEach(v=>{v.currentTime=0;v.play()})">Play all from start</button>
<button onclick="document.querySelectorAll('video').forEach(v=>v.pause())">Pause all</button><main>''' + ''.join(cards) + '</main>'
    (batch/'index.html').write_text(page, encoding='utf-8')


def worker(args):
    runner_hash = digest(Path(__file__))
    batch = batch_path(args.batch)
    manifest = read(batch/'batch.json')
    c = next(c for c in manifest['candidates'] if c['id'] == args.candidate)
    folder = candidate_folder(batch, c)
    # Art runtime is shared read-only; author code and data are batch-local copies.
    sys.path[:0] = [str(ROOT/'Saved/ArtRuntime'), str(ROOT/'Saved/VideoRuntime'), str(batch/'source/Tools')]
    if manifest.get('adapter') == 'cf-controls-v1':
        # The CLI imported legacy validation before inserting the snapshot path.
        # Reload the package from that immutable authoring closure for the worker.
        for module in list(sys.modules):
            if module == 'AnimationAuthoring' or module.startswith('AnimationAuthoring.'):
                del sys.modules[module]
        from AnimationAuthoring import bake
        native_input = folder/'native-input.blend'
        source = bake.build(batch/'source', folder, native_input if native_input.exists() else None)
        print('EDITABLE_SOURCE_READY', source, flush=True)
        receipt_manifest = dict(manifest, native_input_sha256=digest(native_input) if native_input.exists() else None)
        bake.preview(folder, source, receipt_manifest, runner_hash)
        render_required_views(folder)
        return
    import bpy
    import imageio_ffmpeg
    from PIL import Image
    spec = importlib.util.spec_from_file_location('batch_author', batch/'source/Tools/AuthorThirdPersonSwing.py')
    author = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(author)
    author.OUT = folder
    author.SOURCE = folder/'TP_v001_RightHorizontal.blend'
    author.build()
    author.setup_render()
    scene = bpy.context.scene
    scene.camera = bpy.data.objects['TP01_' + args.camera]
    scene.render.resolution_x, scene.render.resolution_y = 512, 416
    scene.render.resolution_percentage = 100
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 2
    scene.display.render_aa = 'FXAA'
    source_hash = digest(author.SOURCE)
    controls_hash = digest(folder/'pose-controls.json')
    preview = folder/'preview.mp4'
    pending = folder/'preview.pending.mp4'
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error', '-f', 'rawvideo',
           '-pix_fmt', 'rgb24', '-s', '512x416', '-r', '30', '-i', '-', '-an',
           '-c:v', 'libx264', '-threads', '2', '-preset', 'veryfast', '-crf', '24',
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(pending)]
    frames = list(range(19, 155, 2))
    with open(folder/'encode.log', 'wb') as error_log:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=error_log)
        try:
            for frame in frames:
                scene.frame_set(frame)
                scene.render.filepath = str(folder/'preview-frame.png')
                bpy.ops.render.render(write_still=True)
                with Image.open(scene.render.filepath) as im:
                    proc.stdin.write(im.convert('RGB').tobytes())
            proc.stdin.close()
            if proc.wait() != 0:
                raise RuntimeError('Preview encoder failed; see encode.log')
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
    pending.replace(preview)
    write(folder/'preview.json', dict(source_sha256=source_hash, controls_sha256=controls_hash,
          preview_sha256=digest(preview), camera=args.camera, fps=30, source_fps=60,
          first_source_frame=19, source_stride=2, frames=len(frames), duration_s=len(frames)/30,
          playback_rate=1, human_acceptance=False, author_inputs=manifest['inputs'],
          runner_sha256=runner_hash, python_version=sys.version,
          blender_version=bpy.app.version_string))

    render_required_views(folder)


def render_batch(args):
    batch = batch_path(args.batch)
    manifest = read(batch/'batch.json')
    for candidate in manifest['candidates']:
        candidate_folder(batch, candidate)
    if args.candidate and not any(c['id'] == args.candidate for c in manifest['candidates']):
        raise ValueError('Unknown candidate')
    if args.camera is None:
        args.camera = 'MEL36_Defender_Perspective_v1' if manifest.get('adapter') == 'cf-controls-v1' else 'FrontThreeQuarter'
    if manifest.get('adapter') == 'cf-controls-v1' and args.camera != 'MEL36_Defender_Perspective_v1':
        raise ValueError('CF controls proof uses the saved MEL-36 camera')
    existing_cameras = {read(batch/c['folder']/'preview.json')['camera'] for c in manifest['candidates']
                        if (batch/c['folder']/'preview.json').exists()}
    camera = manifest.get('camera') or (next(iter(existing_cameras)) if existing_cameras else args.camera)
    if len(existing_cameras) > 1 or args.camera != camera:
        raise ValueError('One comparison camera per batch; create another batch for another view')
    for relative, expected in manifest['inputs'].items():
        if digest(batch/'source'/relative) != expected:
            raise ValueError(f'Snapshot input changed: {relative}; create a new batch')
    manifest['camera'] = camera
    lock = LAB/'render.lock'
    # No stale-lock deletion: inspection/resume is deliberate after interruption.
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(fd, 'w', encoding='utf-8') as handle:
        json.dump(dict(batch=args.batch, pid=os.getpid(), started=time.time()), handle)
    try:
        (batch/'render.lock').write_text(str(os.getpid()), encoding='utf-8')
        write(batch/'batch.json', manifest)
        comparison_cameras = None
        for existing in manifest['candidates']:
            existing_folder = candidate_folder(batch, existing)
            if (existing_folder/'preview-views.json').exists():
                comparison_cameras = checked_views(existing_folder, checked_preview(existing_folder), comparison_cameras)
        for c in manifest['candidates']:
            if args.candidate and c['id'] != args.candidate:
                continue
            folder = candidate_folder(batch, c)
            if (folder/'preview.json').exists():
                comparison_cameras = checked_views(folder, checked_preview(folder), comparison_cameras)
                continue
            started = time.monotonic()
            c['state'] = 'rendering'
            write(batch/'batch.json', manifest)
            with open(folder/'render.log', 'w', encoding='utf-8') as log:
                result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '_worker',
                    args.batch, '--candidate', c['id'], '--camera', args.camera], stdout=log, stderr=subprocess.STDOUT)
            if result.returncode:
                c['state'] = 'failed'
                write(batch/'batch.json', manifest)
                raise RuntimeError(f'{c["id"]} failed; see {folder / "render.log"}')
            comparison_cameras = checked_views(folder, checked_preview(folder), comparison_cameras)
            c['state'] = 'preview_ready'
            c['elapsed_seconds'] = round(time.monotonic()-started, 2)
            write(batch/'batch.json', manifest)
            gallery(batch, manifest)
            print(f'{c["id"]}: source + 1x preview ready ({c["elapsed_seconds"]} s)', flush=True)
    finally:
        lock.unlink()
        (batch/'render.lock').unlink(missing_ok=True)
    print(batch/'index.html')


def select(args):
    batch = batch_path(args.batch)
    if (batch/'render.lock').exists():
        raise ValueError('Wait for this batch render to finish before selection')
    manifest = read(batch/'batch.json')
    c = next((c for c in manifest['candidates'] if c['id'] == args.candidate), None)
    if c is None:
        raise ValueError('Unknown candidate')
    folder = candidate_folder(batch, c)
    cameras = checked_views(folder, checked_preview(folder))
    for other in manifest['candidates']:
        other_folder = candidate_folder(batch, other)
        if (other_folder/'preview.json').exists():
            checked_views(other_folder, checked_preview(other_folder), cameras)
    manifest['selected'] = dict(id=c['id'], reason=args.reason, reviewer=args.reviewer,
                                 observation=args.observation, human_acceptance=False, time=time.time())
    write(batch/'batch.json', manifest)
    gallery(batch, manifest)
    print(f'Selected {c["id"]} for refinement only. Runtime untouched. Source: {folder}')


def refine(args):
    batch = batch_path(args.batch)
    if (batch/'render.lock').exists():
        raise ValueError('Wait for this batch render to finish before refinement')
    manifest = read(batch/'batch.json')
    if not manifest['selected']:
        raise ValueError('Select a previewed winner first')
    name = slug(args.candidate)
    if any(c['id'] == name for c in manifest['candidates']):
        raise ValueError('Candidate exists; choose a new refinement name')
    selected = next(c for c in manifest['candidates'] if c['id'] == manifest['selected']['id'])
    selected_folder = candidate_folder(batch, selected)
    checked_preview(selected_folder)
    folder = batch/'source/Candidates'/name/'TP_v001'
    folder.mkdir(parents=True)
    score = read(selected_folder/'pose-controls.json')
    score['revision'] = name
    score['hypothesis'] = args.reason
    write(folder/'pose-controls.json', score)
    if manifest.get('adapter') == 'cf-controls-v1':
        shutil.copy2(selected_folder/'TP_v001_RightHorizontal.blend', folder/'native-input.blend')
    manifest['candidates'].append(dict(id=name, parent=selected['id'], hypothesis=args.reason,
                                      folder=folder.relative_to(batch).as_posix(), state='draft'))
    write(batch/'batch.json', manifest)
    gallery(batch, manifest)
    editable = folder/('native-input.blend' if manifest.get('adapter') == 'cf-controls-v1' else 'pose-controls.json')
    print(f'Edit {editable}, then render --candidate {name}')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    new = sub.add_parser('new')
    new.add_argument('batch')
    new.add_argument('--seed')
    new.add_argument('--adapter', choices=['legacy','cf-controls-v1'], default=None)
    new.add_argument('--count', type=int, choices=[3, 4], default=4)
    for name in ['render', '_worker']:
        s = sub.add_parser(name)
        s.add_argument('batch')
        s.add_argument('--candidate')
        s.add_argument('--camera', choices=['FrontThreeQuarter', 'Defender', 'RearThreeQuarter', 'MEL36_Defender_Perspective_v1'], default=None)
    s = sub.add_parser('select')
    s.add_argument('batch')
    s.add_argument('candidate')
    s.add_argument('--reason', required=True)
    s.add_argument('--reviewer', default='agent')
    s.add_argument('--observation', choices=['frames', 'continuous', 'user_feedback'], default='frames')
    r = sub.add_parser('refine')
    r.add_argument('batch')
    r.add_argument('candidate')
    r.add_argument('--reason', required=True)
    args = p.parse_args()
    try:
        {'new': make_batch, 'render': render_batch, '_worker': worker, 'select': select, 'refine': refine}[args.command](args)
    except (ValueError, RuntimeError, OSError, StopIteration) as error:
        p.exit(1, f'AnimationLab: {error}\n')


if __name__ == '__main__':
    main()
