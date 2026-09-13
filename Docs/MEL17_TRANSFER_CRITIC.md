# MEL-17 source transfer critic

8 September 2026. Independent visual review against `MEL17_UNREAL_STYLE_PLAN.md`. **Latest: USP_v016 daylight and sampled motion poses are satisfactory; P5 temporal review remains open because videos were not played. P4 and source P2 passed. No user material acceptance is claimed.** Each applicable criterion requires at least 8/10. Earlier findings below are preserved history; the final section supplies the current verdict.

## Inspected evidence

Actually opened with `view_image`:

| Image | SHA-256 |
|---|---|
| `Saved/ArtReview/UnrealStyle/ST_v001/Review/front_smooth.png` | `94a1672ca8b1d4d5039f871a7bac20abf31937f94e7d88572ca2d32bc0d5e42a` |
| `Saved/ArtReview/UnrealStyle/ST_v001/Review/front_authored.png` | `52726127b004f379e1161e9103fb663f40ee5ed1d39a5b0bd369bc591ee7ff2d` |
| `ArtSource/StyleReference/MEL17/06-riot-inspired.png` | `77f24b0957c979ccf57480bf030672011983631b8b231ec4909f12da277bbd6e` |
| `ArtSource/StyleReference/MEL17/Steel_v025/steel-study.png` | `27a3b807d078c95c61dde569833029c06f5ad4baa26a0a2a6ab04f957a34cb6e` |

The portrait supplies construction and warm/cool reference; its crowded surface pattern is moderated by the user's smoother correction and accepted Steel_v025. No historical critic score or source mathematics supplies acceptance here.

## Front findings

| Criterion | Score | Visual finding |
|---|---:|---|
| Steel character | 8/10 | Convincing continuous metallic response, warm lower reflection and cool crown/right reflection. Neither chalky nor painted. Local block boundaries compromise finish but the underlying steel character is present. |
| Restrained variation | 6/10 | Broad quiet areas are appropriate; upper-left visor highlight exposes square stair-step islands, approximately x285–435/y315–458 in the 900×1100 front image. Weaker square contours occur on the lower face. These resemble a coarse field rather than the accepted armor's broad irregular planes. This is the blocking material defect. |
| Selective edge treatment | 8/10 | Center ridge, aperture rim, crown overlap and lower return remain crisp with narrow highlights; broad faces are not uniformly outlined. The sharp side reflection catches already appear in the smooth control and should not be blamed on authored regions. Side-view selectivity remains untested. |
| Accepted form preservation | 9/10, visual front check | Silhouette, slit, crown overlap, center ridge and chin return appear unchanged across the pair. No new apparent front dents from the broad fields. This is a transfer check, not renewed Clay_v005 shape approval or a geometry identity audit. |

## Required correction

Correct the stepped region contours before motion or Unreal work. Inspect region classification/interpolation at the bright visor first; create clean broad irregular boundaries with a controlled narrow transition. Preserve the constant-plane character inside regions, quiet lower face, and existing construction protection. Do not solve this by globally blurring the normal field, adding noisy detail, increasing roughness, or redesigning accepted geometry. Re-render the affected front A/B and matched three-quarter evidence under the fixed source rig.

## Limitations and next gate

This bounded pass did not inspect appended unchanged armor comparator, original portrait detail crop, native-size helmet comparison, source graph/normal samples, or rig settings. No rotation was played or sampled. P2 requires satisfactory remaining still evidence and then fixed-light rotation; there is no P3 authorization from these scores. Engine, daylight, gameplay distance and motion continuity remain entirely unreviewed. Source agent and coordinator received the blocking finding directly.

## Three-quarter follow-up, same revision

Opened `Review/three_quarter_smooth.png` (SHA-256 `569a4d8d3749d1d6b783328b04a6397994a9e14e06893c02653478db2268de6a`) and `Review/three_quarter_authored.png` (`6002311effc1465879e61a75e00e3ed1abcacb1e91a4b632143f2ea39281912e`) under the same ST_v001 evidence directory. The grid contour is more conspicuous across the enlarged left visor: approximately x325–550/y390–480, with an additional stepped notch around x465–520/y335–370. Scores remain steel 8, restrained variation 6, edges 8, form preservation 9. Crown, slit, ridge, visible side wall and chin remain visually consistent across controls. No second independent defect justifies broader rework. The source owner reports boundaries currently inherit the face graph's base grid and proposes continuous per-plate charts; that addresses the observed defect, but its result requires fresh visual review.

## ST_v002 changed-boundary review

Actually opened all nine images below from `Saved/ArtReview/UnrealStyle/ST_v002/Review/` with `view_image`, reusing the previously inspected unchanged portrait and Steel_v025 authority.

| Image | SHA-256 |
|---|---|
| `front_smooth.png` | `67c232c37fdd89fab65604c80a0446d4736f2c386a6daf8ddd9037c2bfd327b5` |
| `front_authored.png` | `34ddbbff7b33b77020c7310ca8dbd112f07fd21988fe7e054a287898e94d2272` |
| `three_quarter_smooth.png` | `9ad9e24b45fad8f11516ebe82eca5adbf8d15f7605b242019ee4647a0ca27a0b` |
| `three_quarter_authored.png` | `69e50df7dcac0fb083be596147ff09e5f14d1aebef18a844ef2e4dae3050ed8d` |
| `accepted_armor_comparator.png` | `5ffbfaed78006303e35b73396a04d34b690d58ba6fe9ac63f79a2bd1957244e9` |
| `front_native_pair.png` | `208b416211d84cc521358c7b67ee1ceedd674e1f91ec0113e9623730ffb1506e` |
| `three_quarter_native_pair.png` | `875cd9a1418b42cde42bf9bd3baccff8a6b69db454f798494cbb9b329ebaf180` |
| `front_portrait_detail.png` | `11bed39c76234067452469f6917db5da2c9b29b57306e2fd8544a24d9d5a94de` |
| `three_quarter_portrait_detail.png` | `31d3a4ad05e5273109bfcba4193dd9d7ec7bb2f8909dad11a3ab145651fb890e` |

| Criterion | Latest score | Finding |
|---|---:|---|
| Steel character | 8/10 | Warm/cool reflective steel remains coherent with the accepted comparator; narrow construction highlights survive. |
| Restrained variation | 8/10 | Square staircases are resolved into broad clean irregular planes. Variation remains legible near visor reflections and restrained across large cheek fields, matching the accepted smoother direction. The lower-left three-quarter cheek has an angular dark wedge; currently it reads as a controlled plane rather than a dent, but its response deserves attention during rotation. |
| Selective edge treatment | 8/10 | Rims and center ridge stay sharp; no broad etched outline or noisy edge damage. |
| Form preservation | 9/10, visual transfer check | Both pairs retain silhouette, slit, crown overlap, visible side wall, ridge and chin. Accepted Clay_v005 shape approval remains closed. |

Stills authorize the short fixed-light source rotation. Do not add roughness or alter geometry to improve these passing stills. The fresh armor comparator visually agrees with the accepted steel study; native pairs and enlarged helmet details reveal no additional blocking defect. The files named `portrait_detail` are helmet render crops, not a crop of the original reference portrait: the plan's original portrait detail comparison is therefore still unfulfilled as a packaged comparison, although the original portrait itself was inspected above. No rotation was played or sampled, no source rig/graph/identity audit was performed by this critic, and no engine or gameplay result is accepted. Final P2 remains pending these stated source-review limitations; P3 baking is not yet cleared.

## Final ST_v002 P2 source verdict

**Satisfactory source comparison; P2 passes for progression to P3.** Final scores remain steel character **8/10**, restrained variation **8/10**, selective edges **8/10**, and visual form preservation **9/10**. No score is averaged to conceal a material mismatch.

Additional actual `view_image` inspection, all under `Saved/ArtReview/UnrealStyle/ST_v002/Review/`:

| Evidence | SHA-256 / scope |
|---|---|
| `reference_helmet_native.png` | `2d2733e647e7578219a608aff334a99780c2e3f12c35e24e7294a5be24455206` |
| `reference_native_comparison.png` | `90fd3aa914ce46da6179fbd11c1d3390bc3869034f60471daeb84241485f3436` |
| `Rotation/contact.png` | `de22bda845731fca5c19d6f220f2e6424cc15a9fdad64536e48959799c9049be`; frames 0, 5, 10, 15, 20, 25, 30, 35 |
| `Rotation/Frames/0015.png`, `0016.png`, `0017.png` | Adjacent full-frame samples, identities recorded in `Rotation/rotation.json` |

The original reference detail is now present. At approximately 184-pixel helmet height the candidate retains clean construction, steel value separation and subdued plane variation. It deliberately has less surface pattern density than the original, consistent with the user's smoother correction and accepted armor comparator. No source-scale disappearance or added crowding blocks transfer.

The sampled yaw views preserve attached planes and continuous broad steel shading without visible grid borders or new apparent dents. The previously noted lower-left cheek wedge does not reveal a blocking mismatch across these sampled views. Construction-side highlights change strongly with angle, consistent with the smooth still control's existing response. No material correction is requested before baking.

`Rotation/rotation.json` was read and records 36 frames, 18 fps, two seconds, 448×560, fixed camera/lights and a -25° to +25° assembly yaw sweep. Its renderer receipt reports complete image decoding and 36 decoded video frames (video SHA-256 `3784e81fb7ac768065ffdda8c4a39bbc3eed6258256736d4659d0b14d0c45552`). This technical receipt is reused, not an independent playback claim. **The critic sampled still frames and contact images; the MP4 was not played.** Sampling cannot establish absence of shimmer, temporal swimming or all interframe discontinuities. Those remain explicit P5 engine motion gates, along with daylight/shade, gameplay distance and user material review. The current decision accepts the source comparison needed for P3 only.

## USP_v016 P4 neutral transfer verdict

**Pass for progression to P5 daylight and motion proof.** Actually opened all five ordinary PIE PNGs under `Saved/ArtReview/UnrealStyle/USP_v016/run_002/` with `view_image`; reused the reviewed ST_v002 source comparison.

| Image | SHA-256 |
|---|---|
| `transfer_matte_matched.png` | `81a1a5ed59c8377a359b94ea3a16d658b567b21c874c51d30d4db17058c9cb38` |
| `transfer_control_front.png` | `32c402459da856475d39a355ccc60f0543847c9137e82f2046af90198808700e` |
| `transfer_normals_front.png` | `7f941bf6a8cd7212dd3637ba6896ac0ac1da6dd6b43e07294f2d4523e2e294a5` |
| `transfer_control_threequarter.png` | `37f48abcabe478112c3d813b7fda1342e769debf68f4bf9761926da514324344` |
| `transfer_normals_threequarter.png` | `affb1719029f4a01cadc03f00ced9cd14cde5a8a712eea28d4948fd83f0fb900` |

Visual checks: silhouette, crown overlap, center ridge, slit, hinges and chin returns remain intact in matte and metallic views. The center construction seam remains a narrow line in both controls, without an authored-only seam catch or breakup. No visible UV boundary, inverted highlight, broken bevel or recurrence of the ST_v001 grid contours blocks transfer. Authored broad planes produce coherent local reflection changes relative to the smooth control while preserving construction.

Neutral-transfer scores: **form preservation 9/10; seams/bevels 8/10; normal-response coherence 8/10; neutral steel character 8/10.** Metal has readable specular response and edge definition. This grayscale rig lacks the source's warm/cool reflection separation, and its lower-face planes are more conspicuous while the crown reads flatter. P5 must judge reflection/color and restrained variation under the intended daylight before final material acceptance. These observations do not currently justify changing the accepted source or geometry; no blocking visual correction is requested before P5.

The coordinator's built-buffer validation and runtime configuration are technical evidence, not the basis of these visual scores. This pass covers only the inspected neutral stills. No engine motion was played or sampled, and daylight, shade transitions, gameplay size, temporal stability and human material acceptance remain open.

## USP_v016 P5 daylight and sampled sequence verdict

**P5 remains open for temporal visual review.** No blocking material defect was found in the inspected daylight stills and sequence poses. This is not a complete motion pass.

Actually opened the six `run_003/daylight_*.png` images: control matched, normals matched, combined matched, combined front, combined threequarter and combined gameplay. Also opened all three `ReviewDiagnostics/*_all_frames.jpg` chronological contact sheets, each containing frames 000–059 for helmet rotation, key sweep and shade transition. These are downscaled derivative contacts, not video playback. Follow-up inspection opened original full PNGs `run_003/motion/helmet_rotation/helmet_rotation_029.png`, `_030.png`, `_031.png`; `motion/shade_transition/shade_transition_000.png`, `_059.png`; and `motion/key_sweep/key_sweep_059.png`. Evidence directories are under `Saved/ArtReview/UnrealStyle/USP_v016/`; frame identities belong to the immutable run's capture receipt.

| P5 criterion | Score / status | Finding |
|---|---|---|
| Material character | 8/10 for inspected stills/poses | Metallic highlight and broad attached planes remain legible. No returned grid islands, apparent dents or seam failures require source changes. |
| Reflection/color | 8/10 for inspected stills/poses | Cool crown and warm visor separation survives daylight. Shade endpoint loses the direct visor highlight while retaining form and subdued variation; it does not collapse to an unreadable black silhouette. |
| Restrained variation | 8/10 for inspected stills/poses | Lower-face planes are stronger than source but remain broad and quiet at the declared small size. No added pattern crowding. |
| Distance readability | 8/10 for the declared still scenario only | Coordinator's measured inclusive box x705–820/y353–523 yields 171-pixel crown-to-chin height in the 1525×870 viewport (870-pixel square camera area). Slit, ridge, outline and steel highlight remain readable. This is not a user-approved gameplay distance or a distance-motion test. |
| Form preservation | 9/10 visual check | Accepted construction survives the sampled sweep and light/shade cases. |
| Motion/distance combined gate | **Unscored / open** | Videos were not played. Chronological contacts and six full-size samples cannot establish absence of distracting shimmer, swimming or temporal seam catches. |

Broad reflections change coherently through the ordered contact frames. Full-size moving rotation frames show more edge pixelation than the settled stills around the silhouette, hinge and fine crown seam; playback must determine whether this becomes distracting shimmer. No static evidence warrants changing geometry or material to address it now.

The coordinator reports a completed 186-image capture receipt, three consecutive 60-frame sequences at fixed 30 fps with next-frame screenshot completion, and an encoder receipt decoding all 60 frames per video. Those receipts establish technical sequence completeness, not visual temporal acceptance. **No MP4 was played by this critic.** Complete P5 requires temporal visual review of the existing videos; no recapture is requested on the current evidence. Human material acceptance and P6 remain unestablished.


## User acceptance and implementation closure

After receiving the three actual Unreal clips, the user explicitly answered **“Accept material and motion.”** `USP_v016/user_acceptance.json` binds this response to capture/video receipt hashes. This completes human material/motion acceptance without changing the critic's sampled-versus-played disclosure. The coordinator subsequently completed the isolated ST_v003/USP_v017 region edit/reimport and restored the preserved USP_v016 winning baseline; technical results are in `USP_v017/repeatability_receipt.json`. The demonstration is a repeatability check, not a replacement winning material or a new artistic score.
