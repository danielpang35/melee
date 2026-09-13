# MEL-6 execution checkpoint

> Historical FP author/export checkpoint. Subsequent native playback and production integration are recorded in [MEL15 delivery](MEL15_PRODUCTION_HANDOFF.md). Its export-blocker and remote-status statements are historical; [current development](DEVELOPMENT.md) owns priorities.

## Latest task selection

MEL-28 export delivered for review. Live Linear and Notion Animation confirm the approved EX_v002 FP baseline. EX_v002/Export contains FBX, full skeleton/weapon samples, evaluated vertex-position reference, manifest and MEL15-HANDOFF.md. Final roundtrip passes 102 bones and all 154 frames at 60fps; all three protected identities remain unchanged and central-passage source preview is pixel-identical. Independent root code/receipt review and artifact hash checks completed without duplicating the export run. **FBX surface parity fails:** arm vertices differ by up to 42.166mm among eight checked frames; imported joints must remain disconnected to preserve translations. Position-only NPZ is a source reference, not standalone playable geometry. MEL-28 is In Review, not complete visual parity. MEL-15 must resolve source-equivalent surface playback and shared contact/phase mapping; no engine or overhead work performed.

Linear updated with EX_v002 first-person right-horizontal success. MEL-6 remains In Progress: approved neutral FP motion does not complete the broader parry/riposte exchange or provide its current-candidate export. Historical EX_v001 export is not proof for EX_v002. MEL-28 reopened as "Export the approved EX_v002 first-person right horizontal and weapon motion" (Todo, selected next, not started), retaining its historical receipt. Preserve the approved source and distinguish FP weapon data from approved gameplay collision. MEL-33 overhead remains paused.

**Paused at user request:** "put a pin in this." Overhead author agent interrupted. Baseline extraction and eight-beat overhead design are saved in Docs/RIGHT_OVERHEAD_BASELINE.md. MEL-33 implementation was just dispatched; no completed overhead preview is claimed. Resume from the saved design and inspect any partial OH_v001 files before continuing. Approved EX_v002 remains the baseline.

## Latest user decision — horizontal baseline accepted; overhead design authorized

User: "Now that's a nice animation. Now that we have a baseline..." EX_v002 is accepted as the visual first-person right-horizontal baseline. MEL-31/MEL-32 marked Done for their source/comparison deliveries; this does not imply engine/external-body acceptance. Baseline source, pose-controls and generator hashes recorded in RIGHT_HORIZONTAL_BASELINE_IDENTITY.json; those files remain protected.

MEL-33 under MEL-13 owns the requested right-overhead design/prototype. Small Sol Medium baseline/author assignment, sequential reuse, then one independent visual review. Notion Animation updated to record approval and source-overhead authorization; older broader integration gates remain separate. Current work: extract baseline and author OH_v001 high-right load → descending hand/hilt passage → low carry → restrained return, not a rotated horizontal clip. No confirmed neutral-overhead capture is available; resulting choreography is authored extrapolation, not exact Mordhau recovery.

## Current direction after user review

EX_v001 is improved but too constrained by physical realism. User now requests direct replication of the visible Mordhau right-horizontal Greatsword swing: readable power, silhouette and timing take priority. Notion Animation page was referenced and updated with this explicit direction.

New chain: MEL-30 reference identification (mordhau_reference) → MEL-31 EX_v002 matching (mordhau_match) → MEL-32 direct comparison (mordhau_compare), each GPT-6 Astra Low with no children. All three agents spawned. Preserve EX_v001; no speculative EX_v002 motion before a confirmed reference.

Confirmed capture received: C:/Users/Daniel Pang/Videos/Captures/MORDHAU   2026-09-07 12-27-58.mp4. User identifies opening partial left, movement, combos, neutral rights, final right feint. Reference agent isolated neutral right native PTS 15.775733–17.775500; onset bracket 15.747967–15.775733. Capture is VFR (native PTS roughly36fps); use real seconds, not nominal fps. Stats from mordstats.com (site Build26.1) cross-check normal strike575ms windup/500ms release/700ms recovery; see STATS.md and raw Greatsword record. Gameplay release remains distinct from visible passage.

All three Astra Low assignments delivered. MEL-30 Done; MEL-31/MEL-32 and parent In Review. EX_v002/EX_v002_MordhauRight.blend, pose-controls.json, MOTION.md, Preview/EX_v002_FP.mp4 and Comparison/EX_v002_vs_Mordhau.mp4 are saved. Candidate/comparison154frames at60fps,2.566667s. Actual comparison preserves native PTS/speed and observed-onset alignment; Comparison/REVIEW.md records one independent six-beat review and timing/endpoints verification. Old provisional montage evidence and EX_v001 preserved.

Current result: dedicated FP reconstruction with full roll, shoulder translations and documented effective limb stretch up to1.50 during offscreen load. Stronger matching screen travel/compact grip, but missing load forearm/sleeve, thinner separated central arm mass and different return blade presentation remain. User normal-speed judgment pending; not exact replication, accepted external-body motion or engine integration. No extra footage needed for this completed reference pass.

Corrective actions this pass: reference-backed key fixes for grip/return roll; severe opened-hand regression caught and fixed before final full render; comparator corrected cadence/resize filter order to retain final frames. No further artistic loop or new export/regression suite after the final actual comparison.

7 September 2026. User requested Linear decomposition and Astra light subagents; light is interpreted as GPT-6 Astra with low reasoning. Parent coordination requested at Astra High; model/effort selection is controlled by the chat settings, not a claimed tool change.

Linear owns task state. Parent: https://linear.app/meleeslasher/issue/MEL-6

| Issue | Assignment | Agent | Owned outputs |
|---|---|---|---|
| MEL-26 | Grip, stage, timing | mel26_stage | StageFreshExchange.py, EX_v001 staging source and STAGING.md |
| MEL-27 | Whole continuous exchange | mel27_animate | AuthorFreshExchange.py, EX_v001_Exchange.blend and Preview clips |
| MEL-28 | Canonical export and focused roundtrip | mel28_export | ExportFreshExchange.py and EX_v001/Export |
| MEL-29 | Independent visual review/handoff | mel29_review | EX_v001/REVIEW.md and review receipt |

Dependency order: 26 → 27 → 28 → 29. Tool preparation overlaps only where file ownership is disjoint; scene generation, rendering and export are serialized. No child subagents. CF_v001 and all existing unrelated dirty work stay preserved.

Initial staging contract: meters, +Z up, forward -Y, anatomical right -X; CF01_CharacterRig; EX01_WeaponRoot at blade base, local +Z blade axis, EX01_BladeBase/EX01_BladeTip markers. Proposed 30fps timeline: 1 idle, 13 parry, 21 riposte start, 29 contact, 37 carry, 49 return, 61 idle. Agent handoff may refine this explicitly.

Boundary: source/export evidence is not human artistic acceptance or playable acceptance. MEL-15 owns new runtime integration and second-edit replay; MEL-11 owns playable review. No broad pose matrix or regression suite for this source work.

Delivered: all four Astra Low assignments executed. MEL-26/MEL-27/MEL-29 and parent MEL-6 are In Review; MEL-28 is Done. EX_v001_Exchange.blend, two actual 30fps/61-frame MP4s, verified FBX/canonical weapon motion and independent REVIEW.md are saved under ArtSource/CharacterReset/EX_v001. Technical integration handoff is ready; continuous normal-speed artistic judgment and user acceptance remain pending. Agents reviewed sampled images, not real-time playback. Fine finger contact and FP cropping remain documented limitations.

Final export: 102/102 hierarchy, 61 frames, maximum endpoint error 3.377 µm and deformation orientation error 0.000977 radians. Source SHA-256 7069d68b8d91bba1c0e397013a220832430779f54c76d8d4c93e530a9fdedfeb. See Export/export-verification.json and Export/MEL15-HANDOFF.md for full receipts. Source preserved through export.

Corrective actions only: independent review added twist-sensitive export checks; a failed first verification required FBX import-frame-offset and reconstructed-tail convention corrections. A focused rerun passed. FP offscreen carry did not trigger an unnecessary camera regeneration because reference guidance permits clearing the view during recovery.
