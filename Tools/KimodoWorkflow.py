"""Isolated Kimodo generation and deliberate source conversion; never promotes assets.

Run with D:/AI/Kimodo/venv/Scripts/python.exe. Jobs are JSON files with
candidate, prompt, duration_seconds, seed and optional constraints (relative path).
One invocation reuses the loaded model for its explicitly named jobs.
"""
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
INSTALL = Path('D:/AI/Kimodo')
EXPERIMENT = ROOT / 'ArtSource/Kimodo/RH_20260913'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def environment():
    cache = ROOT / 'Saved/Kimodo/cache'
    cache.mkdir(parents=True, exist_ok=True)
    for key, val in {
        'HF_HOME': INSTALL / 'cache/huggingface', 'TORCH_HOME': cache / 'torch',
        'TEMP': cache, 'TMP': cache, 'TEXT_ENCODER_DEVICE': 'cpu',
        'TEXT_ENCODER_MODE': 'local', 'LOCAL_CACHE': 'True',
        'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1',
        'HF_HUB_DISABLE_TELEMETRY': '1', 'PYTHONDONTWRITEBYTECODE': '1',
    }.items():
        os.environ[key] = str(val)
    sys.dont_write_bytecode = True


def inspect():
    from kimodo.skeleton import SOMASkeleton30
    sk = SOMASkeleton30()
    EXPERIMENT.mkdir(parents=True, exist_ok=True)
    data = {}
    for s in [sk, sk.somaskel77]:
        data[s.name] = dict(names=s.bone_order_names,
                            parents=s.joint_parents.tolist(),
                            neutral=s.neutral_joints.tolist())
    write(EXPERIMENT / 'skeletons.json', data)
    print(json.dumps(data['somaskel30']), flush=True)


def effective_constraints(path):
    """Use supported postprocess masks without editing the installed package.

    Installed postprocess._build_constraint_masks_dict recognizes left-hand and
    right-hand, but skips generic end-effector (despite model conditioning accepting
    it). Split paired hand sets so both inference AND postprocessing see them.
    """
    result=[]
    for constraint in json.loads(Path(path).read_text()):
        if constraint['type']=='end-effector':
            assert set(constraint['joint_names']) <= {'LeftHand','RightHand'}, 'Unhandled generic end-effector postprocess mask'
            for name in constraint['joint_names']:
                copy={k:v for k,v in constraint.items() if k!='joint_names'}
                copy['type']={'LeftHand':'left-hand','RightHand':'right-hand'}[name]
                result.append(copy)
        else: result.append(constraint)
    return result


def validate_attack_job(job, constraints):
    """Check explicitly declared attack clocks before allocating the model.

    Historical transfer diagnostics without attack metadata retain their scope.
    New attack jobs declare frame_count and attack_timing; their release is500ms.
    """
    timing = job.get('attack_timing')
    if timing is None:
        if job.get('purpose') == 'attack':
            raise ValueError('Attack jobs must declare attack_timing')
        return None
    fps = timing['fps']
    count = job['frame_count']
    start, end = timing['release_start_index'], timing['release_end_index']
    if not all(isinstance(v, int) and not isinstance(v, bool) for v in [count,start,end]):
        raise ValueError('Attack frame counts and zero-based phase indices must be integers')
    if not math.isfinite(fps) or fps <= 0 or not 0 <= start < end < count:
        raise ValueError('Attack release must lie within a finite positive source clock')
    if not math.isclose(job['duration_seconds']*fps, count, rel_tol=0, abs_tol=1e-6):
        raise ValueError('Attack duration/FPS must describe the explicit sample count')
    config_path = ROOT/'Config/CombatDefaults.json'
    configured = json.loads(config_path.read_text(encoding='utf-8-sig'))['EXReleaseDuration']
    duration = (end-start)/fps
    for value in [timing['required_release_seconds'], configured, duration]:
        if not math.isclose(value, .5, rel_tol=0, abs_tol=1e-9):
            raise ValueError(f'Attack release must be authored as500ms; got {value}s')
    fullbody_frames = set()
    for constraint in constraints:
        indices = constraint.get('frame_indices', [])
        if any(not isinstance(i,int) or isinstance(i,bool) or not 0 <= i < count for i in indices):
            raise ValueError('Constraint frame is outside the declared attack source clock')
        if constraint['type'] == 'fullbody':
            fullbody_frames.update(indices)
    if not {start,end} <= fullbody_frames:
        raise ValueError('Fresh full-body poses must explicitly define both release boundaries')
    return dict(fps=fps, frame_count=count, release_start_index=start, release_end_index=end,
                release_seconds=duration, config_sha256=sha(config_path))


def generate(jobs):
    # Validate every destination before allocating the model or generating anything.
    requests = []
    for path in jobs:
        path = Path(path).resolve()
        assert EXPERIMENT in path.parents, 'Job must be inside this experiment'
        job = json.loads(path.read_text())
        assert job['candidate'] == path.parent.name
        assert job['duration_seconds'] > 0 and job['prompt'].strip()
        assert not (path.parent / 'motion.npz').exists(), 'Retain raw output; use a new candidate'
        constraints = path.parent / job.get('constraints', 'constraints.json')
        assert constraints.is_file(), 'Every job explicitly provides its constraints, including []'
        timing = validate_attack_job(job, json.loads(constraints.read_text()))
        requests.append((path, job, constraints, sha(path), sha(constraints), timing))
    print('Loading numerical and Kimodo libraries', flush=True)
    import numpy as np
    import torch
    import kimodo
    from kimodo import load_model
    from kimodo.constraints import load_constraints_lst
    from kimodo.exports.motion_io import save_kimodo_npz
    from kimodo.tools import seed_everything
    started = time.monotonic()
    print('Loading cached SOMA model and CPU text encoder', flush=True)
    model = load_model('Kimodo-SOMA-RP-v1.1', device='cuda')
    snapshots = INSTALL / 'cache/huggingface/hub/models--nvidia--Kimodo-SOMA-RP-v1.1'
    revision = (snapshots / 'refs/main').read_text().strip()
    snap = snapshots / 'snapshots' / revision
    identity = {p.name: sha(p) for p in snap.iterdir() if p.is_file()}
    for path, job, constraints, job_hash, constraint_hash, timing in requests:
        assert sha(path) == job_hash and sha(constraints) == constraint_hash, 'Inputs changed during model loading'
        shutil.copyfile(__file__, path.parent/'generator-used.py')
        if timing is not None and not math.isclose(model.fps, timing['fps'], rel_tol=0, abs_tol=1e-9):
            raise ValueError('Loaded model FPS differs from the authored attack clock')
        count = timing['frame_count'] if timing is not None else int(job['duration_seconds'] * model.fps)
        assert count >= 2
        effective=effective_constraints(constraints)
        write(path.parent/'constraints-effective.json', effective)
        constraint_list = load_constraints_lst(effective, model.skeleton)
        seed_everything(job['seed'])
        print('GENERATING ' + job['candidate'], flush=True)
        start = time.monotonic()
        output = model([job['prompt']], [count], constraint_lst=constraint_list,
                       num_denoising_steps=100, num_samples=1, multi_prompt=False,
                       post_processing=True, return_numpy=True)
        single = {k: (v[0] if hasattr(v, 'shape') and len(v.shape) and v.shape[0] == 1 else v)
                  for k, v in output.items()}
        for key in ('posed_joints', 'global_rot_mats'):
            assert np.isfinite(single[key]).all(), key
            assert single[key].shape[0] == count, (key, single[key].shape, count)
        dest = path.parent / 'motion.npz'
        save_kimodo_npz(str(dest), single)
        write(path.parent / 'generation.json', dict(
            job=job, attack_timing_validation=timing, model='Kimodo-SOMA-RP-v1.1', model_snapshot=revision,
            weights_and_config_sha256=identity, generator_sha256=sha(__file__),
            installed_package=str(Path(kimodo.__file__).parent),
            installed_generator_sha256=sha(Path(kimodo.__file__).parent/'scripts/generate.py'),
            package_versions={name:importlib.metadata.version(name)
                              for name in ('kimodo','torch','transformers','peft')},
            job_sha256=job_hash, constraints_sha256=constraint_hash, raw_sha256=sha(dest),
            effective_constraints_sha256=sha(path.parent/'constraints-effective.json'),
            fps=float(model.fps), frames=count, sample_span_seconds=(count-1)/model.fps,
            display_duration_seconds=count/model.fps, first_sample=0,
            endpoint='N samples at i/FPS; final sample displays for one frame interval; no added endpoint',
            post_processing=True, diffusion_steps=100, cfg='model defaults',
            generation_seconds=time.monotonic()-start,
            elapsed_since_load_seconds=time.monotonic()-started,
            shapes={k:list(v.shape) for k,v in single.items() if hasattr(v,'shape')},
            human_acceptance=False))
        print('SAVED ' + str(dest), flush=True)


def convert(candidate):
    folder = EXPERIMENT / candidate
    assert folder.parent == EXPERIMENT and (folder/'motion.npz').is_file()
    dest = folder / 'transfer-standard-tpose.bvh'
    assert not dest.exists(), 'Transfer already exists'
    gen = json.loads((folder/'generation.json').read_text())
    # Use the public converter entry point; conversion is always a separate invocation.
    from kimodo.scripts.motion_convert import main
    result = main([str(folder/'motion.npz'), str(dest), '--from', 'kimodo',
                   '--to', 'soma-bvh', '--source-fps', str(gen['fps']), '--bvh_standard_tpose'])
    assert result == 0 and dest.is_file()
    write(folder/'conversion.json', dict(raw_sha256=sha(folder/'motion.npz'),
          bvh_sha256=sha(dest), standard_tpose=True, bvh_units='centimeters', fps=gen['fps']))


def postprocess(source_name, destination_name):
    """Retain input; deliberately reprocess an isolated copy with corrected masks."""
    import numpy as np
    import torch
    import kimodo
    from kimodo.skeleton import SOMASkeleton30
    from kimodo.constraints import load_constraints_lst
    from kimodo.postprocess import post_process_motion
    from kimodo.exports.motion_io import save_kimodo_npz
    source=EXPERIMENT/source_name;dest=EXPERIMENT/destination_name
    assert source.parent==EXPERIMENT and dest.parent==EXPERIMENT and not dest.exists()
    raw=source/'motion.npz'; raw_hash=sha(raw)
    data=np.load(raw);sk=SOMASkeleton30()
    effective=effective_constraints(source/'constraints.json')
    constraints=load_constraints_lst(effective,sk)
    local=sk.from_SOMASkeleton77(torch.from_numpy(data['local_rot_mats']).float())
    roots=torch.from_numpy(data['root_positions']).float()[None]
    contacts=torch.from_numpy(data['foot_contacts']).float()[None]
    started=time.monotonic()
    fixed=post_process_motion(local[None],roots,contacts,sk,constraints)
    fixed['foot_contacts']=contacts
    output=sk.output_to_SOMASkeleton77(fixed)
    single={k:v[0].detach().cpu().numpy() for k,v in output.items()}
    assert all(np.isfinite(v).all() for v in single.values())
    dest.mkdir()
    write(dest/'constraints.json',effective)
    shutil.copyfile(__file__,dest/'postprocessor-used.py')
    save_kimodo_npz(str(dest/'motion.npz'),single)
    original=json.loads((source/'generation.json').read_text())
    write(dest/'generation.json',dict(operation='Existing Kimodo native postprocessor on a retained transfer copy; no diffusion rerun',
        source_raw=str(raw.relative_to(ROOT)),source_raw_sha256=raw_hash,raw_sha256=sha(dest/'motion.npz'),
        source_generation=original,postprocessor_sha256=sha(Path(kimodo.__file__).parent/'postprocess.py'),
        wrapper_sha256=sha(__file__),constraints_sha256=sha(dest/'constraints.json'),
        fps=original['fps'],frames=original['frames'],sample_span_seconds=original['sample_span_seconds'],
        display_duration_seconds=original['display_duration_seconds'],elapsed_seconds=time.monotonic()-started,
        correction='Expand combined hand targets into recognized left-hand/right-hand postprocess masks',human_acceptance=False))
    assert sha(raw)==raw_hash
    print('POSTPROCESSED '+str(dest),flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=['inspect', 'generate', 'convert', 'postprocess'])
    p.add_argument('inputs', nargs='*')
    a = p.parse_args()
    environment()
    if a.operation == 'inspect': inspect()
    elif a.operation == 'generate': generate(a.inputs)
    elif a.operation == 'postprocess': postprocess(*a.inputs)
    else:
        for candidate in a.inputs: convert(candidate)
