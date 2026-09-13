# Tool guide

Every agent reads [AGENTS.md](../AGENTS.md) and [current development](../Docs/DEVELOPMENT.md). Policy MCL-DEV-2026-09-08: cheap batches → select → refine. Tools are invoked for the actual question, not as a startup checklist.

| Purpose | Entry point |
|---|---|
| Isolated whole-motion candidate batches | AnimationLab.py new / render / select / refine |
| Explicit playable benchmark | PlayBenchmark.ps1; -ThirdPerson selects TP; -PrepareOnly records without launching |
| Carry rules to older worktrees/global entry | InstallProjectRules.ps1 (preview), -Apply (project-only pointers) |
| Selected TP export/import | ExportThirdPersonSwing.py / ImportThirdPersonSwing.py |
| Current single-source TP author | AuthorThirdPersonSwing.py; owned by the current TP task, not a batch scratch directory |
| Changed C++ | Build.ps1 |
| Affected state/contact/audio regressions | TestCore.ps1 / TestCombatAudio.ps1 |
| Optional focused engine diagnostic | CaptureThirdPersonProof.ps1 / VerifyThirdPersonProof.py |
| Explicit broad integration diagnosis only | RunThirdPersonProof.ps1 / MEL15CaptureMatrix.ps1 |
| Existing asset maintenance | Character, Citadel and audio tools as needed |

[Executable candidate workflow](../Docs/ANIMATION_WORKFLOW.md) and [lean validation](../VALIDATION.md) supersede older instructions making proof matrices mandatory for every revision. Do not rerun CF_v001 studies or inherited Cascadeur setup merely to start an animation.

Saved/ArtRuntime and Saved/VideoRuntime provide installed dependencies. Legacy helpers retain export knowledge and recovery use; they are not mandated stages. Current source/runtime must never depend solely on an ignored scratch folder without a deliberate delivery handoff.
