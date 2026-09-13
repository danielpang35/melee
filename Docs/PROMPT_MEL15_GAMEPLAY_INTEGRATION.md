# New-instance prompt — integrate the approved horizontal swing into gameplay

> Historical implementation request. Production EX integration and package reload were subsequently delivered; see [delivery evidence](MEL15_PRODUCTION_HANDOFF.md). Follow [current development](DEVELOPMENT.md), not the pre-integration state below.

Implement this task; do not stop at a plan or another isolated preview.

## User objective and authorization

Integrate the approved EX_v002 first-person right-horizontal swing into the actual playable melee game. I want to build it myself from my usual checkout, launch the game, move and aim, swing repeatedly, and interact with opponents and the world. Preserve the previously praised weight, satisfaction, commitment, spatial manipulation and responsiveness.

You may reconstruct entire portions of the codebase when that produces a cleaner, correct integration. Old presentation architecture, trajectory assumptions, rig formats and correction layers are replaceable. Preserve unrelated work and the approved animation assets. Use judgment on reversible implementation choices; do the integration work rather than repeatedly asking whether to proceed.

## Workspaces and authority

My normal checkout and intended delivery location is:
`C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation`

The implemented EX_v002 viewer and contact trial are currently in a DIFFERENT checkout:
`C:/Users/Daniel Pang/.codex/worktrees/0893/swingmanipulation`

The main checkout still selects RC_v008 in `Config/RightCutCandidate.txt` and defaults to `CombatLabGameMode`. Building it does not currently install the new swing. The worktree has substantial inherited uncommitted/untracked work. Inspect both checkouts and reconcile the relevant changes and asset dependencies deliberately. Do not overwrite the main tree wholesale, reset dirty work, or assume a Git merge captures untracked assets. Preserve a recoverable copy of files being replaced. Temporary isolated development is fine, but the deliverable must reach my normal checkout with verified build/launch instructions.

Read applicable AGENTS.md files, including `C:/Users/Daniel Pang/.codex/AGENTS.md`. Apply these user rules in both checkouts: optimize total consumption; Astra High for architecture/technical planning and light reasoning for a settled backlog; small self-contained assignments with `fork_turns="none"` and no child subagents; prefer sequential work; reuse evidence; one independent review for consequential changes; focused verification; no broad pose matrix or repeated unchanged polling. Keep one compact checkpoint and concise updates. Do not claim token savings without measured usage.

Fetch current Linear MEL-15 and relevant MEL-6 dependency state, then read these Notion design pages:
- Animation: https://app.notion.com/p/3d32e3c3f8f881e08474defe7febb171
- Melee Swing Model: https://app.notion.com/p/3d32e3c3f8f881028f05c2a960248ff1
- Current Milestone: https://app.notion.com/p/3d32e3c3f8f8813c8883ed9e8bd1f299

Read these files in the 0893 worktree:
- `Docs/MEL15_CONTACT_TRIAL.md` — latest implementation/evidence checkpoint.
- `Docs/MEL15_INTEGRATION_HANDOFF.md` — accepted identity, reload proof, timing and missing bindings.
- `ArtSource/CharacterReset/EX_v002/Export/MEL15-HANDOFF.md` — export/deformation contract.
- Relevant local validation/ownership instructions, without restarting old investigations.

Notion owns design and Linear owns task state. Some Notion and MEL-6 text predates completed EX_v002 export, Unreal playback and reload verification; use the identified receipts to resolve those stale implementation statements. Neither stale status nor generic rewrite permission revokes recorded animation approval. Do not post remote comments/messages without explicit authorization; keep the handoff local if authorization is absent.

## Preserve this established baseline

The user explicitly approved EX_v002 source and basic Unreal first-person playback as believable, clear and satisfying. Selected revision:
`EX_v002-source-1615b76b-FBX-6a34514c-native-unreduced-v1`.

`Config/EXPreview.json` identifies the native skeletal assets and weapon JSON. Verify their identities against the handoff before modifying integration. Preserve source animation, grip/deformation, projection and native unreduced compression. The documented FBX surface mismatch does not undo human approval and is not a reason to redesign this swing.

The user approved skipping source 0–0.30 s idle lead-in and then playing at 1×. The source has 154 samples at 60 Hz, with the last sample at 2.55 s. Do not compress it into legacy strike durations or apply legacy trajectory acceleration/reach corrections to its sampled weapon motion. Preserve weight through the accepted motion and legal combat behavior; accels/drags change spatial contact through aim and footwork, not playback speed.

The current neutral contact trial is technically verified, not full gameplay integration:
- `Combat/Attacks/EXWeaponMotion.h` samples the delivered ~103.5 cm blade.
- `Combat/EXContactTrial.h` uses existing state and contact resolver in an isolated stepping harness.
- `Visual/EXPreviewGameMode.*` enables it only with `-EXContactTrial`.
- `Tools/PlayEXContactTrial.ps1` launches LMB cut / R reset / M near-far target.
- Normal-speed recording: `Saved/MEL15/EX_contact_body.mp4`.
- Tests: `Tools/TestEXContact.ps1`; receipts under `Saved/MEL15/contact-trial`.

The trial stops after one cut or an unbound interruption. Its fixed camera, reset requirement and independent stepping harness are not acceptable substitutes for production integration.

## Implementation requirements

1. Establish one production combat transaction and clock. Integrate canonical authored motion into the real player/CombatSimulation path and sample presentation from that clock. Refactor or replace conflicting systems rather than maintaining a second gameplay driver beside the old one. Mesh collision and animation notifies must not become damage authority.
2. Make the right horizontal reachable through normal input with movement and yaw/pitch manipulation. Preserve applicable legal feint/feint-to-parry, stamina, parry, riposte, hit/flinch, wall and combo/morph rules. Do not disable legal actions merely because the neutral clip lacks their presentation. Keep unrelated attack families functional or explicitly isolate any temporary fallback; do not silently reinterpret their timing as EX timing.
3. Provide continuous ready → swing → carry/recovery → ready and repeat input behavior. The current source endpoint differs from frame 19 by about 5.58 cm at the hilt; direct restart snaps. Implement appropriate transitions without delaying legally available inputs or retiming the approved action. Missing branch clips require explicit bindings/transitions, not a frozen trial or an undisclosed jump to the old rig.
4. Carry one shared world transform through canonical blade and presentation. The source-to-gameplay conversion is `100(-y,-x,z)`; the trial uses camera pivot `(11.5,0,168)` cm. Resolve actor origin, camera, crouch/lean, aim and movement coherently. Do not mix full camera pitch with the old 0.75-scaled torso pitch for separate threat paths. Preserve actual blade length and once-per-target contact.
5. Treat the current phase mapping as a tested candidate: source windup 0.30–62/60 s, release 62/60–80/60 s, recovery through 153/60 s. Full-release damage is a trial proposal, not recorded human gameplay approval. Establish a defensible mapping in gameplay and present it for review; do not stall implementation merely because human acceptance remains pending.
6. Correct contact/state ordering in the integrated path. The trial resolves each release span before completing its state transition, excluding preceding windup geometry and retaining the final release span before miss cost. Production must handle release and damage-window boundaries correctly, including large render deltas, interruptions and queued transitions. Do not copy the trial wholesale as another permanent simulator.
7. Preserve render/collision subframe agreement. The accepted renderer uses shortest-path normalized quaternion FastLerp in `FTransform::Blend`; SLERP produced up to ~9 mm disagreement on rapid roll. Validate rig quaternion endpoints as well as visible-world endpoints. Keep revision selection coherent through an attack; source edits should remain replayable without C++ recompilation.
8. FP and external views may have separate visual bindings but must communicate the same attack side, phase, threat, reach and contact outcome. EX_v002's FP upper-arm deformation cannot simply be displayed externally. Create/adapt separate candidate bindings where necessary while preserving the approved neutral FP asset. Missing complete external/defensive performance remains an acceptance dependency; it must not prevent doing the available production horizontal integration first. Clearly distinguish provisional presentation from completed whole-exchange acceptance.

## Build and verification

Fix the actual user-facing build route while delivering. The previous main-checkout failure was `Unable to delete hot-reload file ...UnrealEditor-MeleeCombatLab-1019.dll`: a running Unreal process had that suffixed DLL loaded. The launcher/build logic checked only the unsuffixed DLL and missed this situation. Reinspect current processes/modules; do not reuse old PIDs or kill unrelated/unsaved sessions. Handle locked suffixed modules safely and report the correct remedy rather than retrying an unchanged failure.

Reuse existing evidence: native body contact at attack age 0.8375 s at 30/60/144 Hz; range miss; release boundary and parry/wall ordering; verified source/animation hashes; same-process newly selected skeletal-package reload. The last trial capture had one hit and peak visible/canonical tip error 0.000041618 cm. These certify the trial, not your changed production path. Refresh affected checks against the actual selected production artifact.

Preserve the inherited SwingOnly late-contact and PresentationOnly swivel-continuity assertions. Diagnose relevant failures when replacing their paths; demonstrate any contract's retirement rather than deleting or weakening assertions to obtain green results. Run focused changed-contract tests, build the actual delivery checkout and inspect a concise normal-speed gameplay recording. Show repeated cuts with movement/aim, hit and miss, and relevant defensive/interruption behavior; use synchronized external/defender evidence when those bindings are available. No broad art regeneration, pose matrix, unrelated feature expansion or packaged profiling unless this delivery needs it.

## Deliverable

Finish with the new horizontal bound into the normal playable game in my usual checkout, exact build/launch commands, identified selected assets/build, a short review recording and one compact handoff describing changes, verification and remaining limitations. Do not leave another hidden-worktree-only demo. Keep technical completion and human visual/gameplay acceptance separate; do not claim full MEL-15/MEL-11 completion while required whole-exchange bindings or review remain open.
