"""Package the selected helmet proof and its reproducible source dependencies."""
from pathlib import Path
import json, zipfile, hashlib

root=Path(__file__).resolve().parents[1]
art=root/'ArtSource/StyleReference/MEL17'
candidate=json.loads((art/'latest-helmet.json').read_text())['candidate']
files=list((art/candidate).glob('*'))
files += [art/p for p in ['helmet-review.html','latest-helmet.json','HELMET_ITERATIONS.md','06-riot-inspired.png','Steel_v025/Steel_v025.blend','Steel_v025/steel-study.png','Steel_v025/CRITIC.md']]
files += list(art.glob('Helmet_v*/CRITIC.md'))
files += [root/'Tools'/p for p in ['BuildHelmetStudy.py','BuildHelmetReview.py','BuildPaintedSteelStudy.py','PackageHelmetReview.py']]
files=sorted(set(p for p in files if p.is_file()))
archive=art/f'MEL17-{candidate}-review.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
for view in json.loads((art/candidate/'settings.json').read_text())['views']:
    assert hashlib.sha256((art/candidate/(view['view']+'.png')).read_bytes()).hexdigest()==view['sha256']
receipt={'archive':str(archive.relative_to(root)),'bytes':archive.stat().st_size,'files':len(files),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
(root/'Saved/HelmetReview-receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
