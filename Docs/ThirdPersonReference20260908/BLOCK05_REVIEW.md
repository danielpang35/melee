# Block05 — arm-driven swing and readable load

The revision follows the user's playback feedback: make the complete action read as a swing, exaggerate the windup, and use stylized deformation when it helps communicate intent and state. Physical realism and natural reach are not acceptance gates.

## What changed

- The low guard-like windup is replaced by a shoulder-level right-side chamber with the blade behind the character. At its apex the right elbow is bent and points down, as requested, before the arm opens into delivery.
- The hands establish a broader side-to-side arc and continue farther past the left torso before gathering into recovery. The carry uses deliberate animated right-arm stretch and compensating wrist scale to keep the hand shape stable. The source hilt at frame88 moves16cm farther left and8cm higher; the compact catch is delayed to frames94–100. These are authoring choices, not reference measurements.
- The grasp uses separate finger/thumb poses for the two mirrored hands, correcting the former open-loop appearance beside the handle.

Block04 is preserved under `ArtSource/CharacterReset/TP_v001/Baseline_Block04`. Source Block05 is frozen at SHA256 `87aed0c7e3fd62e98dc25b0394c6b09855c873c6449f7195ed125c74bae701b7`.

## Review boundary

The animation critic passed the more distinct chamber, downward bent elbow and corrected grasp in bounded source views. The wider carry shows leftward travel before return, but remains visibly flexed. The complete arm-driven swing-through must be judged in normal-speed playback; stills and transform checks cannot establish that artistic result. No further anatomy-driven pose sweep is planned.

The existing Mordhau Greatsword reference remains the benchmark. Training Sword horizontals remain supporting readability evidence; the trainer's overheads were not added to this one-action scope. Hidden feet and pelvis in the primary reference remain an authored interpretation.

## Source and runtime

The editable Blender source and pose controls remain under `ArtSource/CharacterReset/TP_v001`. The arm stretch is authored in the source, not reconstructed by runtime IK. Source-to-Unreal checking now includes the actual uniform animated scale and its carry peak, in addition to positions and rotations. This verifies preservation of the chosen deformation, not physical plausibility.

The dedicated TP clip retains the existing source clock and phase boundaries. Approved EX_v002 first-person assets, selection and gameplay remain preserved. TP visual and canonical contact alignment remain a separate unresolved adoption concern; no proposed canonical track is selected.

## Reproduce this iteration

Edit the TP source/controls, inspect only changed load/delivery/carry keys, and render normal-speed before/after. Export with `Tools/ExportThirdPersonSwing.py`, import with `Tools/ImportThirdPersonSwing.py`, then run `Tools/VerifyThirdPersonImport.py`. Capture using `Tools/RunThirdPersonProof.ps1` with a fresh take name and a verified baseline from the same build. A new source edit needs export/reimport; a C++ presentation change needs a new build/control. Preserve previous takes and source revisions.

## Completed media and verification

- [Block04 versus Block05 at normal speed](../../ArtSource/CharacterReset/TP_v001/Preview/TP_v001_Block04_vs_Block05_1x.mp4).
- [Historical v001 synchronized views, before foreground grip correction](../../Saved/TPProof/TP_Block05_v001_synchronized_views.mp4).
- [Stepped source preview](../../ArtSource/CharacterReset/TP_v001/Preview/TP_v001_Block05_stepped.mp4) and [final pose sheet](../../ArtSource/CharacterReset/TP_v001/Preview/Block05_final_keys.jpg).

Native revision `TP_v001-source-87aed0c7-FBX-83e776bb5d96` imported successfully. The all154-frame runtime source check passed (maximum head error0.000431083cm, rotation0.004708918°). The focused25-sample check includes carry88/94/100 and nearby subframes; it preserved the authored uniform scale ratios within0.000005201. This is pose/uniform-scale fidelity; shear and vertex-level skinning parity are outside the proof. Source/native receipts live in `Saved/TPProof`.

All three480-frame replays passed, with identical combat/control fields and two-hit/one-miss events versus `TP_baseline_fp_v001`. Ten pinned baseline files remain unchanged. Existing C++ consumer/build was reused. The reviewer found and closed selection-binding and take-preservation gaps in the reusable capture/packaging scripts before this replay.

The external blade still differs from the preserved canonical release by up to32.01cm at its base and38.91cm at its tip. The [separate diagnostic proposal](../../Saved/TPProof/proposed-canonical-Block05/TRADEOFF.md) preserves tested hit/miss outcomes and three-target order, but changes timing/contact locations; it is not selected. Readability remains the artistic target, while contact agreement remains an adoption concern.

## Foreground defender hand follow-up

The user clarified that the incorrect left hand belonged to the foreground defender. EX's provisional ready presentation now rolls the left wrist/finger subtree 180 degrees around the shaft before creating grip goals. The 0.10 s windup entry blend bridges this ready pose into the authored attack. This changes ready/entry presentation; EX and TP source assets, source clocks and canonical gameplay remain unchanged.

Build succeeded. Independent review of ready frame0008 and entry frames0012/0015/0018 found a clearer grip and no visible snap or detached wrist in those samples. Parent inspected the matching [defender frame0045](../../Saved/MEL15/TP_block05_defender_v002/frames/0045.png) against v001: the foreground left-hand orientation is changed and the attacker pose remains intact. Continuous artistic acceptance remains open.

All three fresh v002 captures passed 480-frame verification against `TP_baseline_fp_v002`, with identical control fields and two-hit/one-miss events. The fresh baseline also matched the prior build's control/events. [Current synchronized three-view replay](../../Saved/TPProof/TP_Block05_v002_synchronized_views.mp4), SHA256 `d32e1e769c436ef784adc0be436f7bc4ff8880fa5b8d4a924afe14b9b106b970`. Packaging verified matching selections/build and input hashes; parent decoded and inspected its frame at 0.75 s. Earlier v001 media is preserved. Full receipts are in `Saved/MEL15/TP_block05_*_v002/verification.json` and `Saved/TPProof/TP_Block05_v002_synchronized_views.json`.
