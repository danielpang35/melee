# Project stocktake and Cascadeur reset

> Historical stocktake (7 September). Its reset, blockers and remote issue statuses are an as-of record, not current instructions. See [current audit and implementation plan](PROJECT_AUDIT.md) and [current development](DEVELOPMENT.md).

7 September 2026. Scope: repository structure, workflow, Linear project/milestone and Notion design. This is a project reset, not new animation implementation or acceptance.

**Development speed is key.** The project now has one short path: prove the authoring-to-preview system, author one coordinated right cut, then obtain a playable decision. Weight, rhythm, silhouette and intent lead review; technical checks establish their own contracts.

## Capture removal — subsequent user request, 7 September 2026

Deleted 27,471 historical screenshots, review videos and raw pose-capture files totaling 45.06 GiB in logical file size. All targeted files were verified absent; no deletion failures occurred. Source assets, Cascadeur inputs, runtime source/config/content, Mordhau reference material and small written/JSON result summaries were retained. This supersedes the capture-retention statements from the initial reset below. Historical image/video links may now refer to intentionally removed files.

The file inventory and result are in Saved/ProjectReset/historical-capture-removal.json and historical-capture-removal-result.json. Logical bytes removed do not necessarily equal local disk space recovered for OneDrive placeholders.

## What the stocktake found

| Finding | Consequence |
|---|---|
| Prepared Cascadeur kit, with no setup-result file and manifest stage `prepared_not_yet_imported_into_cascadeur` | Application import/save/export must be demonstrated; no completed Cascadeur pipeline is claimed |
| `CombatRigMesh.cpp` writes bone transforms; `KnightPresentation.cpp` already reloads scalar performance CSV data | Preserve the useful baseline, but build a skeletal clip consumer that retains the coordinated source performance |
| Manifest selects module 1010; the mixed-pointer initializer in PresentationTests is already fixed | Retire the handoff that treats module 1006 and that initializer as current blockers; verify actual loaded identity at next play review |
| Overlapping joint-repair, horizontal, full-body and readability tasks | Consolidate performance ownership; eliminate duplicated acceptance dependencies |
| Old README/spec/validation and bible export mix obsolete tuning, historical checks and active instructions | Replace top-level guidance and archive old instructions with clear historical labels |
| Historical build failures record exhausted commit/paging capacity; later recovery notes report a large OneDrive commit footprint | Bound build concurrency and serialize heavy work. Treat historical process/resource observations as history until reproduced |
| The art brief had added multiplayer harness/client-latency work to a single-player slice | Remove that scope; retain the approved art reference and future networking direction |

The user's praised swing feel has no exact approved DLL identified in the source records. Preserve a reproducible comparison; never label an arbitrary module as user-approved.

## Repository changes

- Replaced README, PROJECT_SPEC and VALIDATION with current scope, commands and change-based review rules. Added [DEVELOPMENT.md](DEVELOPMENT.md) as the single local work guide and [Tools/README.md](../Tools/README.md) as the short tool index.
- Archived 18 superseded motion/audit/handoff documents, three old visual plans, the duplicate Notion bible tree, the original top-level documents and four old movement package entries. Repaired relative Markdown links and marked archived documents historical. See [archive](Archive/README.md).
- Retained active Ren/Kronk references, movement contracts, Citadel build/credits, audio provenance and exact capture evidence. Existing runtime animation and tests remain available until replacement is proven.
- Build.ps1 now defaults to two compiler actions, with an explicit automatic-concurrency override. CaptureMatrix defaults to two views (FP/side, eight cuts), down from nine views (36 cuts); explicit wider coverage remains available.
- Ignored Python bytecode and Cascadeur Blender backup files. No cache purge, raw capture deletion, runtime source deletion, test weakening, source-asset deletion or tuning change was performed.

## Storage at entry

Logical file sizes, not a measurement of locally allocated OneDrive storage:

| Folder | Files | Size |
|---|---:|---:|
| Saved | 35,562 | 46.56 GiB |
| Saved/ArmRepair (included above) | 21,492 | 36.19 GiB |
| Intermediate | 314 | 2.67 GiB |
| ArtSource | 386 | 0.98 GiB |
| Binaries | 24 | 0.77 GiB |
| Docs | 592 | 97.5 MiB |
| Content | 75 | 67.5 MiB |

Most footprint is accumulated review evidence. It has not been reclaimed or relabeled as disposable. Stop accumulating broad per-edit frame matrices; preserve a comparison baseline and meaningful checkpoints with short clips/decisions. A later storage reclamation needs an identified retention set, since these uncommitted captures may be the only exact evidence for prior revisions. Archiving files within this workspace improves navigation, not disk usage.

## Linear and Notion

[Linear project](https://linear.app/meleeslasher/project/melee-combat-lab-longsword-exchange-c906057fa194): revised all 12 project issues, project description/status and the existing milestone without creating duplicate tasks. Owners were left unchanged.

| Lane | Live issue |
|---|---|
| In Progress | [MEL-15 — Prove the Cascadeur-to-Unreal skeletal preview loop](https://linear.app/meleeslasher/issue/MEL-15) |
| Todo, blocked by MEL-15 | [MEL-6 — Author one coordinated right cut in Cascadeur](https://linear.app/meleeslasher/issue/MEL-6) |
| Todo, blocked by MEL-6 | [MEL-11 — Play-review the Cascadeur right-cut pilot and decide expansion](https://linear.app/meleeslasher/issue/MEL-11) |
| Consolidated, not accepted | MEL-5 into MEL-6; MEL-9 into MEL-11 |
| Backlog | MEL-7/8/10/12/13/14/16 |

MEL-11 no longer waits on separate audio, movement, joint and readability projects. Opposite horizontal and overhead are first expansion steps in MEL-13 after the pilot decision. The rear shoulder and overhead appearance defects remain known, not fixed by reprioritization.

[Notion home](https://app.notion.com/p/3d32e3c3f8f88166821dcab5f044efa2): revised 12 pages: home, Project Vision, Animation, Melee Swing Model, Current Milestone, Current Development, Playtesting, Findings, Visual Direction, Accepted Decisions, the art implementation brief, and the task page. The task page is now **Execution — Linear**, with the historical B-series table removed from active guidance. Child pages and the approved art image were preserved.

The [pre-reset connected-source snapshot](Archive/2026-09-07/remote-before.json) retains original descriptions and pages. Linear owns live execution; Notion owns design; local docs own commands and implementation workflow. Keep histories as evidence, not parallel work queues.

## Verification and remaining work

PowerShell syntax checks passed. Dry runs confirmed two default capture commands and all nine explicitly selected camera commands without launching Unreal. SHA-256 comparison confirmed all 144 existing files under Source, Config and Content remained unchanged. Live reads confirmed the three-issue dependency chain, consolidation relations and Notion page structure. All 21 relative links in the active guides resolved; git diff --check passed.

No full Unreal build or gameplay suite was run for these documentation/default changes. No faster loop, new clip or artistic improvement is claimed before measurement and review. The first actual implementation deliverable remains Cascadeur setup plus a repeatable full-skeleton Unreal preview that can replay a second edit without a C++ rebuild.
