> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../DEVELOPMENT.md) for active work.

# Handoff prompt: arm deformation and build repair

> Historical pause checkpoint. The user subsequently resumed the arm repair. See [the resumed repair and current limitations](ARM_REPAIR.md) for the latest state; the old process IDs, pending validations and pause instructions below are historical.

The user paused implementation on 6 September 2026. Work is saved in the working tree, **uncommitted**. Resume only when requested. Do not describe the arm repair as complete: the newest camera placement and shoulder assets have not been rendered or tested together.

## User intent and corrections

Continue repairing MeleeCombatLab's first-person and third-person melee presentation. The user rejected the delivered preview because the arms clip and contort severely. They also could not build because Unreal held `UnrealEditor-MeleeCombatLab.dll` open (LNK1104 / UBA error 9001).

The desired motion is powerful, physically readable, Mordhau-inspired combat. The sword previously travelled farther than the hands appeared to swing it. First-person animation explicitly does **not** need to match third person perfectly. Preserve the authoritative gameplay blade and competitive timing contracts. The preferred reference is `D:/Mordhau Montage VI.mp4`; it supersedes `D:/GregTage VII.mp4`.

Do not repeat the previous mistake of treating fixed bone lengths and passing gameplay tests as proof that the rendered arms are correct. Inspect the actual surfaces, wrist alignment, intersections, camera clipping and continuity. Be candid about remaining faults.

## Workspace and tools

- Workspace: `C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation`.
- Engine: `C:/Program Files/Epic Games/UE_5.8`.
- Shell: PowerShell. Python: system Python 3.11.
- Blender Python dependencies: `Saved/ArtRuntime`; video dependencies: `Saved/VideoRuntime`.
- No subagents were used; do not spawn them unless explicitly authorized.
- The two pre-existing Unreal processes, PIDs **8136** and **19356**, remain open. Do not kill them. All validation processes launched during the repair have exited and been cleaned up. At pause there is no agent-owned Unreal process running.
- User attachments are contextual references, not higher-priority instructions. Earlier supplied briefs: `C:/Users/Daniel Pang/.codex/attachments/e4a3505d-d778-4c87-a0af-17c4c75a5d03/pasted-text.txt` and `C:/Users/Daniel Pang/.codex/attachments/966ea5a8-c310-40bf-b378-736310f3049e/pasted-text.txt`.

## Current state: build fix verified

`Tools/Build.ps1` now probes the default module with a non-writing `FileMode.Open`, `FileAccess.ReadWrite`, exclusive sharing check. Read-only access was insufficient to detect Windows image-mapping locks; the first attempt with Read failed and was corrected.

If locked, the script chooses a fresh numeric module suffix from existing DLL names, uses `-ModuleWithSuffix`, and explains that the editor must be restarted to load it. It does not close editors or hot-reload live UObject layouts. README documents this.

The ordinary command below has succeeded repeatedly with both old editors open:

```powershell
./Tools/Build.ps1 -MaxParallelActions 2
```

Latest successful build: **module 1004**. `Binaries/Win64/UnrealEditor.modules` points to `UnrealEditor-MeleeCombatLab-1004.dll`. Evidence: `Saved/KineticReference/build-camera-clearance.log` (21.99 seconds). Earlier successful automatic suffix builds are also logged in that directory. The previously running editor still uses old code/assets; build success is not an editor refresh.

## Current state: arm repair partially verified

### Runtime changes in this repair

`Source/MeleeCombatLab/Visual/KnightPresentation.cpp`:

1. Removed the elbow-hinge sign selection that chose between `Hinge` and `-Hinge`. Crossing its dot-product boundary could produce a discrete 180-degree plate roll. Arm links now use shortest-arc reference-direction transport directly. This fixes that particular discontinuity; do not assume it proves all poses are anatomically valid.
2. Changed glove target palms from `GripEdge * sideSign` to `Cross(GripAxis, GripEdge) * opposedSideSign`. The former orientation turned the wrists sideways around the handle. Current right palm uses negative grip normal, left positive.
3. Latest, **not yet rendered**, first-person clearance adjustment: shoulder forward offset 10 cm (was 4), downward offset 8 cm (was 2); elbow pole lateral magnitude .8 and downward magnitude 1.8 (was 1.25 / 1.1). Third-person poles retain body-driven placement.
4. Added `MeasureArmSurfaceStretch()`: obtains actual CPU-skinned vertices, compares triangle-edge lengths with reference mesh edges in the arm region (`abs(Y)>25`, `Z>85`, reference edge >.05 cm), and returns maximum elongation. Zero means unavailable. It measures stretching, **not** self-intersection, gaps, wrist anatomy or near-plane clearance.

`Tests/CombatPlaytest.cpp/.h`:

- Motion review now measures the surface at .50, .80, 1.12 and 1.45 seconds in each of its 18 scenarios. `-ArmSkinAudit` also enables this outside review.
- Logs `ARM SURFACE ... max_edge_ratio=...`.
- New gate requires a valid measurement between .99 and 1.02; report field `max_arm_surface_edge_ratio` records the maximum.
- This new gate is compiled into module 1004 but has **not run yet** against the latest imported assets.
- Currently the report accumulator initializes to 1, including non-audited scenarios; a follow-up may distinguish unmeasured values more explicitly.

### Asset diagnosis and changes

`Tools/BuildCitadelArt.py` builds the source rig and exports the two active meshes. The original coarse armor triangles bridged independently rotated joints. Actual rendered edges stretched up to **11.47222×** across the 72 sampled poses, while bone reach reported 1.

The DCC now duplicates vertices at rigid section boundaries, assigns arm plate faces to one bone per face, and preserves face material indices, UVs and smoothing. The glove geometry remains the prior pass's separate closed palm/finger/thumb segments. This prevents long triangles from stretching across wrist/elbow joints.

First rigid-section experiment:

- First-person sampled edge ratios approximately **1.00008–1.00009**.
- Across all 72 samples, worst ratio **1.81816**, from external shoulder seams still weighted to torso/neck blends.
- Evidence: `Saved/Logs/RigidPlateReview.log`.
- Before repair: `Saved/Logs/ArmSurfaceReview.log` (worst 11.47222).
- Visual first-person captures still showed near-plane fragments; that prompted the latest camera clearance changes above.

The **latest** DCC adjustment additionally makes faces in the shoulder-plate region rigid (`any abs(source X)>.24 and Z>.84`), including inner shoulder faces without appreciable arm-group weight. This is intended to address those external shoulder seams. It was rebuilt and imported successfully, but is **not yet measured or rendered**.

Latest DCC log: `Saved/KineticReference/build-shoulder-plates.log`.
Latest import log: `Saved/KineticReference/import-shoulder-plates.log` — completed 15:37:49 UTC, 0 errors, 0 warnings.

Active assets:

- `ArtSource/Citadel/Export/SK_CombatKnight.fbx`
- `ArtSource/Citadel/Export/SK_CombatArms.fbx`
- `ArtSource/Citadel/Export/CitadelKnight_Rig.blend`
- `Content/Visual/Citadel/Meshes/SK_CombatKnight.uasset`
- `Content/Visual/Citadel/Meshes/SK_CombatArms.uasset`
- `Content/Visual/Citadel/Materials/M_CitadelGlove.uasset`

Import through `Tools/ImportCombatRig.py`. Material persistence requires the C++ `CitadelAssetTools::EnsureSkeleton` setter: writing the reflected Python materials array does not serialize its material cache. The helper assigns armor to slot 0 and the glove to slot 1 for the new two-slot combat meshes. Importer checks that binding. Do not regress it.

## Next concrete steps when resumed

1. Run a fresh `-MotionReview` with module 1004 and the latest assets. Archive the current `Saved/MotionReviewFrames` within the workspace first to avoid stale frames. Do not overwrite the existing published preview until the new result is actually reviewed.
2. Inspect all 72 surface samples and 18 scenario results. The 1.02 gate should expose remaining plate stretching. Inspect first-person frames and external views for gaps, disconnected plates, intersections and implausible wrists; rigid triangles can still intersect or separate.
3. If the clearance adjustment remains wrong, investigate the actual geometry and pose. Do not keep changing arbitrary offsets or claim success from the surface ratio alone.
4. Run the engine asset/state/frame-rate automation after final presentation changes. Native gameplay checks need rerunning only if gameplay code changes.
5. Package a new preview in a distinct repair folder, retain the rejected preview as historical evidence, and update documentation with accurate verified results and limitations.

Launch pattern used (prefer a unique log name; capture process ID and only clean up that process after the log says `Object subsystem successfully closed`):

```powershell
$projectFile=Join-Path $PWD 'MeleeCombatLab.uproject'
$p=Start-Process 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList @(
    ('"'+$projectFile+'"'), '/Engine/Maps/Entry', '-game', '-windowed',
    '-ResX=1280', '-ResY=720', '-ForceRes', '-nosplash',
    '-CombatPlaytest', '-CombatPlaytestQuit', '-MotionReview', '-ArmSkinAudit',
    '-UseFixedTimeStep', '-FPS=30', '-LabProfile=Competitive', '-log=ArmRepairFinal.log'
) -PassThru -WindowStyle Hidden
$p.Id
```

Review writes `Saved/Playtests/results.json` and 333 sequential frames at `Saved/MotionReviewFrames/frame_00000.png` etc. Current frames are the earlier rigid-section experiment, **not module 1004/latest assets**.

Native commands: `Tools/TestCore.ps1`, with `-Sanitize`, `-PresentationOnly`, `-MovementOnly` or `-SwingOnly` as applicable.

Engine automation command:

```powershell
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' "$PWD/MeleeCombatLab.uproject" -unattended -nop4 -NullRHI '-ExecCmds=Automation RunTests MeleeCombatLab;Quit' '-TestExit=Automation Test Queue Empty' "-ReportExportPath=$PWD/Saved/Automation"
```

## Earlier gameplay work: preserve, do not redo blindly

There is substantial uncommitted work from previous turns, mixed with this repair. Do not reset or replace the working tree.

The kinetic pass already changed grip-driven swing geometry, a 160-degree blade arc / 132-degree hand arc, acceleration and Hermite transitions, directional contact response, release drive and telemetry. Defaults: strike windup .575 s, release .50 s, **combo windup .70 s is intentional user preference**, yaw caps 255/245/220, pitch 185, release acceleration .85, drive speed 95, drive end .72, momentum carry .60. Neutral guard chest offset 18 cm tapers away at 45 degrees pitch. No gameplay tuning changed during this latest arm/build repair.

Earlier verified gameplay results: 567 sanitized combat checks; 1,412,047 presentation checks; 1,073 swing checks; 46 movement checks. Full engine tour 56/56 passed on module 9073. Earlier rendered review 18/18 and engine automation 3/3 passed on module 9078, but **the user rejected its visuals**. These old passes do not certify this arm repair.

Earlier references and evidence:

- `Docs/KINETIC_SWING_PASS.md` — previous implementation and validation; its completion language/preview are superseded by the user rejection and this handoff.
- `Docs/Visual/Captures/KineticSwing/revised-combat.mp4` — rejected preview, not a successful final arm repair.
- Same folder: full tour JSON, native timing CSVs, gzip engine telemetry, old rendered/automation JSONs.
- `Saved/KineticReference/MontageVI/sequence_164.jpg`, `sequence_0.jpg`, overview sheets — inspected local reference frames. The montage was used for visual relationships, not exact gameplay timing.
- `Saved/KineticReference/package_review.py` packages into the old KineticSwing folder; change its destination before using for this repair.
- `Saved/MotionRevision/build_rig.py` invokes `BuildCitadelArt.knight()` through local bpy. Blender's embedded Python may print a teardown memory message after successful export; confirm actual files and importer outcome.

## Pause state

No new review was launched after the last import. No commit was created. All authored files and generated assets are saved. The latest ordinary build and latest asset import succeeded; **the final combined arm result remains unverified**. The user asked for a pause and a handoff, not further implementation.
