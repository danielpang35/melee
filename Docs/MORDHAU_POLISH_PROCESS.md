# From playtest swing to Mordhau-quality motion

> Dated evidence and assignments below are superseded for current execution by [DEVELOPMENT](DEVELOPMENT.md) and the [TP checkpoint](THIRD_PERSON_CHECKPOINT.md). See [documentation ownership](DOCUMENTATION_OWNERSHIP.md). Historical timing, candidate and issue status are not live values or authorization to resume deferred work.

## Governing direction — 9 September 2026 architecture reassessment

Daniel rejects the current complete motion as stiff and weak and requests a comprehensive audit and plan. The active [architecture plan](MORDHAU_ANIMATION_ARCHITECTURE_PLAN.md) supersedes earlier local-refinement assignments and universal zero-wrist, low-elbow or clear-face prescriptions. Target a powerful reference-directed hand launch, exaggerated but continuous body/arm/grasp motion, and a convincing complete performance. Subtle wrist articulation and useful nonphysical deformation are allowed; the sword follows the authored grasp. Current local refinement is stopped. Earlier wrist-direction feedback is not whole-animation acceptance. Preserve EX/runtime/gameplay; this audit does not itself implement or promote the new architecture.

## Current authoring authority

Daniel's latest direction is arm-led motion with stable local wrists: body/arms move the hands, and the sword follows their grip. For the active source study, this supersedes the fixed hilt/blade-path constraint below. A derived source path may diverge; protect accepted EX and runtime gameplay, retain the derived track, and require explicit integration reconciliation before promotion. Follow the top of [THIRD_PERSON_CHECKPOINT.md](THIRD_PERSON_CHECKPOINT.md) and [specialist brief](ANIMATION_SPECIALIST_BRIEF.md). Earlier path-preserving experiments are history, not the new dependency direction.


Process adopted for execution, 9 September 2026. Policy MCL-DEV-2026-09-08. This document specifies the production loop; it does not itself establish animation acceptance. [THIRD_PERSON_CHECKPOINT.md](THIRD_PERSON_CHECKPOINT.md) records the executed batches, current selection and unresolved quality gap and remains the sole moving selection/acceptance checkpoint.

The same animation critic reviewed this process twice; [findings and review scope](MORDHAU_PROCESS_CRITIC.md). The second review's evidence-index clarification is incorporated below.

The objective is a neutral right-horizontal swing with Mordhau-level readable preparation, forceful delivery, convincing grip/body coordination and effortless carry, followed by that quality in a playable exchange. Mordhau is the motion gold standard. A numerical score, matching blade coordinates, or a better elbow pose cannot establish parity. Daniel's source-speed visual and playable acceptance closes the work.

## Starting point and protected work

Resolve the active source, unchanged comparison and next assignment from the top of [THIRD_PERSON_CHECKPOINT.md](THIRD_PERSON_CHECKPOINT.md) before editing. The resumed review rejected D/E structural experiments, subsequent G/H whole-route performances and J weapon-frame transport; F is static diagnostic evidence and I an invalid input study. Useful proximal-arm/right-wrist gains do not close the support-wrist and whole-route blocker. The [current specialist brief](ANIMATION_SPECIALIST_BRIEF.md) supplies the editable packet for a bounded direct authoring/control experiment on the existing rig. Do not restart completed wrist/roll or minor route variants; [critic findings](../Saved/MordhauPolishReview/critic-review.md) identify the persistent limitation without declaring the rig or canonical path impossible.

H_support_fold and its sampled C2/C3/C7/C9 = 5/6/6/6 assessment are historical choreography evidence. Retain the liked body drive, eased approach and restrained wrists where compatible, but do not restart from H or reuse its scores as a current assessment. Continuous timing and native gameplay acceptance remain open.

Preserve approved `EX_v002-source-1615b76b-FBX-6a34514c-native-unreduced-v1`, `Config/EXPreview.json`, current production TP and C++ attack/contact authority. Exploration uses isolated AnimationLab candidates. One author owns edits and selection; one animation critic is reused through the workstream. Critic reviews do not edit source or promote assets. Serialize renders/imports/builds and preserve unrelated dirty work.

## 1. Establish the critic's complete reference packet once

At execution entry, inventory all supplied animation footage and animation documentation, including linked Notion Animation, Swing Model and SWING-01 pages. Refresh current design authority then; this draft uses the local documented state. Record source availability, identity, actor, weapon, neutral/riposte entry, manipulation, visible interval and review method. Mark each source reviewed, context-only, superseded, excluded for this action, or unavailable. Missing clips stay explicit; a report about footage is not direct inspection of that footage.

| Material | Required role in the review |
|---|---|
| [Corrected Mordhau catalogue](MordhauAnimationAtlas/README.md), frame catalogue and original tutorial identified by its receipt | Primary TP neutral RH: yellow-mask opening actor, 30.0–31.5 s; visible preparation around 30.2–30.7 s. Review surrounding action to preserve actor identity. Foreground parry/riposte hands are another actor. Recovery is partly obscured. |
| [Third-person A/B captures](ThirdPersonReference20260908/REVIEW.md) and clip analyses | Supplementary Greatsword A at 5.383900–7.278233 s and Training Sword B at 0.456067–2.067100 s. Different weapons/actions/cameras; do not splice them or reinstate the older primary-reference wording. Use them for supported body/carry questions. |
| [Confirmed first-person Greatsword reference](MordhauRightReference/REFERENCE.md) and matching contract | Approved FP context; selected neutral attack 15.775733–17.775500 s at native PTS. It is not a recovered external skeleton or permission to replace accepted EX. |
| [Ren report and footage](REN_MORDHAU_REFERENCE_REPORT.md) | Economy, moving hilt and deliberate manipulation; separate camera/footwork from base animation. |
| [Kronk report and footage](KRONK_MORDHAU_REFERENCE_REPORT.md) | Expressive exchanges, carry, target changes and consequence; wider manipulation stress cases after neutral selection. |
| Remaining corrected tutorial families | Coverage/context now; use the correct parry side and attack origin when authoring the later riposte. RH-A/RH-D are excluded from the neutral-load target. Neutral overhead/underhand remain unverified. |
| [Workflow](ANIMATION_WORKFLOW.md), current checkpoint, [rubric](ART_CRITIC_REVIEW.md), [development](DEVELOPMENT.md), [validation](../VALIDATION.md), [production handoff](MEL15_PRODUCTION_HANDOFF.md), specialist brief and animation source decisions | Current constraints, existing capabilities, prior failures and acceptance boundaries. Archived instructions are history, not renewed gates. |
| [Reference direction](MEL17_REFERENCE_ROUTE.md), [art guide](Visual/STYLE_AND_PERFORMANCE.md), [UI guide](Visual/UI_STYLE_GUIDE.md) | Presentation context for integrated review; other games do not replace Mordhau as sword-motion authority. |

The critic considers the whole packet but cites the relevant exact clip/beat for each recommendation. Reuse unchanged reference evidence on subsequent passes; revisit the disputed interval and any new documentation. Do not rewatch unrelated footage on every elbow change. Index any additional discovered animation references before calling the packet complete.

Maintain the existing `Docs/MORDHAU_REFERENCE_INDEX.md` as the single evidence index, not another selection checkpoint. Keep document review separate from footage review. Use a row per inspected interval with native PTS/timestamp basis, actor/action/POV, reviewer, evidence link and observation mode (`document`, `sampled_frames`, `continuous_1x`, `context_only`, `unavailable`). Keep source role/exclusion in a separate field. Attribute Daniel's continuous-review feedback to Daniel; it does not turn an agent's sampled-frame inspection into continuous viewing. Reuse unchanged integrity receipts; decode/hash success verifies file usability and identity, not motion quality or absence of recording artifacts.

Compare each whole action at its native speed. Align one visible landmark for side-by-side presentation, label differing durations and avoid time warping, inferred synchronized views or copying screen coordinates into world-space joints. Slow motion and sheets diagnose a specific fault after the whole-action comparison. If the agent can inspect only frames, record that limitation; source-speed weight/rhythm remains for continuous human review.

## 2. Critic diagnoses the performance before authoring

Review the active unchanged control and primary N-RH side by side, then consult supplementary footage for the obscured carry and grasp. Break the whole performance into ready, opening/load, moving reversal, early drive, passage, carry and return. For each beat state what is visible, the artistic interpretation and what cannot be established.

Deliver no more than three ranked blockers. Each blocker must include:

1. Candidate frame/time and reference actor/time; direct observation and confidence.
2. Why it weakens intent, weight, path, coordination or recovery at gameplay distance.
3. Exact source file/control family and interval to change, direction of change, and elements to preserve.
4. Expected visible improvement and one regression to watch for.
5. A comparison that would falsify the recommendation, plus whether it changes the shared blade/phase contract.

Reject vague instructions such as “make it fluid.” Do not invent precise joint angles from occluded footage. Derive numeric control edits from the actual rig, label them experimental and judge their visible result.

## 3. Author three distinct complete performances

For a new choreography search, create a fresh batch using the existing [AnimationLab commands](ANIMATION_WORKFLOW.md), keeping the active control unchanged. The hypotheses below describe the earlier H-era choreography search; that search has already run and must not be repeated as unfinished work. Use the current brief's hypotheses instead. A demonstrated isolated defect can justify one structural experiment, but the resumed A-based transport experiments have already run. Do not count repeated joint offsets as distinct performances.

| Candidate | Concrete authoring experiment | What must remain convincing |
|---|---|---|
| A: compact lateral load | Lower and lateralize preparation before release, coauthoring hilt position/direction with shoulder aim and torso placement. Ease into a moving reversal; distribute the departure into early delivery. | Reads as a right horizontal, without a high overhead cue or a sudden approach surge. |
| B: body clears the crossing | Change pelvis/chest sequencing and shoulder placement relative to the fixed release hilt. Keep the head above/clear of the crossing mass and let elbow opening develop progressively. | Preserves liked body commitment and connected grips without excessive ducking, stretch or an arm-driven rigid torso. |
| C: outward delivery into absorbed carry | Redistribute non-damaging approach and exit travel, with an outward opening and a distinct lower carry before the support arm folds home. Coauthor torso deceleration and return. | Powerful passage continues through the target line; no early pullback, wrist flourish or mechanically reversed recovery. |

These are whole-action hypotheses, not three elbow offsets. Resolve editable controls and the actual author snapshot through the active checkpoint; work on new candidate copies. Relevant controls include `h`, `d`, pelvis/chest controls, shoulder aims, elbow poles, `power_bend_deg`, `power_extension` and grasp articulation. Inspect the snapshot author's actual interpretation before assigning values. Current frame landmarks are diagnostic coordinates, not a required format for future clips.

Preserve canonical damaging blade path and phase by default, currently inspected around 62–82. A connected support hand cannot have shorter world reach while the hilt is fixed; elbow-pole changes alter silhouette only. If credible staging cannot work within that path, document the exact restriction and create a separately labelled source-only path experiment. Reconcile any proposed path/phase change explicitly across gameplay/FP/TP before integration. No silent compensating runtime layer.

Render the complete candidates at 512×416 source speed in one fixed camera, serially: normally three for choreography, or one for the justified structural experiment above. Keep baseline and all candidates on the same clock/camera. No imports, C++ builds, broad tests or pose matrices for this stage.

## 4. Repeated critic → implement → verify loop

The same critic ranks the batch on whole-action intent, load/delivery contrast, hilt/blade route, body/arm coordination and recovery. “Reject all” is valid. Pick a provisional winner autonomously; do not ask Daniel to approve every draft.

Apply the top one to three coherent corrections to a new copy of the winner. Render the complete action and return it to the critic. Compare the active unchanged control, previous take and new take; mark each previous blocker resolved/partial/unchanged/regressed and cite visible evidence. A requested change is not evidence of success. Review the final refined take too. Record arm transport and grasp changes separately; a combined result cannot establish which change caused every improvement.

Continue while convincing gains occur. After two refinement passes without convincing improvement, stop local repair and return to a materially different complete-motion batch or a bounded control experiment addressing a demonstrated limitation. Do not reset that count by renaming the same elbow edits. After two coherent batches expose the same specialist limitation, prepare the [one-exchange specialist brief](ANIMATION_SPECIALIST_BRIEF.md), attaching best/rejected motion and the failing interval. No automatic commissioning; the unresolved quality gap remains open.

Keep critic decisions short, with the smallest top-priority backlog. Update one checkpoint with selected identity, reference version, last resolved blocker, current blocker, review modality and next action. Retain editable source and unique evidence. Record time to reviewable batch and rework where measured.

## 5. Select by the visible quality bar

Advance a provisional winner when no major source-motion blocker remains and a source-speed review supports these conditions:

- The load clearly promises a lateral cut; slowing toward reversal contrasts with committed delivery without a frozen wait.
- Hands transport the hilt and the blade sweeps through; the central passage does not read as a stab or a broad arm band across the face.
- Body drive, delayed arm opening and restrained wrists explain the weapon's apparent weight; no conspicuous snapping, disconnected grips or distracting collapse.
- Carry absorbs the action before a deliberate return; the finish feels connected to delivery and can lead into the next legal action.

Use scoped C2/C3/C7/C9 anchors of at least 8 as a review target, with every blocker explicitly assessed; do not average away a weak category. Frame-only scores cannot satisfy continuous C9 or certify parity. Daniel's normal-speed reference comparison establishes whether the source feels polished enough. If that input is pending, report “source candidate ready for visual review,” with timing/feel still open, rather than manufacture acceptance.

## 6. Carry the winner into a playable exchange

Use the existing explicit selected export/native TP import route once. Check the changed source intent in the actual defender view at gameplay distance. Preserve EX and record actual selected package/config/module identity. Review neutral hit and miss, then author/finish ready → parry → right riposte → carry → ready using the correctly classified riposte reference and the same critic loop; a neutral swing is not a riposte entry pasted after parry.

Review hit, miss, interruption and controlled aim/footwork at unchanged clip speed. The critic now checks threat direction/reach, grip/deformation after export, transition continuity, grounding, and whether sound, reaction, camera and restrained effects communicate the resolved event. Fix faults where they originate. A pose-only correction does not require C++ tests; a contact/state/timing change requires the affected build/tests and one independent consequential-code review under VALIDATION.md.

Return integrated visual faults to the same critic and author until resolved. Use one additional view only for a specific ambiguity. Target-resolution/temporal or performance evidence is needed only for claims about those properties; a cheap 30fps preview does not establish the project's 100–144 FPS target.

## Completion and handoff

“Mordhau-level selected sword swing” requires both the source comparison and the playable result: critic blockers closed with appropriate evidence, no unexplained threat/contact mismatch, and Daniel's explicit visual/play acceptance. Scores are supporting judgments, not a guarantee of equivalence. Missing continuous or playable evidence remains open, never silently passed.

Deliver the selected editable motion, a short unretimed reference/before/after comparison, the final critic assessment with resolved blockers, and one playable benchmark with its identity. State the visible gain, relevant checks and remaining limits. Only then expand opposite horizontal, overhead and the remaining vocabulary through this same process. Completing one polished swing does not certify the entire animation library or game.
