"""Build a small visual receipt from already-selected reference evidence."""
from pathlib import Path
import hashlib, json, re, subprocess, sys
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT/'Saved/VideoRuntime'))
import imageio_ffmpeg
from PIL import Image, ImageDraw

ff = imageio_ffmpeg.get_ffmpeg_exe()
selections = {
    'A': {'folder':'neutral-native', 'start':5.3839, 'end':7.306,
          'keys':[(6,'Ready'),(26,'Right-side load'),(35,'Delivery'),(47,'Left-side carry'),(60,'Return'),(67,'Ready restored')]},
    'B': {'folder':'first_swing', 'start':0.456067, 'end':2.22,
          'keys':[(2,'Ready'),(8,'Right-shoulder load'),(12,'Delivery'),(16,'Left-side carry'),(18,'Return'),(20,'Ready restored')]},
}
receipts=[]
for clip, selection in selections.items():
    folder=BASE/clip/selection['folder']
    frame_receipt=json.loads((folder/'receipt.json').read_text())
    records=json.loads((folder/'frames.json').read_text())
    crop=tuple(map(int,frame_receipt['selection']['crop'].split(',')))
    x0,y0,cw,ch=crop
    tw=640
    th=round(tw*ch/cw)
    cellh=th+36
    sheet=Image.new('RGB',(3*tw,2*cellh),'#171a20')
    d=ImageDraw.Draw(sheet)
    selected=[]
    for j,(index,label) in enumerate(selection['keys']):
        rec=records[index-1]
        img=Image.open(folder/rec['file']).crop((x0,y0,x0+cw,y0+ch))
        x=j%3*tw
        y=j//3*cellh
        sheet.paste(img.resize((tw,th)),(x,y+36))
        d.text((x+10,y+11),f"{clip} | {label} | source {rec['source_pts_s']:.6f} s",fill='white')
        selected.append({'beat':label,**rec})
    sheet.save(BASE/clip/'selected-beats.jpg',quality=94)
    output=BASE/clip/'selected-source-speed.mp4'
    src=frame_receipt['source']
    trim=f"trim=start={selection['start']}:end={selection['end']}"
    proc=subprocess.run([ff,'-hide_banner','-i',src,'-map','0:v:0','-vf',trim+',showinfo,setpts=PTS-STARTPTS',
        '-an','-fps_mode','passthrough','-enc_time_base','1:30000','-c:v','libx264','-crf','17','-preset','fast','-movflags','+faststart','-y',str(output)],capture_output=True,text=True)
    proc.check_returncode()
    (BASE/clip/'excerpt-source.log').write_text(proc.stderr,encoding='utf8')
    source_pts=[float(t) for t in re.findall(r'pts_time:([0-9.]+)',proc.stderr)]
    check=subprocess.run([ff,'-hide_banner','-i',str(output),'-vf','showinfo','-an','-fps_mode','passthrough','-f','null','-'],capture_output=True,text=True)
    check.check_returncode()
    (BASE/clip/'excerpt-verify.log').write_text(check.stderr,encoding='utf8')
    result_pts=[float(t) for t in re.findall(r'pts_time:([0-9.]+)',check.stderr)]
    assert len(source_pts)==len(result_pts), 'Excerpt frame count changed'
    error=max(abs((s-source_pts[0])-r) for s,r in zip(source_pts,result_pts))
    assert error<0.00004, 'Source timing changed beyond one timebase tick'
    receipt={'clip':clip,'source':src,'source_sha256':frame_receipt['sha256'],
        'excerpt':str(output),'excerpt_sha256':hashlib.file_digest(output.open('rb'),'sha256').hexdigest(),
        'trim_start_inclusive_s':selection['start'],'trim_end_exclusive_s':selection['end'],
        'actual_source_first_pts_s':source_pts[0],'actual_source_last_pts_s':source_pts[-1],
        'frames':len(source_pts),'max_relative_pts_error_s':error,'audio':'omitted',
        'continuous_playback_review':'not performed by model; decoded frame inspection only',
        'keys':selected}
    receipts.append(receipt)
(BASE/'review-receipt.json').write_text(json.dumps(receipts,indent=2))
print(json.dumps([{k:r[k] for k in ['clip','frames','actual_source_first_pts_s','actual_source_last_pts_s','max_relative_pts_error_s']} for r in receipts]))
