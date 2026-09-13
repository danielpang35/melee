"""Author a restrained, editable HDR reflection stage for the isolated steel proof."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Saved/ArtRuntime'))
import numpy as np


def smoothstep(lo, hi, value):
    t = np.clip((value - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def write_hdr(path, rgb):
    """Radiance RGBE scanlines; literal RLE blocks keep the writer auditable."""
    h, w, _ = rgb.shape
    peak = np.maximum(rgb.max(axis=2), 1e-32)
    mantissa, exponent = np.frexp(peak)
    scale = mantissa * 256 / peak
    rgbe = np.empty((h, w, 4), dtype=np.uint8)
    rgbe[:, :, :3] = np.clip(rgb * scale[:, :, None], 0, 255).astype(np.uint8)
    rgbe[:, :, 3] = (exponent + 128).astype(np.uint8)
    with path.open('wb') as f:
        f.write(f'#?RADIANCE\nFORMAT=32-bit_rle_rgbe\n\n-Y {h} +X {w}\n'.encode('ascii'))
        for row in rgbe:
            f.write(bytes([2, 2, w >> 8, w & 255]))
            for channel in range(4):
                for start in range(0, w, 128):
                    values = row[start:start + 128, channel].tobytes()
                    f.write(bytes([len(values)]))
                    f.write(values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', default='Environment_v001')
    parser.add_argument('--treatment', choices=['baseline', 'neutral-lower', 'lower-ramp', 'reference-hierarchy', 'reflection-boundary'], default='baseline')
    args = parser.parse_args()
    if not re.fullmatch(r'Environment_v\d{3}', args.revision):
        parser.error('Expected Environment_vNNN')
    out = ROOT / 'ArtSource/StyleReference/MEL17/UnrealProof' / args.revision
    if out.exists():
        parser.error('Preserve prior evidence; choose a new revision')
    width, height = 1024, 512
    azimuth = (np.arange(width)[None, :] + .5) / width * 360 - 180
    elevation = 90 - (np.arange(height)[:, None] + .5) / height * 180
    azimuth = np.broadcast_to(azimuth, (height, width))
    elevation = np.broadcast_to(elevation, (height, width))
    sky = smoothstep(-8, 35, elevation)
    ground = np.array([.11, .085, .052], dtype=np.float32)
    cool = np.array([.24, .34, .50], dtype=np.float32)
    rgb = ground + sky[:, :, None] * (cool - ground)
    # A warm wall takes up a broad azimuth range, with a single dark aperture.
    wall = smoothstep(-80, -65, azimuth) * (1 - smoothstep(40, 55, azimuth))
    wall *= smoothstep(-35, -25, elevation) * (1 - smoothstep(25, 36, elevation))
    rgb = rgb * (1 - .6 * wall[:, :, None]) + np.array([.34, .255, .16]) * .6 * wall[:, :, None]
    aperture = smoothstep(-33, -27, azimuth) * (1 - smoothstep(-8, -2, azimuth))
    aperture *= smoothstep(-18, -13, elevation) * (1 - smoothstep(18, 24, elevation))
    rgb *= 1 - .83 * aperture[:, :, None]
    # Broad skewed four-sided warm reflection mass; no point-like baked sun.
    yaw = 135.0
    dx = (azimuth - yaw + 180) % 360 - 180
    dy = elevation - 40.0
    edge_distance = np.maximum(abs(dx + .27 * dy) / 39, abs(dy - .12 * dx) / 20)
    warm = 1 - smoothstep(.77, 1.0, edge_distance)
    rgb += warm[:, :, None] * np.array([.72, .60, .41])
    if args.treatment in ('neutral-lower', 'lower-ramp', 'reference-hierarchy', 'reflection-boundary'):
        # The initial uniformly brown lower field concealed normal changes.
        # Keep one broad oblique value boundary across cheek reflection rays.
        # This is a directional environment signal, never color painted on armor.
        lower_weight = 1 - smoothstep(-12, 4, elevation)
        side = smoothstep(65, 89, azimuth + .65 * (elevation + 35))
        warm_gray = np.array([.245, .232, .205])
        cool_gray = np.array([.115, .135, .163])
        lower = warm_gray + side[:, :, None] * (cool_gray - warm_gray)
        if args.treatment in ('lower-ramp', 'reference-hierarchy', 'reflection-boundary'):
            # Env2's flat sectors gave a small normal perturbation no signal
            # to sample. A continuous low-frequency field supplies a gradient
            # across both cheeks without adding painted islands or noise.
            phase = np.radians(azimuth - 20)
            level = .24 + .16 * np.sin(phase) + .055 * np.sin(np.radians(elevation * 2))
            temperature = .5 + .5 * np.sin(phase - .8)
            if args.treatment in ('reference-hierarchy', 'reflection-boundary'):
                level = .17 + .10 * np.sin(phase) + .035 * np.sin(np.radians(elevation * 2))
                temperature = .4 + .2 * np.sin(phase - .8)
            if args.treatment == 'reflection-boundary':
                # Runtime WorldNormal A/B proves the fields transfer. The old
                # sinusoid supplied only ~.011 unfiltered luminance change at
                # active cheek interiors. Keep its .17 midpoint/.10 range,
                # but place broad 25/30-degree boundaries across those rays.
                oblique = azimuth + .15 * (elevation + 25)
                mass = smoothstep(0, 25, oblique) * (1 - smoothstep(115, 145, oblique))
                level = .17 + .10 * (2 * mass - 1) + .035 * np.sin(np.radians(elevation * 2))
            warm_tint = np.array([1.05, 1.0, .92])
            cool_tint = np.array([.94, 1.0, 1.09])
            tint = warm_tint + temperature[:, :, None] * (cool_tint - warm_tint)
            lower = level[:, :, None] * tint
        rgb = rgb * (1 - lower_weight[:, :, None]) + lower * lower_weight[:, :, None]
        # Restrain the sky's rectangular highlight mass and blue saturation;
        # direct-key specular is compared independently inside the engine.
        rgb -= warm[:, :, None] * np.array([.50, .40, .25])
        sky_desaturate = smoothstep(12, 65, elevation)
        sky_luma = rgb @ np.array([.2126, .7152, .0722])
        rgb = rgb * (1 - .35 * sky_desaturate[:, :, None]) + sky_luma[:, :, None] * .35 * sky_desaturate[:, :, None]
        if args.treatment in ('reference-hierarchy', 'reflection-boundary'):
            # Adding a weak warm lobe to blue sky left its final RGB blue.
            # Explicitly author a pale warm reflection mass, and retain a
            # darker lower field, matching the portrait's large value order.
            rgb = rgb * (1 - warm[:, :, None]) + np.array([.56, .51, .43]) * warm[:, :, None]
    neutral = np.repeat((rgb @ np.array([.2126, .7152, .0722]))[:, :, None], 3, axis=2)
    assert np.isfinite(rgb).all() and rgb.min() >= 0
    out.mkdir(parents=True)
    write_hdr(out / 'T_AuthoredDaylight.hdr', rgb)
    write_hdr(out / 'T_AuthoredNeutral.hdr', neutral)
    np.savez_compressed(out / 'EditableEnvironment.npz', daylight_linear=rgb, neutral_linear=neutral, wall_mask=wall, aperture_mask=aperture, warm_mass_mask=warm)
    (out / 'generator.py').write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')
    receipt = {'revision': args.revision, 'treatment': args.treatment, 'size': [width, height], 'format': 'Radiance RGBE linear HDR latitude-longitude', 'direction_convention': 'azimuth 0 = +X; +90 = +Y; elevation +90 = +Z; verify engine orientation', 'warm_mass_center_degrees': {'yaw': yaw, 'elevation': 40}, 'intended_key_rotation_degrees': {'pitch': -40, 'yaw': -45}, 'rgb_range': [float(rgb.min()), float(rgb.max())], 'purpose': 'Optional controlled reflection environment experiment after built-in cubemap baseline; not a source-portrait texture or preaccepted match.', 'limits': ['Synthetic scene-scale reflection field, not a physical HDR photograph.', 'Engine cubemap orientation and key coherence require an actual Unreal A/B.', 'Not enabled by this source generator.'], 'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
    (out / 'settings.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({'output': str(out), 'size': receipt['size'], 'range': receipt['rgb_range']}))


if __name__ == '__main__':
    main()
