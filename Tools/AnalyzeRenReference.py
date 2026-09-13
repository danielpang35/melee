"""Extract timestamped native-frame evidence for the Ren reference report."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Saved/VideoRuntime'))
import imageio_ffmpeg
from PIL import Image, ImageDraw

source = Path('D:/Mordhau Montage VI.mp4')
out = ROOT / 'Docs/Visual/Captures/RenReference'
out.mkdir(parents=True, exist_ok=True)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
sequences = [('R01', 2.4), ('R02', 164.1), ('R03', 260.3)]
for name, start in sequences:
    folder = out / name
    folder.mkdir(exist_ok=True)
    subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-ss', str(start),
        '-i', str(source), '-frames:v', '36', '-vsync', '0', '-q:v', '2',
        '-y', str(folder / '%03d.jpg')], check=True)
    frames = sorted(folder.glob('*.jpg'))
    for page in range(3):
        sheet = Image.new('RGB', (1920, 1552), '#14191e')
        draw = ImageDraw.Draw(sheet)
        for j, frame in enumerate(frames[page*12:(page+1)*12]):
            x, y = (j%3)*640, (j//3)*388
            stamp = start+(page*12+j)/30
            sheet.paste(Image.open(frame).resize((640, 360)), (x,y+28))
            draw.text((x+8,y+7), f'{name}  {int(stamp//60)}:{stamp%60:06.3f}  source frame {round(stamp*30)}', fill='white')
        sheet.save(out/f'{name}-{page+1}.jpg', quality=90)
manifest = {'source': str(source), 'bytes': source.stat().st_size,
    'sha256': hashlib.file_digest(source.open('rb'), 'sha256').hexdigest(),
    'method': '36 consecutive decoded source frames per sequence; 30 fps timestamp grid; no interpolation; sheets resize only',
    'sequences': sequences}
(out/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps(manifest))
