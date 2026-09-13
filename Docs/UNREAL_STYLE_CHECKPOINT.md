# Unreal style proof checkpoint



## Implementation completed — 8 September 2026



User authorized enacting the six-package MEL-17 plan with subagents. Source/material owner, engine technical owner and independent art critic are assigned bounded work without child agents; heavy renders/imports remain serialized. Linear MEL-17 was read as In Progress; no remote state was changed. Existing unrelated workspace edits are preserved.



P1 `SteelTransfer/ST_v002` preserves the accepted evaluated geometry and construction normals (61,132 metal triangles) and both accepted source hashes. Actual source A/B stills are under `Saved/ArtReview/UnrealStyle/ST_v002/Review`. The prior ST_v001 is retained as failed evidence: stepped region boundaries scored variation 6. Corrected continuous plate charts receive independent scores steel 8, variation 8, edges 8 and shape transfer 9. Finalization records exact accepted-comparator pixel equality and a direct construction-only/zero-influence comparison with maximum 1/255 difference and zero pixels over 2 levels. Original-reference/native comparison and a fully decoded 36-frame, 18 fps fixed-light source rotation are delivered. The critic inspected eight rotation samples plus adjacent frames 15–17; rotation was sampled, not played. P2 passes for P3, without temporal-stability or user material acceptance.



P3 corrected `UnrealProof/USP_v016` completed from finalized ST_v002: 64,108 triangles, 32,086 vertices, 16 explicit parts/slots, 35 cm proof height, frozen blend/FBX, 2K N0/N1/masks and a compressed full triangle-corner render contract. Actual UV occupancy is 1,164,266 pixels (27.76%), with 8-pixel padding; endpoint unit errors are at most 2.384e-7. Preparation/bake logs and `export_receipt.json` are under `Saved/ArtReview/UnrealStyle/USP_v016`. Manifest SHA-256: `bba0a5b9de8ea7124c1d806f68754fb58ae42ea712d3ac25478bddab79a90818`. Actual import and user acceptance are recorded below.



P4 actual built LOD0 buffers verify all 64,108 triangles/192,324 corners: max position error 1.35e-6cm, UV 2.98e-8, normal 0.001453deg, tangent 0.001470deg; exact signs and slots pass. UE 5.8 ProceduralMesh inspection reads sign from TangentX.W instead of stored TangentZ.W, so ReadUnrealRenderFBX.py reads actual render-data FBX (export_source_mesh=False). Source parser smoke data is explicitly non-Unreal. The import succeeded and saved all assets; immediate startup shutdown then crashed in editor-mode teardown. Importer cleanup now defers120 ticks; the v017 import verified clean shutdown with that correction.

Neutral ordinary PIE run_002 completed five fully decoded 1525x870 PNGs with clean exit; actual square camera area is870px. Independent P4 scores: form9, seams/bevels8, response8, neutral steel8; pass to P5. Daylight/motion/shade run_003 completed186 validated PNGs with clean exit. All three60-frame sequences have consecutive request frames, next-frame completion and fixed30fps timestep. Three videos fully decode60frames each; one black padding column accommodates odd viewport width without rescaling. Critic daylight/sample scores: material8, reflection/color8, restraint8, distance8, form9. Gameplay helmet bounds x705-820/y353-523 inclusive measure171px tall. This is a declared proof scenario, not general gameplay-distance approval.

The critic inspected all180 motion frames as contacts and six full-size PNGs; no model MP4 playback is claimed. The user subsequently explicitly answered "Accept material and motion" after receiving all three clips. user_acceptance.json binds that answer to exact capture/video receipts. P5 human material/motion acceptance is complete. P6 winning USP_v016 combined/Environment_v005/Stage_v003 map saved successfully with clean exit and winning_state.json. P6 isolated ST_v003 to USP_v017 edit/reimport completed. Only left wrapping brow region7 target changed by6 degrees; geometry/UV/split normals and roughness masks match baseline. All N1 changes above1 LSB are localized; tiny one-level numerical differences are recorded. Actual smooth controls differ by at most2 RGB levels, while the authored difference is confined to the target brow. USP_v017 run_002 exited cleanly after capture cleanup was corrected to let queued PIE teardown finish. Final read-only restore selected USP_v016, verified actual component/camera/settings equality and left all77 baseline assets byte-identical. Earlier stage-helper restores reserialized one unchanged warm stage material; the helper now skips redundant writes and read-only mode forbids mutation. repeatability_receipt.json binds the result. Delivery review/archive includes sources, scoped assets, tools and receipts; no broader character/global rendering changes were made.

Unreal import of v014 stopped on 44 undefined source tangent corners. Corrected v016 supplies a finite signed frame at every corner without changing geometry/UVs. N0/N1 emission bakes invert Unreal's actual nonorthogonal interpolated frame, verified against UE 5.8 `MaterialTemplate.ush`/`LocalVertexFactory.ush` and an analytic reconstruction test. FBX contains only TransferUV, while the frozen editable blend retains ST_SurfaceChart; this avoids Blender's last-UV tangent-cache export behavior. Reparsed binary FBX tangent/binormal arrays exactly match all 192,324 frozen corner frames. Failed v015 retains its maps/log after a writer-array count guard failed. Do not reuse v014's maps or render contract as validated engine input.



Preserved failed preparation revisions v012/v013 exposed split-normal quantization and 1.788e-7 tangent recomputation noise. Exact construction normals now feed both endpoint bakes through a frozen corner attribute; a hashed tangent snapshot is checked exhaustively with 1e-6 component tolerance and exact signs. Geometry/triangle/UV/split-normal fingerprints remain exact. No accepted source changed.



Implementation tooling now includes complete PNG decoding/CRC/dimension/nonblank checks, receipt/file/hash binding, mandatory complete/consecutive motion evidence, and a compact `transfer` still capture set. Six focused capture tests pass. Schema-v2 preflight/render-contract validation has fourteen passing tests and one Windows symlink-permission skip; the actual legacy USP_v001 package also passes explicit legacy preflight. Independent technical review addressed receipt binding, cleanup, finite timestep checks, source foundation, actual UV occupancy and imported corner verification. Actual import/capture verification and human acceptance are recorded above. Efficiency correction: run only the source still correction before rotation or engine launches; reject incomplete motion instead of treating numbered held poses as temporal proof. Reuse validated maps for export-wrapper-only corrections rather than introducing another unchanged bake.



## Planning delivery — 8 September 2026



The [implementation plan](MEL17_UNREAL_STYLE_PLAN.md) now defines six sequential packages with concrete tool changes, outputs and gates: editable plane-target steel source → accepted-rig material proof → frozen UV/tangent bake → scoped Unreal transfer → daylight/motion/shade/distance → accepted packaging and edit/reimport. Two bounded planning agents supplied source/material and engine architecture findings; one independent plan review found no actionable defects. The selected bake contract preserves a construction-normal foundation and a complete authored endpoint; intermediate runtime blending is diagnostic, not equivalent to source influence. Historical handoff instructions are labeled accordingly. Linear MEL-17 was read as In Progress; no remote write, new variant, render, engine run or fresh visual acceptance occurred. Next visible deliverable remains the accepted helmet/armor steel comparison. Documentation references were checked; no build or gameplay test was needed.



## Latest user direction — supersedes provisional scores



8 September 2026: the user explicitly accepts Clay_v005: "Looks very nice. The shape is quite perfect." The geometry gate is closed. Preserve `GeometryReview/Clay_v005/Helmet_Clay_v005.blend` (SHA-256 `a9937b6b9cb04973a4a3b4b383f4a635c55e63c2241f737e9f573489a631c263`) as the shape authority and Steel_v025 as the material authority. The current request is to plan next steps; no new production variants are made by this planning update. The updated sequence is in `Docs/MEL17_UNREAL_STYLE_PLAN.md`: source preservation/export preparation → faithful steel transfer and accepted-rig comparison → bake/scoped Unreal proof → daylight, movement and shade → material review. The older blockiness rejection applies to superseded helmet sources, not Clay_v005.



The completed Unlit diagnostic (`USP_v011/run_004`) was rejected: surface3.5, steel/reflection2.5, native4.5, matte/resin appearance. No custom-renderer integration is justified by it. Source audit identifies a material-transfer mismatch: accepted Steel25 targets connected constant plane normals, whereas current additive fields retain underlying normal curvature. The accepted armor itself should remain unchanged.



## Geometry rebuild packet — current work



`ArtSource/StyleReference/MEL17/GeometryReview/Clay_v005/` contains the rebuilt editable source, actual matte front/matched three-quarter/side/rear views, and a ten-second fixed-light turntable (180 frames at 18 fps). `Review/review.html` includes the unchanged portrait crop and a uniform crown-to-chin native-size comparison. Independent scores progressed 5/6 → 6.5/6.5 → 7/7 → 7.5/8 → 8/8 for resemblance/craftsmanship. The critic retained **8/10 in both categories** after inspecting eight rotation samples, with no major correction requested. The critic inspected sampled geometry, not video playback or all frames. The user subsequently accepted the shape; materials and Unreal behavior remain unscored. All earlier sources and critiques are preserved. The original packet's pending-human-review wording records its delivery-time status; preserve its hashes and use this checkpoint for current acceptance.



Geometry now has gently convex peaked crown panels, a physical angular roof/brow overlap, wrapping slit with real plate thickness, compound cheeks, a central keel, chin returns and seated side/hinge overlaps. The rear is inferred. Source audit reports 61,132 evaluated metal triangles with zero degenerate faces or loose vertices. All 11 Steel_v025 files were hash-checked unchanged. Source units are proportional study units; runtime scale, UVs/tangents, steel transfer and Unreal validation remain later work.



The local plan's stale material-first deliverable and planning pause were corrected. Notion chosen-direction content and supplied/global AGENTS instructions were reviewed during the rebuild; the user's geometry instruction superseded Notion's older planning pause. One modeler and one independent critic were reused. Full rotation was deferred until known shape/construction defects were corrected, avoiding repeated animation renders. OptiX startup produced no frames during kernel compilation; the completed rotation uses the proven Cycles CPU route. Human shape review is now complete; the next planned deliverable is a faithful steel transfer comparison under the accepted armor rig, before Unreal validation.



## Authority reviewed



8 September 2026: user requests implementation of the Unreal integration plan, with delegated production and an independent expert 3D art critic. Read the supplied AGENTS instructions and `C:/Users/Daniel Pang/.codex/AGENTS.md`; no ancestor AGENTS.md was found in this checkout. Existing unrelated working-tree changes are preserved.



Notion pages fetched: [project bible](https://app.notion.com/p/3d32e3c3f8f88166821dcab5f044efa2), [Visual Direction](https://app.notion.com/p/3d32e3c3f8f881dabc3be8eff5b29360), and [Chosen Art Direction — Playable Slice Implementation Brief](https://app.notion.com/p/3d42e3c3f8f881abb5c1c356dc68ee07). Relevant source: `Docs/MEL17_UNREAL_STYLE_PLAN.md`.



Decisions: original portrait remains the shape anchor; smoother Steel_v025 is accepted; Helmet_v009 is a starting shell, not a reference match. Build an isolated Unreal helmet proof with real captures, controlled comparisons, editable sources and honest per-criterion review. Broader character production stays behind the existing exchange/user gates. Notion defers dedicated broad benchmarking; collect proof settings and asset costs now, without turning this into a full performance campaign.



## Implementation evidence



Latest geometry evidence: `Saved/ArtReview/UnrealStyle/USP_v011/run_001/`. Critic provisionally scored visible static construction8 and native geometry7.5; the user's subsequent blockiness rejection above supersedes the proposed mesh freeze. Latest lit surface evidence (`USP_v010/run_001/`, same maps) remains surface4, reflections5.5, native4.5; motion unscored. Stage_v003 moves the black opening clear of the limestone helmet backdrop. The prior 18-degree camera is retained as a comparison baseline, subject to the new reference construction analysis. Cubemap angle -90 degrees corrects the verified UE 5.8 long-lat import offset. The saved scoped GameMode spawns no pawn and activates the proof camera in PIE. These are technical successes, not whole-proof acceptance.



USP_v005 corrected slit protection and added one cheek field. Strength2 produced soft dents and was rejected. USP_v007's .10 feather instead of .32 produced little aesthetic gain. Actual `USP_v007/run_002/WorldNormal_*` proves coherent field transfer: sampled cheek interior changes consistently while adjacent outside/wall samples stay unchanged. This closes a runtime transfer question, not the full handedness/seam or artistic gates. A read-only unfiltered reflection-ray approximation finds only .011 mean environment luminance change across active cheek interiors; Environment_v005 therefore tests stronger local lower reflection gradients at unchanged upper colors and lower luminance range. Compare old normals/new control/new normals before further material changes.



USP_v008 replaces the subpixel near-coplanar brow ribbon with a continuous 2.60 mm forehead plate return (11,466 triangles, new UVs, .063 mm slit-position normalization drift reported). Critic retained it at shape7.5 before the later temple work. Source hashes are validated; this did not establish whole-proof or motion acceptance.



USP_v011 corrects the hinge face orientation after v009 exposed only its edge. Both facets pass36/36 source visibility rays; actual matte capture confirms their visible construction. USP_v010 replaces two closed cheek patches with edge-connected polygons. Actual whole-cheek WorldNormal A/B proves a broad left tilt survives (17.6% changed above stated RGB threshold after seam/ridge exclusions), while current Env5 supplies only .001 approximate unfiltered radiance change over the moved fields. Repeated standard-lit tests have demonstrated transfer but not fidelity. The critic authorizes the plan's one isolated stylized-response diagnostic now, preserving the standard-lit fallback. Scoped Unlit output must be explicitly labeled as lacking automatic scene-shadow/reflection integration; it cannot receive production acceptance from an attractive still.



Source USP_v001 is exported: 35 cm assembly, 9,488 triangles, four original source materials, 2K DirectX tangent normals and linear packed masks. Sparse authored regions cover 7.59% of sampled mesh UV area. Exact source/export hashes and source validation are in `ArtSource/StyleReference/MEL17/UnrealProof/USP_v001/manifest.json` and `validation.json`. UV occupancy is 33.2%; this is a proof atlas, not a finalized production layout. Unreal handedness/seam validation remains open.



Independent initial critic: existing Helmet_v009 studio result is 4/10 reference fidelity, separately shape 5, surface 3, reflection/color 4; motion unscored. `Docs/UNREAL_STYLE_CRITIC.md` identifies projection, crown/brow construction, sparse normal transfer and daylight reflection masses as the next work. Those initial scores concern the studio baseline only.



First actual unobstructed PIE images: `Saved/ArtReview/UnrealStyle/USP_v001/run_003`. Critic scored shape 5, surface 3 (visibility limited), reflections 1; motion unscored. These show a black lower faceplate and studio reflection streak. Subsequent receipt inspection found positional `Rotator` arguments produced the wrong key orientation, and the default black lower sky hemisphere suppresses ground reflections. Correct the constructors with named pitch/yaw/roll, disable the solid lower hemisphere for the authored environment, and compare under a verified identical key. Run 003 is actual rendered diagnostic evidence, not the intended final daylight setup or a definitive material limit. Runs 001–002 remain failed capture setup diagnostics.



Actual UE 5.8.2 import succeeded: `/Game/Visual/StyleProof/USP_v001/L_HelmetStyleProof`, four preserved slots with control/normal/combined variants, imported height exactly 35 cm. Initial 20 saved assets total 919,328 bytes on disk (not texture residency or measured GPU cost). Imported FBX and both texture hashes independently match the source packet. The manifest gained documentation hashes after import; retain the original receipt hash and record that metadata-only difference rather than rerunning unchanged assets. Unreal classifies FBX nodes containing USP as sphere collision; corrected the internal node to `SM_Helmet_StyleProof001`.



Notion implementation section appended to the art brief and fetched back successfully. It preserves the historical shell score while clarifying the later reference mismatch and current Unreal scope.



## Coordination



- Technical architecture/integration: Astra High; importer, saved map, controlled PIE captures and verified UE API behavior.

- Source author and independent art critic: separate Astra Low agents, reused for their bounded revisions; no child agents.

- PM: authority, reflection-field authoring, acceptance criteria, sequencing, technical review and evidence packaging.

- Efficiency correction: inspect novel UE property aliases before another engine launch; preserve setup failures without treating them as artistic candidates. Reuse unchanged source hashes and geometry evidence instead of rebuilding C++ or running broad combat tests.

- Efficiency correction: use occlusion-aware projected face visibility for localized construction, not silhouette size alone. After repeated weak material variants, inspect actual normal buffers and reflection response before further tuning; switch the responsible mechanism when evidence warrants it.



## Acceptance



Actual Unreal control and authored material comparison first. Separate shape, surface, reflection/color and motion/distance judgments; each applicable criterion must reach 8/10 before calling the proof artistically satisfactory. User acceptance remains separate. No broad armor expansion from a successful import or a flattering still.



# Review and verification



Updated 7 September 2026. **Speed is key:** deliver visible results; no automatic pose matrices, all-camera captures or repeated broad test runs. The CF_v001 source/export study and review package are delivered; further pose testing is not a prerequisite for finishing that task.



Normal-speed review and play establish weight, rhythm, intent, visibility and control. Technical checks establish their narrower contracts. Neither implies the other; do not claim human acceptance from metrics or generated footage.



## Smallest useful check



- Artistic edit: review the changed motion and the specific visible issue.

- Export/playback change: verify source intent, rig/scale/time and a second edited revision in the engine.

- C++ gameplay/contact change: build and run affected state/contact tests.

- Documentation or cleanup: verify paths, references, retained dependencies and actual remote updates; no engine rebuild.



## Audit checkpoint — not a fresh engine acceptance



The 7 September audit copy passed 917 core checks with AddressSanitizer, 46 movement checks, 322 audio checks with AddressSanitizer, authored-performance tests and mocked Cascadeur loader contracts. PresentationOnly failed hand swivel continuity; SwingOnly failed a late-arc hit/miss fixture. Later checks in those failing suites were not reached. Do not weaken assertions or call the whole project validated.



Run Tools/TestCore.ps1 with the relevant suite switch, or Tools/TestCombatAudio.ps1 for affected audio routing. Inspect Unreal automation's completed report, not exit code alone. Broad regressions belong at justified integration checkpoints, not every pose edit.



## Candidate state



RC_v008/module 1019: historical technical implementation, overall visual approach rejected. CF_v001: delivered character/source/export candidate, artistic acceptance and game integration pending. Neither is an accepted authored exchange.



Keep one short acceptance record: candidate/source/config/module identity, actual review artifact or runnable instructions, technical result, human decision and next visible issue. [Current development](Docs/DEVELOPMENT.md) owns next steps; [cleanup](Docs/DISCARDED_ITEMS.md) records recovery. Historical counts remain in Docs/Archive and are not current-build acceptance.

# Current development — fresh character and whole exchange



Updated 7 September 2026 after coordination with the character agent. **Speed is key.** Deliver visible results through short iterations; no automatic pose matrix, broad capture sweep or repeated diagnostics. Quality is judged in the result, not assertion counts.



## Now and next



- **MEL-25 — In Review:** CF_v001 editable character, FBX and review sheets are delivered. The source/export study is complete; artistic acceptance and game integration are not established. Do not restart testing the finished delivery.

- **MEL-6 — Todo:** author idle → parry → right riposte → carry → return as one body/hand/weapon performance. Use the fresh foundation and concise normal-speed feedback. Tool choice is open.

- **MEL-15 — Backlog:** integrate the new performance through minimal skeletal playback and canonical weapon data. Reuse export knowledge, not the old 20-bone/271-frame constraints or substantial runtime correction stack. Replay a second edit without recompiling C++.

- **MEL-11 — Todo:** review the resulting playable exchange, preserve responsiveness and readable contact, then decide whether to expand.



MEL-13 expands to opposite horizontal and overhead only after that decision. Broad art, audio, profiling, additional weapons/maps and multiplayer production remain deferred. MEL-14's old-mesh shoulder repair is canceled as superseded, not fixed.



## Retained design



Keep weight, satisfaction, responsive legal input, spatial manipulation and a single authoritative combat transaction. Coauthor canonical weapon motion with the body; gameplay samples it for collision and damage. FP/external poses may differ while communicating the same phase, threat and contact result. Do not inherit rejected mesh proportions, hand offsets, weapon fittings or guide paths.



## Status and evidence



RC_v008 and the follow-up module 1019 were technically implemented but the user rejected the overall visual result. The old lab is retained for regression and comparison, not further polish. [Legacy integration](RIGHT_CUT_INTEGRATION.md) describes it; [cleanup](DISCARDED_ITEMS.md) records removed items and recovery.



[Character reset](CHARACTER_ANIMATION_RESET.md) and [CF_v001 review](../ArtSource/CharacterReset/CF_v001/REVIEW.md) describe the new foundation. [Review policy](../VALIDATION.md) separates technical evidence from visual acceptance. [Agent alignment](CLEANUP_AGENT_ALIGNMENT.md) records ownership and protected paths.



Use focused checks for an actual defect or changed contract. Preserve the audit's unresolved PresentationOnly hand-continuity and SwingOnly late-arc failures; investigate when the relevant retained/integrated path is changed. Do not weaken assertions or call the whole project green.



Linear owns task state; Notion owns design. Preserve candidate identity and a brief decision at useful checkpoints. Serialize heavy builds/imports/captures and avoid broad regeneration.



Final delivery: `Docs/MEL17_IMPLEMENTATION_HANDOFF.md` and `Saved/ArtReview/UnrealStyle/USP_v016/Review/review.html`. Efficiency corrections: reuse byte-identical retry images for visual comparison; do not re-save an already-correct stage material on every frame/restore; encode UTF-8 checkpoint text before touching its destination. No additional broad tests or character production were launched.
