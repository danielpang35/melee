# EX_v002 first-person gameplay integration

> Delivered integration evidence. First-person-only priority and third-person deferral below describe the delivery scope at that time. [Current development](DEVELOPMENT.md) now prioritizes TP motion and the complete exchange; historical verification applies only to the recorded revisions.

Delivery checkout: `D:/Projects/swingmanipulation-recovered-20260911`.

Current priority is first-person animation. Third-person animation design is explicitly deferred; the fresh CF external body is a provisional gameplay placeholder. Technical integration does not claim human gameplay/phase-mapping acceptance or full MEL-15/MEL-11 completion. Notion design, applicable AGENTS.md instructions and current MEL-15/MEL-6 state were reviewed. Accepted export/reload receipts resolve stale implementation statements. No remote comments or status changes were posted.

## Delivered behavior

- Normal CombatLabGameMode and AMeleeCharacter select EX through `Config/EXPreview.json`. Movement, aim, repeated cuts and existing combat input work in the usual checkout. One CombatSimulation accumulator drives state, source sampling and contact; presentation consumes that clock.
- Ordinary neutral right horizontal skips the first .30 s and plays at 1x through 2.55 s. Candidate windup ends at 62/60 s, release at 80/60 s; full-release damage awaits gameplay review. Spatial manipulation changes contact without playback acceleration or legacy reach correction.
- Each outgoing release/damage span resolves before its boundary transition, miss cost or queued attack. Native shortest-path normalized FastLerp, rig quaternion endpoints, actual 103.5 cm blade length and sampled camera transforms preserve render/contact agreement, including subframes.
- Ready/swing/recovery/ready repeat without reset. A .18 s cosmetic return and conditional .10 s entry bridge preserve legal input timing. Alternate directions, stabs, combo, morph and riposte explicitly retain their existing motion/timing with provisional fresh-rig poses. For unbound states, upper-body pose blends in sampled camera space and imported split arm chains fit the retained canonical hand goals. This removes the parry shoulder crossing the camera; the approved authored neutral path remains unchanged. These are candidate bindings, not finished authored branch clips.
- The old character renderer is retired. Eight old mesh/skeleton/sword packages were moved outside game Content into `Saved/MEL15/production-backup/retired-character`, with original paths and verified hashes in `production/retired-character.json`. They cannot be loaded by normal gameplay or included by the broad Visual cook rule. Historical source/import tools remain recoverable.
- The CF placeholder uses its independent 102-bone source plus the FBX armature root and two eye nodes. Only wrist/finger binding transfers from EX; approved FP upper-arm deformation is never displayed externally. Its source surface, including shorts, is persisted with Unreal's native material setter. Viewing another character uses that character's first-person camera/visibility, avoiding self-head occlusion.

## Selected artifacts and recovery

Approved revision: `EX_v002-source-1615b76b-FBX-6a34514c-native-unreduced-v1`.

Source SHA-256: `1615b76b69fe19dab8973ef7a4cea6ebf6589fe5c05fc4674a089a2230b1c49e`.
Animation package SHA-256: `c82d1a287a3e70fb7062188dc627b97f1ff3be16709b868b0f519f40835025ab`.
Approved source, grip/deformation, projection and native unreduced animation were preserved. CF source SHA-256: `bb7e8914325caecd99243d89ea5e7a083ae64571b4bd75da37cd9d316ad8acd9`.

`Saved/MEL15/production/delivery-artifact.json` records the current DLL and selected mesh, skeleton, animation, weapon and material hashes. `production-backup/manifest.json`, copied-asset receipts and `production/changed-files.json` identify recoverable originals and changes. Both inherited dirty trees were preserved without a Git reset or wholesale copy.

## Verification and limitations

- Delivery build passes: `production/build-fp-binding.log`, Development Editor, 187.88 s. This verifies the normal Editor `-game` route, not packaging. Build preflight detects loaded suffixed and unsuffixed gameplay DLLs, identifies owning processes and asks users to save/close the matching session; it never auto-kills sessions or retries an unchanged lock.
- Core suite: 917 checks pass. Focused EX suite passes at 30/60/144 Hz: repeated hits, moving aim, miss, exact entry, final-release/wall ordering, partial damage boundaries, parry/riposte, FTP, morph and alternating/slower combo fallback. Contact is .841666667 s with fixture eye (0,0,168); the prior .8375 s trial used eye (11.5,0,168).
- Fresh Unreal asset contract passes (`production/fresh-assets-final/index.json`). It checks real native bone counts, independent skeletons, finite reference transforms/surface, materials, 180 cm body scale and 103.5 cm blade. Assets are unchanged by the final candidate articulation fix; the runtime loader also validates both imported arm chains before publishing a selection.
- Original SwingOnly and PresentationOnly assertions remain unchanged except diagnostic output. Both failures reproduce against the untouched pre-integration backup (`production/baseline`). SwingOnly's other-direction fallback still contacts at 1.0291667 s versus 1.0125 s expected. The old solveGripArm swivel test still reports 57.0038 degrees at pitch 85/recovery frame 332; that presentation path is retired from gameplay. Neither assertion was weakened.
- Independent review closed clock-boundary, transition metadata, ordinary-entry, atomic loader and sampled-camera findings. The fresh binding and final camera-space candidate implementation also received bounded review. Defensive and alternate-attack FP poses still need artistic review; third-person design is deferred.
- Same-process newly named animation-package reload passes on the final DLL with approved selection restored and no recompilation (`EX_fp_reload/reload-verification.json`). This is selection/replay of a new package, not in-place reimport.

Primary first-person review: `Saved/MEL15/EX_fp_review.mp4`, 14 seconds at unretimed 60 fps, SHA-256 `a29b13ebca29e5cd92159809ebd66512b7729a0a6bc4593eccd90194fbde262a`. It passes repeated hits, moving aim/footwork, range miss, FTP, successful parry/riposte and flinch. Peak blade error is 0.000000995 cm, authored pose error 0.000053034 cm, and candidate wrist/shoulder-anchor error 0.000004107 cm. Candidate arm reach scale peaks at 1.10004491 (about 10% cosmetic stretch), a remaining artistic limitation. Entry, held parry, return and riposte frames were inspected; human continuous-playback/feel acceptance remains open.

`EX_fp_review/verification.json` is the final capture receipt. Earlier recordings are superseded as the primary review. The prior synchronized three-view comparison remains under `production/review-verification.json`; final FP combat events match it exactly (`production/firstperson-comparison.json`). That is supporting evidence, not a request for third-person design or acceptance.

## Build and play

```powershell
Set-Location 'D:/Projects/swingmanipulation-recovered-20260911'
& .\Tools\Build.ps1 -MaxParallelActions 2
& .\Tools\PlayGameplay.ps1
```

WASD move; mouse aim; LMB directional cut; 1 explicit right horizontal; RMB parry/FTP; Q feint; E stab; R reset; F2 opponent pattern; F5 external inspection. Normal gameplay reads EXPreview.json; RC_v008 and `-LegacyCombat` cannot restore the old character renderer.
