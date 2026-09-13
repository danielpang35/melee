# Right overhead baseline and `OH_v001` authoring brief

> Dated evidence and assignments below are superseded for current execution by [DEVELOPMENT](DEVELOPMENT.md) and the [TP checkpoint](THIRD_PERSON_CHECKPOINT.md). See [documentation ownership](DOCUMENTATION_OWNERSHIP.md). Historical timing, candidate and issue status are not live values or authorization to resume deferred work.

## Status and evidence boundary

**Reference correction, 9 September 2026:** the [courtyard tutorial catalogue](MordhauAnimationAtlas/README.md) separates right-overhead ripostes after left parry (XR-A/B) and right parry (RO-A/D). Neither is independently verified as a neutral overhead exemplar; they do not remove the extrapolation limitation below.


The user has approved the visual result of `ArtSource/CharacterReset/EX_v002` as the horizontal baseline. That is approval to use its first-person composition, mass, timing character and connected two-hand presentation as the starting standard. It does not establish an exact Mordhau match, third-person or engine acceptance, collision/reach validity, or acceptance of an overhead that has not yet been rendered.

The confirmed capture and `Docs/MordhauRightReference/reference.json` directly support the horizontal event clock and visible hilt UV where measured. Offscreen UV, every depth value, roll, shoulder translation, arm-length multiplier, camera FOV and all hidden anatomy are reconstruction choices already declared in `pose-controls.json`. Ren R03 supports the qualitative combination of high preparation and low connected delivery under large player aim changes, but is not a neutral overhead capture. Therefore the trajectory below is an **authored overhead extrapolation**, guided by the accepted horizontal, Mordhau qualities and the Notion design principle that the body and hands must visibly generate the sword. It is not footage-derived overhead motion.

## What the accepted horizontal actually does

Coordinates are `[u, v, depth_m]`: `u=0/1` is left/right, `v=0/1` is top/bottom, and larger depth moves away from the camera. Values outside 0–1 deliberately place the weapon offscreen.

| Beat | Time from visible onset | Hilt | Authored roll | Meaning |
|---|---:|---:|---:|---|
| visible load start | 0.000 s | `[0.60, 0.73, 0.62]` | -15° | departure begins after 0.306 s pre-roll |
| delivery reentry | 0.722 s | `[0.98, 0.66, 0.58]` | +4° | hands/hilt return from the right |
| central passage | 0.833 s | `[0.53, 0.56, 0.72]` | +4° | closest named target-line beat |
| left exit | 1.028 s | `[-0.26, 0.92, 0.49]` | +10° | 0.306 s reentry-to-exit crossing |
| return blade | 1.667 s | `[-0.08, 1.08, 0.53]` | -15° | return begins after a clear carry interval |
| near idle | 2.000 s | `[0.54, 0.73, 0.62]` | -15° | economical reset; another 0.250 s idle tail follows |

The full key set sends the hilt as far as `u=1.47, v=0.90, depth=0.48` in the right load and `u=-0.70, v=1.40, depth=0.42` in the cleared left carry. Across all keys hilt depth ranges from 0.42–0.72 m. The passage moves away to 0.72 m while the offscreen carry comes close; this depth change and translated hilt prevent an axle-like blade rotation. The defining spacing is a patient 0.722 s load, rapid acquisition through a 0.306 s visible crossing, about 0.639 s of cleared carry, then a 0.333 s return.

`Tools/AuthorMordhauRight.py` line 18 linearly interpolates dense local pose intervals, preserving their nonuniform spacing; line 150 forces all baked F-curves to linear. At 60 fps this is a bake/presentation grid over source seconds, not a source-frame-rate claim. Hilt and tip screen/depth targets become camera-space points at line 32. The weapon quaternion is rebuilt per frame from the hilt-to-tip axis (`+Z`, `Y` up), then receives local-Z roll. `face_blade` blends that roll toward the camera-facing broadside at lines 100–104; quaternion signs are flipped when needed for continuity. Horizontal roll keys progress -15° → -10° → +4° → +10° and return to -15°; `face_blade` stays zero through the strike and becomes one for the returning blade face.

The paired grip is an intentional first-person construction. At line 109, right and left wrist targets sit 0.075 m and 0.155 m behind the hilt along the weapon axis, share a 0.082 m palm offset, and receive opposite 0.026 m side offsets. Wrist bases are mapped from the source palm axes; finger joints use fixed curls. Shoulder origins follow hilt displacement from `[0.50, 0.88, 0.60]`, and line 127 translates the shoulder when ordinary segment reach is insufficient. `arm_scale` ranges 1.05–1.50, with 1.50 confined to the offscreen load; this is editable first-person FK deformation, not a physical limb solve. The dedicated arm mask, up-to-0.025 m sleeve-envelope widening, compact pommel/rear grip, 1.6× blade width and 1.15× blade length are composition cheats worth retaining for the first overhead pass.

The camera is static at `(0, -0.115, 1.68)`, looks horizontally down world `-Y`, uses a 20 mm lens on a 36 mm horizontal sensor, and has no aim, sway or montage motion. Retain this exact projection for the overhead comparison so vertical hand travel belongs to the authored action and remains separable from player pitch.

## `OH_v001` authored overhead

The overhead should feel related through mass and tempo, not through a 90-degree rotation of the horizontal coordinates. Its main gesture is: paired hands rise and compress near the right shoulder; the lead side opens a steep cutting lane; both hands pull and then drive forward/down through the target; the hilt clears the high chest and finishes below the sternum, slightly left of center; momentum settles briefly before a compact return. The blade may clear the frame, but the lower-right sleeve mass should remain long enough to explain the load.

Use this eight-beat first-pass contract. The values are deliberately explicit starting hypotheses for visual iteration, not accepted measurements.

| Beat | Time from onset | Candidate hilt `[u,v,d]` | Candidate tip `[u,v,d]` | Roll / face | Pose and spacing intent |
|---|---:|---:|---:|---:|---|
| 1. pre-roll idle | -0.306 s | `[0.54,0.73,0.62]` | `[0.77,-0.10,0.90]` | -15° / 0 | reuse the accepted quiet lower guard |
| 2. load starts | 0.000 s | `[0.60,0.68,0.60]` | `[0.82,-0.18,0.88]` | -12° / 0 | lead with the paired grip; no instant elbow flare |
| 3. high-right compression | 0.472 s | `[0.75,0.24,0.48]` | `[0.92,-0.62,0.76]` | -8° / 0 | hilt close to right shoulder; elbows elevated in different, useful planes; retain lower-right sleeve mass |
| 4. release acquisition | 0.722 s | `[0.68,0.34,0.57]` | `[0.63,0.92,0.78]` | +2° / 0.15 | hands begin forward/down; trailing hand visibly pulls and wrists turn the edge into the lane |
| 5. target passage | 0.833 s | `[0.55,0.48,0.68]` | `[0.49,1.25,0.88]` | +6° / 0.35 | steep, slightly right-to-left near-vertical passage; hilt and both hands cross the target line with the blade |
| 6. low carry / finish | 1.028 s | `[0.43,0.88,0.72]` | `[0.34,1.55,0.86]` | +10° / 0.55 | hands finish below sternum toward upper abdomen/waist; shoulders and elbows extend behind the hilt, then settle |
| 7. carried hold and return pickup | 1.556 / 1.667 s | `[0.39,0.96,0.66]` → `[0.45,0.88,0.58]` | `[0.28,1.42,0.82]` → `[0.64,0.12,0.90]` | +10° → -10° / 0.7 → 1 | preserve weight briefly, then turn the blade face into a small readable return without a decorative loop |
| 8. near idle | 2.000 s | `[0.54,0.73,0.62]` | `[0.77,-0.10,0.90]` | -15° / 0 | arrive continuously at the accepted guard and keep the 0.250 s tail |

For the arm controls, begin around `arm_scale=1.08` at idle, peak near 1.18–1.22 in the high load/passage, and return through 1.10 to 1.08; avoid the horizontal's 1.50 offscreen extension because this load must remain bodily readable. Start `shoulder_follow` near 0.4, rise to roughly 0.65–0.80 through load/acquisition, reduce near 0.45–0.55 at passage, and use only enough follow in the low carry to keep the forearms connected. Replace the single horizontal elbow-pole behavior with overhead phase keys: right elbow supports the high-right load without winging, left/trailing elbow stays lower and pulls the handle, and both poles descend continuously behind the hilt during release. Hand contacts and weapon axis offsets remain paired; strict reach is secondary to a convincing first-person silhouette, but wrist folding, palm separation and sleeve gaps must be judged visually.

## Safe implementation boundary

Own the prototype as `ArtSource/CharacterReset/OH_v001/`, with `OH_v001_RightOverhead.blend`, `pose-controls.json`, `MOTION.md`, and `Preview/`. Add `Tools/AuthorRightOverhead.py` by copying the accepted generator into the new output namespace, opening `EX_v002_MordhauRight.blend` as a read-only starting asset, clearing animation in memory, and saving only into `OH_v001`. Do not change `Tools/AuthorMordhauRight.py`, `EX_v002/pose-controls.json`, or the accepted blend.

Reuse these stable hooks: `lerp_pose` and the 60 fps event bake (lines 18 and 90), `screen_point` (line 32), static camera setup (lines 50–55), weapon quaternion/broadside construction (lines 98–106), paired wrist basis and targets (lines 109–118), and explicit shoulder/FK solve (lines 121–138). Extend the pose schema with `elbow_bias_R` and `elbow_bias_L` vectors or an equivalent per-side overhead pole control; the current scalar `elbow_drop` and fixed pole at line 129 encode a horizontal-specific lateral/down preference and should not be rotated wholesale. Keep the accepted camera, weapon fittings, grip offsets, arm mask and sleeve envelope unchanged for the first key pass. Judge the eight beats first; continuous normal-speed review and any collision/engine work belong after the authored trajectory reads correctly.
