# Project audit and next implementation

> **Dated record; active assignments and status superseded (12 September 2026).** Preserve the technical/design history below. [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) owns current source, selection, pilot outcome and resume; [DEVELOPMENT](DEVELOPMENT.md) owns operational scope. Step 4 (parry/riposte, branch integration, full-exchange packaging and expansion) is deferred. [Documentation ownership](DOCUMENTATION_OWNERSHIP.md) and [audit](DOCUMENTATION_AUDIT.md) define current authority. Linear owns live execution.

9 September update: the [new animation architecture audit](MORDHAU_ANIMATION_ARCHITECTURE_PLAN.md) supersedes the TP selections and continuation/refinement instructions below. No TP candidate is currently selected or accepted. [Linear planning checkpoint](LINEAR_ANIMATION_PLAN_CHECKPOINT.md) records the replacement bounded queue and cleanup; start with MEL-36 reference packet, then MEL-37 editable-control proof. The following 8 September reconciliation is historical evidence, not current Linear status.

8 September 2026. Policy MCL-DEV-2026-09-08. Audit of repository rules, checkpoints, selectors, relevant runtime paths, Git state and live Linear/Notion guidance. No fresh gameplay, visual acceptance or full code review is claimed. Existing receipts establish only their recorded revisions. This is the audit checkpoint; DEVELOPMENT owns priorities and THIRD_PERSON_CHECKPOINT owns moving candidate identity.

## Assessment

The project has a working combat lab and an authoring/integration route. The critical gap is a convincing complete exchange, especially external threat readability and branch presentation. A new pipeline, anatomy reset or broad art production would postpone that decision.

| Area | Established evidence | Remaining gap |
|---|---|---|
| FP | EX_v002 source/native playback accepted; Config/EXPreview.json selects the recorded revision | Whole-exchange feel and provisional defensive/alternate poses remain open |
| Simulation | Existing C++ state/contact authority and delivered EX integration; prior focused tests in MEL15 handoff | No fresh test pass inferred for this dirty checkout; preserve recorded SwingOnly and retired PresentationOnly failures |
| TP | Batch manifest selects D_open_sweep by agent frame inspection; runtime selector still selects Block13 Attempt C | D still has forward/stab impression; reported source discrepancy 17.72 cm and Block13 engine discrepancy 22.60 cm are different measurements, not a comparable improvement score |
| Branches | TPCombatPresentation::Present uses native authored motion for exActive states and falls back outside those states | Native neutral success does not supply authored parry/riposte/interruption performances |
| Workflow | AnimationLab isolates candidates; benchmark records source/config/module identity | Preserve cheap iteration; preparation receipt does not prove the engine loaded that module |
| Character/art | CF foundation exists; USP_v016 material/motion accepted in isolated proof | Full armored deformation, gameplay composition and performance remain unproven; retain accepted proof |
| Audio | CombatAudio loads named assets under /Game/Visual/CombatAudio | Source palette/audition does not establish loaded bank identity or in-play mix acceptance |
| Delivery | Numerous source/config/content/tools/docs files are untracked; TP selection references Saved/TPProof motion JSON | A Git checkout alone cannot currently reproduce the delivered state; build/packaging support is narrower than a shipped build |

## Conflicts resolved in this audit

Marked the old project stocktake, character reset, MEL6 export checkpoint, MEL15 implementation prompt and pullback-elbow handoff as historical. Scoped MEL15's FP-only/TP-deferred language to its original delivery. These records retain source history and evidence but no longer present themselves as current ordering. No historical assertions, sources or unique evidence were deleted.

Current priority remains one playable exchange. The visual rubric and movement inventory describe later completeness and quality targets, not mandatory per-draft proof sweeps. Material acceptance does not imply whole-game art acceptance; FP acceptance does not imply TP or gameplay acceptance. D is an isolated provisional selection, not the installed engine candidate. Live Linear/Notion were subsequently reconciled at the user's request; old remote snapshots remain historical.

## Linear and Notion reconciliation

Updated 23 existing open Linear issues and created only two missing bounded tasks: MEL-34 TP motion selection and MEL-35 reproducible delivery. Current source umbrella is MEL-6; execution is MEL-34 → MEL-27 branch source → MEL-15 selected integration → MEL-35 delivery → MEL-11 human decision. MEL-15 may perform its TP stage after MEL-34, but finishes after branch delivery. Removed the obsolete MEL-25 blocker and duplicate parent/export dependencies; verified the live critical chain has no cycle.

MEL-26 staging, MEL-29 historical technical review, MEL-28 accepted native export handoff and MEL-17 reference/Unreal proof are Done at their explicit delivered scopes. No new human acceptance was invented. MEL-25 foundation review stays In Review without blocking motion; MEL-33 stays user-paused in Backlog. Other expansion/production tasks remain downstream. Existing assignees and historical closed/consolidated tasks were preserved. The project and existing milestone now describe a convincing and reproducible playable exchange.

Aligned 11 Notion pages: home, vision, current development, milestone, execution navigation, animation, swing model, playtesting, accepted decisions, visual direction and art implementation brief. Preserved child pages and the approved reference image. Recorded accepted Clay_v005 geometry and USP_v016 material/motion without asserting finished-character/gameplay acceptance. Replaced obsolete reset, export-pending, helmet-rebuild and per-render critic-loop instructions. Linear remains the only execution backlog.

Before-state and final receipts: Saved/ProjectAudit20260908/remote-before.json and remote-after.json. Exact-match edits encountered two stale remote sections; refreshed those pages and applied the reconciled changes successfully. Final readback confirmed critical task relations, milestone and updated Notion structure. No remote messages/comments, gameplay code or asset changes were made.

## Sequential implementation packages

### 1. Finish the right-horizontal motion decision

Owner: one animation owner. Inputs: existing C/D comparison and compact batch, preserving accepted EX source/config and production TP. Inspect the whole action at source speed; use the disputed forward interval to identify choreography, not to optimize elbow numbers alone. One remaining bounded refinement may change hand/blade sweep and torso sequencing. If that does not improve the action, generate 3–6 different complete choreographies. Retain the selected editable controls, preview and short reason. Follow the existing two-pass limit and conditional specialist brief if two coherent batches expose a persistent limitation.

Deliverable: readable load, sweep, carry and return with connected grips. Agent selection permits progress; human acceptance stays separately recorded. No export/build for drafts.

### 2. Resolve selected TP threat/contact agreement

Paths: selected source, ExportThirdPersonSwing.py, ImportThirdPersonSwing.py and TPCombatPresentation.cpp only if integration requires it. Export/import the winner through the existing route under a new identity; preserve Block13 recovery data. Inspect one affected external engine view against canonical blade/contact during damaging release. Existing BladeBaseErrorCm/BladeTipErrorCm diagnostics help locate disagreement but do not certify readability.

Default implementation: author TP hands/body/weapon to communicate the existing canonical threat, retaining FP and C++ timing/contact. If convincing motion requires a materially different damaging path, record that explicit integration decision before changing EXWeaponMotion/CombatSimulation and both view bindings. Do not silently change collision or add a runtime compensation stack. Selected integration needs visible hit/miss agreement, not an invented universal centimetre threshold.

### 3. Complete ready → parry → right riposte → carry → ready

Inspect AttackStateMachine, CombatSimulation, EXCombatPresentation and TPCombatPresentation bindings to enumerate the exact branch states that currently use fallback. Author only the missing exchange performances, using the same batch method per action. Preserve neutral EX. Bind selected clips to existing C++ phase/serial/source time; use existing entry/return blending and package loaders before extending their schema. If the current selector cannot represent a required branch, add the smallest explicit action/phase binding, with atomic validation and fallback on invalid selection; do not build a general animation framework first.

Evidence: short actual exchange including successful parry/riposte, range miss, flinch/interruption and moving aim/footwork. Check legal inputs and contact ordering only where contracts change. Build changed C++; run affected EX/core tests and one independent review for consequential state/contact changes. Keep attack playback rate unchanged for accels/drags. Sound/camera/body response should communicate the same resolved event; inspect existing event routing before changing it.

### 4. Make the selected slice reproducible

Inventory selected Source/Config/Content dependencies and editable authoring inputs, preserving unrelated dirty work. Move or copy required TP motion data out of ignored Saved into a durable selected-artifact location and deliberately update its selector. Preserve original recovery evidence. Record actual source/package/config/module identities and loaded audio bank; distinguish user tuning overrides. Prepare a scoped Git/LFS or artifact-storage delivery set appropriate to the existing repository, then verify its required paths from a clean staging copy. Do not stage all dirty work, delete history, or assume ignored backups are delivery assets. This package is required before calling the slice reproducible; it need not block isolated drafts.

### 5. Expand after the exchange decision

First opposite horizontal and overhead, then remaining strike/stab and branch vocabulary. Add locomotion start/stop/strafe/turn and ground response where the playable slice exposes deficiencies. Apply the accepted steel treatment to production surfaces only after motion/deformation establishes their needs. Player HUD readability and synchronized feedback precede environment expansion. Define actual hardware/resolution before measuring the 100–144 FPS target. Networking and broad product systems remain deferred.

## Verification of this audit

Read relevant local authorities once; inspected selection manifests, TP native/fallback logic, FP loader reference, audio asset route and Git tracking. Other recently listed project tasks were idle/not loaded; no shared runtime/source edits were made. Changes are documentation only; validate changed links/content and whitespace, with no engine launch, render, import or build. No measured model token breakdown is available.

Next executable assignment: package 1, followed by package 2 only for a selected convincing motion. Packages 3–4 complete the playable milestone; package 5 is the subsequent backlog. All assignments carry the absolute canonical AGENTS.md path and preserve the approved FP baseline.
