"""Combine the verified, unretimed production replays after checking synchronization."""
import csv, hashlib, json, subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
saved = root / 'Saved/MEL15'
views = ('firstperson', 'external', 'defender')
tags = ['EX_gameplay_' + view for view in views]
receipts = [json.loads((saved / tag / 'verification.json').read_text()) for tag in tags]
launches = [json.loads((saved / (tag + '-launch.json')).read_text(encoding='utf-8-sig')) for tag in tags]
rows = []
for tag in tags:
    with (saved / tag / 'frames.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows.append(list(csv.DictReader(stream)))
assert all(r['events'] == receipts[0]['events'] for r in receipts)
assert all(l['module_sha256'] == launches[0]['module_sha256'] and l['selection'] == launches[0]['selection'] for l in launches)
keys = ('frame', 'time', 'serial', 'phase', 'elapsed', 'source', 'ex_active', 'hits', 'player_hits', 'x', 'y', 'yaw', 'pitch')
assert all([[r[k] for k in keys] for r in view] == [[r[k] for k in keys] for r in rows[0]] for view in rows)
ffmpeg = next((root / 'Saved/VideoRuntime').rglob('ffmpeg*.exe'))
video = saved / 'EX_gameplay_review.mp4'
args = [str(ffmpeg), '-hide_banner', '-loglevel', 'error', '-y']
for tag in tags:
    args += ['-i', str(saved / (tag + '.mp4'))]
args += ['-filter_complex', '[0:v][1:v][2:v]hstack=inputs=3[v]', '-map', '[v]', '-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', str(video)]
subprocess.run(args, check=True)
receipt = dict(video=str(video), video_sha256=hashlib.sha256(video.read_bytes()).hexdigest(),
               duration_seconds=14, fps=60, left_to_right=views, synchronized_events=receipts[0]['events'],
               module_sha256=launches[0]['module_sha256'], selection=launches[0]['selection'],
               all_per_frame_combat_and_controlled_player_aim_fields_identical=True,
               scope='Three deterministic views of the same production input replay; no time scaling. External/defensive performance and phase mapping await human acceptance.')
(saved / 'production/review-verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
