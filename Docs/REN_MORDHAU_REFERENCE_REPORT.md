# Ren's Mordhau — economical motion and deliberate manipulation

Published in the [Notion Bible](https://app.notion.com/p/3d42e3c3f8f88199b54eed401936acac), with three selected timestamped frame sheets.

Local figures: [R01 delivery](Visual/Captures/RenReference/R01-3.jpg), [R02 hilt transfer](Visual/Captures/RenReference/R02-1.jpg), [R03 aim and delivery](Visual/Captures/RenReference/R03-3.jpg).

**Reference ID: REN-01 · 7 September 2026 · Status: footage analysis and design guidance; no animation implementation or new play acceptance.**

## Finding in brief
Preserve the weight and timing already praised in Astra Ultra's swings. The visual target is **economical, coordinated hilt-and-hand motion that makes the blade's travel legible**, with enough arm/body participation to explain it. The footage does not justify making every torso turn, hand arc or recovery larger.

Treat Ren's camera, aim, footwork and timing changes as purposeful by default, per the user's assessment of his precise, economical inputs. This makes the footage a high-signal reference for controlled manipulation. It does not turn the final screen trajectory into an unmodified animation clip, nor establish the exact intent of every input.

## How to cite this report
Use **REN-01 / F1–F6** for findings, **REN-01 / R01–R06** for timestamped evidence, and **REN-01 / A1–A4** for application guidance. Timestamps refer to the supplied montage, not engine attack clocks.

## Scope and method
Source: `D:/Mordhau Montage VI.mp4`, identified by the user as Ren's footage. The existing source record reports 1280×720, 30 fps, approximately 4:44. This pass confirmed the file remains available and recorded its identity.

Reviewed six existing timestamped 8 fps context sheets: 0:02–0:03.875, 1:04–1:05.875, 1:42–1:43.875, 2:44–2:45.875, 3:20–3:21.875 and 4:20–4:21.875. Then extracted and inspected **108 consecutive source frames** across three selected 1.2-second intervals: R01, R02 and R03 below. Those sheets contain all 36 decoded frames per interval, without motion interpolation.

This is a sequential frame analysis, not a continuous audiovisual playback assessment, controlled input experiment or recovered skeletal animation. Labels such as load, transfer and passage describe visible motion; exact attack type, release boundaries and defensive result are not asserted where the HUD/contact evidence is ambiguous. First-person arms are visible; Ren's own pelvis, chest and support foot generally are not.

Source SHA-256: `f71bde2385fdc5e4657314313fa279af546f607818deae2bda1835728852273f`. Size: 76,339,804 bytes. Reproduction: `Tools/AnalyzeRenReference.py`. Evidence: `Docs/Visual/Captures/RenReference/manifest.json`, individual frames and R01/R02/R03 sheets.

## Isolating authored motion from deliberate manipulation
Read each exchange in three coordinate systems:
1. **Screen/view:** track guard/hilt, both wrists and the blade axis relative to the frame. This shows the composed weapon/arm performance, including any aim-dependent procedural posing.
2. **Environment:** compare stone corners, gate towers, paving and horizon across frames. Coherent scene displacement indicates viewpoint change; near/far parallax can suggest translation. Do not use moving opponents as the only camera reference.
3. **Target relationship:** track where the target is relative to the blade and whether distance/attack line changes. This describes the purpose that manipulation could serve; it does not independently identify mouse or movement inputs.

Repeated hand/weapon relationships under different scene motion are **candidates for the authored component**. Strong scene movement accompanying a crossing is evidence that the crossing cannot be assigned wholly to the base clip. A comparatively steady background while the hilt moves is useful evidence of view-relative animation/adaptation.

Do not subtract a single background pixel displacement from the hilt and call the remainder pure animation. Perspective, depth, translation, camera rotation, view-model composition and aim-driven body adjustments differ. This review isolates likely contributions qualitatively; it does not recover a unique 3D base trajectory. Intentional input can still produce camera inertia, hit response or other secondary effects.

## Timestamped evidence
### R01 — Compact preparation, then committed hand travel
**0:02.400–0:03.567; native-frame sheets R01-1 through R01-3.**
At 0:02.400–0:02.567 the guard and paired hands move toward the lower-right edge while the distant gate remains broadly in the same region. By approximately 0:02.700–0:03.033 much of the weapon/hand assembly is below the frame. At 0:03.100–0:03.333 both forearms extend back into view toward the engagement; the subsequent blade/hand passage moves left/up through 0:03.567. The scene and targets also shift.
**Inference:** a compact or partly offscreen preparation can feed a substantial, purposeful delivery. Keeping the hands continuously centered and visible would misread this example. Native release onset and an isolated accel/drag label remain unverified.
**Use:** study preparation-to-delivery contrast and arm extension, not a universal screen-path template.

### R02 — Hilt transport and a coupled two-hand frame
**2:44.100–2:45.267; sheets R02-1 through R02-3.**
At 2:44.100–2:44.267, the hands and handle are high/right and close to the camera. At 2:44.300–2:44.467 the paired hands and hilt travel leftward across the view while their relationship to the handle remains readable. The scenery changes relatively less during the early part than during the later target switch. From 2:44.500 onward, a second opponent enters centrally and viewpoint/target relationships change strongly; the hands travel toward the lower-left. At 2:45.000–2:45.267 the weapon extends across the target area with visible contact particles and recipient motion.
**Inference:** the hilt is a transported and reoriented part of the action, not a visually fixed axle. The later crossing combines this performance with deliberate manipulation. The exact split, contact type and player purpose are not recoverable from images alone.
**Use:** strongest close-up reference here for hand/handle coupling and hilt passage; do not label the entire interval one pure authored attack.

### R03 — High preparation and low delivery coexist with large aim changes
**4:20.300–4:21.467; sheets R03-1 through R03-3.**
At 4:20.300–4:20.667 the hand/guard assembly rises close to the upper-right view as the tower and sky shift. At 4:20.700–4:21.067 the weapon passes high/out of view while the view turns downward toward the opponent and ground. At 4:21.100–4:21.267 both forearms and hands extend toward the lower central attack line. By 4:21.400–4:21.467 the view redirects around the tower toward overlapping threats.
**Inference:** dramatic high-to-low screen motion includes purposeful aim and spatial adjustment. Baking the camera dip or the tower-side redirection into every attack would duplicate player agency.
**Use:** stress reference for composed manipulation and a compact, connected hand delivery; not a neutral overhead clip.

### R04 — Corner movement is part of the exchange
**1:04.000–1:05.875; existing context sheet reference_064_0.**
The near stone corner moves substantially through the view while the opponent closes and the arms appear and clear it.
**Inference:** positional/view adjustment is integral to the exchange; do not attribute relative target travel to automatic attack lunge or oversized body sway.
**Confidence:** high that viewpoint/relative spacing change; low for a specific WASD sequence, lunge rule or evasion intention.

### R05 — Contact, visibility and return
**1:42.000–1:43.875; existing context sheet reference_102_0.**
Close crossed weapons and particles around 1:42.500 give way to a more open view. The blade returns into view around 1:43 and changes orientation as the next engagement approaches.
**Inference:** readability includes what the hands clear after the exchange. Recovery need not occupy the center with a large decorative loop.
**Limit:** do not infer exact parry/chamber classification or recovery duration from this montage excerpt.

### R06 — Spacing changes can carry much of the drama
**3:20.000–3:21.875; existing context sheet reference_200_0.**
The forward weapon presentation retracts/reorganizes while distance to the plumed opponent changes, followed by renewed raised and forward weapon poses.
**Inference:** approach/withdrawal and changing target relation contribute to perceived force and commitment. They do not establish that the base attack requires large root translation.
**Limit:** this is relative spacing; each actor's separate contribution is unknown.

## Findings and implications
### F1 — Preserve manipulation as an independent layer
R02's later crossing, R03 and R04 show substantial scene changes during weapon action. Under the user's intentional-input assumption, treat these as meaningful steering/spacing evidence rather than noise to smooth away. Reconstruct a plausible neutral attack first, then test how intentional aim and footwork compose with it. **Confidence: high for mixed contributions; moderate for their qualitative separation.**

### F2 — Fix the moving hilt and connected arms before enlarging the blade arc
R01 and especially R02 show a changing hilt location, hand-frame orientation and forearm configuration. This supports the user's complaint about the project sword “sprinklering”: a broad blade rotation without a convincing transported handle can read as an axle-driven prop. The footage does not establish the project's exact root cause; small but visible hilt translation, appropriate depth change and coordinated arm motion are the first variables to examine. **Confidence: high for visible coupling; proposed application to our defect.**

### F3 — Economy means useful contrast, not uniformly tiny motion
R01's compact/offscreen preparation and visible delivery, plus R02's close high hand pose, show that economical control can still contain large local excursions. What matters is whether motion loads, delivers, responds or transfers. Avoid extra shoulder pumping, symmetric windmill arcs, redundant recovery loops and compulsory body sway. These are design cautions, not claims that the footage proves every such motion absent. **Confidence: moderate; qualitative animation interpretation.**

### F4 — The minimum is a coordinated relationship, not a defensible number of centimeters
The evidence supports changing forearm configuration, carrying/reorienting the paired hands and producing a legible delivery/return. It cannot establish the minimum pelvis yaw, shoulder travel or hilt distance needed for power. Ren's own torso and feet are mostly hidden, and perspective changes apparent amplitude. Other visible combatants are not measurements of Ren's body motion. Use small, independently timed body contributions and increase only when the silhouette or delivery needs them. Do not mistake “body generates the sword” for “every joint must make a large visible excursion.” **Confidence: high about evidence limits; minimum-amplitude choice requires our own A/B.**

### F5 — Readable grip is a combination of contact, pose and asset quality
R01 and R02 provide usable views of two hands along the handle with distinct roles relative to guard and pommel. Their silhouettes remain interpretable while wrists and handle orientation change. This does not prove our existing contacts wrong or supply exact 3D offsets. Compare actual contact placement separately from forearm pose, palm/finger shape, deformation and texture/material. The reference's low or partly offscreen poses also do not prove an exact stomach-height idle; that remains the user's explicit design requirement. **Confidence: high for visible relationships, low for hidden contact geometry.**

### F6 — Preserve successful weight while removing wasted visual motion
The user's positive assessment of Astra Ultra's current swings is a separate source from the montage. Retain that timing, acceleration character and responsiveness as the control condition. Revise the visual arm/hilt performance; do not discard the successful feel in pursuit of more realistic or more exaggerated movement. Advanced physics remains an eligible tool when it improves quality or saves resources, including baked source motion. **Status: established user direction plus application of F1–F5.**

## Application and acceptance
**Expert role:** Act as an expert in first-person melee animation and technical animation, specializing in economical two-hand weapon choreography, screen-space hilt composition and separation of authored motion from player manipulation. Apply supporting rigging and material expertise to grip diagnosis.

### A1 — Build the neutral motion before the manipulated comparison
Preserve a reproducible snapshot of the praised swing. At matching clocks, camera/FOV and weapon dimensions, review stationary neutral-aim attacks as well as the existing spatially manipulated variants. Author load, delivery, passage and return/transfer with full weapon orientation and paired hand targets. Keep hilt translation and blade rotation separately inspectable; do not imitate montage camera motion as an automatic flourish.

### A2 — Find the smallest convincing motion through reduction
Start from a coordinated version, then reduce hilt excursion, shoulder contribution and pelvis/chest amplitude one at a time. Keep phase relationships, grip and accepted timing stable. Review normal-speed first-person and external clips in shuffled order. Retain the least motion that still communicates origin, commitment, connected hand delivery and outcome without losing the user's liked weight. This is a proposed experiment, not a minimum measured from Ren's footage.

### A3 — Test the combination of motion and control
Use neutral input, deliberate yaw manipulation, deliberate pitch change and movement separately, then combine them. Judge whether authored motion plus steering creates duplicated sway, unexpected wrist folding or renewed “sprinkler” travel. New authoritative hilt paths can change reach/contact timing even with unchanged clocks; preserve visible/collision agreement and record those effects. Track normalized screen hilt paths and wrist/blade orientation alongside world-space traces; compare shape and phase rather than blindly matching pixels between different cameras.

### A4 — Referenceable quality gate
A reviewer should be able to identify where the hands carry the handle, how the forearms accommodate it, why the blade crosses the target line and where the action goes next. Ask separately: “Does it retain the liked weight?”, “Do the arms explain the swing?”, and “Is any movement unnecessary?” Check lower idle and transitions, grip under neutral/final materials, and both views at normal speed. Exact endpoints and IK tests remain supporting evidence. Existing execution homes: MEL-5 diagnosis/idle, MEL-6 horizontal hilt/arm performance, MEL-15 full-body/overhead and MEL-11 integrated acceptance.

## What this changes in the Bible
Read “powerful” and “exaggerated” as **clear, purposeful contrast with economical motion**, not a mandate for larger excursions. Ren's footage is the preferred high-signal reference under the intentional-input assumption. Separate base action, view/aim manipulation and relative spacing before borrowing motion. Preserve the accepted swing feel and let hand/body motion earn its amplitude.

## Sources and evidence boundaries
- Primary visual source: the user-supplied Ren / Mordhau Montage VI footage identified above; timestamped observations R01–R06.
- User direction in this conversation, 7 September 2026: Ren's inputs are exceptionally precise/economical; assume most visible manipulation intentional. Earlier clarification praises Astra Ultra's swing feel, distinguishes visual arm/hilt problems, and leaves actual grip correctness open.
- Existing extraction context: `Saved/ReferenceAnalysis/analyze_reference.py` and the six named sheets. Earlier interpretation in `Docs/REFERENCE_ANALYSIS_AND_NEXT_STEPS.md` is context, not independent corroboration.
- Current design: <mention-page url="https://app.notion.com/p/3d32e3c3f8f881e08474defe7febb171"/> and <mention-page url="https://app.notion.com/p/3d32e3c3f8f881469e06e14d281e5bee"/>.
No recovered input log, raw animation data, calibrated camera, exact skeletal measurements or fresh project playtest was available in this analysis. Intentional-input assumptions improve interpretation but do not eliminate those ambiguities.
