"""Compose an evidence board from actual matte renders; never retouch source imagery."""
from pathlib import Path
import argparse
import hashlib
import html
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Saved/VideoRuntime'))
from PIL import Image, ImageDraw, ImageFont

ART = ROOT / 'ArtSource/StyleReference/MEL17'
REFERENCE = ART / '06-riot-inspired.png'
CROP = (417, 170, 572, 390)
HELMET_HEIGHT = 184
BG = (42, 46, 50)


def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', size)


def matte_panel(path, size, helmet_height=None):
    im = Image.open(path).convert('RGBA')
    bounds = im.getchannel('A').getbbox()
    if not bounds or bounds == (0, 0, *im.size):
        raise ValueError(f'{path}: helmet alpha required for honest scale matching')
    im = im.crop(bounds)
    scale = helmet_height / im.height if helmet_height else min((size[0]-24)/im.width, (size[1]-24)/im.height)
    im = im.resize((round(im.width*scale), round(im.height*scale)), Image.Resampling.LANCZOS)
    panel = Image.new('RGB', size, BG)
    x = (size[0]-im.width)//2
    y = round(9*helmet_height/HELMET_HEIGHT) if helmet_height else (size[1]-im.height)//2
    panel.paste(im, (x,y), im)
    return panel, {'source_alpha_bbox': list(bounds), 'uniform_scale': scale, 'display_helmet_size': list(im.size), 'display_offset': [x,y]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', required=True, type=Path)
    p.add_argument('--three-quarter', default='three_quarter.png')
    p.add_argument('--front', default='front.png')
    args=p.parse_args()
    folder=args.candidate.resolve()
    out=folder/'Review'
    out.mkdir(exist_ok=True)
    ref=Image.open(REFERENCE).convert('RGB').crop(CROP)
    native, scale=matte_panel(folder/args.three_quarter, (155,220), HELMET_HEIGHT)
    matched,_=matte_panel(folder/args.three_quarter, (465,660), HELMET_HEIGHT*3)
    front,_=matte_panel(folder/args.front, (465,660), HELMET_HEIGHT*3)
    board=Image.new('RGB',(1510,1060),(23,27,31))
    d=ImageDraw.Draw(board)
    d.text((30,18),'MEL-17 / HELMET FORM REVIEW',font=font(28),fill='#e8edf0')
    d.text((30,61),'Actual modeled geometry | Uniform matte | Reference geometry remains the target',font=font(18),fill='#aab6be')
    for x,label,panel in [(30,'Gold-standard reference / 3x',ref.resize((465,660),Image.Resampling.NEAREST)),(520,'Rebuilt / matched three-quarter',matched),(1010,'Rebuilt / front diagnostic',front)]:
        d.text((x,103),label,font=font(20),fill='#e8edf0')
        board.paste(panel,(x,138))
    d.text((30,820),'NATIVE REFERENCE SCALE',font=font(20),fill='#e8edf0')
    board.paste(ref,(30,856));board.paste(native,(203,856))
    d.text((390,863),'Original crop: 155 x 220 pixels. Helmet: approximately 184 pixels high.',font=font(18),fill='#c0cbd2')
    d.text((390,897),'Candidate is uniformly scaled by crown-to-chin height; width is not forced to fit.',font=font(18),fill='#c0cbd2')
    d.text((390,931),'Enlargement adds no reference detail. Camera match is an artistic estimate.',font=font(18),fill='#c0cbd2')
    d.text((390,965),'Front and hidden rear construction are inferred; steel and Unreal validation follow later.',font=font(18),fill='#c0cbd2')
    # Allow the full native crop without clipping.
    expanded=Image.new('RGB',(1510,1100),(23,27,31));expanded.paste(board,(0,0))
    expanded.paste(ref,(30,856));expanded.paste(native,(203,856))
    expanded.save(out/'comparison.png')
    native.save(out/'candidate-native.png')
    shutil.copy2(REFERENCE,out/'reference.png')
    notes=[
      ('Crown', 'Preserve the peaked profile and roof shoulders; shallow convex panels must not become a continuous bell-shaped dome.'),
      ('Brow and aperture', 'A separate brow wraps in depth toward the temples. The eye slit follows that volume with an actual gap, plate thickness and tucked returns.'),
      ('Cheeks and chin', 'Broad compound curvature sweeps from a crisp central ridge into the temples, then inward into a compact chin return.'),
      ('Temple construction', 'Seat the visible angular hinge cover into overlapping plates; avoid floating strips and unsupported decorative seams.'),
      ('Evidence boundary', 'Only the illustrated view is observed. Hidden rear, underside and exact hinge mechanics are inferred and judged for coherent craftsmanship.')
    ]
    notes_html=''.join(f'<li><b>{html.escape(a)}</b> — {html.escape(b)}</li>' for a,b in notes)
    template='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MEL-17 helmet geometry review</title>
<style>*{box-sizing:border-box}body{background:#171b1f;color:#e8edf0;font:16px/1.55 system-ui;margin:0}main{max-width:1540px;margin:auto;padding:28px}h1{font-size:34px;margin:.2em 0}p{max-width:1040px;color:#bbc6ce}a{color:#acd6e8}img{max-width:100%;height:auto}figure{margin:0}figcaption{font-size:13px;color:#bbc6ce}.native{display:flex;gap:24px;align-items:flex-start}.native img,.native svg{max-width:none;width:155px;height:220px}.native figure{flex:0 0 155px}video{max-width:800px;width:100%;background:#292e32}li{margin:12px 0}details{padding:16px;background:#232b32;margin:20px 0}</style>
<main><small>MEL-17 / CANDIDATE</small><h1>Helmet form, before steel</h1>
<p>Rebuilt editable geometry, rendered in uniform neutral matte shading. Assess resemblance and craftsmanship separately. This packet is a geometry study; material response, Unreal integration and human acceptance remain separate gates.</p>
<a href="comparison.png"><img src="comparison.png" alt="Gold-standard reference beside actual matte three-quarter and front renders"></a>
<h2>At the reference’s actual size</h2><div class="native"><figure><svg viewBox="417 170 155 220" aria-label="Original unaltered reference at one display pixel per source pixel"><image href="reference.png" width="1024" height="1536"/></svg><figcaption>Unchanged portrait crop</figcaption></figure><figure><img src="candidate-native.png" alt="Helmet scaled uniformly to reference crown-to-chin height"><figcaption>Matte candidate, equal helmet height</figcaption></figure></div>
<p>The helmet occupies approximately 184 pixels vertically in the original portrait. Candidate height matches that span; its width remains proportional. Browser zoom changes physical display size. Diagnostic enlargement adds no source detail.</p>
<h2>Slow turntable</h2><video controls loop muted preload="metadata" src="../turntable.mp4"></video><p>Fixed camera and lights; the helmet rotates once. The rear and underside are inferred. <a href="../turntable-contact.png">Inspect sampled angles</a>.</p>
<details open><summary>Reference construction criteria</summary><ol>NOTES</ol></details>
<p><a href="../CRITIC.md">Independent art critique</a> · <a href="packet.json">Evidence and scale receipt</a> · <a href="../settings.json">Render settings</a> · <a href="../Helmet_CANDIDATE.blend">Editable Blender source</a></p>
</main></html>'''
    (out/'review.html').write_text(template.replace('NOTES',notes_html).replace('CANDIDATE',html.escape(folder.name)),encoding='utf-8')
    records={p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/args.three_quarter,folder/args.front,out/'comparison.png',out/'reference.png']}
    receipt={'candidate':folder.name,'reference_sha256':hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),'reference_crop_xyxy':list(CROP),'reference_helmet_height_estimate_px':HELMET_HEIGHT,'scale_match':scale,'source_imagery_retouched':False,'composition':'Unchanged reference crop; neutral matte render alpha composited over gray; uniform resizing only. No generative image, surface repainting, warping or steel transfer.','construction_criteria':dict(notes),'hashes':records}
    (out/'packet.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps({'comparison':str(out/'comparison.png'),'review':str(out/'review.html'),'native_scale':scale}))


if __name__=='__main__':main()
