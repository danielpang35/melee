import json,sys,subprocess,re
from pathlib import Path
sys.path.insert(0,'Saved/VideoRuntime');import imageio_ffmpeg
p=Path('Docs/MordhauRightReference/reference.json');r=json.loads(p.read_text());r['keys'][0].update(beat='early departure from idle',hilt_guard_center_uv=[.60,.73],right_visible_grip_center_uv=[.58,.79]);r['keys'][-1].update(hilt_guard_center_uv=[.54,.73],right_visible_grip_center_uv=[.50,.81],blade_visible_end_uv=[.74,0])
f=imageio_ffmpeg.get_ffmpeg_exe();x=subprocess.run([f,'-hide_banner','-i',r['source'],'-vf','trim=start=15.470167:end=18.025767,showinfo','-an','-f','null','-'],capture_output=True,text=True)
t=[float(v) for v in re.findall(r'pts_time:([0-9.]+)',x.stderr)];r['timing'].update(excerpt_actual_first_pts_s=t[0],excerpt_actual_last_pts_s=t[-1],excerpt_frames=len(t));p.write_text(json.dumps(r,indent=2));print(t[0],t[-1],len(t))
