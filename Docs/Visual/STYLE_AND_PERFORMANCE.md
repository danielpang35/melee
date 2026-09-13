# Art implementation and performance guide

> Derived local design/implementation reference. Notion owns product intent, reference interpretation, acceptance criteria and human decisions; this page retains implementation guidance and dated observations under [documentation ownership](../DOCUMENTATION_OWNERSHIP.md).

8 September 2026. Current guide for the confirmed original-knight/Hound direction. [Reference analysis](../MEL17_REFERENCE_ROUTE.md) owns style evidence; [rubric/audit](../ART_CRITIC_REVIEW.md) owns scores and priorities; [UI guide](UI_STYLE_GUIDE.md) owns interface rules; [animation workflow and inventory](../ANIMATION_WORKFLOW.md) own motion requirements. Everything marked target/proposed below is an implementation requirement or experiment, **not an already shipped feature or measured budget**. Older results below are retained history.

## Approved direction and priorities

**13 September 2026 update:** Daniel's Hunyuan model is now the primary surface-style authority. The [Hound surface style guide](HOUND_SURFACE_STYLE_GUIDE.md) owns the derived recipes, measured appearance palette, whole-game extrapolations and changing-lighting proposal. Preserve its broad painted color/value organization; earlier smooth-steel prescriptions below are historical where they conflict. This is art documentation and source inspection, with no runtime material replacement. The original knight remains a supporting family/form reference.

Sunlit medieval stylization: natural armored proportions, distinctive sculpted silhouettes, coherent steel reflections with deliberately shaped angular variation, dark mail/padding and muted heraldic cloth. The supplied Hunyuan Hound model governs surface style; the original full-body knight remains a supporting form/family anchor. CS2 informs foreground acuity and sunny spatial organization; Valorant informs controlled surface detail; Zelda informs economical geometric effects and contextual UI; Mordhau informs embodied weapon control. Do not import unapproved game modes, gliders, futuristic motifs or flashy Valorant effects.

Form hierarchy: major silhouette/volume first; construction overlaps, ridges and material blocks second; rivets, wear and mail detail last. Hound's projecting visor and crown should remain distinct at opponent distance. A variant can have open face, cloth coverage or rounded chest without leaving the family. Reference front/side images contain local inconsistencies and hidden construction: resolve one coherent 3D asset rather than reproducing contradictions. Facial performance/lip sync is not required by the helmeted practice slice; open-face studies do not automatically add a dialogue system.

## Asset production and ownership

| Boundary | Current owner / rule |
|---|---|
| Gameplay | `Source/MeleeCombatLab/Combat` and movement component own legal input, state, clock, world movement, swept blade contact and damage. Visual authoring never silently changes these |
| Accepted FP | `Config/EXPreview.json` and `ArtSource/CharacterReset/EX_v002`; preserve EX_v002-source-1615b76b-FBX-6a34514c-native-unreduced-v1, projection and native playback |
| TP selection | `Docs/THIRD_PERSON_CHECKPOINT.md` owns current source/candidate; `Saved/TPProof/selection.json` identifies current engine option. D_open_sweep is separate from Block13; no automatic promotion |
| Character foundation | CF_v001 and existing exporters/importers; no unsolicited anatomy reset or return to retired Citadel character |
| Material proof | `Docs/UNREAL_STYLE_CHECKPOINT.md` owns accepted USP_v016/ST material evidence. It proves a bounded material route, not a finished armored character or target-device budget |
| Exploration | Isolated versioned `ArtSource` batch/candidate folders, editable controls and small preview; render tools do not export/import/select automatically |
| Production art | Deliberately selected `Content` packages plus exact source/config/import identity; ownership stays with one source/selection owner through refinement |
| UI | Game-native Unreal presentation and localized text; developer tuning/diagnostics remain separate. See UI guide for lifecycle and source-level failures |

Before changing shared source, coordinate with current editor/owner and preserve unrelated dirty work. No full folder overwrite or deletion of unique source/evidence. Existing filenames and pipeline formats remain valid. For **new** production assets, use readable convention examples: `SK_MCL_HoundHelmet_v001`, `SM_MCL_Longsword_v001`, `M_MCL_Steel`, `MI_MCL_Steel_Hound`, `T_MCL_Hound_BaseColor`, `T_MCL_Hound_Normal`, `T_MCL_Hound_Masks`, `A_MCL_TP_RightHorizontal_v001`; include LOD suffix only when the importer uses it. These are proposed naming examples, not claims these assets exist. Keep action origin and FP/TP explicit. Avoid “final”, duplicate “latest” folders and using display names as stable asset IDs.

Each selected asset records: source and license/provenance, revision/hash, scale/axes, parent rig, mesh/material slots, texture channel meanings, expected view distance, clip bindings if any, export command/config, imported package path, cheap preview, known inferred surfaces, artist selection and human acceptance separately. Keep one manifest per selected package and one checkpoint; link supporting evidence instead of duplicating histories.

## Scale, proportions, rig and export

Use the existing Unreal centimeter world and source exporter conversion. Source character foundation is approximately 180cm in its recorded asset checks; preserve actual approved scale rather than enforcing an image-derived anatomy ratio. The original portrait's roughly 6.8 projected helmet-heights is a **projection observation**, not a skeleton ratio. Match armored silhouette and perspective before refining parts. The accepted FP source's 103.5cm blade is recorded gameplay data; a visual redesign must preserve that calibrated contact or trigger an explicit gameplay integration decision.

Keep hard plates continuously shaped with real rim thickness and plausible overlaps. Rigid-bind plates to suitable bones; skin padding/mail and flexible junctions; maintain finger/thumb articulation for the selected grip. Do not weld armor across a bending joint or treat every tonal patch as mesh triangulation. Test visor/neck/shoulder clearance in one selected exchange. Preserve CF/EX skeleton identity and author-controlled deformation, including intentional scale/stretch. Current source rig counts and imported extra root/eye nodes differ; importer manifest, not a universal guessed bone count, is the authority.

Export selected revisions through existing Blender/Unreal tools with explicit units, axis convention, evaluated transforms, skeleton/mesh identity and source timing. Preserve the accepted EX no-key-reduction contract. New clips may use compression only after a bounded visual/contact comparison; never retime the comparison to conceal a mismatch. Verify normals/tangents/UVs and material channel handling for the changed asset. The isolated steel proof uses source-specific normal fields; do not tile them over a new helmet or copy object-space normals onto a deforming surface without appropriate conversion/baking. Root motion cannot move the combat capsule.

## Palette, materials and texture hierarchy

Initial palette tokens, derived from established project direction rather than calibrated swatch measurements: warm limestone `#C9B892`, blue-gray shadow `#667785`, heraldic blue `#294A68`, muted red `#813D36`, leather `#3C2B20`, neutral cool steel, near-black padding/mail recesses. UI semantic colors are specified separately. Lighting changes their appearance; do not force flat screen RGB matches under every light.

- Steel: preserve continuous convex volume, selected sharp ridges, thin construction-edge accents and the new exemplar's broad painted cool/warm regions. Use unequal patch scales with quiet areas; retain the illustrated character of the approved model. Avoid uniform patch noise, indiscriminate grunge and blown white borders. The new guide distinguishes permanent color from reflection shapes that may need reconstruction for moving light.
- Implementation starting point: preserve the supplied Hunyuan maps as the appearance comparator. Their low metallic and high roughness values are measured source facts; a relightable steel reconstruction is a separate, unproven variant. Prior physically metallic steel and roughness .30/.23 settings are **older study-specific evidence**, not the new default. Follow the guide's bounded reconstruction proposal before changing material architecture.
- Mail: use silhouette/overlap geometry only where it matters; filter normal/color detail at distance. Dense individual ring sparkle must not beat the visor/sword for attention. Padding stays matte with large quilt/fold rhythm; leather has controlled seams and wear near use points.
- Stone: large block/bevel forms and useful occlusion first; low-contrast wear and sparse cracks second. Background microdetail must be quieter than combat actors. Cloth color acts as a broad grouping cue, not an animated neon identifier. Avoid identical repeated damage decals.
- Texture import: base color uses the existing color workflow; normal and mask data are linear, with documented channel packing and normal handedness. Preserve UV padding and correct mip filtering. Check seams on changed mesh; no claim of final texel density from concept art. Proposed starting size is 2K for a selected hero armor/FP surface and 1K for small props, reducing with distance; confirm effective screen coverage and resident memory before increasing.

## Environment, lighting, camera and effects

Build a complete **small duel space** before a grand vista. Use one memorable lane terminus/landmark, distinguish approach/combat/rest areas, and keep movement routes readable. Vary meaningful module groups, not random wall damage. Place decorative props outside the frequent attack/footwork envelope; collision and visual affordance must agree. Warm stone with cool shade and limited banners/greenery supports the fantasy. Silvermere/mountain references govern larger shapes and atmospheric depth; fog is not a substitute for distant composition and must not erase nearby threats.

Stable daylight key plus useful fill is the starting lighting model. Preserve actor/weapon separation in both sun and shade; avoid exposure pumping, deep black faces/hands, bloom halos, unnecessary depth of field and combat motion blur. Test the actual materials under relevant lighting before tuning postprocess. Native CS2 clarity is a visual benchmark, not an instruction to over-sharpen captured 360p evidence. Keep metal highlights readable, not clipped.

Primary camera is first person; defender/external view evaluates third-person threat. Preserve accepted FP projection; any proposed lens/weapon-framing change requires explicit review against it. Establish screen-space hierarchy: opponent intent/weapon → spacing/contact → own resources. UI cannot block the opponent's hands or blade to celebrate a successful defense. Assess actual body/weapon grouping, edge crop and target overlap through the entire action, not only a pleasing ready pose.

Effects are brief and event-specific: compact parry/chamber spark, hit response, grounded dust if justified. Wind-like ribbons may inspire shape economy but are not an automatic sword trail. No always-on emission, large bright particles or camera shake masking readable motion. Cap transparency/overdraw by measuring a selected scene. Provide reduced-motion and flash-intensity controls when implemented; a setting cannot remove the only available gameplay cue. Environmental water/cloth remain subordinate to combat.

Sound quality is part of the target, but no audio score was derived from silent frame inspection. Match release air, contact transient, body response, UI and optional haptics to authoritative events. Distinguish miss from impact, parry from body hit and legal opportunity from decorative flourish. Read the [animation event policy](../ANIMATION_WORKFLOW.md#event-synchronization-and-review-evidence); the PrecisionSteel_v5 audition is not proof of runtime selection. A sound designer may be needed for final transient/mix consistency; do not claim reference parity without listening in play.

## PC performance target and existing quality paths

**Confirmed user target: mid-tier PCs should achieve 100–144 FPS.** This corresponds to 10.0–6.94ms total frame time. Minimum CPU/GPU/RAM, exact resolution, team size and timeline remain unspecified. Use 1080p as a **provisional review resolution** from project history, not a newly confirmed requirement. Historical RTX 3060/4060 suggestions are candidate test machines only. Actual evidence was recorded on RTX 5070/Ryzen 5 1600/16GB in an editor-linked game; it does not certify minimum hardware or a packaged build.

Current `Config/GraphicsProfiles.ini` centrally defines Competitive, High and Showcase; `Source/MeleeCombatLab/Visual/TournamentGraphics.cpp` applies them, defaults to High at initialization unless `-LabProfile=` overrides, and cycles them. The initially declared Profile string is not the startup selection. Source settings:

| Setting | Competitive | High | Showcase |
|---|---|---|---|
| Screen percentage / AA | 100 / method2 (TAA) | same | same |
| Dynamic GI / virtual shadows | off / off | off / off | off / off |
| Shadow quality / max resolution / cascades | 2 / 1024 / 2 | 3 / 2048 / 3 | 5 / 4096 / 4 |
| Reflection method / SSR quality | 0 / 0 | 2 / 2 | 2 / 3 |
| Bloom / AO levels / refraction | 0 / 0 / 0 | 2 / 1 / 1 | 3 / 2 / 2 |
| Motion blur | off | off | off |
| Effects / postprocess tier | 1 / 1 | 2 / 2 | 3 / 3 |

These are configured values, not fresh measured performance or asset fallbacks. No runtime capability detection, persistence, automatic hysteresis, safe profile switching or device-loss recovery is claimed from this code. The project is Unreal, so the user's conditional **Three.js Low/Balanced/High/Ultra implementation is not applicable**. Do not add a parallel web rendering system. If a wider hardware range is later approved, extend the existing central Unreal profile system with real LOD/material/secondary-motion fallbacks and profile persistence after a bounded design/measurement pass.

### Proposed allocation for the selected two-combatant slice

These are starting ceilings/hypotheses, **not measurements**. Replace them with captured costs on the confirmed mid-tier device before promising 100–144 FPS. CPU game/render and GPU overlap and must not be added as independent serial budgets. The 6.94ms goal is demanding on CPU; prioritize stable 100FPS floor before claiming sustained 144.

| Area | Initial allocation / content hypothesis | Fallback preserving meaning |
|---|---|---|
| Total frame | p95 ≤10ms for 100FPS target; stretch p95 ≤6.94ms for 144, with p99/stutters reported | Reduce cosmetic cost; never slow input, attack clock or collision |
| CPU | Game thread target ≤3ms, render thread ≤3ms; animation/IK/secondary subset ≤1ms | Reuse meshes/materials, disable redundant work, throttle only distant non-threat presentation |
| GPU | Opaque environment 1.5ms; characters/FP 1.2; light/shadow 1.6; effects .35; AA/post .8; reserve1.49 =6.94ms | Cheaper background shading, fewer cosmetic transparent layers, conventional shadows |
| Visible geometry | Start around 200k character/FP triangles and 500k environment triangles per duel view; ≤300 draw calls | Character silhouette/grip first; environment instancing; test LOD by projected size rather than fixed arbitrary meters |
| Rig/animation | Reuse current approximately102-bone source foundation; two nearby bodies plus FP; no immediate-threat throttling | Authored secondary bones, fewer distant layers; keep attack/weapon/event sampling coherent |
| Textures | Typical hero maps2K, small props1K; initial art texture residency target≤512MiB | Correct mips/LOD, reduce background maps first; actual pool/VRAM ceiling needs hardware measurement |
| Lighting | One primary shadowed sun, no required shadowed effect lights; existing profile resolutions | Bounded shadows; material readability without SSR dependence |
| Effects | Few short contact bursts, initial≤128 live cosmetic particles in duel; transparency cost measured | Mesh/sprite alternatives and reduced density retain hit/parry distinction |
| Memory/loading | Track process/VRAM peak, loading hitches and asset residency; no verified RAM/VRAM ceiling yet | Small slice preload, shared instances, explicit ownership/release of transient effects and previews |

The isolated USP_v016 helmet proof is roughly64k triangles with16 parts/slots in its receipt. That demonstrates a material-transfer workflow, **not a final per-helmet allocation**. Do not multiply that cost across a full armor roster. A bounded production topology/material-slot pass must retain its silhouette and reflections at gameplay size. LOD screen thresholds and texture budgets are unmeasured until the actual asset exists; propose thresholds only with comparison evidence. Do not equate geometric triangle count alone with performance.

Selected quality-path review: same camera/time, same gameplay inputs, unchanged hit timing and UI across profiles. Capture cold start, ordinary duel, highest approved pressure, particles/shadows, locomotion/animation load, menu open/close, resize, background/resume and profile switching on actual supported devices. Device/context-loss recovery is an explicit unverified scenario. Record unsupported cases and a player-readable failure path; no raw error on the player surface. This is integration acceptance coverage, not a recurring draft animation matrix.

## Review, extension and troubleshooting

Follow the existing cheap candidate loop: 3–6 distinct whole-motion hypotheses, consistent 1x preview, select/refine, then integrate only the winner. For art, review form and hierarchy at gameplay distance before dense texture polish. One meaningful affected-view check beats an all-camera sweep. Broader testing occurs only for actual changed contracts; C++ builds/tests are required only when changed. Human visual/play acceptance stays separate from scores and hashes.

Symptoms → first useful check: plastic metal → lighting/roughness/normals on unchanged shape; crowded patches → reduce small high-contrast regions, retain authored large shapes; blurred weapon → inspect native target-resolution source and AA before sharpening; floating feet → compare actual velocity/planted contact, not pose stills; stab-like horizontal → whole hand/blade/body choreography, not elbow-only tuning; misread parry → blade/actor/UI overlap and shared event timing; poor FPS → frame-time/thread/GPU trace on identified hardware, not historical mean FPS.

Implementation plan and owners are in [the audit](../ART_CRITIC_REVIEW.md#prioritized-improvement-plan). No production code, asset promotion, quality-profile implementation or game launch was performed for this documentation task. The guide specifies future work and accurately records current settings. Preserve existing source, diagnostics and unresolved tests. Do not commission specialists or expand production scope automatically.

---

## Historical visual development record (superseded implementation/status prose)

The following September6 record is retained for provenance and its explicitly labeled measurements. Some linked captures were later removed at the user's request; [capture retention](Captures/README.md) owns that fact. Old claims that Content was empty, broad validation prescriptions and old character baselines are historical, not current instructions.

Current audit: [REHAUL.md](../Archive/2026-09-07/Docs/Visual/REHAUL.md). Stage statuses below are historical; the September 6 rehaul record at the end supersedes them.

Style: Sunlit low-fantasy tournament. Warm limestone (#C9B892), shadow blue-grey (#667785), muted heraldic blue (#294A68), red (#813D36), leather (#3C2B20), weathered steel (neutral cool grey, roughness 0.35â€“0.5). Stable exposure; no persistent combat-obscuring effects.

## Provisional Competitive budgets at 1080p

These are allocation goals, not measured costs. Total frame budget: 6.94 ms. CPU game thread should remain below 3 ms, render thread below 3 ms; CPU/GPU overlap means these are not additive.

| System | GPU allocation | Content ceiling / fallback |
|---|---:|---|
| Courtyard opaque geometry/materials | 1.5 ms | Shared instanced modules; primary lanes uncluttered |
| Two knights and first-person presentation | 0.8 ms | Approximately 15k visible triangles/knight; <=32 render components/knight; shared meshes/materials; coarse distance meshes |
| Lighting and shadows | 1.6 ms | One shadowed sun; conventional shadows in Competitive; no Lumen dependency |
| Fountain and combat particles | 0.35 ms | Opaque water in Competitive; bounded streams; combat sparks prioritized |
| Post process / AA | 0.8 ms | TAA, stable exposure, no motion blur, restrained bloom |
| Engine overhead / reserve | 1.89 ms | Profile before consuming reserve |

## Baseline method

`Tools/Benchmark.ps1 -Label stage1-baseline -Profile Baseline` launches an isolated Development Editor executable in game mode at forced 1920x1080, no VSync or frame cap. Route v1 runs six seconds of warmup and 24 seconds of sampling through the duel lane and fountain ring at 154 cm eye height. It records raw frame samples, stat-unit thread/GPU counters, RHI draw calls/primitives, working-set memory, settings and hardware. Three screenshot frames remain in the sample and may create tail spikes. Raw CSV and Unreal CSV profiler captures are retained. Compare this identical route on every visual stage and profile.

The local RTX 5070 is faster than the target GPUs; Ryzen 5 1600 is older/slower than a modern six-core CPU. Measurements are local observations, not a 144 FPS certification for RTX 3060/4060 hardware. Executable remains editor-linked until a packaged target is measured. GPU pass cost is unavailable if the engine does not emit per-pass counters; do not replace missing measurements with zeros or estimates presented as facts.

## Local asset audit

Project Content folder was empty. Installed Epic UE 5.8 templates contain mannequin/XR assets, but no knight or armor asset was found in the inspected template library. No external asset is downloaded. The first pass will use original procedural modular geometry and UE-provided basic primitives. Remaining production asset gap: authored medieval knight skeletal mesh, baked normal details, skin-weighted gloves, and custom animation polish.

## Stage status

1. Baseline profiler and independent combat regression fixture implemented; measurements pending.
2. Courtyard blockout pending.
3. Modular knight and matching arms pending.
4. Shared materials / sunlight pending.
5. Fountain detail / ambient audio pending.
6. Graphics profiles / measured optimization pending.

## Extension rules

Preserve portable combat files and saved tuning during visual work. New render components have collision disabled; only explicit environment blockout shapes collide. First-person blade hilt/tip remain exactly the simulation endpoints. Save before/after screenshots and same-route data per bounded change, run the native suite, Unreal automation, and the combat tour, then update this record. Never infer target-tier performance from this GPU's uncapped FPS.

## Stage 1 observed baseline

1920x1080, Development Editor executable -game, RTX 5070 / Ryzen 5 1600 / 16 GB. 3,043 samples: mean 7.887 ms (126.8 FPS), p95 9.990 ms, p99 11.258 ms. Stat-unit raw game/render/GPU means 4.946 / 7.200 / 1.013 ms. Thread timing can include waiting; these values are not independent additive CPU costs. Mean RHI draw calls 124.8, primitives 13,202. GPU CSV scopes (whole capture including warmup): base pass 0.050 ms, shadow depths 0.053 ms, shadow projection 0.019 ms, translucency 0.011 ms, postprocessing 0.156 ms; local GPU memory 636 MB. Nested scopes are not additive. Raw records and screenshots: Saved/VisualPerformance/stage1-baseline. CPU-side work and draw calls warrant attention; GPU headroom on this above-target GPU is not a target-tier certification.


## September 6 rehaul — current measurements

1920x1080, RTX 5070 / Ryzen 5 1600 / 16 GB, UE 5.8 Development Editor executable
in game mode. Route v1 unchanged: 6 s warmup, 24 s sample, three screenshot
frames retained, uncapped/no VSync. Profiles were run sequentially with no other
lab or build running. These are single-run local observations, not target-tier
certification or statistically established differences between High/Showcase.

| Scene / profile | Mean frame ms | FPS from mean | p95 ms | Game ms | Render ms | GPU ms | Draw calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| Before / Competitive | 5.614 | 178.1 | 7.746 | 4.080 | 5.244 | 0.831 | 174.3 |
| After / Competitive | 5.855 | 170.8 | 7.799 | 4.099 | 5.399 | 0.884 | 211.4 |
| After / High | 6.186 | 161.7 | 7.980 | 4.200 | 5.712 | 1.095 | 232.9 |
| After / Showcase | 6.122 | 163.3 | 7.705 | 4.180 | 5.649 | 1.204 | 234.9 |

Game/render/GPU counters are raw stat-unit values, can include waiting, and must
not be added together. High and Showcase are close in total frame time despite
Showcase's higher GPU cost; this is consistent with CPU limitation and run
variance. Competitive p95 remains above the 6.94 ms budget, so a stable 144 FPS
claim is not justified even though the local mean exceeds 144 FPS.

The first final-art Competitive capture was 7.429 ms (134.6 FPS). Inspection
found that recursively setting unchanged body visibility dirtied all child
render states every frame. Updating only on visibility transitions reduced the
same scene to 5.855 ms (170.8 FPS), versus 5.614 ms (178.1 FPS) before the rehaul.
The final scene renders the player's body in external views in addition to the
two original dummies. This adds visible geometry to the baseline comparison.

Final generated library: 12 material/texture assets, approximately 229 KB on disk
before cooking. Body has 22 render components, equipment/arms 12, total 34 per
external knight, slightly above the provisional 32-component ceiling. Next
optimization: combine static helmet/torso detail or use an authored skeletal
mesh. No heavy translucent fountain effect or additional shadow-casting light
was added. Existing graphics tiers remain available through F7.

The initial `rehaul-after` capture used failed material shaders and is explicitly
an intermediate diagnostic, NOT the delivered visual result. `rehaul-final-*`
records precede the visibility optimization. Delivered measurements are
`rehaul-optimized-*`; raw frame CSVs and route images remain under Saved/VisualPerformance.
Portable summaries and before/after images are preserved in Docs/Visual/Captures.
Per-pass GPU scopes, packaged build validation and RTX 3060/4060-tier results
remain outstanding; no GPU-pass allocation is presented as measured here.

Final screenshots were inspected at Competitive and Showcase settings. Material
compilation, missing instancing flags, unbuilt reflection capture and courtyard
attachment warnings seen earlier in the pass are resolved. Remaining visible
limitations include procedural rigid joints, simple cloth panels, generic
micro-textures, no authored locomotion/finger animation and basic fountain
geometry. The artwork is a stronger fallback and integration foundation; the
premium rigged-character stage remains necessary.
