> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../DEVELOPMENT.md) for active work.

# Hand anatomy correction — 6 September 2026

The user rejected the hands in `HANDS_AND_LEAN.md`: they were upside down and did not resemble human hands. That rejection supersedes the earlier visual-completion claim. The original technical tests remain valid for their stated contracts.

## Reference and diagnosis

Reference: `D:/Mordhau Montage VI.mp4`, inspected at 0.30 s for the resting first-person grip and 164.30 s for the exposed gloved two-hand grip during a raised cut. Extracted source frames are under `Saved/HandAnatomy/`.

Three separate defects contributed to the appearance:

1. The DCC and runtime grip frames agreed with each other, but mirrored anatomical handedness. The upper grip pointed the knuckles back at the player. Both cross-product signs were changed together, accounting for the Blender-to-Unreal handedness conversion.
2. The thumb originated on the little-finger side. It now originates at the index side toward the guard and opposes the fingers on the proximal side of the shaft.
3. Four identical 260-degree finger loops made roughly 14 cm centerlines. The new fingers have distinct lengths, tapered phalanges, knuckle fullness and rounded tips; the back of the hand is a lofted metacarpal surface. The thumb follows the outside of the shaft. An intermediate Bezier thumb crossed the shaft and was cut into stumps by the fitting boolean; that version was rejected during close visual inspection.

## Delivered implementation

- `Tools/BuildCitadelArt.py`: anatomical mirrored grip frames; joined wrist/palm/fingers/thumb; rounded palm termination; index/middle/ring/little centerline arcs of 149/160/153/133 degrees, with radii 33/34/33/31 mm; a continuous opposed thumb; 24 mm fitted handle cavity.
- `Source/MeleeCombatLab/Visual/KnightPresentation.cpp`: matching rest-grip cross-product signs. Palm contact calibration and the authoritative weapon trajectory remain unchanged.
- Regenerated `SK_CombatKnight.fbx`, `SK_CombatArms.fbx`, `CitadelKnight_Rig.blend`, and imported both `/Game/Visual/Citadel/Meshes/SK_Combat*` assets.
- Each source glove is one closed connected surface: 16,845 right / 16,849 left vertices. Only boolean crumbs with at most 16 vertices and diameter below 0.5 mm are discarded; larger disconnected geometry fails generation.

## Validation and remaining limitation

The corrected neutral render has the right thumb facing the player, fingers closing around the far side of the handle, and wrists entering from behind. The neutral skinned wrist-axis proxy is 27.83 degrees; it is supporting evidence, not an anatomical acceptance test.

Native presentation checks passed 1,413,854 checks with AddressSanitizer before the camera-clearance experiment; the final native presentation functions and tests retain that implementation. The experiment is excluded from the delivered code.

**Remaining extreme-pitch issue:** at +85-degree aim during a raised attack, the hand is roughly 6 cm ahead of the eye and the forearm enters the camera. The hands themselves remain ahead of the 2 cm near plane. Forcing only the elbow forward produced an 88-degree wrist-axis proxy and an inferior wrist pose, so that experiment was removed. Resolving this needs coordinated hand/hilt travel and arm posing, to be addressed with MEL-15. It is not acceptable to claim all camera clipping or broader swing biomechanics are solved by this hand correction.

Rear shoulder coverage remains deferred under MEL-14. Existing hip lean, gameplay collision, timing, contact centers, and concurrent audio work are preserved. Work remains local and uncommitted in the shared checkout.

## Final evidence

- Final Unreal build succeeded (`Saved/HandAnatomy/build-release.log`). Final rig import completed without logged errors or warnings (`Saved/Logs/HandAnatomyImportFinal.log`).
- Final neutral and 18 moving scenarios: `Saved/ArmRepair/HandAnatomyFinalNeutral` and `HandAnatomyFinalMotion`. All 18 technical scenario checks passed; the selected continuous capture contains 333 frames at 30 fps. First-person, external and extreme-pitch pose sheets were visually inspected.
- The full skinned audit immediately before the final thumb-base volume adjustment is under `Saved/ArmRepair/HandAnatomyRelease`: 72 captures / 144 arm samples, zero open arm boundary edges, maximum rigid-fit error 0.000022 cm. Wrist-axis maximum is **80.332 degrees**, at `40_air_fp_upper_left_pose_1`, left hand. This remaining pose defect is supplied to MEL-15; a numerical pass does not make it acceptable anatomy. The final thumb-base adjustment does not change bone poses; the final neutral also has fresh skinned samples.
- `Saved/HandAnatomy/AutomationFinal` records the final imported rig's Citadel asset-contract test. Earlier full gameplay/lean results remain in `HANDS_AND_LEAN.md`; they were not rerun or represented as new hand-appearance tests.

Review: [before/after](../../../Visual/Captures/HandAnatomy/before-after.jpg), [neutral](../../../Visual/Captures/HandAnatomy/neutral.png), [first-person poses](../../../Visual/Captures/HandAnatomy/first-person-poses.jpg), [external poses](../../../Visual/Captures/HandAnatomy/external-poses.jpg), [pitch poses](../../../Visual/Captures/HandAnatomy/pitch-poses.jpg), [selected motion](../../../Visual/Captures/HandAnatomy/selected-motion.mp4), [reference at 164.30 s](../../../Visual/Captures/HandAnatomy/reference-16430.png), [checkpoint hashes](../../../Visual/Captures/HandAnatomy/checkpoint.json).

## Next task

The user requested a new GPT-6 Astra / High task after the hand correction, to start work from Linear. MEL-15 is the next relevant unstarted issue: third-person swing biomechanics and overhead hand follow-through. Its new baseline must preserve the corrected handedness and thumb topology and include the known first-person wrist/clearance defects above. MEL-7 audio work is active elsewhere; MEL-14 rear shoulder coverage remains deferred. Do not equate the technical hand-correction checks with user acceptance of the broader animation.

A GPT-6 Astra / High project task was created for MEL-15 (initial queued setup ID `client-new-thread:702c888f-1215-4354-9624-c1112f7952af`). Automatic approval review rejected both attempted Linear status comments as insufficiently authorized disclosure of internal implementation details, paths and defects. Neither comment was posted. Reviewable shorter drafts are in `HAND_LINEAR_UPDATE_DRAFT.md`; user approval was requested. The new task was explicitly told to keep this rejected handoff payload local rather than post it indirectly.
