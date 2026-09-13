"""Encode validated continuous PIE evidence and fully decode each delivery video."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/VideoRuntime'))
from UnrealStyleCaptureValidation import validate_motion
import imageio_ffmpeg


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--captures',type=Path,required=True)
    args=parser.parse_args()
    folder=args.captures.resolve()
    receipt=json.loads((folder/'capture_receipt.json').read_text())
    assert receipt.get('completed'),'Incomplete capture run'
    verified_motion=validate_motion(receipt['captures'],receipt['motion_requirements'])
    # Reuse complete-image validation from capture, bound by hashes. FFmpeg
    # decodes motion PNGs during encoding; delivery packaging revalidates images.
    for capture in receipt['captures']:
        path=Path(capture['file']).resolve()
        assert path.is_relative_to(folder) and capture.get('complete_image_validated')
        assert hashlib.sha256(path.read_bytes()).hexdigest()==capture['sha256'],'Capture changed'
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    records=[]
    for motion in verified_motion:
        name=motion['name'];assert re.fullmatch(r'[a-z_]+',name)
        output=folder/(name+'.mp4');assert not output.exists(),'Preserve existing video'
        source=folder/'motion'/name/(name+'_%03d.png')
        subprocess.run([ffmpeg,'-v','error','-framerate',str(motion['fps']),'-i',str(source),
                        '-frames:v',str(motion['frame_count']),'-vf','pad=ceil(iw/2)*2:ceil(ih/2)*2:0:0:black',
                        '-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],check=True)
        decoded=subprocess.run([ffmpeg,'-v','error','-i',str(output),'-progress','pipe:1','-f','null','-'],capture_output=True,text=True,check=True)
        counts=re.findall(r'^frame=(\d+)$',decoded.stdout,re.M)
        assert counts and int(counts[-1])==motion['frame_count'],'Decoded video frame count mismatch'
        records.append({'file':output.name,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
                        'decoded_frames':int(counts[-1]),'fps':motion['fps'],
                        'source_frames':[str(Path(f).relative_to(folder)) for f in motion['files']],
                        'processing':'H.264 delivery encode, no rescaling; black padding at right/bottom only if dimensions are odd.',
                        'review':'Full decoder verification; human/model playback assessment remains separate.'})
    target=folder/'motion_video_receipt.json';assert not target.exists()
    target.write_text(json.dumps({'capture_receipt_sha256':hashlib.sha256((folder/'capture_receipt.json').read_bytes()).hexdigest(),'videos':records},indent=2))
    print(json.dumps({'videos':len(records),'receipt':str(target)}))


if __name__=='__main__':main()
