# External audit disposition

> Dated evidence and assignments below are superseded for current execution by [DEVELOPMENT](DEVELOPMENT.md) and the [TP checkpoint](THIRD_PERSON_CHECKPOINT.md). See [documentation ownership](DOCUMENTATION_OWNERSHIP.md). Historical timing, candidate and issue status are not live values or authorization to resume deferred work.

9 September 2026 (EDT). Policy MCL-DEV-2026-09-08. Reviewed the supplied audit against checkout `dde6bcabcf6ec029bdd4ecc52927c8a9bd041f43` plus existing dirty documentation. This is the compact workstream checkpoint; Linear owns execution status. Source audit and tuning snapshots are preserved in `Saved/ExternalAudit20260909/` for this local review.

## Confirmed result

`ACombatLabGameMode::LoadTuning` still overlays built-in values, project JSON, then Saved JSON. Its success status does not identify the actual sources. `Tools/PlayBenchmark.ps1` already copies and hashes both files, but those preparation snapshots do not lock or prove engine-loaded tuning. README now explains precedence, clamping, reset semantics and this limitation.

The current C: Saved file is readable. Its differences from project JSON are:

| Field | Project | Saved |
|---|---:|---:|
| StrikeWindup | 0.575 | 0.65 |
| BladeLength | 110 | 130 |
| BladeRadius | 4 | 3 |

Project SHA256: `4ee4ee7ccd4c9e7382ee66fdc7f62066b4da0499d3e16c90639c325174abbc4d`.
Saved SHA256: `e2529b291b3d7ea69f494c4ac4de0faf5ae925ab891dcc6938d329bb3588d6e6`.
These are file comparisons, not a fresh play-session measurement or recovered D: tuning. Neither file was changed.

## Disposition by recommendation

| Audit recommendation | Decision and execution |
|---|---|
| Preserve simulation authority, deterministic state/contact and read-only presentation | Retained. No gameplay or runtime edits. |
| Reconcile tuning documentation | Implemented in README. Current JSON windup is 0.575, so the audit's claim that checked-in windup is 0.65 is stale. |
| Expose tuning source/version; deterministic benchmark mode | Explicitly deferred to new [MEL-41](https://linear.app/meleeslasher/issue/MEL-41), High. Requires a bounded loader change, build and affected checks; no silent change to saved settings. Existing delivery [MEL-35](https://linear.app/meleeslasher/issue/MEL-35) now references it. |
| Diagnose D:; recover and compare old tuning | Explicitly deferred to new [MEL-43](https://linear.app/meleeslasher/issue/MEL-43). Historical symptoms lack a current device diagnosis and exact old project path. C: authoring can continue. No storage/repair probe was run here. |
| Reproduce double-parry and four rendered failures | Explicitly deferred to new [MEL-42](https://linear.app/meleeslasher/issue/MEL-42), High. The 557-check/34-of-38 evidence is archived. Later [MEL15 handoff](MEL15_PRODUCTION_HANDOFF.md) records 917 core passes and preserved SwingOnly late-contact and retired PresentationOnly swivel failures. Neither receipt proves this checkout passes now. Classify each old case before changing behavior or fixtures. |
| Remove all limb stretching; introduce hierarchical fixed-length IK | Blanket prescription rejected as superseded by current policy permitting intentional deformation and authored complete performances. Demonstrated collapse, grip discontinuity and elbow defects remain deferred to existing [MEL-25](https://linear.app/meleeslasher/issue/MEL-25), whose scope was updated. New solver work needs a demonstrated limitation, not the historical clip alone. |
| Split FP/TP cosmetic presentation | Separate authored EX/TP implementations already exist. A new generic profile rewrite is not justified by the old shared-pose description. Selected compatibility/readability work stays deferred to [MEL-39](https://linear.app/meleeslasher/issue/MEL-39), updated with this disposition, then [MEL-40](https://linear.app/meleeslasher/issue/MEL-40) native review. |
| Richer hilt/orientation, explicit roll, torso/pelvis sequencing, recovery | Continue existing authored performance work in [MEL-34](https://linear.app/meleeslasher/issue/MEL-34) and editable controls in [MEL-37](https://linear.app/meleeslasher/issue/MEL-37). No new competing source owner or runtime curve architecture. The moving [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) governs the candidate and user feedback. Native/contact changes remain deferred until selected integration. |
| Hand/elbow/shoulder/reach/edge/phase and velocity diagnostics | Explicitly deferred to new [MEL-44](https://linear.app/meleeslasher/issue/MEL-44), Low. Add only diagnostics needed for a concrete selected-integration question, reusing existing evidence and tools. |
| Legacy momentum/lunge terminology | Deferred under MEL-42's fixture/authority reconciliation. Preserve compatibility until callers are examined; no movement retuning justified by terminology alone. |
| Finger/grip articulation | Deferred to MEL-25 after selection; do not polish around unresolved controls or weak motion. |
| Impact, camera, audio/VFX polish | Deferred to existing [MEL-7](https://linear.app/meleeslasher/issue/MEL-7) and [MEL-12](https://linear.app/meleeslasher/issue/MEL-12), following playable feedback. Cosmetic nondeterminism alone does not establish a gameplay bug. |
| Six-direction FP/TP, extreme aim, high-rate diagnostic captures | No automatic sweep. MEL-39/40 and MEL-44 own focused selected-motion evidence; remaining vocabulary is deferred to [MEL-13](https://linear.app/meleeslasher/issue/MEL-13). Preserve source-speed comparison and disclose sampled-frame inspection. |
| Networking/prediction, montage authority, simulation rewrite, concealing motion with cinematic effects | No implementation requested by the audit, which explicitly excludes these. Retain current single-player scope and authority; do not create speculative implementation work. |

## Verification and handoff

Read canonical rules/development, current audit/planning/TP checkpoints, lean validation and relevant runtime/benchmark paths. Compared the two local JSON files and preserved copies. Reviewed existing Linear backlog to avoid duplicate animation tasks; created MEL-41–44 in Backlog and appended scoped notes to MEL-25/35/39 without changing their status or source selection.

Only README and this disposition are implementation changes. Checked changed content, local links, snapshot hashes and whitespace. No C++ build, test run, import, render or new visual acceptance is claimed. Existing dirty animation documents and console experiments remain untouched. Next useful engineering task: MEL-41; active motion ownership remains unchanged. Runtime fixes are explicitly deferred, not reported complete.
