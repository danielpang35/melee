"""Small CF performance schema. Native Blender curves are editable authority."""
import json
import math

ADAPTER = 'cf-controls-v1'
CAMERA = 'MEL36_Defender_Perspective_v1'
CHARACTER = 'ArtSource/UserKnight/KN_v002/Knight_Animation.blend'
INPUTS = [
    'Tools/AnimationAuthoring/__init__.py',
    'Tools/AnimationAuthoring/performance.py',
    'Tools/AnimationAuthoring/rig.py',
    'Tools/AnimationAuthoring/bake.py',
    CHARACTER,
    'ArtSource/UserKnight/KN_v002/manifest.json',
    'ArtSource/AnimationLab/MEL36_reference/camera_setup.py',
    'ArtSource/AnimationLab/MEL36_reference/camera-spec.json',
    'ArtSource/AnimationLab/MEL36_reference/packet.json',
]


def validate_score(score):
    if score.get('adapter') != ADAPTER:
        raise ValueError('Expected cf-controls-v1 performance')
    fps, end = score.get('fps'), score.get('frame_end')
    if not isinstance(fps, int) or not 1 <= fps <= 120 or not isinstance(end, int) or end < 2:
        raise ValueError('Performance needs positive FPS and a complete frame range')
    for channel, keys in score.get('channels', {}).items():
        frames = [k[0] for k in keys]
        if len(keys) < 2 or frames[0] != 1 or frames[-1] != end or frames != sorted(set(frames)):
            raise ValueError(f'{channel}: keys must uniquely span the whole performance')
        if any(not isinstance(f, int) or not 1 <= f <= end for f in frames):
            raise ValueError(f'{channel}: invalid key frame')
        for _, value in keys:
            if len(value) != 3 or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in value):
                raise ValueError(f'{channel}: expected finite XYZ values')
    required = {'body', 'chest', 'clavicle.R', 'clavicle.L', 'primary_position', 'primary_orientation', 'elbow.R', 'elbow.L'}
    if set(score.get('channels', {})) != required:
        raise ValueError('Missing or unknown performance channels')
    for event in score.get('events', []):
        if not isinstance(event['frame'], int) or not 1 <= event['frame'] <= end:
            raise ValueError('Event outside source range')
    json.dumps(score, allow_nan=False)


def seed_score():
    # Sparse hand/arm posing assistance at authored keys only. No blade samples
    # are inputs; the saved FK curves, grasp frames and constraints stay editable.
    def keys(frames, values):
        return [[f, v] for f, v in zip(frames, values)]
    end = 97
    ready = [-.08, -.31, 1.24]
    ready_rot = [5, -16, -8]
    return dict(adapter=ADAPTER, revision='A_control_proof', fps=30, frame_end=end,
        hypothesis='Collected lateral load, outward hand launch, high opposite carry, absorbed return. Rough control proof only.',
        native_source_authority='TP_v001_RightHorizontal.blend; edit CF_CTRL pose channels/grasp empties. JSON is the reproducible initial blocking recipe.',
        reference='MEL36_reference/packet.json; neutral identity and supplementary B throwing gesture are separate sources; timing here is authored.',
        events=[dict(name=n, frame=f, confidence='authored', authority='descriptive only') for n, f in [
            ('ready',1),('preparation begins',9),('maximum load',31),('hand launch',36),
            ('rough passage',44),('maximum extension',47),('carry',57),('braking',65),('return',76),('ready restored',97)]],
        channels={
            'body': keys([1,9,29,41,59,76,end], [[0,0,-2],[0,0,-2],[0,0,-13],[0,0,7],[0,0,22],[0,0,7],[0,0,-2]]),
            'chest': keys([1,10,32,43,60,79,end], [[2,0,-3],[2,0,-3],[-3,-4,-24],[9,3,18],[4,3,30],[-1,0,8],[2,0,-3]]),
            'clavicle.R': keys([1,12,33,45,62,82,end], [[0,0,0],[0,0,0],[0,-7,-10],[0,12,14],[0,6,23],[0,0,5],[0,0,0]]),
            'clavicle.L': keys([1,11,30,43,58,80,end], [[0,0,0],[0,0,0],[0,5,-12],[0,-6,-32],[0,0,5],[0,0,2],[0,0,0]]),
            'primary_position': keys([1,9,25,32,37,44,49,58,68,80,end], [ready,ready,[-.27,-.23,1.32],[-.32,-.15,1.43],[-.32,-.26,1.48],[-.08,-.44,1.49],[.16,-.43,1.50],[.26,-.21,1.53],[.17,-.21,1.46],[.03,-.31,1.31],ready]),
            'primary_orientation': keys([1,9,27,34,39,46,52,61,71,84,end], [ready_rot,ready_rot,[66,-8,-65],[82,0,-86],[90,0,-60],[90,0,4],[94,0,55],[96,0,91],[70,4,72],[26,8,22],ready_rot]),
            'elbow.R': keys([1,9,32,44,59,79,end], [[-.4,.1,-.4],[-.4,.1,-.4],[-.55,.18,-.18],[-.4,.15,-.3],[-.18,.12,-.5],[-.3,.05,-.4],[-.4,.1,-.4]]),
            'elbow.L': keys([1,9,30,45,60,80,end], [[.45,0,-.4],[.45,0,-.4],[.35,.08,-.25],[.45,.05,-.35],[.55,.15,-.22],[.4,.05,-.35],[.45,0,-.4]]),
        })
