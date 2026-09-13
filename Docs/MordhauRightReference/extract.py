from pathlib import Path
import sys,subprocess,json
sys.path.insert(0,'Saved/VideoRuntime')
import imageio_ffmpeg
from PIL import Image,ImageDraw
out=Path('Docs/MordhauRightReference'); ff=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff,'-hide_banner','-loglevel','error','-ss','47.8','-i','D:/Kronktage v14.mp4','-t','1.4','-map','0:v:0','-an','-c:v','libx264','-crf','16',str(out/'provisional-k14-47.8-49.2.mp4')],check=True)
subprocess.run([ff,'-hide_banner','-loglevel','error','-ss','48.3','-i','D:/Kronktage v14.mp4','-frames:v','18','-vsync','0','-q:v','2',str(out/'native-%02d.jpg')],check=True)
sheet=Image.new('RGB',(1280,1152),'#151515');d=ImageDraw.Draw(sheet)
for j,i in enumerate([1,4,7,10,13,16]):
 x=(j%2)*640;y=(j//2)*384
 sheet.paste(Image.open(out/f'native-{i:02d}.jpg').resize((640,360)),(x,y+24))
 d.text((x+8,y+5),f'PROVISIONAL K14 {48.3+(i-1)/30:.3f}s',fill='white')
sheet.save(out/'provisional-beats.jpg',quality=92)
print('Created 1.4s excerpt and six-frame sheet; native sequence 48.300-48.867 at 30fps.')
