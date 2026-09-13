# Clip B visual analysis

Source: `C:/Users/Daniel Pang/Videos/Captures/MORDHAU   2026-09-08 01-46-20.mp4` (1920×1080, ~21.31 s). SHA-256 and decoder metadata: `B/overview/receipt.json` and `decode.log`.

User clarification during this review: the instructor uses a **Training Sword**; the rear-view character in clip A uses a **Greatsword**. B is supporting evidence for body coordination and defender readability, not a second camera on the same weapon/performance. The user has not separately confirmed the exact attack inputs. Right-origin classification below is visual inference.

Further user clarification during implementation: **the trainer performs both horizontals and overheads**. The selected lateral cycles below are supporting horizontal evidence; the clip as a whole is not a homogeneous horizontal reference. Overheads are excluded from the scoped right-horizontal choreography.

## Selection and interpretation

Preferred complete cycle: **source PTS 0.456067–2.067100 s**. This is an instructor's externally visible two-handed sword swing recorded from the player's first-person camera, not a third-person chase camera. It is useful as a third-person character animation reference because the attacking character is visible. The load is on the instructor's anatomical right (viewer left when frontal), followed by a sweep toward his left (viewer right). Call it a **right-origin horizontal**; do not silently equate this with an engine's named `Right` enum or reverse it based on screen direction.

The initial camera is comparatively stable and both the preparation and return are present. “Neutral-looking” means a conventional upright attack without an obvious extreme lean, overhead preparation, or deliberate dramatic look manipulation. It does not establish neutral control inputs, root motion, or an unmodified animation asset. The attack contacts the viewer; damage distortion begins during late delivery/carry, so it is not a clean no-contact reference.

## Useful keys (exact sampled source PTS)

| Source PTS (s) | Visible observation | Evidence |
|---|---|---|
| 0.456067 / 0.539400 | Ready: upright blade near his right side, hilt in front of lower chest/upper abdomen, elbows flexed and hands separated along grip. | first_swing frames 1–2 |
| 0.628300 / 0.711633 | Preparation begins: joined grip travels outward toward his right; arms open while torso starts turning. | frames 3–4 |
| 0.794933 / 0.878333 | Hands remain forward/right, then begin drawing toward shoulder; blade changes from upright diagonal toward a flatter rearward line. | frames 5–6 |
| 0.978267 / 1.061567 / 1.144933 | Loaded silhouette: elbows bent, grip near right upper chest/shoulder, blade extending behind and across upper silhouette; torso turned, face still broadly toward opponent. | frames 7–9 |
| 1.228233 / 1.311567 / 1.394867 | Delivery: torso opens toward frontal, both arms extend outward together, hilt advances before passing across center; weapon is foreshortened toward viewer. | frames 10–12 |
| 1.478267 / 1.561600 | Cross-body passage toward his left; elbows begin folding. Viewer damage distortion and camera displacement contaminate screen-space trajectory. | frames 13–14 |
| 1.644933 / 1.728267 | Left-side carry: grip high near left chest/shoulder, bent arms wrap across torso, head tilts/turns down toward carried side. | frames 15–16 |
| 1.817167 / 1.900433 / 1.983767 | Return: torso faces forward, hands unwind inward and downward, blade rises to near vertical in front of face/chest. | frames 17–19 |
| 2.067100 | Ready silhouette restored. | frame 20 |

These are sampled visual landmarks, not game windup/release/recovery boundaries. Adjacent samples are roughly 0.083–0.100 s apart despite a requested 0.08 s step; actual PTS must be used. A defensible broad description is preparation visible by 0.628300, loaded by 0.978267, outward delivery visible by 1.228233, carry by 1.644933, ready again by 2.067100. Do not convert those observations into exact engine phase durations.

## Corroborating repetition

`B/repeat_swing` samples **6.450367–8.411500 s**. Ready at 6.450367; hands open right at 6.533733–6.706033; bend into same shoulder load at 6.872633–7.044833; extend through delivery at 7.128133–7.389300; carry left at 7.472667–7.722600; unwind at 7.805900–7.889200; ready by 7.978100–8.061500. The repeated pose order supports the first-cycle interpretation. Player yaw/position shifts are conspicuous during this cycle, and damage/blood further obscure delivery. Use it for pose corroboration, not a cleaner trajectory measurement.

## Animation implications and limits

- Preserve a connected two-hand grip and a coherent hilt path: ready → forward/right opening → bent-elbow shoulder load → outward cross-body delivery → folded left carry → inward/downward return. A blade-only rotation would omit the most readable movement.
- The breastplate changes orientation with the arm action. The head remains more opponent-facing during the right load than the torso and then turns/tilts into the carry. These are observable silhouettes; exact spine distribution, shoulder joint angles, neck counter-rotation, and muscle mechanics are inferred, not measured.
- The hilt and both hands are generally clearer than the blade tip. Foreshortening, player sword/arms, frame edges and blur prevent reliable full 3D blade-plane reconstruction. “Horizontal” describes a lateral cross-body strike, not a perfectly level blade or constant-height hand path.
- Lower legs/feet are partly obstructed in the preferred cycle. Later full-body views show stance changes but cannot separate locomotion, camera movement, root turn and authored foot action. Do not prescribe exact foot planting, hip translation or root motion from this clip.
- Armor hides joint centers. Camera tilt/yaw, perspective, NPC tracking and contact effects preclude degree-accurate torso/head angles or world-space speed. No inference about networking, attack inputs or engine contact timestamps is warranted.

## Evidence and method

Viewed both `B/overview/sheet-01.jpg` and `sheet-02.jpg`, then both sheets in `B/first_swing` and `B/repeat_swing`. This was decoded frame-sequence inspection, **not continuous real-time playback**. Each sequence retains full-resolution original frames; fixed crops are only used for its contact sheets. `frames.json` maps every file to actual source PTS and `receipt.json` records source identity, crop and extraction settings. No source video or animation assets were changed.
