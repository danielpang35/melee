"""Historical weapon-led TP score contract. Not an exploration-wide clock."""
import json
import math


def validate_score(score):
    beats = score.get('beats', [])
    frames = [b.get('f') for b in beats]
    if score.get('fps') != 60 or len(beats) < 4 or frames[0] != 1 or frames[-1] != 154:
        raise ValueError('This adapter expects the current 154-frame, 60 Hz TP score')
    if any(not isinstance(f, int) for f in frames) or frames != sorted(set(frames)):
        raise ValueError('Beat frames must be unique and increasing')
    for beat in beats:
        for key, size in [('h', 3), ('d', 3), ('p', 3), ('er', 3), ('el', 3), ('sr', 2), ('feet', 2)]:
            value = beat.get(key)
            if not isinstance(value, (list, tuple)) or len(value) != size or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in value):
                raise ValueError(f'Invalid {key} at frame {beat.get("f")}')
        if sum(x*x for x in beat['d']) < 1e-10:
            raise ValueError('Blade direction cannot be zero')
    json.dumps(score, allow_nan=False)
