# Visual quality rubric and current-game audit

> Derived local design/implementation reference. Notion owns product intent, reference interpretation, acceptance criteria and human decisions; this page retains implementation guidance and dated observations under [documentation ownership](DOCUMENTATION_OWNERSHIP.md).

8 September 2026. Daniel confirmed the [target direction and reference roles](MEL17_REFERENCE_ROUTE.md). Policy MCL-DEV-2026-09-08 applies. This document owns the rubric, dated assessment, state coverage and improvement priorities. [Art implementation](Visual/STYLE_AND_PERFORMANCE.md), [UI implementation](Visual/UI_STYLE_GUIDE.md) and [movement/animation inventory](ANIMATION_WORKFLOW.md#finished-slice-movement-inventory) own production requirements. The earlier study-only critic notes at the bottom are historical and cannot impose repeated review/render gates.

## Result and limits

**13 September 2026 reference update:** the [Hound surface style guide](Visual/HOUND_SURFACE_STYLE_GUIDE.md) now defines the primary surface target, including painted appearance and selective reflection reconstruction. Existing scores below remain dated comparisons against the earlier reference set. Do not use older smooth-steel preferences to reject fidelity to the newly approved Hunyuan exemplar, and do not infer new scores or runtime acceptance from its documentation.

**Provisional AAA visual-readiness index: 3.1/10 for the assessed gameplay presentation, against 8.4/10 for the category-matched approved reference composite.** This is a visible-presentation comparison, not a claim about AAA budget, team, content volume or production scope. It is not a shipping certification. A complete-game score is unavailable: locomotion, temporal integrity, complete menus and several critical state transitions lack adequate evidence. Scores are judgment anchored to visible evidence; decimals in the aggregate do not imply measurement precision. Plausible reviewer variation is roughly one point per category.

The strongest isolated accomplishment is the accepted helmet/steel proof. It is **not present on the gameplay characters in the assessed recordings**, and is excluded from the aggregate. The weakest observed critical state is the close defender attack/parry exchange: overlapping foreground blades, crowded opponent hand poses and central outcome text compete for the information needed to defend. The largest persistent visual identity gap is the unarmored gray character and plain white weapon in a game targeting crafted steel/mail/cloth.

This assessment reuses current documented presentation-package evidence, not fresh live play. The FP capture is bound to EX_v002, module `470DD1F3...`; the TP capture is Block13 `47a71a84/dd9f6fbd8721`. Current selectors were read and identify those asset revisions, but this does not prove the current DLL, saved tuning and full running scene match the old captures. The newer D_open_sweep source draft is separate and not promoted. Do not relabel these findings as a fresh benchmark of every dirty source change.

## Evidence register

All local recording timestamps below start at recording time zero; simulation event times in receipts have a warmup offset and must not be substituted for video times.

| ID | Evidence actually inspected | What it can establish |
|---|---|---|
| G-FP | [Nine gameplay frames](Visual/Captures/QualityAudit20260908/G-FP-overview.jpg), from `Saved/MEL15/EX_fp_review.mp4`; 640x360/60fps, 14 seconds; samples 0, .8, 1.15, 3.967, 6.5, 9.5, 10.783, 11.3, 13.45s | Coarse composition, rendered surfaces, UI, poses and sampled consequences; not target-resolution sharpness or continuous rhythm |
| G-TP | [Nine defender frames](Visual/Captures/QualityAudit20260908/G-TP-overview.jpg), from `Saved/MEL15/TP_block13_defender_v001.mp4`; see manifest for decoded dimensions; samples 0–6s | Block13 threat/pose/foreground relationships; not a new candidate selection |
| G-MAT | [Accepted isolated close proof](Visual/Captures/QualityAudit20260908/G-MAT.png) and [distance view](Visual/Captures/QualityAudit20260908/G-MAT-DIST.png), USP_v016 | Visible metal volume, visor and reflection treatment. Technical study stage/background is not a game environment |
| G-DRAFT | [D_open_sweep source strip](Visual/Captures/QualityAudit20260908/G-DRAFT.jpg) | Whole-action pose sequence, source frames 19–151; small dark preview, no continuous-motion or integration claim |
| R-KN / R-H | [Original knight](Visual/Captures/TargetVision20260908/original-knight.png), [Hound Bascinet](Visual/Captures/TargetVision20260908/ArmorStudies/11-hound-bascinet.png) and 15 companion studies | Confirmed concept/style targets, not AAA runtime evidence or exact mechanical plans |
| R-CS | [Anubis](Visual/Captures/TargetVision20260908/anubis-overview.jpg), 0–32.32s; [Mirage](Visual/Captures/TargetVision20260908/mirage-overview.jpg), 0–9.26s | First-person foreground finish, sunny geometry, HUD, objective and outcome presentation |
| R-V | [Valorant](Visual/Captures/TargetVision20260908/valorant-overview.jpg), 0–19.78s | Surface simplification, HUD and outcome hierarchy. Exclude flashy VFX, montage blur and subscriber overlay as targets |
| R-Z | [Zelda](Visual/Captures/TargetVision20260908/zelda-overview.jpg), 0–47.27s; full-frame 11.818s glider inspected | Stylized forms, subtle motion ribbons, contextual prompts, dialogue and saving notice; no inventory/settings evidence |
| R-M | [K14-03 native sheet](Visual/Captures/KronkReference/K14-03-native-1.jpg), 4:55.800–4:56.167; [KRONK-01](KRONK_MORDHAU_REFERENCE_REPORT.md), [REN-01](REN_MORDHAU_REFERENCE_REPORT.md) | Specialist melee reference. Montage edits/input uncertainty remain; no sound assessment |
| C-UI | `Source/MeleeCombatLab/Debug/CombatDebugHUD.cpp`, `CombatTuningPanel.cpp`, `Training/CombatLabGameMode.cpp` | Source-level UI behavior, labels, default widget choices and save/load branches; not proof of their rendered/focused/error states |

[Audit manifest](Visual/Captures/QualityAudit20260908/manifest.json) preserves source hashes and sampling. Copied capture/verification receipts sit beside it. Reference manifests remain in TargetVision20260908. No deleted historical image is used as visible evidence. All video inspection here was sampled frames; audio was not heard and full-speed continuous playback was not evaluated. Human one-second readability testing is still pending.

## Scoring rules

Use 1–10; 1 means fundamentally failing the intended presentation, 5 means functional but visibly unfinished, 8 means convincing at gameplay distance, and 10 means exemplary through demanding transitions and relevant platforms. Interpolate only with written evidence. AAA references are scored with the same anchors and are not automatically 10. Mark **NE** for insufficient evidence and **NA** for mechanics outside approved scope; neither equals zero. Record observations separately from interpretations.

Weights total 100. The provisional index is `sum(weight * assessed score) / sum(assessed weights)`. C10 and C14 are NE, leaving 90/100 weight partially assessable. This **90% is rubric-weight coverage, not 90% state/test completion**. C3/C9/C12 are deliberately limited to visible aspects; their missing runtime tests remain blockers. Show the weakest critical state alongside the mean. No release-ready claim is allowed while a critical threat/action/outcome state is below 5 or unreviewed. A selected slice should reach at least 8 in threat readability, combat communication and HUD communication before being described as matching the reference quality; this is a review target, not an automatic per-draft gate.

### Anchors, failure modes and checks

| Category / weight / measures | 1 | 5 | 8 | 10 | Common generated-art failures | Useful checks |
|---|---|---|---|---|---|---|
| C1 Direction/identity 8: does the intended fantasy read? | Unrelated styles/placeholders | Medieval theme, generic identity | Distinct original/Hound family across visible layers | Immediately recognizable identity through all states | Style drift, ornamental excess, generic PBR | Compare native gameplay frame to R-KN/R-H; identify armor, place and mood before detail |
| C2 Silhouette/form 8: readable shapes and proportions | Indistinct actor/weapon | Functional but generic/blocky | Natural proportions, designed ridges/profile, clear sword | Strong recognition from every relevant direction/LOD | Inflated hands, melted gear, faceting the whole shell | Silhouette at actual opponent sizes; front/oblique profile; hilt/tip distinction |
| C3 Modeling/deformation 7: construction, anatomy and contacts | Broken parts, disconnected grips | Usable shape with distracting joints | Continuous-looking grips, useful deformation, coherent plates | Clean demanding transitions including deliberate stretch | Extra digits, conflicting views, interpenetrating plates | Selected exchange: fingers, wrist, shoulder, knee; one extra view only for ambiguity |
| C4 Materials/detail 9: metal/cloth/mail/stone and detail hierarchy | Flat/unrelated surfaces | Materials identifiable but noisy/generic | Coherent steel volume with authored patches; quiet cloth | Identity survives light, distance and motion | Camouflage steel, baked shadows, uniform grunge, plastic | Neutral/daylight comparison for changed material; reduced-size read; metal vs padding separation |
| C5 Lighting/value/color 7: focal separation and mood | Threat lost in darkness/glare | Pleasant light, uneven separation | Warm stone/cool steel, useful shadows, stable exposure | Robust separation across sun/shade/dense action | Random emissive accents, crushed blacks, bloom wash | Squint/grayscale read; opponent against brightest/darkest relevant wall; shadow crossing |
| C6 Environment/story/scale 6: navigable purposeful place | Empty/undifferentiated background | Functional repeated kit | Routes, landmarks and lived-in detail support duel | Memorable compositions and consistent spatial logic | Random clutter, inconsistent module scale, repeated noise | Route recognition; human scale; near/mid/far hierarchy; combat-lane clutter check |
| C7 Complete-frame camera 7: where the eye goes | Subjects cropped/occluded | Usable framing with competition | Actor, weapon and target remain distinct in action | Strong staging even in dense manipulation | Decorative lens effects, static heroic pose bias | One-second focal order; image-space weapon/UI footprint; same-speed actor/target sequence |
| C8 State/affordance 8: action, danger and consequence | Player cannot tell what matters | Core state readable with study | Own resources, threat, action and result distinguishable | Reliable first-glance read through reversals/errors | Unattached labels, color-only states, ambiguous bars | Identify owner/target/action/result; parry vs miss vs hit; legal/expired opportunity |
| C9 Combat motion/system 12: intent, delivery and recovery | Misleading/stab-like cut, broken transitions | Readable attack, stiff or uneven branches | Strong load/delivery contrast, coordinated carry and legal transitions | Expressive manipulation with consistent defender readability | Elbow-only repair, disconnected weapon, arbitrary retiming | Full action 1x plus chosen disputed interval; FP/TP phase/reach/contact consistency; accepted C++ events |
| C10 Locomotion/grounding 6: motion explains velocity | Sliding/floating | Cycles work, transitions obvious | Starts/stops/turns, feet and terrain support intent | Layering remains convincing under combat and slope changes | In-place skating, speed-mismatched stride, foot pop | Directional stop/reverse/crouch/jump/land; track planted foot against ground at 1x |
| C11 Action/VFX 4: effects clarify cause and outcome | Obscure or falsify action | Basic contact signals | Sparse geometric cues clearly distinguish outcomes | Precise, prioritized effects in busiest exchange | Huge particles, constant trails, bloom and wrong contact | Hit/miss/parry timing, effect location; silhouette remains visible; freeze without effects also readable |
| C12 Game UI 10: HUD/menu presentation and feedback | Debug-first, confusing actions | Functional but generic | Clear hierarchy, game-native style, complete applicable states | Accessible, responsive and coherent through all flows | Web dashboard cards, tiny buttons, raw IDs, focus traps | UI subrubric and button matrix in linked guide; focus/back flow and success/failure copy |
| C13 Cross-state cohesion 4: consistent finish and meaning | One polished screen hides broken core | Uneven state quality | Consistent art grammar and semantic colors | No weak critical state across supported contexts | Random icons, different materials per screen, polish islands | State matrix minimum and spread; compare quiet/action/outcome at same settings |
| C14 Technical integrity 4: stable usable image | Severe clipping/flicker/blur | Intermittent visible defects | Stable target-resolution play | Stable under effects, transitions and target-device pressure | Shimmering mail, transparency halos, LOD pops | Target hardware/resolution footage; p95/p99 traces; aliasing, shadow and context-transition checks |

### Current/reference comparison and smallest useful correction

Reference scores apply only to observed comparable qualities. C3 does not rate unseen topology or rig architecture; C9 compares visual action staging and sampled weapon handling in CS2 with Mordhau as a specialist supplement, not shooter attacks as sword mechanics. Runtime/polish ceilings cannot be awarded from isolated images.

Feasibility codes: **A** = bounded UI/lighting/composition work plausible with the current tools; **B** = attainable for one selected exchange/asset with focused authoring; **S** = sustained specialist craft likely needed if two coherent batches fail. All are scope judgments, **not schedule promises**: staffing, deadline and minimum hardware are unconfirmed. Daniel confirmed **100–144 FPS on mid-tier PCs**; exact CPU/GPU/RAM and resolution are still unspecified. The implementation guide translates that target into provisional allocations, not measured support.

| Cat. | Game | Approved AAA reference | Visible evidence and gap (observation → interpretation) | Smallest correction / main owner / feasibility |
|---|---:|---|---|---|
| C1 | 2 | 9, CS2/V/Z within their own fantasy | G-FP gray unclothed body and white sword vs R-KN/H steel/mail/cloth; R-CS/V/Z retain identity during play → target is mostly absent from gameplay | Dress one opponent plus FP hands/weapon in coherent selected materials / art direction + assets / B,S |
| C2 | 3 | 9, R-CS foreground, R-Z actor | G-FP guard and blade are simplified and broad; character silhouette lacks armor; references distinguish functional forms → prototype silhouette | Refine sword profile and one armor silhouette at gameplay distance / modeling / B |
| C3 | 3 | 8, R-CS Mirage 0–2.315s, Anubis 12.12s | G-FP grips exist but hands and intersections look unfinished at contact; reference weapon/glove component separation is clear → visible craft gap; hidden/deforming surfaces NE | Fit glove/guard together on accepted source; resolve one distracting intersection / character art + animation / B,S |
| C4 | 2 | 9, R-CS and R-V quiet walls/foreground | G-FP white blade and uniform skin; tiled ground has more texture than hero assets → detail priority reversed | Selected sword and glove metal/leather separation, calm background detail / materials / B |
| C5 | 5 | 9, R-CS Anubis 16.16s / Mirage 5.787s | G-FP sun/shadow clear; dark gray recesses and repetitive light pillars compete with pale actors → lighting exists but focal hierarchy weak | Test opponent values against one sun/shade lane, preserve daylight / lighting / A |
| C6 | 3 | 8, R-CS route/fountain | G-FP repeated arches and banners around broad cobble field; Anubis has purposeful elevation, openings and landmark → arena lacks hierarchy | One distinguishing landmark and readable lane terminus; reduce repeated contrast / environment / A,B |
| C7 | 4 | 8, R-CS navigation/combat | G-FP 10.783/13.45s broad blades cross face/hands; R-CS foreground usually leaves aim region clear → threat can be occluded | Review weapon-camera framing through exchange without changing accepted FP projection; first move redundant feedback / camera + UI / A,B |
| C8 | 3 | 8, R-CS defuse/loss, R-Z 11.818s | G-FP thin unlabeled bars, PARRY/RIPOSTE overlap; reference prompts attach action to glyph/context → ownership/consequence ambiguity | Label own health/stamina; one outcome indicator; readable next action / UI + VFX / A |
| C9 | 4 | 8, R-CS handling; R-M specialist 8 for observed sequence | G-TP 1s hands/weapon form a narrow forward mass; carry differs visibly later; G-DRAFT improves spread but forward crossing persists → attack direction remains ambiguous. Frame-only confidence low | One complete motion batch if current refinement fails; retain load and curved travel; explicit TP contact decision / animation / B,S |
| C10 | NE | NE: R-Z snippets insufficient for full inventory | Locomotion system exists in code; no suitable current start/stop/turn/terrain motion coverage | Capture one selected movement sequence after appropriate clips exist / animation / B,S |
| C11 | 3 | 8, R-Z wind ribbons; R-CS compact contact feedback | G-FP parry rays/text present, hit vs miss response poorly distinguished in sampled frames → basic cues lack tactile consequence | Compact contact-specific spark/reaction and short nonoverlapping outcome cue; verify audio together / VFX + animation / B |
| C12 | 2 | 8, reference UI composite (details in UI guide) | G-FP development revision label visible even in clean HUD; central feedback competes with opponent; references have stable semantic icon groups → player presentation unfinished | Separate diagnostics, establish player HUD resources and native input glyphs / UI / A |
| C13 | 3 | 8, observed R-CS/V/Z state consistency | G-FP quiet scene is legible, contact frame loses clarity; G-MAT polished island not integrated → uneven complete-frame finish | Bring one entire exchange to the same level before expanding armor roster / direction + integration / B |
| C14 | NE | NE for target-device motion | Current captures are low-resolution; reference streams are compressed/edited. Neither establishes target-device temporal quality | One target-resolution selected-exchange capture and relevant trace; no broad per-draft sweep / technical art / unknown hardware |

Aggregate arithmetic: current `276/90 = 3.0667 → 3.1`; reference `752/90 = 8.3556 → 8.4`. The 5.3-point gap is descriptive. It must not be interpreted as a percent of work remaining or averaged with concept-art scores.

### Isolated source/asset assessment (excluded from gameplay total)

| Asset | Narrow score | Evidence / useful next action |
|---|---:|---|
| USP_v016 helmet | Shape 7, visible steel treatment 7 against confirmed knight family | G-MAT has coherent visor/slit/volume and controlled angular reflections; simplified hardware/rims and smooth large surfaces differ from detailed R-H. Hound is a family exemplar, not the same helmet design. At distance G-MAT-DIST preserves head identity. Preserve accepted proof; refine on the actual production surface only if comparison requires it |
| EX_v002 FP action | No replacement standalone score | Previously user-accepted source/native playback. Current frame subset rates integrated presentation under C9, not reverses that acceptance |
| D_open_sweep draft | Pose-sequence clarity 5, low confidence | G-DRAFT shows load, opening, sweep/carry and return; forward horizontal interval persists. This is not a runtime score or human selection |

## Representative visual-state matrix

Cells are state-specific 1–10 judgments using the same category anchors. Dash = category not scored for that state; NE = required evidence missing. Values need not equal category-wide score. Color/material/shape deficiencies apply across the visible states; they are not counted again in this matrix average. **Do not calculate a second weighted mean from this table.**

| State / evidence | Frame C7 | Read C8 | Motion C9 | UI C12 | Cohesion C13 | Main finding |
|---|---:|---:|---:|---:|---:|---|
| Quiet ready / G-FP 0s | 5 | 4 | — | 2 | 3 | Actor distinguishable; whose bars/next training action unclear |
| Committed close cut / G-FP .8–1.15s | 4 | 3 | 4 | 2 | 3 | Hands/blade/target overlap; unfinished hero surface dominates |
| Movement and range miss / G-FP 3.967–9.5s | 5 | 3 | 4 | 2 | 3 | Open space readable; miss/spacing lesson not explicitly communicated |
| Successful parry into riposte / G-FP 10.783–11.3s | 3 | 3 | 4 | 2 | 2 | Foreground blade and stacked outcome text obstruct threat region |
| Incoming hit/interruption / G-FP 13.45s, event receipt frame807 | 3 | 2 | 3 | 2 | 2 | Incoming weapon traverses head area; sampled image alone cannot establish flinch timing |
| Defender close attack / G-TP .5–2s | 3 | 2 | 3 | 2 | 2 | Weakest critical threat read; narrow forward hand/blade mass can suggest stab |
| Distant opponent / G-TP 6s | 5 | 3 | — | 2 | 3 | Actor separates from wall but small weapon/pose detail weak |
| Player downed/reset | NE | NE | NE | NE | NE | Text exists in source; no reviewed rendered downed/reset sequence |
| Training selection/tuning/save/load | NE | NE | — | NE | NE | Source audited; no rendered menu/button sequence |
| Title/pause/player settings/loading | NE | NE | — | NE | NE | Required for a player-facing slice; no established finished flow |
| Dense multi-attacker pressure | NE | NE | NE | NE | NE | Only two test actors observed; not a stress-scene pass |
| Locomotion starts/stops/turns/jump/landing | NE | NE | NE | — | NE | Current capture is not a locomotion review set |
| Close final armored character / world vista | NE | NE | — | — | NE | Isolated helmet and concept vista do not substitute for integrated states |
| Inventory/shop/skills/quests/progression/affordability/team ownership | NA | NA | NA | NA | NA | Open product decisions, not current lab features; do not invent systems to fill audit |

Reference state scores: R-CS quiet/route C7=9 C8=8 UI=7; Anubis combat C7=8 C8=8 UI=7; defuse 20.20s C8=9 UI=8; loss 24.24s C8=9 UI=8. R-V combat C7=8 C8=8 UI=8, success 17.308s C8=9 UI=8. R-Z glide 11.818s C7=8 C8=9 VFX=8 UI=9, dialogue 17.726–23.635s C7=8 UI=9, saving 29.544s UI=8. Reference title/settings/inventory/button focus/error flows remain NE. User-excluded Valorant spectacle earns no target credit.

### Complete-frame read and one-second review

Intended combat focal path: **opponent shoulders/hands and threatening blade → contact/spacing → own resources or available follow-up**. Environment landmarks support orientation in peripheral vision. Current inferred competing path: **large white own blade → bright cobbles/pillars → overlapping yellow text → opponent**. This is an analyst interpretation, not a tested player gaze trace. See [annotated parry frame](Visual/Captures/QualityAudit20260908/parry-annotation.svg) and [annotated reference glide](Visual/Captures/QualityAudit20260908/glide-annotation.svg); overlays are diagram annotations, not edits to the original evidence pixels.

For selected integration, show a critical frame for one second to a representative unfamiliar player, then mask it. Ask who/what is the focal subject, current state, immediate threat/opportunity, available action and likely consequence. Record exact answers and errors, not just a pass claim. Proposed target: at least 4/5 answers correct per critical frame and no dangerous confusion about threat/ownership; repeat through short 1x motion when stills omit essential cues. Use at least three players for a useful early signal, without claiming statistical validation. This test has not been run. Do not expose diagnosis text or freeze gameplay to make the production state understandable.

## Prioritized improvement plan

Effort estimates are bounded scopes, not calendar commitments. Preserve EX_v002 and accepted material/source identities; exploration must remain isolated. Existing 22.60cm TP endpoint discrepancy is a recorded contact-integration question, not proof that every apparent strike misses. No silent gameplay reach change.

| Priority / scope | Action / ownership | Acceptance evidence | Expected effect / dependency |
|---|---|---|---|
| Quick win 1 | UI engineer: hide development revision/phase labels outside diagnostics; keep F4 tuning in a clearly marked developer tool | One clean HUD and one diagnostic frame; verify original diagnostics retained | Removes a visible player-facing quality failure; no asset dependency |
| Quick win 2 | UI designer/engineer: named health/stamina grouping, one parry/riposte cue, consistent action glyphs | Ready, parry, damage and downed frames; one-second check | C8/C12/C7 improve without touching accepted FP projection |
| Quick win 3 | Environment/lighting owner: quiet the immediate wall/floor behind opponents; retain one useful landmark | Same-camera sun/shade before/after | Clearer threat read; no entire map rebuild |
| High impact 1 | Animation owner: resolve one ready/parry/riposte/carry/return exchange with miss and interruption | One 1x whole exchange; focused changed contact checks and human play decision | Highest gameplay value; use current D comparison before another batch |
| High impact 2 | Character artist: finish one sword/FP glove and one coherent armored opponent with approved material vocabulary | In-context close/duel-distance view and selected motion | Establishes actual identity. Hound may be a candidate; preference does not auto-replace accepted assets |
| High impact 3 | UI owner: native pause/settings/retry/training flow, full relevant button states and recovery text | Keyboard/mouse flow and supported controller path; failed settings save case | Makes lab understandable as a player-facing slice; platform inputs need confirmation |
| High impact 4 | Technical artist/audio owner: contact reaction, restrained effects and audio mix together | Real hit/miss/parry recording at 1x, no dubbed audition presented as game | Communication and tactile weight; requires stable exchange/event routing |
| Specialist if needed | Combat animator after two coherent weak batches: author one exchange from actionable brief; character artist for skinning/armor construction; sound designer for transient/mix polish | Bounded deliverable, editable source, reference comparison and playable result | No automatic commissioning. Limit to demonstrated skill bottleneck |
| Later | Environment artist: one complete arena composition; performance engineer: target-device optimization; localization/accessibility UI specialist | Selected slice on confirmed minimum hardware and input devices | Do not expand roster/vistas before weakest core state works |

Likely achievable within a small project: a coherent, polished one-exchange slice and a small armor family, subject to sustained craft work. Matching these games' breadth, cinematics, world density or entire UI inventory cannot be promised from available team/timeline information. Unknown hardware prevents a confident performance feasibility claim for final assets.

## Review operation and completion receipt

Authority read once for this workstream: AGENTS/DEVELOPMENT/VALIDATION, README/PROJECT_SPEC, current FP/TP/material checkpoints, movement contract and current locomotion source. Notion [Game Structure](https://app.notion.com/p/3d32e3c3f8f88147bcaeffd4e1764989), [Swing Model](https://app.notion.com/p/3d32e3c3f8f881028f05c2a960248ff1), [Defense](https://app.notion.com/p/3d32e3c3f8f881149047ee9c11b8ea7a), [Movement](https://app.notion.com/p/3d32e3c3f8f88121bb01f4d381024731) supply mechanics; current project rules override stale reset/integration prose. Game structure does not approve a shop, bomb mode or progression. Current source includes release-drive/momentum behavior; old movement prose saying no additive drive is not current authority for that detail.

Commands: `python Saved/ReferenceIntake20260908/current_audit.py` extracted only 18 frames from two retained videos and copied three distinct source/study images and receipts. No runtime code/assets changed, no engine launch/import/build/regression or device testing. Documentation link/weight/evidence checks are recorded in `Visual/Captures/QualityAudit20260908/documentation-check.json`. No independent review agent was required for this documentation-only change. Future consequential C++/contact edits need the existing single independent review. Full interaction, audio, target-resolution and hardware tests remain explicitly outstanding.

---

## Historical artistic iteration review (7 September; retained provenance)

User instruction, 7 September 2026: employ an independent art critic to rate renders out of 10 and give pointed, specific improvements toward the eventual design aesthetic.

For each meaningful artistic candidate, give one critic a bounded assignment: inspect the actual render and the original approved reference, then return a score, visible evidence, prioritized corrections and the next render prescription. Keep the critic independent of the author's self-assessment. Reuse the critic for revisions of the same study; no child subagents or duplicate reviews.

The primary criterion is the Valorant-esque authored texture aesthetic, with Arcane also endorsed by the user. The latest correction is decisive: resemble painted texture without appearing to be actual paint. Evaluate angular tonal hierarchy and relation to form, intrinsic steel response, selective edge treatment, color and clarity. Reject brush marks, camouflage, closed-cell mosaics and generic smooth PBR. Iterate until the independent critic awards 8–10/10 without relaxing the standard. A successful tool run is not aesthetic success. State scope limits: material proxies cannot establish final armor likeness, deforming hand quality or gameplay readability. Ratings describe the candidate's visual fidelity, not effort, completion percentage or user acceptance.

Each review records candidate/path, numerical score, 3–5 concrete corrections in priority order and the smallest next render. Preserve score changes and reasons. Do not turn the rubric into broad pose matrices or repeat unchanged checks. Show the user the image and concise critique; human acceptance remains separate.

Apply this review to subsequent artistic work in this project. MEL-17 candidates and scores are tracked in ArtSource/StyleReference/MEL17/ITERATION_LOG.md.

Latest user correction after seeing v020: texture feels too crowded and the surface should feel smoother. This supersedes the earlier interpretation favoring dense faceting. Favor broad calm steel with a few restrained angular catches, and judge the next render against this explicit preference.

The user accepted Steel_v025 and authorized a helmet proof. Helmet_v009's historical 8/10 shell-cleanliness score was superseded by the user's later blockiness/reference-fidelity rejection; it does not establish an accepted helmet. Preserve Steel_v025 unchanged.

Current geometry-first review: `ArtSource/StyleReference/MEL17/GeometryReview/Clay_v005/CRITIC.md` rates the rebuilt matte helmet 8/10 for resemblance and 8/10 for visible craftsmanship after matched/front evidence and eight rotation samples. The user subsequently accepted it: "Looks very nice. The shape is quite perfect." The shape gate is closed; preserve Clay_v005. The ten-second turntable and native-size comparison remain in `Clay_v005/Review/review.html`; their original delivery-time acceptance wording is historical. Next assess faithful Steel_v025 transfer on the unchanged shape, scoring material response separately. Rear design is inferred, and articulation/runtime readiness remain outside this judgment. See `Docs/MEL17_UNREAL_STYLE_PLAN.md` for the updated sequence.

