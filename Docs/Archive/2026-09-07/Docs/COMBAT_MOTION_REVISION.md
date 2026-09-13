> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../DEVELOPMENT.md) for active work.

# Arm deformation and motion revision — 6 September 2026

This revision responds to the supplied Unreal recording and supersedes the visual conclusions in COMBAT_MOTION_PASS.md. The earlier numerical checks did not establish acceptable deformation.

## Rig corrections

- Replace nearest-bone arm regions with longitudinal elbow/wrist blend bands. Keep torso vertices out of the arm regions and include the distal glove vertices; the previous height cutoff left fingertips following the torso.
- Keep armor link lengths and scale fixed. Clamp wrist reach before solving instead of stretching plate armor to reach a target.
- Resolve the elbow plane's mirrored normal ambiguity against the transported reference front. This removes the unwanted half-turn around the arm.
- Bind shoulder plates principally to the clavicles, with a transition to the upper-arm sleeve underneath.
- Calibrate the glove's palm frame against the handle. Pre-curl the source mitten geometry into a grip. This source still has no articulated finger skeleton.

The active meshes are SK_CombatKnight and SK_CombatArms. They share the existing skeleton and material. Tools/BuildCitadelArt.py exports the matching new FBX files; Tools/ImportCombatRig.py imports only these two meshes. Old Citadel meshes are retained because an existing editor session may still have them loaded.

## Animation and camera

The load reaches its pose before release and briefly holds tension. Increased pelvis/chest rotation and forward drive lead the cut. Recovery continues through the cutting plane before returning through a ready pose. Brace compression gives the torso movement a grounded response.

The camera is raised from collarbone height to eye height (82 cm above capsule center). An explicit 18 cm compensation preserves the standing weapon's world-space origin. Attack timestamps and the user's CombatDefaults settings are retained.

First-person shoulder placement and elbow poles are solved separately for camera composition. They are not required to duplicate the third-person pose. The hands still target the same handle, and both views retain the authoritative blade trajectory. These are procedural action curves and rig posing, not newly authored animation clips or a claim of Mordhau-equivalent quality.

## Review

Launch with `-CombatPlaytest -CombatPlaytestQuit -MotionReview -UseFixedTimeStep -FPS=30` to capture sequential frames under Saved/MotionReviewFrames. The review exercises 18 first-person/external air-swing and extreme-view scenarios; it records first-person horizontal and external horizontal, overhead, underhand and stab clips. Clear or archive previous frame output before capturing another run.

The delivered video uses those engine frames at 30 fps, without interpolating or slowing them down. Its limitations remain visible: the stylized armor is bulky and the glove has a baked grip rather than independently moving fingers.

## Validation and delivery

- UE 5.8 Development Editor build, module suffix 9067: passed.
- Latest engine automation: 3 passed, 0 failed, 0 warnings (13:36:17).
- Final rendered review: 18/18 passed. Maximum reported blade error 0 cm; arm link scale 1. These metrics supplement frame inspection and do not measure perceived power or surface quality.
- Native checks after action/camera changes: 562 combat, 46 movement, and 1,412,017 presentation checks passed.
- Preview: [revised-combat.mp4](../../../Visual/Captures/MotionRevision/revised-combat.mp4). Contact sheet and copied reports are in the same directory.

Restart the existing Unreal Editor session to load the new module and active meshes. Its already-loaded DLL is from the earlier pass; a fresh standalone validation process loaded this revision successfully.
