"""Reproducible source-PTS samples for action/actor classification; no asset promotion."""
from pathlib import Path
import sys, subprocess, re, json, hashlib
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Saved/VideoRuntime'))
import imageio_ffmpeg
from PIL import Image, ImageDraw
SOURCE = ROOT/'Saved/ReferenceVideos/Mordhau_KMA2nf278No/source.mp4'
OUT = Path(__file__).parent
WINDOWS = [('LH-A',28,36),('LH-D',56,64),('XR-A',82,90),('XR-B',112,120),('RH-A',142,150),('RH-D',170,178),('RO-A',198,206),('RO-D',226,234),('LO-A',254,262),('XL-A',282,290),('XL-D',312,320),('RU-A',340,348),('RU-D',368,376),('LU-A',398,406),('LU-D',432,440)]
def extract(name,start,end,step=.5):
    dest=OUT/'review'/name; dest.mkdir(parents=True,exist_ok=True)
    # Seek with original timestamps retained, then select by decoded PTS.
    vf=f"select='between(t,{start},{end-0.0001})*if(isnan(prev_selected_t),1,gte(t-prev_selected_t,{step-0.00001}))',showinfo,scale=960:-1"
    p=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-copyts','-ss',str(start),'-t',str(end-start),'-i',str(SOURCE),'-vf',vf,'-an','-fps_mode','passthrough','-q:v','3','-y',str(dest/'%03d.jpg')],capture_output=True,text=True)
    p.check_returncode()
    pts=[float(v) for v in re.findall(r'pts_time:([0-9.]+)',p.stderr)]
    frames=sorted(dest.glob('[0-9][0-9][0-9].jpg'))
    assert len(pts)==len(frames) and pts, (name,len(pts),len(frames))
    records=[{'file':str(f.relative_to(OUT)).replace('\\','/'),'source_pts_s':t} for f,t in zip(frames,pts)]
    (dest/'frames.json').write_text(json.dumps(records,indent=2))
    for page in range(0,len(frames),16):
        subset=records[page:page+16]
        sheet=Image.new('RGB',(1600,((len(subset)+3)//4)*255),'#181c23');d=ImageDraw.Draw(sheet)
        for j,r in enumerate(subset):
            x=j%4*400;y=j//4*255
            sheet.paste(Image.open(OUT/r['file']).resize((400,225)),(x,y+30))
            d.text((x+5,y+8),f"{name} | {r['source_pts_s']:.3f}s",fill='white')
        sheet.save(dest/f'sheet-{page//16+1:02}.jpg',quality=91)
    print(name,len(records),pts[0],pts[-1],flush=True)
    return records
if __name__=='__main__':
    if len(sys.argv)>1:
        extract(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]) if len(sys.argv)>4 else .5)
    else:
        records={name:extract(name,s,e) for name,s,e in WINDOWS}
        (OUT/'source-receipt.json').write_text(json.dumps({'source':str(SOURCE),'bytes':SOURCE.stat().st_size,'sha256':hashlib.file_digest(SOURCE.open('rb'),'sha256').hexdigest(),'method':'Decoded PTS; 0.5 s overview samples; frame-sequence visual inspection, not continuous playback','windows':WINDOWS,'samples':sum(map(len,records.values()))},indent=2))
