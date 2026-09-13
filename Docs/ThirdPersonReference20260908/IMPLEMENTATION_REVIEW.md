# TP implementation review — 2026-09-08

Block05 diagnostic-driver review (parent): inspected `Tools/CompareThirdPersonCanonical.py`. It binds the frozen source/export and preserved EX/core identities, derives a separate unselected track, reuses a pinned harness, requires exact reproduction of the original baseline event corpus, and preserves old outputs. No actionable finding in this bounded read-only review. Runtime/visual adoption is outside its scope.

Scope: independent focused code inspection of TPCombatPresentation, the TP integration in KnightPresentation/EXCombatPresentation, EXGameplayCapture, CaptureThirdPersonProof.ps1 and VerifyThirdPersonProof.py. Read user authority once. No duplicate build, test run, or visual/art review performed.

## Actionable findings

1. P2 — First-person proof cannot pass its advertised verifier. `Tools/VerifyThirdPersonProof.py:34` applies authored-output requirements to every nonbaseline launch, but `Source/MeleeCombatLab/Visual/KnightPresentation.cpp:172` deliberately excludes first-person TP sampling (and MeleeCharacter skips Knight Present for an active EX first-person view). Starting CaptureThirdPersonProof.ps1 with `-View firstperson` and a valid TP selection therefore produces no `tp_authored` rows and fails “No unblended authored output”. Make verification view-aware: first-person should verify accepted FP output and absence of TP visibility; external/defender should verify TP output.

2. P2 — Authored-output proof does not establish visible output or complete release coverage. `Tools/VerifyThirdPersonProof.py:36-41` only checks a nonempty subset selected by tp_authored and tp_blend and never requires tp_active, nor requires every release row of each attack to be selected. A hidden TP component or one missing most release frames can therefore pass the numeric proof. Require selected/active/authored at all expected external release samples for each serial, expected source clock, and full-weight commit checks on that set. Keep canonical endpoint deltas diagnostic as currently intended.

## Inspected properties

- Simulation is passed const into TP presentation; TP components disable collision and overlap generation. The visible TP weapon is separate from canonical simulation weapon data.
- Sampling uses State.exSourceTime, with .30 ready pose, and release disables the cosmetic transition.
- Reload validates all 154 source/native samples, unit weapon scale/quaternion, blade marker positions, native duration, material presence, and fallback hierarchy before replacing live sampler/output. Failed validation destroys a candidate sampler and retains prior selection.
- No gameplay implementation changes were reviewed or made. Accepted EX assets/config integrity is a parent verification responsibility.
- Native-vs-canonical divergence remains diagnostics; this review does not certify contact-order or art acceptance.

## Deferred

ExportThirdPersonSwing.py and ImportThirdPersonSwing.py were absent at inspection. Review these when available, including source/weapon binding consistency, faithful native import settings, and selection publication only after successful validation.

## Focused resolution check
First-person gate now checks TP inactivity; baseline checks no TP selection/output; external/defender require active authored coverage for all expected attack samples. Reported hidden-output and first-person failure scenarios resolved. Remaining refinement requested: require tp_blend > .999999 on every expected RELEASE sample so release fidelity cannot evade checks through the blend-filtered subset. Import/export still pending. No duplicate tests/builds.

## Export/import review and current status

Initial findings 1 and 2 are resolved, including an explicit full-weight gate for every release sample (`VerifyThirdPersonProof.py:38`). No duplicate tests or builds were run.

Reviewed ExportThirdPersonSwing.py and ImportThirdPersonSwing.py. Export snapshots 154 source frames, records diagnostic subframes, hashes outputs, checks source/baseline preservation, and gates its manifest on a Blender FBX roundtrip. Import verifies file/source hashes, uses separate TP skeleton/assets, imports at 60 Hz with explicit transform/compression settings, and publishes copied motion metadata. Import receipts explicitly leave the full source/native fidelity gate pending runtime. Dedicated weapon mesh refresh occurs outside the component-creation branch, so reload changes its geometry correctly.

Open P2: `Tools/ImportThirdPersonSwing.py:34` identifies a revision solely by exported file bytes, and line 39 skips skeletal import when its mesh exists. An importer settings repair with unchanged exports therefore silently reuses the old native mesh/animation. Exporter-only metadata changes can instead collide with the immutable manifest check at line 155. Include the importer/profile fingerprint and relevant complete manifest in the identity so changed import pipelines receive a fresh destination. A failed partial import leaving a mesh but no animation also cannot recover via a straight retry under the current mesh-only existence predicate; require complete assets before reuse or use a fresh revision for recovery.

Native weapon geometry/source appearance and canonical-contact discrepancy remain parent/art workstreams; this code review does not certify them.

## Final focused code-review status

Revision invalidation P2 resolved: ImportThirdPersonSwing.py now includes importer SHA, explicit import profile, and complete manifest SHA in the destination identity and import receipt. Initial verifier findings and release blend refinement remain resolved.

Remaining recovery limitation (P2, not a successful-capture correctness blocker): line 41 still decides reuse solely from mesh existence. If an interrupted/failed import saves TPBody but no animation, every unchanged retry skips skeletal import and later fails the animation-count assertion. No invalid selection is published. Complete-revision detection and a fresh attempt destination, or explicit supported recovery, would close this limitation.

Independent code inspection is complete. Parent reports two successful builds (315.35 s and 57.76 s); this reviewer did not rerun or independently observe those builds. Final source/art/native proof remains parent-owned and outside this code review.

## Import verifier and recovery resolution

Focused read-only resolution check, 2026-09-08: `VerifyThirdPersonImport.py:8` now binds native mesh/animation and source hash to the selected revision. Its coverage gate requires exactly16 unique times (seven phase keys and nine source diagnostic subframes), checks native transform dimensions/finiteness, and selects t0 explicitly. Both reported verifier gaps are closed; the quaternion reflection and relative-rotation math remain correct.

The partial-import recovery P2 above is closed. ImportThirdPersonSwing.py checks for a compatible mesh plus exactly one 2.55 s sequence before reuse. Incomplete native imports are preserved, and a fresh `_retryNN` destination is selected within a20-attempt bound. The attempt receipt is written before import; the final receipt identifies the chosen destination and preserved failures. No invalid selection is published through that recovery path.

Parent reports successful selection `dfcffc2bfc14`: independent key/subframe position error0.00032952 cm and rotation error0.0003465°; runtime all154-frame position error0.00049287 cm and rotation error0.00069463°. These results were supplied by the parent and were not rerun for this resolution check. No tests, builds or engine processes were launched. Artistic acceptance, vertex-level deformation parity and canonical-contact agreement remain separate from these source/native pose checks.

## Sequential runner / packaging resolution

Focused read-only resolution check, 2026-09-08: all three reported P2 findings are closed. RunThirdPersonProof.ps1 requires an actual baseline control, compares the complete FP selection with that control, pins FP/TP selection hashes across each sequential capture, and checks launch identity before verification. PackageThirdPersonProof.py requires matching complete FP/TP selections, TP selection hashes, module identity and comparison baseline tags, and rehashes all input videos against their verified receipts before encoding. Packaged filenames now include revision and take; existing MP4/receipt files are refused and ffmpeg uses `-n`.

Capture → process completion → verifier → packaging sequencing remains correct. This check inspected only the reported resolutions; no tests, builds or engine processes were run.

## Foreground ready-hand correction, 8 September 2026

User identified the foreground defender's left hand. The lower-effort reviewer traced it to EX's provisional ready presentation. Parent corrected the patch to rotate fresh weapon-relative left wrist/descendant targets before blending and constructing HandGoals; a later ReadyPose-only rotation would have been overwritten. Independent focused review confirmed the shaft axis/pivot, goal order and authored-target boundary. A 0.10 s windup entry blend bridges the changed ready grip; source time and release/contact paths stay unchanged.

Incremental build passed in 38.65 s. Fresh baseline `TP_baseline_fp_v002` matched the earlier control fields and two-hit/one-miss events. All ten preserved files and frozen TP source hash still match. Independent visual sampling compared ready frame0008 before/after and new entry frames0012/0015/0018: grip direction reads more clearly, without a visible wrist pop or detached grip in those samples. This is not continuous artistic acceptance. Fresh three-view take v002 results are recorded in `BLOCK05_REVIEW.md` after capture completion.
