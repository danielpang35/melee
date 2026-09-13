"""Extract timestamped source frames; no animation/assets are modified."""
from pathlib import Path
import argparse, hashlib, json, re, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Saved/VideoRuntime'))
import imageio_ffmpeg
from PIL import Image, ImageDraw

SOURCES = {
    'A': Path('C:/Users/Daniel Pang/Videos/Captures/MORDHAU   2026-09-08 01-36-39.mp4'),
    'B': Path('C:/Users/Daniel Pang/Videos/Captures/MORDHAU   2026-09-08 01-46-20.mp4'),
}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('clip', choices=SOURCES)
    p.add_argument('--start', type=float, default=0)
    p.add_argument('--end', type=float, default=10000)
    p.add_argument('--step', type=float, default=1)
    p.add_argument('--name', default='overview')
    p.add_argument('--crop', help='x,y,width,height in source pixels')
    p.add_argument('--columns', type=int, default=4)
    p.add_argument('--tile-width', type=int, default=480)
    args = p.parse_args()
    source = SOURCES[args.clip]
    out = Path(__file__).parent / args.clip / args.name
    out.mkdir(parents=True, exist_ok=True)
    selector = f"select='between(t,{args.start},{args.end})*if(isnan(prev_selected_t),1,gte(t-prev_selected_t,{args.step}))',showinfo"
    proc = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-i', str(source),
        '-map', '0:v:0', '-vf', selector, '-an', '-fps_mode', 'passthrough', '-q:v', '2', '-y',
        str(out / 'frame-%04d.jpg')], capture_output=True, text=True)
    (out / 'decode.log').write_text(proc.stderr, encoding='utf8')
    proc.check_returncode()
    pts = [float(t) for t in re.findall(r'pts_time:([0-9.]+)', proc.stderr)]
    records = [{'index': i + 1, 'source_pts_s': t, 'file': f'frame-{i+1:04d}.jpg'} for i,t in enumerate(pts)]
    (out / 'frames.json').write_text(json.dumps(records, indent=2))
    crop = tuple(map(int,args.crop.split(','))) if args.crop else None
    if not records:
        raise RuntimeError('No frames selected')
    sample = Image.open(out / records[0]['file'])
    w,h = (crop[2:4] if crop else sample.size)
    tw = args.tile_width
    th = round(tw*h/w)
    cellh = th+27
    pages = []
    per_page = args.columns*4
    for offset in range(0,len(records),per_page):
        batch = records[offset:offset+per_page]
        sheet = Image.new('RGB',(args.columns*tw,cellh*((len(batch)+args.columns-1)//args.columns)),'#171a20')
        draw = ImageDraw.Draw(sheet)
        for j,rec in enumerate(batch):
            frame = Image.open(out / rec['file'])
            if crop:
                x,y,cw,ch=crop
                frame=frame.crop((x,y,x+cw,y+ch))
            x=j%args.columns*tw
            y=j//args.columns*cellh
            sheet.paste(frame.resize((tw,th)),(x,y+27))
            draw.text((x+8,y+6),f"{args.clip} #{rec['index']}  source {rec['source_pts_s']:.6f} s",fill='white')
        page=out/f'sheet-{offset//per_page+1:02d}.jpg'
        sheet.save(page,quality=92)
        pages.append(str(page))
    receipt = {'source':str(source), 'source_bytes':source.stat().st_size,
        'sha256':hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),
        'source_frame_size':sample.size, 'selection':vars(args), 'frames':len(records),
        'first_pts_s':pts[0], 'last_pts_s':pts[-1], 'sheets':pages,
        'method':'Decode source frames with FFmpeg select; labels are decoded source PTS, not index/fps. Aspect ratio preserved; optional fixed crop.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt))
    print('\n'.join(line for line in proc.stderr.splitlines() if 'Duration:' in line or 'Stream #0:0' in line))

if __name__ == '__main__':
    main()
