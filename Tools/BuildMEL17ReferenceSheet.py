"""Build a portable HTML reference board; embed original bytes without editing images."""
import base64
import hashlib
import html
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'ArtSource/StyleReference/MEL17'
SOURCES = [
    ('06-riot-inspired.png', 'Original approved knight portrait',
     'https://app.notion.com/p/3d42e3c3f8f881abb5c1c356dc68ee07',
     'Codex knight style exploration and user decisions, 7 September 2026, as attributed in Notion. Original generator record unavailable. Design reference.'),
    ('mirage.png', 'Mirage — historical B-wall before/after',
     'https://blog.counter-strike.net/2013/06/7149/', 'Valve, The Mirage Process, 2013. Reference only; not a current CS2 capture.'),
    ('anubis.jpg', 'Anubis — historical creator screenshot',
     'https://steamcommunity.com/sharedfiles/filedetails/?id=1984883124', 'Roald, jakuza, jd40; creator Workshop gallery. Reference only; not a current CS2 capture.'),
    ('split.jpg', 'Split — concept comparison',
     'https://playvalorant.com/en-us/news/dev/the-creation-of-split/', 'Riot Games, The Creation of Split, 2020. Concept art; reference only, not a gameplay capture.')
]
ASSET_URLS = {
    '06-riot-inspired.png': 'Notion attachment 3435c2ba-4215-49a8-be17-59c270090151; signed URL intentionally omitted',
    'mirage.png': 'https://blog.counter-strike.net/wp-content/uploads/2013/06/Bwall.png',
    'anubis.jpg': 'https://images.steamusercontent.com/ugc/787506473926164425/DAF9BC60FACACE626EE98A1B6422ECD22E59201D/',
    'split.jpg': 'https://cmsassets.rgpub.io/sanity/images/dsfx7636/news_live/50c491ab214dd376e74a7d5d1704757bc6c5fdae-1920x531.jpg'
}
manifest = {'retrieved': '2026-09-07', 'preference': 'Mirage and Anubis preferred; Split acceptable secondary; Icebox rejected.', 'files': []}
uris = {}
for filename, title, source, credit in SOURCES:
    raw = (OUT / filename).read_bytes()
    mime = 'image/png' if filename.endswith('.png') else 'image/jpeg'
    uris[filename] = 'data:' + mime + ';base64,' + base64.b64encode(raw).decode('ascii')
    manifest['files'].append(dict(file=filename, title=title, source=source, asset_url=ASSET_URLS[filename], credit=credit,
                                  sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw)))
(OUT / 'source-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

notes = [
    ('Helmet & visor', 48, 17, 'Peaked crown, narrow black slit, central ridge. Thin bright rims over a continuous shell.'),
    ('Shoulder layers', 35, 28, 'Rounded cap plus overlapping lames. Dark mail separates the arm from the torso.'),
    ('Painted steel', 50, 33, 'Broad irregular warm-gray patches and cooler reflections sit on a curved breastplate.'),
    ('Edge accents', 42, 40, 'Selective pale bevels on bracer and rims. Sparse glints; broad surfaces retain midtones.'),
    ('Articulated hands', 57, 45, 'Separate plated knuckles and curled finger segments. Dark gaps; two stacked grips.'),
    ('Longsword', 77, 22, 'Tapered double edge, two distinct blade faces, simple crossguard and faceted pommel.'),
    ('Blue cloth', 52, 57, 'Muted blue center panel with large folds and restrained warm edging. No visible crest.'),
    ('Adult silhouette', 38, 76, 'Tapered waist, long legs, functional armor. About 6.8 helmet-heights in this projection.'),
    ('Daylight', 84, 70, 'Warm stone, cool fill, ground shadow cast toward image left. Exact light setup is inferred.'),
    ('Quiet value groups', 18, 32, 'Large dark arch left, pale wall behind torso, restrained greenery. Preserve fighter separation.')
]
note_html = ''.join(f'<li><b>{i:02d} / {html.escape(n)}</b><p>{html.escape(t)}</p></li>' for i,(n,x,y,t) in enumerate(notes,1))
markers = ''.join(f'<a class="marker" href="#n{i}" style="left:{x}%;top:{y}%" aria-label="{html.escape(n)}">{i}</a>' for i,(n,x,y,t) in enumerate(notes,1))
for i in range(1, 11):
    note_html = note_html.replace(f'<li><b>{i:02d}', f'<li id="n{i}"><b>{i:02d}')

def detail(title, box, text):
    x,y,w,h = box
    return f'<article class="detail"><svg viewBox="{x} {y} {w} {h}" role="img" aria-label="{title}"><use href="#reference-image"/></svg><h3>{title}</h3><p>{text}</p></article>'

details = ''.join([
    detail('Shell, paint & rim', (298,174,352,440), 'Geometry supplies continuous volume. Painted patches vary at a larger scale than edge wear.'),
    detail('Grip construction', (477,560,240,265), 'Visible articulation is the anchor. Hidden thumb/palm contact requires a functional 3D interpretation.'),
    detail('Cloth & joint separation', (320,688,350,360), 'Large blue folds, dark padding/mail and hard steel remain three distinct material families.')
])
examples = ''
captions = {
    'mirage.png': 'Primary geometry / clarity reference. Compare the lower image: simple warm wall planes and readable arches, with less competing texture contrast. Historical before/after, not current CS2.',
    'anubis.jpg': 'Primary color / geometry reference. Warm sandstone masses, turquoise water, blue sky and restrained painted bands. Transfer the color relationships and clear forms to the existing medieval scope.',
    'split.jpg': 'Acceptable secondary reference. Broad authored color fields, selected warm/cool accents and clear large forms. This is a concept comparison, not the target environment or a shader specification.'
}
for filename,title,source,credit in SOURCES[1:]:
    examples += f'<article><img src="{uris[filename]}" alt="{html.escape(title)}"><h3>{title}</h3><p>{captions[filename]}</p><small>{credit} <a href="{source}">Source ↗</a></small></article>'

page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MEL-17 · Reference specification</title>
<style>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#10191e;color:#e9e7dd;font:16px/1.5 'Segoe UI',sans-serif}main{max-width:1480px;margin:auto;padding:36px}h1{font-size:42px;line-height:1.1;letter-spacing:-1px;margin:14px 0}h2{font-size:26px;margin:36px 0 18px}h3{font-size:19px;margin:16px 0 6px}p{margin:6px 0 12px}a{color:#a3d9e1}small,.muted{color:#a9bbc2}.eyebrow{font-size:13px;letter-spacing:2px;color:#b7a57c}.lede{max-width:1000px;font-size:19px}.status{display:inline-block;padding:6px 12px;border:1px solid #637982;border-radius:20px;font-size:13px}.hero{display:grid;grid-template-columns:minmax(0,1fr) minmax(360px,.85fr);gap:32px;margin-top:26px}.portrait{position:relative;align-self:start}.portrait>svg{width:100%;display:block}.marker{position:absolute;transform:translate(-50%,-50%);display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:#112a34;color:white;border:2px solid #e4d1a4;text-decoration:none;font-size:13px;font-weight:bold;box-shadow:0 2px 6px #0008}.hide .marker{display:none}button{background:#233944;border:1px solid #7599aa;color:#fff;padding:8px 14px;border-radius:4px;cursor:pointer;font:inherit}ol{padding:0;list-style:none;margin:0}li{border-bottom:1px solid #34454c;padding:10px 0}li p{font-size:15px;color:#b9c8cc;margin-bottom:2px}li:target{background:#263b43}.panel{background:#1b2b33;padding:20px;margin-top:18px;border-left:3px solid #b5a16d}.details{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}.detail svg{width:100%;height:340px;background:#17262d;display:block}.detail p{color:#b9c8cc}.examples{display:grid;grid-template-columns:repeat(2,1fr);gap:26px}.examples img{width:100%;height:340px;object-fit:contain;background:#18262c}.examples article:last-child{grid-column:1/-1}.examples article:last-child img{height:auto;max-height:350px}.gates{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.gate{padding:20px;background:#1b2b33}.gate b{color:#dec997}footer{border-top:1px solid #34454c;margin-top:32px;padding-top:18px;font-size:13px;color:#a9bbc2}@media(max-width:850px){main{padding:20px}h1{font-size:32px}.hero,.details,.examples,.gates{grid-template-columns:1fr}.hero{gap:20px}.examples article:last-child{grid-column:auto}.detail svg{height:350px}}@media print{body{background:white;color:#17232a}main{padding:0}button{display:none}.hero{grid-template-columns:1fr 1fr}a{color:#173c4c}.panel,.gate{background:#eff3f3}li p,small,.muted,.detail p,footer{color:#384d56}article,.gate{break-inside:avoid}h2{break-after:avoid}}
</style><main>
<div class="eyebrow">MELEE COMBAT LAB / MEL-17 / 07 SEPTEMBER 2026</div>
<h1>Stylized steel. Clear geometry. Strong color.</h1>
<p class="lede">The approved knight anchors character geometry. Valorant and Arcane inform authored texture that resembles painted art without looking like actual paint; <b>Mirage and Anubis lead the environment's geometry and color</b>. Split is secondary. Icebox is excluded.</p>
<span class="status">Reference preparation · production and visual acceptance pending</span>
<section class="hero"><div><div class="portrait" id="portrait"><svg viewBox="0 0 1024 1536" role="img" aria-label="Unchanged original approved full-body armored knight with longsword in warm limestone courtyard"><image id="reference-image" href="__PORTRAIT__" width="1024" height="1536"/></svg>__MARKERS__</div><p class="muted">Original 06-riot-inspired.png · 1024 × 1536 · unchanged source bytes</p><button onclick="document.getElementById('portrait').classList.toggle('hide');this.setAttribute('aria-pressed',document.getElementById('portrait').classList.contains('hide'))" aria-pressed="false">Toggle annotations</button></div><div><ol>__NOTES__</ol><div class="panel"><b>Observation ≠ hidden construction</b><p>Backplate, unseen fasteners, rear cloth, plate thickness, lens and exact lighting are inferred. The portrait is not an orthographic or mechanical blueprint.</p></div><div class="panel"><b>Paint on volume</b><p>Use broad authored patches and selective rims over continuous armor surfaces. Inspect clay shape, material and daylight separately.</p></div></div></section>
<h2>Three details that define the character</h2><section class="details">__DETAILS__</section>
<h2>Environment direction — preferred and secondary references</h2><section class="examples">__EXAMPLES__</section>
<div class="panel"><b>Proposed translation for the existing courtyard</b><p>Clear arches and wall planes; warm stone against blue/cool accents; local decoration kept quieter than the fighter. Preserve crisp blade, finger and silhouette edges at gameplay resolution. Color should stay lively without clipping the steel highlights. Exact palette and target map version remain review decisions.</p></div>
<h2>Shortest route to a reviewable result</h2><section class="gates"><div class="gate"><b>01 / Prepared now</b><p>Original and source hashes. Read-only asset audit. Fresh anatomy/rig candidate; new armor, hands, cloth and sword shape required.</p></div><div class="gate"><b>02 / After exchange review</b><p>MEL-18 matches camera and pose. MEL-19 proves helmet, shoulder and breastplate before the full armor build.</p></div><div class="gate"><b>03 / Playable decision</b><p>Review material fidelity, clear geometry, color and motion separately. Agents author and capture; the user reviews the result.</p></div></section>
<footer>Original attribution: Codex knight exploration and user decisions, as recorded in <a href="https://app.notion.com/p/3d42e3c3f8f881abb5c1c356dc68ee07">Notion</a>. Supporting game images belong to their credited creators/publishers and are reference-only. This sheet contains no new knight render or claim of artistic acceptance. Full route: Docs/MEL17_REFERENCE_ROUTE.md · Rebuild: python Tools/BuildMEL17ReferenceSheet.py.</footer></main></html>'''
for token,value in [('__PORTRAIT__',uris['06-riot-inspired.png']),('__MARKERS__',markers),('__NOTES__',note_html),('__DETAILS__',details),('__EXAMPLES__',examples)]:
    page = page.replace(token,value)
latest = json.loads((OUT / 'latest-study.json').read_text(encoding='utf-8')) if (OUT / 'latest-study.json').exists() else None
study = OUT / (latest['image'] if latest else 'PaintedSteel_v002/painted-steel-study.png')
if study.exists():
    study_uri = 'data:image/png;base64,' + base64.b64encode(study.read_bytes()).decode('ascii')
    study_section = '<h2>Painted-steel study · revision 2</h2><p class="lede">The painted texture aesthetic is the primary success criterion. This is an actual Blender render of two original curved plates using the same authored paint maps, seen at different angles.</p><img style="display:block;width:100%;height:auto" src="' + study_uri + '" alt="PaintedSteel_v002 actual rendered curved plate material study"><div class="panel"><b>Independent critic: 4/10 aesthetic fidelity · user review pending</b><p>Editable UV paint masses, roughness maps and packed Blender source are delivered. These are unrigged material proxies, not finished knight armor. Compare the broad patches and light response against the original below; the current patches still read too much like camouflage and the rim highlight is too uniform. The painted aesthetic is not yet matched. Next: form-following strokes, warm ivory / blue-gray separation, selective rims and a directional key.</p></div>'
    if latest:
        study_section = '<h2>' + html.escape(latest['candidate']) + ' / stylized steel study</h2><p class="lede">Authored texture character within steel, without the appearance of applied paint.</p><img style="display:block;width:100%;height:auto" src="' + study_uri + '" alt="Actual stylized steel material render"><div class="panel"><b>Independent critic: ' + str(latest['score']) + '/10 material-study quality</b><p>' + html.escape(latest['summary']) + '</p><p>Actual Blender geometry and material. This score does not certify a finished AAA character or replace user acceptance.</p></div>'
    page = page.replace('<section class="hero">', study_section + '<h2>Original character reference</h2><section class="hero">')
(OUT / 'reference-sheet.html').write_text(page, encoding='utf-8')
package_files = [OUT / f[0] for f in SOURCES] + [OUT / n for n in ('reference-sheet.html', 'source-manifest.json', 'asset-audit.json')] + [ROOT / p for p in ('Docs/MEL17_REFERENCE_ROUTE.md', 'Tools/MEL17Audit.py', 'Tools/BuildMEL17ReferenceSheet.py', 'Docs/ART_CRITIC_REVIEW.md')]
if study.exists():
    package_files += [p for p in study.parent.iterdir() if p.suffix in ('.blend','.json','.png','.md','.py','.sha256')]
    package_files += [ROOT / 'Tools/BuildPaintedSteelStudy.py', ROOT / 'Tools/BuildStylizedSteelStudy.py']
    if latest: package_files += [OUT / 'latest-study.json', OUT / 'ITERATION_LOG.md']
with zipfile.ZipFile(OUT / 'MEL17-review.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in package_files:
        archive.write(file, file.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT / 'MEL17-review.zip') as archive:
    assert archive.testzip() is None
print(json.dumps({'sheet_bytes': len(page.encode('utf-8')), 'sources': len(SOURCES), 'zip_bytes': (OUT / 'MEL17-review.zip').stat().st_size, 'zip_integrity': 'passed'}))




