# Arm polish handoff — pause snapshot, 9 September 2026

**Historical pause snapshot. Work resumed at Daniel's request; the active [checkpoint](THIRD_PERSON_CHECKPOINT.md) owns subsequent experiment and selection status. The rejected sources and findings below remain evidence.**

Read `C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/AGENTS.md`, [DEVELOPMENT](DEVELOPMENT.md), the current [arm brief](ANIMATION_SPECIALIST_BRIEF.md), and [polish process](MORDHAU_POLISH_PROCESS.md). Policy MCL-DEV-2026-09-08. Preserve EX_v002/config, production TP, sword path and clock. Keep experiments isolated; no automatic import/promotion or broad tests.

## Reevaluate first

- [Batch gallery](../ArtSource/AnimationLab/arm_brief_20260909_first/index.html): **A_square_drive, B_folded_support, C_open_delivery**, all complete/editable and rejected. K is also user-rejected.
- [A versus K at1x](../Saved/MordhauArmBrief/A_square_drive-before-after-1x.mp4), [A close](../Saved/MordhauArmBrief/A_square_drive-close.jpg), [A grips](../Saved/MordhauArmBrief/A_square_drive-grips.jpg), [final batch critique](../Saved/MordhauArmBrief/critic-batch1.md). Equivalent B/C evidence is beside these.
- [Reference index](MORDHAU_REFERENCE_INDEX.md): primary yellow-mask neutral RH30.0–31.5s; supplementary B1.394867 for grasp. Notion authorities were refreshed and unchanged. Reuse indexed footage/docs in their stated roles. Agent inspection was **sampled frames only**.

## Findings

Mirrored CF palm seating and CF-specific finger curl improved the initial fists. Transport still fails: support-hand U-thumb/lifted hooks at73/94; triangular right forearm at19/63; pinched upper arms and shoulder shelf at73. C is worst. Initial closed fists and matching ready/end matrices did not establish successful motion.

Leading implementation hypothesis: `frame_arm()` replaces all four arm-segment orientations with a full elbow-plane frame plus large absolute roll keys, over-rotating the chain against its shoulder. This is not proven causality or proof of bad skin weights. B's folded carry87–105 is a useful fragment; **A is the unchanged control for the next experiment**.

## Next bounded action

Make **one** complete A-based corrective candidate. Retain upstream shoulder/segment orientation, then distribute small explicitly authored local axial contributions; avoid another imposed-hand residual solver. Track grasp correction separately.

Unbuilt proposal: `Saved/MordhauArmBrief/staging_transport/Tools/AuthorThirdPersonSwing.py`. It also proposes diagonal-shaft-aware enclosure. **Not syntax/runtime verified.** Author four-value `arm_local_roll_R/L` arrays at every beat, freeze a NEW batch with actual input hashes, then use `python Tools/AnimationLab.py render <new_batch> --candidate <new_id>`. No second batch exists. Do not rerun old `freeze.py` unchanged: it targets the existing first batch and old controls.

Compare complete512×416 FrontThreeQuarter1x motion, close19/40/63/73, grips73/94, departure19–29/return105–117 and ready reset with the same critic. Require visible arm/grasp improvement before selection; continuous human/play acceptance remains open.

[Receipt](../Saved/MordhauArmBrief/final-receipt.json): three source/control/preview identities, unchanged blade controls/path62–82 and93 protected files. No runtime changes. `Saved/MordhauArmBrief/evidence.py <candidate/TP_v001>` generates whole-sheet/K comparison from its finished preview.
