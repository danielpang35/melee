# Kronk’s Mordhau — expressive control and coherent weapon motion

Published in the [Notion Bible](https://app.notion.com/p/3d42e3c3f8f881d8b2e7d845679e8eb7), with three selected timestamped frame sheets.

**Reference ID: KRONK-01 · 7 September 2026 · Status: reference analysis and design guidance; no implementation or playtest acceptance.**

## Finding in brief
**Give the player a coherent weapon and enough control to compose beautiful exchanges.** Kronk’s sequences suggest that expressiveness comes from the combination of attack presentation, aim changes, relative spacing, target transitions and readable consequences. A more elaborate base swing alone would capture only part of the appeal.

Ren remains the reference for economical, deliberate manipulation. Kronk adds a complementary stress test: the arms and weapon must remain convincing through more adventurous compositions. “Economical” means avoiding compulsory wasted movement; it does not impose a small range on intentional player expression. Preserve the swing weight, timing, acceleration character, commitment and responsiveness already praised in Astra Ultra’s work.

## How to reference
Use **KRONK-01 / F1–F7** for findings, **K18-01–K18-04 and K14-01–K14-04** for evidence, and **A1–A5** for proposed application. All timestamps are positions in the supplied montage, not engine phase times.

Companion: [REN-01 — Ren’s Mordhau: economical motion and deliberate manipulation](https://app.notion.com/p/3d42e3c3f8f88199b54eed401936acac).

## Source context and method
The user identifies these as Kronk’s montages and describes his creative swings, footwork, awareness and visceral play as a project aspiration. His reputation, background relative to Ren and use of default 240 controls rather than six directional binds are **user-supplied context**, not conclusions established by footage.

Sources: `D:/Kronktage v18.mp4` (3:49.72) and `D:/Kronktage v14.mp4` (5:50.02), both 1280×720 at 30 fps. Reviewed 73 overview frames sampled every eight seconds, eight four-second sequences sampled at six frames per second (192 frames), and 36 consecutive source frames from v14 4:55.800–4:56.967. Frame sheets reduce image size for comparison.

This is sequential-frame visual analysis, **not continuous audiovisual playback**. Audio and music were not evaluated. Montage selection, cuts and possible speed editing prevent reliable conclusions about typical match frequency or real-time attack duration. The edit at approximately v14 5:28.8 interrupts K14-04: do not interpret the following exchange as uninterrupted footwork.

Separate three evidence levels: directly visible image changes; plausible motion interpretation; proposed design application. Screen motion combines animation, view orientation, movement, opponent movement, perspective and editing. Without input logs, camera transforms or a replay, the underlying authored clip cannot be uniquely recovered. Intentional steering is the working hypothesis; exact buttons, phases, drag/accel classifications and unseen body mechanics remain unverified.

## Timestamped evidence
### K18-01 — v18 0:22.000–0:25.833 · shaft weapon, close exchanges
The long shaft changes from upright to across the foreground while separated hands carry it. Nearby fighters enter from different sides and apparent distance changes repeatedly. Transfer the coordinated transport and changing spatial relationship; this wide shaft grip is not a longsword hand-placement template.

### K18-02 — v18 0:30.000–0:33.833 · several opponents around a tower
The view moves between a group near the tower and a fighter in open grass, then returns to close pressure. Around 0:32.3–0:32.8, visible contact effects and score feedback accompany an exchange; the foreground subsequently clears before the weapon rises again. Useful for target transitions, recovery visibility and spatial composition. Score feedback alone does not identify the exact input sequence.

### K18-03 — v18 2:14.000–2:17.833 · close crowd and strong viewpoint changes
Hands carry a long shaft high across the foreground while fighters and tower landmarks shift substantially. The scene opens and closes around successive nearby opponents. The combination is consistent with purposeful steering and repositioning. It does not reveal an exact footwork route, nor prove what information Kronk was aware of offscreen.

### K18-04 — v18 3:26.000–3:29.833 · one-handed sword
The sword alternates between an extended position, a high guard near the camera and a subsequent outward sweep as nearby opponents change sides. An open off-hand is visible, so this is **one-handed reference**, not evidence for paired longsword grip. Around 3:28.0–3:28.3 the guard/hand stays high while the opponent shifts; around 3:28.5–3:29.3 the weapon and forearm travel through a different screen region as the view tilts. Useful for full hilt orientation and pose transitions, with weapon-specific anatomy retained.

### K14-01 — v14 0:46.000–0:49.833 · two-handed sword, changing lines
The paired arms extend, settle to a lower diagonal ready presentation, rise again and carry the weapon across changing foreground lines. Around 0:48.3 the hands rise high on the right; subsequent frames turn toward other nearby fighters before a more extended presentation returns. This is a better two-handed reference than the polearm or one-handed sequences. It supports distinct poses and transported hands rather than a fixed screen pivot.

### K14-02 — v14 3:58.000–4:01.833 · short hammer, outcomes and reset
A conspicuous hit outcome is followed by an upright weapon return and clearer view of other fighters. Low ready positions contrast with subsequent extension and further visible hit feedback. Useful for the relationship between action, consequence and renewed visibility. The hammer’s grip and delivery must not be copied directly to the sword; this visual inspection does not assess sound’s contribution.

### K14-03 — v14 4:54.000–4:57.833 · two-handed sword beside stone wall
The paired hands and guard recur high near the camera, pass across the upper foreground, then the forearms carry the weapon toward the edge while the view changes markedly. Native-frame inspection at 4:55.800–4:56.967 shows both hands remaining associated with the same handle; the guard and blade change orientation together. Contact sparks occur during high crossed-arm presentations, so these frames include defensive/contact transitions and must not all be labelled attack windup or release. By approximately 4:56.6–4:56.9 the near forearm dominates the right foreground and the courtyard opens into view. This is a qualitative pose sequence, not a recovered 3D attack spline.

### K14-04 — v14 5:26.000–5:29.833 · one-handed mace at waterside
Two nearby threats occupy different directions. A high hand/weapon presentation gives way to extension, hit feedback and a view toward the pier supports, followed by an open view and upright mace. The scene cuts around 5:28.8 to another exchange. Transfer the pre-cut relationship between threat positioning, weapon transport and visibility; do not stitch across the edit or use the mace grip as sword anatomy.

## Findings
### F1 — Expressiveness is composed across systems
**Observed:** K18-02, K18-03 and pre-cut K14-04 repeatedly change opponent arrangement, distance and view direction alongside weapon presentation.
**Interpretation:** Much of the creativity lives in how actions are placed in space and chained across threats.
**Application:** Evaluate animation under player steering and footwork, as well as against a stationary target. Avoid baking a montage camera route or automatic target choreography into the base attack. Confidence: high for visible changes; moderate for their exact causes.

### F2 — A believable weapon needs a moving hilt and changing orientation
**Observed:** K14-01 and K14-03 transport paired hands/guard across different screen regions; K18-04 shows a distinct one-handed solution.
**Interpretation:** The sword reads as carried by the arms through changing poses rather than merely rotating its tip around one screen point.
**Application:** Author translation and full orientation of the weapon with both hands and arm poses. Diagnose the current “sprinkler” appearance using hilt, guard and forearm motion, not blade-tip travel alone. Confidence: high for the visual reference; current implementation cause remains a hypothesis.

### F3 — Compact readiness and large deliberate changes can coexist
**Observed:** Lower ready presentations and brief clearing of the foreground alternate with high, close or extended poses (K14-01–03).
**Interpretation:** Contrast and useful transitions convey more than uniformly large arm travel.
**Application:** Keep the adopted stomach/upper-abdomen idle goal; allow attack and defence their own required ranges. Do not lower every phase or amplify every torso motion. First-person frames cannot establish precise own-body torso/shoulder amplitudes. Confidence: high for pose contrast; moderate for the proposed transfer.

### F4 — Visibility between actions supports expressive play
**Observed:** After busy foreground motion, opponents become visible again in K18-02, K14-02 and K14-04.
**Interpretation:** Recovery presentation can help the player read the next opportunity without demanding that the weapon remain permanently unobtrusive.
**Application:** Assess how soon useful threat information returns, alongside readable commitment. Brief arm occlusion may be appropriate; permanent chest-level obstruction or extra ornamental recovery would work against this goal. Confidence: high for image visibility; gameplay benefit requires testing.

### F5 — Visceral satisfaction includes consequence
**Observed:** Contact effects, opponent reactions, changed spacing and score feedback punctuate sequences such as K18-02 and K14-02.
**Interpretation:** The appealing exchange includes anticipation, contact and resolution, not only the swing arc.
**Application:** Preserve accepted weight and evaluate unedited exchanges with coherent contact/reaction presentation. This report cannot assign the montage’s excitement quantitatively to animation, audio, editing or player skill. Confidence: high for visible consequences; subjective causal weighting unmeasured.

### F6 — Default 240 is a reference context, not proof of a unique animation system
The user’s account makes freedom of attack selection a relevant design aspiration. Footage alone cannot demonstrate that a particular path required 240 selection, could not be made with binds, or needs looser turn limits. Attack-direction selection and subsequent aim/footwork manipulation are separate design concerns. The project’s 240 Hz simulation rate is unrelated to Mordhau’s “240” control name.

**Application:** Test continuity and predictable direction selection across adjacent angles, plus responsiveness during legal manipulation. Do not infer a required sample count, copy sensitivity values or retune caps from these images. Confidence: control history attributed to user; causal hardware/input claims unresolved.

### F7 — Ren and Kronk are complementary acceptance references
Use Ren to ask whether a clean action communicates power with purposeful motion. Use Kronk to ask whether those same coherent fundamentals survive unusual angles, tight spacing and successive threats. Neither asks for a personality-specific animation pack. Both favor player authorship over compulsory flourish.

The user’s success aspiration spans all three supplied videos: expressive and beautiful swing manipulation. This is a direction for evaluation, not a measured claim that the current prototype has achieved it.

## Proposed application and review
**Expert review role:** animation direction, combat systems and first-person readability. These are proposed review activities, not completed tests or new production scope.

### A1 — Preserve the baseline before visual changes
Record a matched-input baseline of the swings the user likes. Compare timing, acceleration character, responsiveness and perceived weight after the visual rehaul. Keep gameplay clock and contact geometry authoritative; investigate reach/contact changes if weapon-path changes are required.

### A2 — Diagnose grip separately from arm presentation
Review idle, high defensive poses and representative deliveries with a readable neutral hand material. Check handle contact, wrist alignment, elbow placement, proportions and texture separately. Use two-handed K14-01/K14-03 for the paired sword reference; use other weapons only for transferable principles. Do not move grip offsets merely because poor arm/model presentation looks wrong.

### A3 — Separate base motion from manipulation in our own captures
Capture the same attack with fixed view/feet, aim-only variation, movement-only variation and combined legal inputs. Compare hand/guard paths in screen and weapon-local space alongside gameplay weapon geometry. This controlled comparison can identify contributions that montage frames alone cannot isolate.

### A4 — Add an expressive review set without changing the combat rules
Review adjacent attack angles, close and farther engagement, elevated/depressed aim and consecutive direction changes. Where existing tooling supports multiple opponents, review transitions between threats and recovery visibility. Preserve player control, stable hand contact, coherent arm motion and readable consequences. Multi-opponent production work is not required merely to reproduce a montage composition.

### A5 — Choose animation technology by result and cost
Authored procedural poses/curves remain the preferred means of controlling the presentation. Advanced physics may generate, bake or drive motion when it saves authoring/iteration/runtime resources or improves the final animation. Compare its benefit against simpler methods; realism itself is not the acceptance test.

## Selected frame sheets
Three selected frame sheets are embedded in the Notion report with the user's explicit approval. Local figures: [paired sword hands](Visual/Captures/KronkReference/K14-03-native-1.jpg), [one-handed sword](Visual/Captures/KronkReference/K18-04-2.jpg), [multiple threats](Visual/Captures/KronkReference/K18-02-2.jpg).
- Figure 1: `K14-03-native-1.jpg` — 4:55.800–4:56.167, paired sword hands/guard across a contact/defensive transition. Do not label every frame as attack release.
- Figure 2: `K18-04-2.jpg` — 3:28.000–3:29.833, one-handed sword: high guard, transported hilt and changing view.
- Figure 3: `K18-02-2.jpg` — 0:32.000–0:33.833, several opponents, contact feedback and renewed foreground visibility.

## Reproducibility
Extraction: `Tools/AnalyzeKronkReference.py`; evidence and source probe: `Docs/Visual/Captures/KronkReference/manifest.json`. Context extraction arguments are version, sequence ID, start seconds, 4 seconds, step 5. Starts: v18 22 / 30 / 134 / 206; v14 46 / 238 / 294 / 326. Native extraction: version 14, K14-03-native, 295.8, 1.2, step 1. Images are sampled from 30 fps decoded video; displayed millisecond labels are rounded.
- v18 SHA-256: `aa6a776f5daec84e6de593a3573e7367c1b78770711a151d2bbdd17a2ff03ec3`.
- v14 SHA-256: `e76c20f6db1eee15a483e575984fbc353334578a5e0758d8a174d5277b08c9f3`.
