> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../DEVELOPMENT.md) for active work.

# MEL-15 resumed authoring — 7 September 2026

Expert role: principal melee combat animator, supported by rigging, deterministic combat simulation and Unreal build/capture validation.

Implementation resumed from the revised handoff. Preserve the successful swing clocks (.575/.500/.675 s; combo windup .700 s), acceleration and responsiveness. The specific user-approved feel checkpoint is not identified by an exact DLL in the source record. Module 1007 is the reproducible entry control for this session, not a claim of visual acceptance.

## Entry recovery

- Preserved the dirty checkout, module1006 manifest and historical assets/evidence. Entry snapshots and hashes: `Saved/MEL15/Resume20260907`.
- Fixed the mixed const/non-const pointer initializer in PresentationTests. Current combined source passes 2,387,215 presentation checks, 931,330 swing checks and 605 combat checks. These are fresh runs, distinct from the handoff's older counts.
- Removed immediate `;Quit` from Build.ps1 automation invocation. The helper still requires queue-empty and final report verification.
- Initial sandboxed build stopped at UnrealBuildTool log rotation. The authorized build succeeded as module1007, SHA256 `0288d9479ad3d735bfdfd6abdfbb40f89bd0e5ebb7a46e019458a13623bb6b26`.
- User authorized closing the existing project editor and temporarily quitting/restarting OneDrive. Both normal close requests failed to exit their processes; the verified processes were then stopped. OneDrive held approximately35GB private commit. Restart path is recorded in `Saved/MEL15/Resume20260907/onedrive-restart-path.txt`; restart remains required after build/capture work.
- Fresh R0_Front captured all four core cuts and verified actual module1007 load in the engine log. R0_FP is the matched first-person entry capture. Engine automation/final regressions remain outstanding.

## Diagnosis and direction

Annotated historical/reference sheets and source-backed glove diagnosis are in `Saved/MEL15/Resume20260907/Diagnosis`. Images support a high idle and horizontal hilt carriage crowded at face/chest. Corrected grip contact/chirality is preserved; circular finger sections, broad curved thumb and uniform glove shading remain separate appearance problems. Exact hidden Mordhau grip offsets and input timing cannot be recovered from the montage.

Fresh module1007 front frames confirm idle under the face and folded horizontal forearms. The diagonal finish is useful progress and must not be discarded. First fit stomach/upper-abdomen idle and transitions, then author the horizontal/overhead chain from that foundation. Do not increase all body excursions or replace the praised feel.

## Evidence safeguards

The harness now emits actual attack age and phase metadata and supports legal combo/riposte/parry sequences. A follow-up audit checks presentation tick ordering before precise skeletal/phase claims. A transient neutral material flag supports same-pose material isolation. These changes require engine verification.

Rendered still inspection and encoded normal-speed footage are distinct from continuous video perception or human playable acceptance. MEL-5, MEL-15 and MEL-11 remain unaccepted; no numerical pass closes them.
