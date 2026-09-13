# Clip A — Greatsword rear-view analysis

Source: `C:/Users/Daniel Pang/Videos/Captures/MORDHAU   2026-09-08 01-36-39.mp4`. The user identifies the weapon as **Greatsword**. 1920×1080, container duration approximately 17.13 s. Source identity and metadata are in `A/overview/receipt.json` and `decode.log`.

Preferred reference: **5.383900–7.278233 s**, including ready padding. The decoded source-speed excerpt uses the same 67 frames. This is a separated right-origin lateral cut with a visible return, viewed from behind. Exact neutral input and named attack enum are unconfirmed; this classification follows visible loading on the character's right and passage toward the left.

## Observed construction

| Beat | Sampled source PTS (s) | Direct visual evidence | Authoring implication, not recovered rig data |
|---|---|---|---|
| Ready | 5.383900–5.528333 | Blade near vertical on the character's right; shoulders comparatively level and back near frontal to camera. Hands are partly hidden in front of body. | Start from an economical asymmetric ready. The prompt's stomach-height hand placement is a design choice, not something this rear view precisely measures. |
| Load | 5.561633–6.139367 | Grip moves toward screen/character right and downward; shoulder/back silhouette turns and inclines with it. Elbows take different shapes. Late-load hands approach the lower image edge. | Transport the hilt with coordinated shoulders and changing elbow flexion. Avoid a fixed hilt with only blade rotation. Hidden depth, pelvis and the lowest grip position cannot be measured. |
| Delivery | 6.167233–6.567167 | Hilt rises from low right toward head/shoulder height, travels across the forward silhouette and exits left. Arms rise and reorganize; visible back/shoulder orientation changes as the weapon crosses. | The lateral strike has a curved, height-changing hilt path. A horizontal attack should not become a constant-height wrist sweep or a rigid torso-and-arms turn. These visual samples do not identify the damaging interval. |
| Carry | 6.595000–6.878233 | Grip continues down/left, arms extend across the left side, shoulders remain turned; the sword progressively descends toward the lower-left edge. | Give the exit its own shape and persistence. Continue body participation beyond the central crossing, then absorb the carry. Do not teleport to ready. |
| Return | 6.906000–7.278233 | Blade rises from left through diagonal to upright while the torso unwinds and hands come inward. By 7.278233 the near-ready rear silhouette has returned. | Recovery traces a distinct route. It does not simply reverse the high outward delivery arc. |

The last near-ready sample at 5.528333 precedes the first clear departure at 5.561633. First departure to near-ready at 7.278233 is approximately **1.72 s of observed motion**. It is not an input-response measurement or a windup/release/recovery specification. PTS precision identifies frames, not biomechanical event certainty. Decoded sample intervals in this section vary, commonly about 0.028–0.033 s; the container's ~33.73 average fps and 59.94 tbr must not be used as a universal frame-to-time conversion.

## Corroboration and exclusions

- Opening repetition: load visible by 3.283867, lowered right grip by 3.561633–3.706167, raised delivery at 3.956167–4.078333, left carry at 4.228233–4.500500, ready by approximately 5.039367. This corroborates the distinctive low-right → rising cross-body → low-left → upright sequence.
- Later repetitions cover approximately 8.1–9.7, 10.0–11.5, 12.4–14.1 and 14.8–16.4 s. Camera pitch/yaw and terrain framing change, so they are supporting examples of the recurring pose order and aim variation, not the primary fixed-camera measurement set. Times here are coarse overview windows.
- Background landmarks are comparatively stable in the selected 5.38–7.28 s span. They move strongly outside it. No camera calibration or world-space subtraction was performed.

## What this clip adds and leaves unknown

The exposed back makes changing shoulder silhouettes and arm transport much easier to inspect than armored footage. The weapon is visibly carried by the arms/body through a broad curved route. The head moves less conspicuously than the shoulder silhouette during parts of the load, but this view does not expose gaze direction or exact cervical compensation.

Feet and much of the pelvis are outside the original frame. HUD occludes the lower torso; hand overlap, blade clipping and foreshortening hide parts of the motion. Do not claim a support-foot change, heel pivot, exact weight transfer, ground reaction, 3D joint angles, grip pressure or weapon speed from this evidence. A supported lower-body block would be an authored interpretation pending fuller reference/visual review.

Evidence: full-resolution original extracted frames and source PTS maps in `A/neutral-native`; wider sampling in `A/opening` and `A/later`; compact selection in `A/selected-beats.jpg`; source-speed excerpt in `A/selected-source-speed.mp4`. Review used decoded frame sequences, not continuous real-time playback. All source files remain unchanged.
