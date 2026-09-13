# Animation handoff — paused after rejected elbow correction

> **Dated record; active assignments and status superseded (12 September 2026).** Preserve the technical/design history below. [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) owns current source, selection, pilot outcome and resume; [DEVELOPMENT](DEVELOPMENT.md) owns operational scope. Step 4 (parry/riposte, branch integration, full-exchange packaging and expansion) is deferred. [Documentation ownership](DOCUMENTATION_OWNERSHIP.md) and [audit](DOCUMENTATION_AUDIT.md) define current authority. Linear owns live execution.

9 September 2026, 15:32 EDT. Workspace: `C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation`.

## Authorized successor

Daniel subsequently requested dispatch to **a new Astra High instance**, which should resume this work using subagents for bounded subtasks. This original instance remains paused. The successor must follow current Notion guidelines, use **Mordhau as the golden standard**, and actually inspect animations before delivery or production promotion. The latest tooling instruction authorizes the best available techniques: Blender MCP, Python, or other accessible tools that improve the result. Do not persist with unsuccessful pose/pole edits merely because earlier takes used them. The existing native rig is available, and a tool/rig change should address a demonstrated limitation rather than restart exploration without cause.

Refresh these Notion documents through the available connector on entry; the recorded versions are historical retrieval evidence, not a substitute for current guidance:

- [Animation](https://app.notion.com/p/3d32e3c3f8f881e08474defe7febb171?pvs=204).
- [Melee Swing Model](https://app.notion.com/p/3d32e3c3f8f881028f05c2a960248ff1?pvs=204).
- [SWING-01 — Mordhau defender animation atlas and implementation details](https://app.notion.com/p/3d52e3c3f8f88192ababd9338ad3797b?pvs=204).

[Prior authority receipt](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/Saved/MEL37Manual/design-authority.json>) records the last fetched versions. Distinguish current user instructions from historical execution notes in documents. If the successor starts in a fresh worktree, the absolute paths in this brief identify the authoritative existing assets and untracked handoff; do not assume its default git checkout includes them. Copy needed rules/assets into the isolated working area without overwriting originals or rebuilding from stale JSON.

## Current truth

**Work is paused at Daniel's request. N is rejected. Neither the elbow inversion nor the abrupt elbow changes has been accepted as corrected.** Earlier assistant/critic claims that N removed the jumps are contradicted by Daniel's latest playback feedback. Do not carry those claims forward as verified success.

Daniel explicitly confirmed **the sword motion is correct** in M. N preserved M's right/primary chain and sword motion. Preserve that result while fixing the arms. No whole animation has artistic acceptance.

Latest instructions, in order:

> “The upper arm needs to rotate with the body and the sword so the elbow doesn't have to ivnert”

> “The elbow is still inverted. We need to utilize an animation critic who reviews the animations before they are shipped. I already told you that the upper arm needs to point in the direction of the motion of the swing during the end of the swing, so that the elbow has room and so that the arms can continue to direct the swing.”

> “You did not correct the abrupt elbow changes either.”

> “Pause. Let's create a handoff brief for a new instance.”

**Do not reduce this to smoothing elbow-position jumps.** The proximal arm must orient into the swing at the end, giving the elbow room and allowing both arms to continue directing the weapon. Inspect shoulder → upper arm → elbow → forearm, including actual bend direction and surface deformation. Which arm/frames explain all of the latest rejection is not yet established; inspect both, especially late delivery/carry.

## Read at entry

- [Canonical AGENTS.md](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/AGENTS.md>) — policy MCL-DEV-2026-09-08.
- [Development rules](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/Docs/DEVELOPMENT.md>).
- [Animation prototype pipeline](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/Docs/ANIMATION_PROTOTYPE_PIPELINE.md>).
- This brief is the latest handoff. [Long checkpoint](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/Docs/THIRD_PERSON_CHECKPOINT.md>) contains historical, superseded claims; its paused status and Daniel's latest feedback govern.

Use small, bounded subagent assignments and one source owner. No child agents. Critic review must precede shipping/presenting another correction as ready. Preserve unrelated dirty work. No routine C++ builds, broad regressions or draft imports.

## Sources and live Blender state

**M — sword-approved reference; arms rejected:**

[M source](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/ArtSource/AnimationLab/MEL37_manual_swing/source/Candidates/M_forward_idle_return/TP_v001/TP_v001_RightHorizontal.blend>) · [M preview](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/ArtSource/AnimationLab/MEL37_manual_swing/source/Candidates/M_forward_idle_return/TP_v001/preview.mp4>)

Source SHA256 `b613985ddee8135bb865c0c4940f7d9e69ac56030ffc531f81ad87e7922f815f`.

**N_v2 — latest failed correction, not a selected winner:**

[N source](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/ArtSource/AnimationLab/MEL37_manual_swing/source/Candidates/N_left_proximal_carry_v2/TP_v001/TP_v001_RightHorizontal.blend>) · [N preview](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/ArtSource/AnimationLab/MEL37_manual_swing/source/Candidates/N_left_proximal_carry_v2/TP_v001/preview.mp4>)

Source SHA256 `a113df88f2af5b38412c21ed5f68e790365a8bd611bf27ea21470dfac2a39364`; preview `dbd2f49504ffe8560550d8b059a9c15c7f5c7e6c9ce0fe76add161625748473a`.

Both are 64 frames at 30 Hz: 2.1-second key span, 2.133-second MP4 including final-frame display. Keep original timing and sword attachment.

**Live Blender MCP is available, Blender 5.2.1.** At pause, readback confirmed this saved file, clean (`dirty=false`), frame41, playback stopped, range1–64, 30fps:

[Live N 5.2 source](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/Saved/MEL37Manual/elbow-correction/owner/N-v2-review-live-5.2.blend>)

The body and sword are already loaded; do not rebuild/reimport the rig. Verify filepath, dirty state and edit ownership before writes. Preserve this rejected take and work in a new copy. Live5.2 uses layered Actions; existing preview runtime uses Blender4.2. In N, only forty boundary-handle edits were transferred from the live5.2 snapshot into the4.2-compatible source. [Owner receipt](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/Saved/MEL37Manual/elbow-correction/owner/receipt.md>) records this bridge and its evidence; do not assume new live edits appear automatically in the preview source.

## What happened and why prior review failed

K independently rotated the weapon roughly a full turn within the primary grasp. L/M removed that compensation: `CF_Weapon` is rigidly attached to `CF_PrimaryGrasp`, with constant local rotation/location/scale. Corrected idle LH, baseball-like draw-back, forward-aligned finish and forward/up recovery led to Daniel's sword approval. **Do not restore per-pose weapon roll to solve the arm problem.**

M's native audit found conflicting left-arm pose families: a hand-derived elbow plane at16 switched to a fixed-down pole at17, then another opposite plane around28–32. Diagnostics measured approximately27cm elbow travel/75° plane change16→17 and a near150° reversal29→30. These are useful M failure localization, not proof N succeeded.

N rebuilt only left upper/lower-arm/wrist keys17/19/21/23/26/28/32 and repaired boundary tangents. Right/primary/sword/body/timing curves were unchanged; evaluated sword/primary matrices matched M at all64 frames. Left interkey wrist motion changed by up to39.6mm, and larger hand gaps remain in some frames. N's lower diagnostic plane steps and selected views **did not establish a successful visual correction**.

The prior critic tracked hand/sword and recovery fixes without adequately tracing upper-arm/elbow anatomy. M23 was already visible in the review sheet and was praised for projected hands despite the arm defect. The next review focused on16–32 and oblique23/26, then again claimed the jumps were gone. Daniel rejects that claim and reiterates the ending requirement. This is not merely missing samples; it is a failed interpretation and an incomplete acceptance criterion. Root accepted those reviews too readily.

[Earlier critic diagnosis](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/Saved/MEL37Manual/elbow-correction/critic-diagnosis.md>) and [rejected N review](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/Saved/MEL37Manual/elbow-correction/critic-N.md>) are evidence of the failed assessment, not authority that the arms are sound.

## Last unfinished work

The source owner and a newly assigned independent finish/anatomy critic were interrupted immediately on pause. The fresh critic produced no verdict. No O candidate exists and no further corrected animation was shipped.

Two read-only late-pose artifacts were saved before interruption:

- [N late-chain source data](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/Saved/MEL37Manual/elbow-correction/end-direction/owner/N-late-chain-source.json>).
- [Rejected finish41 oblique](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/Saved/MEL37Manual/elbow-correction/end-direction/owner/N-rejected-finish41-oblique.png>).

These were not fully reviewed by root. They do not establish a diagnosis or fix. Inspect them alongside actual N motion, especially23–49 and late32–45, without overlooking the earlier abrupt changes.

## Direction when work resumes

1. Establish a shared, concrete diagnosis with the animation critic before authoring: which upper arm points the wrong way, where the elbow inverts/jumps, and how the shoulder/upper arm must carry the ending. Use actual intermediate frames and a relevant oblique view. Do not label a visually wrong pose acceptable because a metric improved.
2. Make one coordinated proximal-arm correction on the existing editable body. Preserve the approved sword path/attachment/timing; investigate both arms rather than automatically declaring the compact right arm accepted. Keep grasp continuity visible while correcting shoulder/upper-arm direction. If constraints conflict, explain the demonstrated conflict instead of silently changing the sword.
3. Choose the best available authoring technique for the demonstrated defect. Sparse native FK and the existing static posing aid are available starting points; the latest user tooling authorization governs. If a different control/IK/baking technique is needed, test that specific improvement on an isolated copy and preserve editable/reproducible source. Remove conflicting inherited keys when rebuilding an interval; do not add another compensation layer that merely moves the defect elsewhere.
4. Have the critic review the complete motion before another delivery, explicitly judging the abrupt changes **and** late upper-arm alignment, elbow hinge/surface and continued arm-driven follow-through. Root must inspect the cited evidence rather than repeat a reassuring verdict. Frame inspection is not continuous playback or human acceptance.

Persistent artistic requirements: fluid, convincing motion; distinct wrapped hands; natural wrists/arms, with only brief inconspicuous deformation allowed; idle-left physical blade edge remains the striking edge; snappy accelerating draw-back/shoulder load with a thrown release; no axial flip during baseball-like windup; extended paired finish with blade following the arms. Mordhau remains the reference.

[Mordhau hand/reference strip](<C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation/Saved/MEL37Resume/hand-inversion/ReferenceB-windup-hands.jpg>) · [User ending video](<C:/Users/Daniel Pang/Videos/Captures/MORDHAU   2026-09-09 12-42-50.mp4>)

Preserve accepted EX_v002 source/native/config/projection, original F torso/follow-through comparison, KN body, production selectors and C++ gameplay/contact. M's isolated Unreal study exists; N was only previewed in Blender/MP4, with no Unreal import. No native animation study implies production or artistic acceptance. Do not restart old G/H/I/J blade/hand patch loops or commission an animator automatically.
