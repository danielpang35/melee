"""Build a hash-bound neutral contact trial from the selected export, never edit source."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Saved/MEL15/production'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    selection = json.loads((ROOT / 'Config/EXPreview.json').read_text())
    weapon_path = ROOT / selection['weapon_motion']
    manifest_path = weapon_path.parent / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    source = ROOT / 'ArtSource/CharacterReset/EX_v002/EX_v002_MordhauRight.blend'
    assert sha(source) == selection['source_sha256'] == manifest['source_sha256']
    animation = ROOT / 'Content/EXPreview/EX_v002/EX_v002_Anim.uasset'
    assert sha(animation) == selection['animation_package_sha256']
    motion = json.loads(weapon_path.read_text())
    assert motion['fps'] == 60 and len(motion['samples']) == 154
    lines = ['EX_WEAPON_V1 60 154']
    maximum = 0
    for i, sample in enumerate(motion['samples']):
        assert sample['frame'] == i + 1 and abs(sample['time_s'] - i / 60) < 1e-8
        base = sample['blade_base_rig_space_m']
        tip = sample['blade_tip_rig_space_m']
        transform = sample['weapon_rig_space']
        q = transform['quaternion_wxyz']
        assert all(math.isfinite(v) for v in base + tip + q)
        norm = math.sqrt(sum(v*v for v in q))
        assert abs(norm*norm - 1) < .001
        w, x, y, z = [v / norm for v in q]
        assert max(abs(x - 1) for x in transform['scale']) < 1e-5
        length = math.dist(base, tip) * 100
        assert abs(length - 103.5) < .01
        # Independently compare supplied endpoints to the delivered rotation matrix.
        matrix = transform['matrix_row_major']
        predicted = [base[k] + matrix[k][2] * length / 100 for k in range(3)]
        maximum = max(maximum, math.dist(predicted, tip) * 100)
        axis = [2*(x*z+w*y), 2*(y*z-w*x), 1-2*(x*x+y*y)]
        maximum = max(maximum, math.dist([base[k]+axis[k]*length/100 for k in range(3)], tip)*100)
        values = [-base[1] * 100, -base[0] * 100, base[2] * 100] + q + [length]
        lines.append(str(i) + ' ' + ' '.join(format(v, '.17g') for v in values))
    assert maximum < .001
    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / 'EXWeapon.txt'
    output.write_text('\n'.join(lines) + '\n')
    receipt = dict(revision=selection['revision'], source_sha256=sha(source),
                   weapon_sha256=sha(weapon_path), manifest_sha256=sha(manifest_path),
                   sampler_sha256=sha(output), samples=154, endpoint_error_cm=maximum,
                   authority='production mapping candidate; human gameplay acceptance pending',
                   source_start=.30, release_source=[62/60, 80/60], damage='full proposed release',
                   source_end=2.55, rate=1, pivot_gameplay_cm=[11.5, 0, 168])
    (OUT / 'identity.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
