"""Package source-timed TP block movies and compact review sheets."""
import sys,json,subprocess,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/VideoRuntime'))
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
OUT=ROOT/'ArtSource/CharacterReset/TP_v001';PRE=OUT/'Preview'
REV='Block02';PREVIOUS='Block01';BASELINE='Baseline_Block01'
FONT=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
SMALL=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
KEYS=[19,52,63,73,81,94,108,139]
NAMES=['Ready / attack start','Low-right load','Release starts / rising','Central delivery','Release ends','Down-left carry','Upward inward return','Ready restored']
def labeled(path,label,size=None):
    im=Image.open(path).convert('RGB')
    if size:im.thumbnail(size)
    out=Image.new('RGB',(im.width,im.height+34),(22,27,33));out.paste(im,(0,34));ImageDraw.Draw(out).text((10,7),label,font=SMALL,fill='white');return out
def sheet():
    for cam in ['FrontThreeQuarter','RearThreeQuarter']:
        grid=Image.new('RGB',(1440,680),(22,27,33))
        for i,(f,n) in enumerate(zip(KEYS,NAMES)):
            im=labeled(PRE/('Keys_'+cam)/f'{f:04d}.png',f'{n} | source {(f-1)/60:.3f}s',(360,288));grid.paste(im,((i%4)*360,(i//4)*340))
        ImageDraw.Draw(grid).text((12,654),f'TP_v001 {REV} | Initial interpretation; lower-body support authored | Artistic acceptance pending',font=FONT,fill='white')
        grid.save(PRE/f'{REV}_{cam}_keys.jpg',quality=94)
    # Matched source camera comparison; original block untouched.
    grid=Image.new('RGB',(1260,568),(22,27,33))
    for row,folder in enumerate([OUT/BASELINE/'Preview/Keys_FrontThreeQuarter',PRE/'Keys_FrontThreeQuarter']):
        for col,f in enumerate([63,73,81]):
            im=labeled(folder/f'{f:04d}.png',f'{PREVIOUS if row==0 else REV} | frame {f} / {(f-1)/60:.3f}s',(420,252));grid.paste(im,(col*420,row*284))
    grid.save(PRE/f'{PREVIOUS}_vs_{REV}_delivery.jpg',quality=94)
    if REV!='Block02':
        grid=Image.new('RGB',(960,836),(22,27,33))
        for row,folder in enumerate([OUT/BASELINE/'Preview/Keys_RearThreeQuarter',PRE/'Keys_RearThreeQuarter']):
            for col,f in enumerate([52,94]):
                im=labeled(folder/f'{f:04d}.png',f'{PREVIOUS if row==0 else REV} | frame {f} / {(f-1)/60:.3f}s',(480,384));grid.paste(im,(col*480,row*418))
        grid.save(PRE/f'{PREVIOUS}_vs_{REV}_endpoints.jpg',quality=94)
    if (PRE/'CanonicalOverlay/0063.png').exists():
        grid=Image.new('RGB',(1440,434),(22,27,33))
        for col,f in enumerate([63,73,81]):
            im=labeled(PRE/'CanonicalOverlay'/f'{f:04d}.png',f'Cyan = preserved canonical | source {(f-1)/60:.3f}s',(480,384));grid.paste(im,(col*480,0))
        ImageDraw.Draw(grid).text((10,414),'Same neutral source space; visible blade divergence remains a gameplay acceptance blocker.',font=SMALL,fill='white')
        grid.save(PRE/'Canonical_release_overlay.jpg',quality=94)
def movie(stepped=False):
    dest=PRE/f'TP_v001_{REV}_{"stepped" if stepped else "continuous"}.mp4'
    cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','900x768','-r','60','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    for f in range(19,155):
        sample=max(k for k in KEYS if k<=f) if stepped else f
        folder=PRE/'Keys_FrontThreeQuarter' if stepped else PRE/'FrontThreeQuarter'
        im=Image.open(folder/f'{sample:04d}.png').convert('RGB');canvas=Image.new('RGB',(900,768),(22,27,33));canvas.paste(im,(0,48));draw=ImageDraw.Draw(canvas)
        draw.text((12,3),f'TP_v001 {REV} | {"STEPPED" if stepped else "CONTINUOUS 1x"} | shared source {(f-1)/60:.3f}s',font=FONT,fill='white')
        draw.text((12,27),'Greatsword interpretation / support authored / artistic and canonical-contact acceptance pending',font=SMALL,fill=(205,213,225));proc.stdin.write(canvas.tobytes())
    proc.stdin.close();log=proc.stderr.read().decode(errors='replace');status=proc.wait();(PRE/(dest.stem+'.encode.log')).write_text(log)
    if status:raise SystemExit(status)
    return str(dest)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--keys-only',action='store_true');p.add_argument('--revision',default='Block02');p.add_argument('--previous',default='Block01');p.add_argument('--baseline',default='Baseline_Block01');args=p.parse_args();REV=args.revision;PREVIOUS=args.previous;BASELINE=args.baseline;sheet()
    if not args.keys_only:print(movie());print(movie(True))
