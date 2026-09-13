from pathlib import Path
import sys,subprocess
sys.path.insert(0,'Saved/VideoRuntime');import imageio_ffmpeg
from PIL import Image,ImageDraw
out=Path('Docs/MordhauRightReference/confirmed');out.mkdir(exist_ok=True)
ff=imageio_ffmpeg.get_ffmpeg_exe();source=r'C:/Users/Daniel Pang/Videos/Captures/MORDHAU   2026-09-07 12-27-58.mp4'
subprocess.run([ff,'-v','error','-i',source,'-vf','fps=2,scale=480:270','-y',str(out/'overview-%02d.jpg')],check=True)
frames=sorted(out.glob('overview-*.jpg'))
s=Image.new('RGB',(1920,((len(frames)+3)//4)*292));d=ImageDraw.Draw(s)
for j,f in enumerate(frames):
 x=j%4*480;y=j//4*292;s.paste(Image.open(f),(x,y+22));d.text((x,y),f'{j/2:.1f}s overview sampling',fill='white')
s.save(out/'overview.jpg')
