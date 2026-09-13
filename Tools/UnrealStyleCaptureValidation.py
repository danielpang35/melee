"""Strict viewport evidence checks, using only the Unreal Python standard library."""
import hashlib
import math
from pathlib import Path
import struct
import zlib


def validate_png(path, expected_size=None):
    """Decode every pixel of an 8-bit, noninterlaced RGB(A) viewport PNG.

    Reject truncation, corrupt chunks/deflate data, unsupported formats and blank
    RGB output. Alpha variation alone is not rendered scene evidence.
    """
    data = Path(path).read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Invalid PNG signature')
    offset, compressed, size, channels, ended = 8, bytearray(), None, None, False
    seen_idat = False
    idat_closed = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError('Truncated PNG chunk')
        length = struct.unpack_from('>I', data, offset)[0]
        kind = data[offset + 4:offset + 8]
        end = offset + length + 12
        if end > len(data):
            raise ValueError('Truncated PNG payload')
        payload = data[offset + 8:end - 4]
        if zlib.crc32(kind + payload) & 0xffffffff != struct.unpack_from('>I', data, end - 4)[0]:
            raise ValueError('PNG CRC mismatch')
        if size is None and kind != b'IHDR':
            raise ValueError('Missing initial IHDR')
        if kind == b'IHDR':
            if size is not None or length != 13:
                raise ValueError('Invalid IHDR')
            width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', payload)
            if not (0 < width <= 16384 and 0 < height <= 16384) or width * height > 32_000_000:
                raise ValueError('Invalid viewport dimensions')
            if depth != 8 or color not in (2, 6) or compression or filtering or interlace:
                raise ValueError('Expected noninterlaced 8-bit RGB(A) viewport PNG')
            size, channels = (width, height), (3 if color == 2 else 4)
            if expected_size and tuple(expected_size) != size:
                raise ValueError('Unexpected viewport dimensions: ' + str(size))
        elif kind == b'IDAT':
            if idat_closed:
                raise ValueError('Nonconsecutive IDAT chunks')
            compressed.extend(payload)
            seen_idat = True
        elif kind == b'IEND':
            if length or not seen_idat or end != len(data):
                raise ValueError('Invalid PNG end')
            ended = True
            break
        elif kind[:1].isupper() and kind != b'PLTE':
            raise ValueError('Unsupported critical PNG chunk')
        if seen_idat and kind != b'IDAT':
            idat_closed = True
        offset = end
    if not ended:
        raise ValueError('Missing PNG end')
    stride = width * channels
    expected_bytes = height * (stride + 1)
    decoder = zlib.decompressobj()
    raw = decoder.decompress(bytes(compressed), expected_bytes + 1)
    if len(raw) != expected_bytes or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise ValueError('Incomplete or oversized PNG pixel stream')
    previous = bytearray(stride)
    minimum, maximum = [255] * 3, [0] * 3
    for y in range(height):
        start = y * (stride + 1)
        method = raw[start]
        row = bytearray(raw[start + 1:start + stride + 1])
        if method > 4:
            raise ValueError('Invalid PNG filter')
        for x in range(stride):
            a = row[x - channels] if x >= channels else 0
            b = previous[x]
            c = previous[x - channels] if x >= channels else 0
            if method == 1:
                predictor = a
            elif method == 2:
                predictor = b
            elif method == 3:
                predictor = (a + b) // 2
            elif method == 4:
                p = a + b - c
                pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                predictor = a if pa <= pb and pa <= pc else b if pb <= pc else c
            else:
                predictor = 0
            row[x] = (row[x] + predictor) & 255
        for channel in range(3):
            values = row[channel::channels]
            minimum[channel] = min(minimum[channel], min(values))
            maximum[channel] = max(maximum[channel], max(values))
        previous = row
    if max(b-a for a, b in zip(minimum, maximum)) < 2:
        raise ValueError('Blank viewport RGB output')
    return {'width': width, 'height': height, 'sha256': hashlib.sha256(data).hexdigest(),
            'decoded_pixels': width * height, 'rgb_min': minimum, 'rgb_max': maximum,
            'complete_image_validated': True}


def validate_motion(captures, expected_sequences, fps=30):
    """Missing or nonconsecutive engine frames fail, even with numbered files."""
    if not isinstance(fps,(int,float)) or not math.isfinite(fps) or fps<=0:
        raise ValueError('Invalid motion fps')
    results = []
    for name, count in expected_sequences.items():
        frames = [c for c in captures if c.get('motion') == name]
        if count < 2 or len(frames) != count or [c.get('sequence_frame') for c in frames] != list(range(count)):
            raise ValueError('Incomplete motion sequence: ' + name)
        if len({c['file'] for c in frames}) != count:
            raise ValueError('Duplicate motion files: ' + name)
        for frame in frames:
            if not frame.get('complete_image_validated'):
                raise ValueError('Unvalidated motion image: ' + name)
            for key in ('helmet_rotation_deg', 'key_rotation_deg', 'camera_location_cm', 'camera_rotation_deg'):
                values = frame.get(key, [])
                if len(values) != 3 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in values):
                    raise ValueError('Missing motion transform: ' + key)
            if name=='shade_transition':
                values=frame.get('shade_occluder_location_cm',[])
                if len(values)!=3 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in values):
                    raise ValueError('Missing physical shade occluder transform')
            if frame.get('completion_engine_frame', -1) != frame.get('request_engine_frame', -3) + 1:
                raise ValueError('Screenshot not completed on next engine frame: ' + name)
            delta=frame.get('world_delta_seconds',0)
            if not isinstance(delta,(int,float)) or not math.isfinite(delta) or abs(delta - 1/fps) > 0.002:
                raise ValueError('Unexpected motion timestep: ' + name)
        if any(b['request_engine_frame'] != a['request_engine_frame'] + 1 for a,b in zip(frames, frames[1:])):
            raise ValueError('Noncontinuous rendered frame evidence: ' + name)
        results.append({'name': name, 'files': [c['file'] for c in frames], 'fps': fps,
                        'continuous': True, 'frame_count': count,
                        'evidence': 'Complete images, next-frame completion and consecutive engine request frames; playback review remains separate.'})
    return results


def validate_capture_receipt(folder, receipt, revision):
    """Bind a completed receipt to this exact evidence folder before packaging."""
    folder=Path(folder).resolve()
    if not receipt.get('completed') or receipt.get('revision')!=revision:
        raise ValueError('Capture receipt is incomplete or has another revision')
    captures=receipt.get('captures',[])
    if not captures:
        raise ValueError('No captured evidence')
    seen=set()
    for entry in captures:
        path=Path(entry['file'])
        path=(path if path.is_absolute() else folder/path).resolve()
        if not path.is_relative_to(folder) or path in seen:
            raise ValueError('Capture path escapes evidence or is duplicated')
        seen.add(path)
        validated=validate_png(path,(entry['width'],entry['height']))
        if not entry.get('complete_image_validated') or entry.get('sha256')!=validated['sha256']:
            raise ValueError('Capture is unvalidated or changed since capture')
    if seen != {p.resolve() for p in folder.rglob('*.png')}:
        raise ValueError('Evidence folder contains PNGs absent from the capture receipt')
    motion_names={c['motion'] for c in captures if 'motion' in c}
    requirements=receipt.get('motion_requirements',{})
    if motion_names!=set(requirements):
        raise ValueError('Motion requirements missing or inconsistent')
    validate_motion(captures,requirements)
