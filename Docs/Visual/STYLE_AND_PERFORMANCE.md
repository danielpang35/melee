# Visual development record

Current audit: [REHAUL.md](REHAUL.md). Stage statuses below are historical; the September 6 rehaul record at the end supersedes them.

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
