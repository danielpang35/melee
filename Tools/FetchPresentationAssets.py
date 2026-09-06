"""Fetch the CC0 source library, verifying provider hashes; never overwrites game code."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1] / 'ArtSource' / 'Citadel'
ROOT.mkdir(parents=True, exist_ok=True)

def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'MeleeCombatLab/1.0'}), timeout=60) as response:
        return json.load(response)

def fetch(entry, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or hashlib.md5(path.read_bytes()).hexdigest() != entry['md5']:
        with urllib.request.urlopen(urllib.request.Request(entry['url'], headers={'User-Agent': 'MeleeCombatLab/1.0'}), timeout=120) as response:
            data = response.read()
        if hashlib.md5(data).hexdigest() != entry['md5']:
            raise RuntimeError(f'Hash mismatch: {path}')
        path.write_bytes(data)
    return {'file': str(path.relative_to(ROOT)), 'url': entry['url'],
            'md5': entry['md5'], 'license': 'CC0-1.0'}

def main():
    jobs = []
    sword = get_json('https://api.polyhaven.com/files/antique_estoc')['gltf']['2k']['gltf']
    jobs.append((sword, ROOT / 'antique_estoc' / 'antique_estoc.gltf'))
    for name, entry in sword['include'].items():
        jobs.append((entry, ROOT / 'antique_estoc' / name))
    for asset in ('white_sandstone_blocks_02', 'cobblestone_floor_08', 'roof_slates_02'):
        files = get_json('https://api.polyhaven.com/files/' + asset)
        (ROOT / asset).mkdir(exist_ok=True)
        (ROOT / asset / 'provider.json').write_text(json.dumps(files, indent=2))
        for channel, key in (('diff', 'Diffuse'), ('nor_dx', 'nor_dx'), ('rough', 'Rough')):
            entry = files[key]['2k']['jpg']
            jobs.append((entry, ROOT / asset / (channel + '.jpg')))
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda pair: fetch(*pair), jobs))
    knight_url='https://opengameart.org/sites/default/files/armored%20knight.zip'
    knight_hash='edea99305ea1dfffbe56434498693e325d909cf638845f1a473c6d0993aca100'
    archive=ROOT/'knight/source.zip';archive.parent.mkdir(exist_ok=True)
    if not archive.exists():
        with urllib.request.urlopen(urllib.request.Request(knight_url,headers={'User-Agent':'MeleeCombatLab/1.0'}),timeout=120) as response:
            archive.write_bytes(response.read())
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=knight_hash:
        raise RuntimeError('Knight source changed; inspect source and license before accepting it')
    with zipfile.ZipFile(archive) as z:
        (ROOT/'knight/armor.blend').write_bytes(z.read('armor.blend'))
    results.append({'file':'knight/source.zip','url':knight_url,'sha256':knight_hash,'license':'CC-BY-3.0','author':'piacenti'})
    (ROOT / 'manifest.json').write_text(json.dumps(results, indent=2))
    print(f'Verified {len(results)} licensed source files in {ROOT}')

if __name__ == '__main__':
    main()
