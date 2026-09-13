"""Run a fresh diagnostic TP proposal with the pinned existing standalone binary.

--pin-harness records already verified harness/core identities without reading TP
source. A comparison additionally requires the explicitly frozen source SHA256.
"""
import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / 'Saved/TPProof/proposed-canonical'
PIN = HARNESS / 'harness-identity.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_new(path, value):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


def validate_identities(identities):
    for name, expected in identities.items():
        assert sha(ROOT / name) == expected, 'Pinned input changed: ' + name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pin-harness', action='store_true')
    parser.add_argument('--revision')
    parser.add_argument('--source-sha256')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.pin_harness:
        original = read(HARNESS / 'derivation.json')
        identities = {p:h for p,h in original['preserved_identities'].items() if p.startswith('Source/MeleeCombatLab/Combat/')}
        validate_identities(identities)
        for name in ('CompareTPCanonical.cpp', 'CompareTPCanonical.exe', 'CompileAndRun.ps1'):
            path = HARNESS / name
            identities[path.relative_to(ROOT).as_posix()] = sha(path)
        pin = dict(profile='TP_diagnostic_harness_v1', identities=identities,
                   baseline_sampler_sha256=original['preserved_identities']['Saved/MEL15/production/EXWeapon.txt'],
                   baseline_results_sha256=digest(read(HARNESS / 'comparison.json')['baseline']),
                   provenance='Pinned existing harness after its successful original standalone run; core hashes checked against that original derivation receipt. No rebuild.')
        if PIN.exists():
            assert read(PIN) == pin, 'Existing pin differs; review harness provenance before replacing it'
        else:
            write_new(PIN, pin)
        print(json.dumps(dict(harness_pinned=True, binary_sha256=identities[(HARNESS/'CompareTPCanonical.exe').relative_to(ROOT).as_posix()], tp_source_read=False)))
        return
    assert args.revision and re.fullmatch(r'[A-Za-z0-9_-]+', args.revision)
    assert args.source_sha256 and re.fullmatch(r'[a-fA-F0-9]{64}', args.source_sha256), 'Supply the explicitly frozen source SHA256'
    out = (args.out or ROOT / ('Saved/TPProof/proposed-canonical-' + args.revision)).resolve()
    assert out.is_relative_to((ROOT/'Saved/TPProof').resolve()) and out != HARNESS.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for name in ('TP_proposed_EXWeapon.txt', 'derivation.json', 'comparison.json', 'tradeoff.json', 'TRADEOFF.md'):
        assert not (out/name).exists(), 'Use a fresh output directory; preserving ' + name
    pin = read(PIN)
    validate_identities(pin['identities'])
    baseline = ROOT / 'Saved/MEL15/production/EXWeapon.txt'
    assert sha(baseline) == pin['baseline_sampler_sha256']
    selection = read(ROOT/'Config/EXPreview.json')
    baseline_receipt = read(ROOT/'Saved/MEL15/production/identity.json')
    assert selection['revision'] == baseline_receipt['revision']
    assert sha(ROOT/selection['weapon_motion']) == baseline_receipt['weapon_sha256']
    export = ROOT / 'ArtSource/CharacterReset/TP_v001/Export'
    manifest = read(export/'manifest.json')
    assert manifest['source_sha256'].lower() == args.source_sha256.lower() == sha(ROOT/manifest['source'])
    assert read(export/'export-verification.json')['passed']
    for name, expected in manifest['files'].items():
        assert sha(export/name) == expected, name
    source = export/'TP_v001_WeaponMotion.json'
    motion = read(source)
    assert motion['source_sha256'] == manifest['source_sha256'] and motion['fps'] == 60 and len(motion['samples']) == 154
    preserved = dict(pin['identities'])
    for path in (ROOT/'Config/EXPreview.json', ROOT/selection['weapon_motion'], baseline, ROOT/manifest['source'], source,
                 export/'manifest.json', ROOT/'ArtSource/CharacterReset/EX_v002/EX_v002_MordhauRight.blend',
                 ROOT/'Content/EXPreview/EX_v002/EX_v002_Anim.uasset', Path(__file__)):
        preserved[path.relative_to(ROOT).as_posix()] = sha(path)
    assert preserved['ArtSource/CharacterReset/EX_v002/EX_v002_MordhauRight.blend'] == selection['source_sha256']
    assert preserved['Content/EXPreview/EX_v002/EX_v002_Anim.uasset'] == selection['animation_package_sha256']
    lines = ['EX_WEAPON_V1 60 154']
    maximum = 0.0
    for i, row in enumerate(motion['samples']):
        assert row['frame'] == i+1 and abs(row['time_s']-i/60) < 1e-9
        base, tip, q = row['blade_base_world_m'], row['blade_tip_world_m'], row['weapon_world']['quaternion_wxyz']
        assert len(base) == len(tip) == 3 and len(q) == 4 and all(math.isfinite(v) for v in [*base,*tip,*q])
        norm = math.sqrt(sum(v*v for v in q)); assert abs(norm*norm-1) < .001
        w,x,y,z = [v/norm for v in q]
        axis = [2*(x*z+w*y),2*(y*z-w*x),1-2*(x*x+y*y)]
        maximum = max(maximum, math.dist([base[k]+axis[k]*1.035 for k in range(3)],tip)*100)
        assert abs(math.dist(base,tip)*100-103.5) < .001 and maximum < .001
        values = [-base[1]*100+11.5,-base[0]*100,base[2]*100-2,w,x,y,z,103.5]
        lines.append(str(i)+' '+' '.join(format(v,'.17g') for v in values))
    proposed = out/'TP_proposed_EXWeapon.txt'
    proposed.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    derivation = dict(authority='Diagnostic only; never selected or applied', revision_label=args.revision,
                     source_sha256=manifest['source_sha256'], baseline_revision=selection['revision'],
                     proposed_sha256=sha(proposed), harness_pin_sha256=sha(PIN), preserved_identities=preserved,
                     mapping='C(source)=100*(-y,-x,z); stored hilt=C(base)+(11.5,0,-2)cm; native quaternion retained',
                     max_marker_error_cm=maximum, compiler_run=False, engine_run=False)
    write_new(out/'derivation.json', derivation)
    subprocess.run([str(HARNESS/'CompareTPCanonical.exe'),str(baseline),str(proposed),str(out/'comparison.json')],check=True)
    validate_identities(preserved)
    result = read(out/'comparison.json')
    assert digest(result['baseline']) == pin['baseline_results_sha256'], 'Reused binary no longer reproduces the pinned baseline cases'
    assert len(result['baseline']) == len(result['proposed']) == 12
    paired = []
    table = ['| Case | Target ID | Baseline s | Proposed s | Delta ms |','|---|---:|---:|---:|---:|']
    for before, after in zip(result['baseline'],result['proposed']):
        assert before['case'] == after['case'] and before['targets'] == after['targets']
        bh = {e['defender']:e for e in before['events'] if e['result']=='HIT'}
        ph = {e['defender']:e for e in after['events'] if e['result']=='HIT'}
        record = dict(case=before['case'],targets=before['targets'],baseline_hits=bh,proposed_hits=ph,
                      baseline_order=list(bh),proposed_order=list(ph),
                      common_target_timing_delta_s={k:ph[k]['time_s']-bh[k]['time_s'] for k in bh.keys()&ph.keys()})
        paired.append(record)
        for target in before['targets']:
            ident = target['id']; bt = bh.get(ident,{}).get('time_s'); pt = ph.get(ident,{}).get('time_s')
            btext = 'Miss' if bt is None else f'{bt:.6f}'; ptext = 'Miss' if pt is None else f'{pt:.6f}'
            delta = '—' if bt is None or pt is None else f'{(pt-bt)*1000:+.3f}'
            table.append(f"| {before['case']} | {ident} | {btext} | {ptext} | {delta} |")
    write_new(out/'tradeoff.json',dict(**{k:derivation[k] for k in ('authority','revision_label','source_sha256','proposed_sha256')},
              preserved_identities_unchanged=True, pinned_baseline_reproduced=True, cases=paired))
    report = [f'# {args.revision} proposed canonical track — diagnostic only','',
              f"Frozen source: `{manifest['source_sha256']}`. Baseline: `{selection['revision']}`.",
              'The existing pinned standalone binary reproduced its complete baseline event corpus without recompilation. Simulation, baseline selection/assets and source identities were unchanged.',
              'The proposed track was never selected or applied. This table describes bounded differences, not approval or universal equivalence/impossibility.',
              '', 'Conditions: stationary neutral aim; attacker/target centers Z90 cm, capsule radius32 cm and half-height88 cm, eye offset82 cm. Source entry .30 s; release62/60–80/60 s; native60 Hz sampling;240 Hz simulation submitted at60 Hz. No walls, defense, movement, crouching, other attacks or new FP counterpart.',
              'The hilt mapping adds (11.5,0,−2) cm after source→gameplay conversion to compensate the current camera-relative EX pivot against TP capsule feet. Raw contact points and target ordering are retained in comparison.json/tradeoff.json.',
              '',*table,'', 'Review hit/miss, timing, ordering and contact locations together before deciding on any canonical/first-person tradeoff.']
    (out/'TRADEOFF.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    print(json.dumps(dict(output=str(out),cases=len(paired),source_sha256=manifest['source_sha256'],selected=False,recompiled=False)))


if __name__ == '__main__':
    main()
