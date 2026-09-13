"""Reproducible source-frame sheets; timestamps are montage time, not game time."""
from pathlib import Path
import hashlib, json, subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'Saved/VideoRuntime'))
import imageio_ffmpeg
from PIL import Image, ImageDraw
OUT = ROOT/'Docs/Visual/Captures/KronkReference'
OUT.mkdir(parents=True, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()

def extract(version, name, start=0, seconds=None, step=240):
    source = Path(f'D:/Kronktage v{version}.mp4')
    folder = OUT/name
    folder.mkdir(exist_ok=True)
    args=[FF,'-hide_banner','-loglevel','error','-ss',str(start),'-i',str(source)]
    if seconds is not None: args += ['-t',str(seconds)]
    args += ['-vf',f'select=not(mod(n\\,{step})),scale=640:-1','-vsync','0','-q:v','2','-y',str(folder/'%03d.jpg')]
    subprocess.run(args,check=True)
    frames=sorted(folder.glob('*.jpg'))
    for page in range((len(frames)+11)//12):
        sheet=Image.new('RGB',(1920,1552),'#14191e')
        draw=ImageDraw.Draw(sheet)
        for j,frame in enumerate(frames[page*12:(page+1)*12]):
            x,y=(j%3)*640,(j//3)*388
            stamp=start+(page*12+j)*step/30
            sheet.paste(Image.open(frame),(x,y+28))
            draw.text((x+8,y+7),f'v{version} / {name}  {int(stamp//60)}:{stamp%60:06.3f}',fill='white')
        sheet.save(OUT/f'{name}-{page+1}.jpg',quality=89)
    print(name,len(frames))

if __name__=='__main__':
    if len(sys.argv)>1:
        extract(int(sys.argv[1]),sys.argv[2],float(sys.argv[3]),float(sys.argv[4]),int(sys.argv[5]))
    else:
        manifest=[]
        for version in [18,14]:
            source=Path(f'D:/Kronktage v{version}.mp4')
            probe=subprocess.run([FF,'-hide_banner','-i',str(source)],capture_output=True,text=True).stderr
            manifest.append({'source':str(source),'bytes':source.stat().st_size,'sha256':hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),'probe':probe})
            extract(version,f'v{version}-overview')
        (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
