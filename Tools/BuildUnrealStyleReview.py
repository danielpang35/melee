"""Package actual Unreal proof evidence without regenerating or retouching imagery."""
from pathlib import Path
import argparse
import hashlib
import html
import json
import shutil
from UnrealStyleCaptureValidation import validate_png,validate_capture_receipt

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', default='USP_v001')
    parser.add_argument('--captures', required=True, help='Directory containing actual engine evidence')
    parser.add_argument('--output', required=True, help='New portable review directory')
    parser.add_argument('--summary', default='Technical proof in review; no artistic or user acceptance claimed.')
    parser.add_argument('--critic', default=str(ROOT/'Docs/UNREAL_STYLE_CRITIC.md'), help='Critique applicable to this revision')
    parser.add_argument('--source', action='append', default=[], help='Explicit workspace source directory or file to preserve in the portable packet; repeat as needed')
    parser.add_argument('--native-image', action='append', default=[], help='Relative captured PNG to display additionally at exact source-pixel size; repeat as needed')
    parser.add_argument('--native-crop', default='670,315,190,260', help='Pixel viewport x,y,width,height for native images; verify against actual capture')
    args = parser.parse_args()
    if not args.revision.startswith('USP_v') or not args.revision[5:].isdigit():
        parser.error('Expected USP_v followed by revision digits')
    captures = Path(args.captures).resolve()
    output = Path(args.output).resolve()
    if output.exists():
        parser.error('Choose a new output directory to preserve prior evidence')
    files = sorted(p for p in captures.rglob('*') if p.is_file() and p.suffix.lower() in ('.png', '.jpg', '.mp4', '.webm', '.json'))
    if not any(p.suffix.lower() in ('.png', '.jpg') for p in files):
        parser.error('Actual engine image evidence is required')
    capture_receipt=captures/'capture_receipt.json'
    if not capture_receipt.exists():
        parser.error('A completed, validated capture receipt is required')
    validate_capture_receipt(captures,json.loads(capture_receipt.read_text()),args.revision)
    if output == captures or captures in output.parents:
        parser.error('Output must be outside the captured evidence directory')
    try:
        native_crop = [int(v) for v in args.native_crop.split(',')]
        if len(native_crop) != 4 or min(native_crop[:2]) < 0 or min(native_crop[2:]) <= 0:
            raise ValueError()
    except ValueError:
        parser.error('Native crop must contain nonnegative x,y and positive width,height')
    native_panels = []
    for name in args.native_image:
        source = (captures / name).resolve()
        if not source.is_relative_to(captures) or source not in files or source.suffix.lower() != '.png':
            parser.error('Native image must be a captured PNG inside the evidence directory')
        dimensions=validate_png(source)
        width, height = dimensions['width'],dimensions['height']
        x, y, crop_width, crop_height = native_crop
        if x + crop_width > width or y + crop_height > height:
            parser.error('Native crop exceeds actual screenshot dimensions')
        url = html.escape('evidence/' + source.relative_to(captures).as_posix(), quote=True)
        native_panels.append(f'<figure style="width:{crop_width}px;flex-shrink:0"><svg width="{crop_width}" height="{crop_height}" viewBox="{x} {y} {crop_width} {crop_height}" role="img" aria-label="Unretouched Unreal detail at native pixels"><image href="{url}" width="{width}" height="{height}"/></svg><figcaption>{html.escape(name)}</figcaption></figure>')
    source_files = []
    for value in args.source:
        source = Path(value).resolve()
        if not source.exists() or not source.is_relative_to(ROOT):
            parser.error('Source must exist inside this workspace')
        if source == output or source in output.parents:
            parser.error('Source must not contain the output directory')
        source_files.extend(sorted(p for p in source.rglob('*') if p.is_file()) if source.is_dir() else [source])
    output.mkdir(parents=True)
    original = ROOT / 'ArtSource/StyleReference/MEL17/06-riot-inspired.png'
    shutil.copy2(original, output / 'reference.png')
    records = []
    panels = []
    receipts = []
    for source in files:
        relative = source.relative_to(captures)
        target = output / 'evidence' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        url = 'evidence/' + relative.as_posix()
        label = relative.as_posix()
        records.append({'path': url, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'bytes': target.stat().st_size})
        escaped_url, escaped_label = html.escape(url, quote=True), html.escape(label)
        if source.suffix.lower() in ('.png', '.jpg') and 'motion' not in relative.parts:
            panels.append(f'<figure><a href="{escaped_url}"><img loading="lazy" src="{escaped_url}" alt="Actual Unreal capture: {escaped_label}"></a><figcaption>{escaped_label}</figcaption></figure>')
        elif source.suffix.lower() in ('.mp4', '.webm'):
            panels.append(f'<figure><video controls loop muted preload="metadata" src="{escaped_url}"></video><figcaption>{escaped_label}</figcaption></figure>')
        elif source.suffix.lower() == '.json':
            receipts.append(f'<li><a href="{escaped_url}">{escaped_label}</a></li>')
    critic = Path(args.critic).resolve()
    if critic.exists():
        shutil.copy2(critic, output / 'CRITIC.md')
    source_records = []
    for source in sorted(set(source_files)):
        relative = source.relative_to(ROOT)
        target = output / 'source' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        source_records.append({'path': 'source/' + relative.as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'bytes': target.stat().st_size})
    manifest = {'revision': args.revision, 'summary': args.summary, 'reference_sha256': hashlib.sha256(original.read_bytes()).hexdigest(), 'reference_crop_xywh': [417, 170, 155, 220], 'native_engine_crop_xywh': native_crop if args.native_image else None, 'native_images': args.native_image, 'images_unretouched': True, 'evidence': records, 'editable_source': source_records}
    (output / 'packet.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Unreal helmet style proof</title><style>
*{box-sizing:border-box}body{margin:0;background:#141b22;color:#e6e9e7;font:16px/1.5 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:28px}h1{margin:.2em 0;font-size:32px}p{max-width:1000px;color:#bbc6ce}a{color:#aad9e9}.status{padding:16px;border-left:3px solid #cbb58a;background:#202d36}.reference{display:flex;gap:22px;align-items:center;margin:24px 0}.reference svg{width:155px;height:220px;flex-shrink:0}.gallery{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}figure{margin:0;background:#20282e;border:1px solid #35414a}figure img,video{width:100%;height:auto;display:block}figcaption{padding:10px;font-size:13px;overflow-wrap:anywhere}details{margin:24px 0}pre{white-space:pre-wrap} @media(max-width:800px){.gallery{grid-template-columns:1fr}.reference{align-items:flex-start}main{padding:16px}}
</style><main><small>MELEE COMBAT LAB · REVISION</small><h1>Unreal helmet style proof</h1><p class="status">SUMMARY</p>
<section class="reference"><svg viewBox="417 170 155 220" role="img" aria-label="Unchanged original reference, helmet crop"><image href="reference.png" width="1024" height="1536"/></svg><div><b>Original reference detail</b><p>Displayed at the source crop's native pixel size. Larger diagnostic views provide no additional reference detail. Click engine captures for their original resolution.</p><a href="reference.png">Full unchanged portrait</a> · <a href="CRITIC.md">Independent 3D art critique</a> · <a href="packet.json">Evidence hashes</a></div></section>
<div class="gallery">PANELS</div><details><summary>Engine settings and evidence receipts</summary><ul>RECEIPTS</ul></details><p>Shape, steel character, reflections and motion are separate review gates. A still cannot establish temporal stability or gameplay acceptance. Rear helmet construction is inferred.</p></main></html>'''
    receipts.extend(f'<li><a href="{html.escape(r["path"], quote=True)}">{html.escape(r["path"])}</a></li>' for r in source_records)
    if native_panels:
        native_reference = '<figure style="width:155px;flex-shrink:0"><svg width="155" height="220" viewBox="417 170 155 220" role="img" aria-label="Original reference at native pixels"><image href="reference.png" width="1024" height="1536"/></svg><figcaption>Original reference</figcaption></figure>'
        page = page.replace('<div class="gallery">', '<p>Reference and engine details below retain one display pixel per captured pixel. Full screenshots remain unchanged.</p><div style="display:flex;gap:18px;flex-wrap:wrap;align-items:flex-start">' + native_reference + ''.join(native_panels) + '</div><br><div class="gallery">')
    page = page.replace('REVISION', html.escape(args.revision)).replace('SUMMARY', html.escape(args.summary)).replace('PANELS', '\n'.join(panels)).replace('RECEIPTS', '\n'.join(receipts))
    (output / 'review.html').write_text(page, encoding='utf-8')
    print(json.dumps({'review': str(output / 'review.html'), 'evidence_files': len(records), 'reference_sha256': manifest['reference_sha256']}))


if __name__ == '__main__':
    main()
