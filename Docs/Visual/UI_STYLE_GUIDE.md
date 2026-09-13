# MeleeCombatLab game UI style and implementation guide

> Derived local design/implementation reference. Notion owns product intent, reference interpretation, acceptance criteria and human decisions; this page retains implementation guidance and dated observations under [documentation ownership](../DOCUMENTATION_OWNERSHIP.md).

8 September 2026. Applies the [confirmed direction](../MEL17_REFERENCE_ROUTE.md) to a single-player melee practice slice. This is a design/implementation specification and evidence audit, **not an implemented UI redesign**. [ART_CRITIC_REVIEW.md](../ART_CRITIC_REVIEW.md) owns the main score; this page owns UI patterns, state coverage and player-facing language. Hound/original-knight materials and shapes guide identity; CS2/Valorant/Zelda supply approved category-specific quality references.

## Current implementation and scope

13 September 2026: the [Hound surface style guide](HOUND_SURFACE_STYLE_GUIDE.md) now owns the derived whole-game surface identity. Carry its restrained material/color hierarchy into future UI art while preserving the semantic tokens and readability requirements here; sampled steel colors are not replacement status colors. No UI implementation changes accompany this update.

`Source/MeleeCombatLab/Debug/CombatDebugHUD.cpp` draws Canvas text, health/stamina rectangles, reticle and parry/riposte/downed feedback. `CombatTuningPanel.cpp` creates a 520x760 Slate developer panel using stock SButton/SSpinBox/STextBlock. `CombatLabGameMode.cpp` owns tuning load/save/reset and panel input modes; `MeleeCharacter.cpp` binds F3/F4/F5 and keyboard/mouse combat inputs. `bDebug` defaults false, but EX revision/provisional-phase text is drawn before the debug early-return. The assessed G-FP frames visibly contain that text. CITADEL is a legacy visible label, not newly approved final branding.

The lab has no approved shop, inventory, equipment-selection economy, skills, quests, card system or progression. Those categories are NA until product decisions establish them. The Notion Game Structure explicitly leaves match rules/economy/progression open. Player pause/settings, training selection/help, downed/retry and startup/loading/recovery are required presentation flows for a distributable practice slice; completion is not established in this checkout. Dialogue and victory/reward screens are NA for the current lab; reference Zelda dialogue only informs hierarchy. Infinite-health passive dummy means a damage event is not automatically a win.

The developer tuning panel may retain technical field names, ranges and diagnostics inside a clearly marked development-only tool. It is not the player settings menu. Do not remove useful developer controls merely to make a screenshot attractive; isolate their exposure. Player settings must not offer “Promote to project defaults.”

## UI rubric and comparison

Scores below judge visible HUD/prompt presentation only. 1/5/8/10 anchors apply to future menus too; absent menus are NE. Each row's objective check is a review target, not an executed test.

| Category / weight | 1 / 5 / 8 / 10 anchors | Generated/UI failure modes | Objective review |
|---|---|---|---|
| Hierarchy and action clarity 30 | No focal action / usable after reading / subject, status and next action obvious / stays obvious in dense, failure and recovery states | Equal-weight buttons, text walls, decorative dashboard cards | One-second subject/state/action/consequence check; count competing primary actions |
| Type, spacing and icons 20 | Illegible / inconsistent but usable / clear at target size / robust at distance, scaling and localization | Tiny text, arbitrary icon sets, unrecognizable silhouettes | Actual display size, long labels, minimum target sizes and glyph checks |
| State semantics and feedback 20 | State or owner ambiguous / common states differentiated / actions/results/costs clear / timing and recovery remain clear under pressure | Red/green-only meaning, duplicate cues, raw errors | Named owner/resource; selected vs focused; input/result latency; error next action |
| Game-world cohesion 15 | Unstyled widgets / generic dark menu / knight-compatible shapes/materials / coherent visual and audio language in all states | Browser controls, bright SaaS cards, fantasy ornament on every pixel | Side-by-side HUD/menu/character frame; restrained borders, cloth/steel accents |
| Interaction and navigation 10 | Focus trap or nonfunctional / basic pointer flow / full input-state/back behavior / resilient switching/loading/error flows | Fake buttons, keyboard inaccessible controls, focus reset | Full state matrix below; pointer and supported controller/keyboard flow |
| Accessibility/responsiveness 5 | Content unreachable / some scaling works / legible non-color cues, safe areas, localization / all supported configurations preserve meaning | Clipping, hardcoded coordinates, motion-only feedback | Smallest target viewport, text enlargement, safe area, focus order and remapped input |

| Visible subcategory | Current HUD | CS2 | Valorant | Zelda | Evidence/gap |
|---|---:|---:|---:|---:|---|
| Hierarchy | 2 | 7 | 8 | 8 | G-FP central bars/outcome compete with opponent; R-CS edge groups clean but chat/kill feed dense; R-V compact ability grouping; R-Z localized contextual prompt |
| Type/spacing/icons | 2 | 7 | 8 | 8 | G-FP small development label and thin bars; R-CS clear weapon silhouettes; R-V consistent symbols; R-Z recognizable input glyph plus action |
| Semantics/feedback | 3 | 8 | 8 | 9 | G-FP parry is named but stacks with riposte; R-CS defuse timer/round loss; R-V success/health; R-Z actor stamina and Gust association |
| World cohesion | 2 | 7 | 8 | 9 | G-FP plain Canvas prototype; R-CS clean technical overlay; R-V deliberate geometric language; R-Z translucent rounded panel/context motif fits fantasy |
| Interaction/navigation | NE | NE | NE | NE | Clips do not show complete menu/focus/button flows |
| Accessibility/responsiveness | NE | NE | NE | NE | No remap, localization, couch-distance, enlarged-text or target-device test |

Observed-weight totals (85/100): current 190/85=2.24; CS2 615/85=7.24; Valorant 680/85=8.00; Zelda 715/85=8.41. The main rubric uses rounded **game 2 / approved composite 8** for C12; never add this subrubric again to the overall score. These are observed UI subset scores, not complete UI certification. All three reference interfaces have room below 10; their unseen states cannot earn points. Primary gaps are UI design/implementation and cross-layer consistency; a small focused HUD/menu pass is feasible, but calendar and controller scope are unconfirmed.

## Information and composition rules

At first glance a player should recognize: practice context, own danger/resource state, opponent threat, legal next action and recent consequence. Critical threat occupies the central play region; own health/stamina form one stable, explicitly owned group near the lower edge. A short tutorial prompt may appear near the resource group when needed. Attach target labels or indicators to the actor they describe, with occlusion/offscreen policy; do not draw a fixed screen-space bar that could be mistaken for either fighter's health.

Use one strongest action per panel. Proposed pause hierarchy: **Resume** primary; Practice options, Settings, Restart practice secondary; Return to title separate. Opening settings is two activations from play; resuming one. Use Escape/back consistently: dismiss transient tooltip → close modal → previous screen → resume. Return focus to the invoking control. Opening a menu prevents combat inputs reaching the game, and closing it must not fire a queued strike. The existing F4 developer panel is not evidence that these player behaviors are implemented.

Health is persistent; stamina is persistent during practice/combat; expiring riposte opportunity appears briefly without covering the incoming hands/blade. Parry/chamber/hit/miss use one short event cue in a reserved band, with distinct text/symbol plus sound. If cues overlap, priority is danger → current actionable opportunity → result → informational hint. A result is not an instruction to act if its legal window has expired. Do not draw an exact telegraph for deliberately deceptive motion beyond the approved mechanics.

## Visual tokens and layout

These are **starting design tokens**, not measured final colors or newly installed fonts. Validate them against actual bright/dark gameplay frames and enlarged UI.

| Token | Specification |
|---|---|
| Surfaces | Dark charcoal `#20262B`, warm pale text `#F2E8D5`; subdued cloth-blue `#294A68`; limited steel/brass edge accents. Opaque enough to support text; avoid blur as the sole contrast mechanism |
| Semantics | Damage/danger `#B9443B` plus damage icon/text; stamina `#C39A4A` plus label/bar; selected/action `#D7C18F` plus border/check; success `#86A88A` plus symbol/text; disabled keeps readable reason. These swatches are not a contrast certification |
| Type | Readable humanist sans for body/numbers; restrained serif only for short titles if a licensed family is selected. Do not use distressed/pseudo-medieval type for combat instructions. Tabular numerals for counters; text remains localized FText, not assembled English fragments |
| Sizes at 1080p | Body 22–24px-equivalent; secondary 18–20; title 32–40; critical resource 24–28. Scale via viewport-aware UI rules; do not copy Canvas pixel offsets unchanged to every resolution |
| Spacing | 8px base rhythm; 16 between controls; 24–32 between groups; 12–16 internal button padding. Visual alignment follows content, not gratuitous card outlines |
| Buttons | At least 48px-equivalent high with an ample hit area; default 52–56. Supported couch/controller layouts start around 64 and require actual distance testing. Touch is outside confirmed PC scope, but do not claim mobile/touch support |
| Focus | 2–3px-equivalent high-contrast outer indicator plus small fill change; distinguish focus from selection. Ensure visibility on light and dark surfaces without relying on hue |
| Safe areas | Start with 5% inset for essential HUD; menus anchored to a scalable safe container. Test 16:9, 16:10 and ultrawide when supported; avoid stretching HUD to extreme corners |
| Responsive behavior | Column layout collapses rather than clipping; scrolling retains heading/action context. Settings primary/back actions remain reachable. Test +50% text and 30–50% string expansion before claiming localization support |

Use icons drawn from one coherent silhouette/stroke family. At small sizes, a recognizable sword/guard/heart-like resource shape is better than a miniature detailed illustration. Pair ambiguous icons with text. Input glyphs come from the current binding/device, switch without moving the layout, and account for remapping. Keyboard letters must not masquerade as Xbox/Nintendo button mappings. Final device glyph licensing and controller scope are unresolved.

Cards/grids are NA for current gameplay. If equipment selection is approved later, use large item silhouettes, clear selected/focused/equipped states, consistent rarity only when rarity exists, a fixed comparison layout, and explicit before/after values. Show owned quantity, cost, deficit and consequence without arithmetic; include affordable/unaffordable, locked/unlocked and valid/invalid states. Never invent costs or rarity colors merely to decorate a menu.

## Complete button states and current coverage

Every future actionable component uses the following contract. Selected and disabled can coexist with focus; hover is pointer-only; cooldown applies only to genuinely cooldown-driven actions. Retain disabled items in navigation when their explanation matters, or provide an adjacent explanation if skipped. Do not implement a fake wait for a synchronous operation.

| State | Required visual/audio/input behavior |
|---|---|
| Idle | Action verb legible; primary/secondary emphasis obvious; no unnecessary looping animation |
| Hover | Modest fill/edge emphasis; optional short tick on entry; no layout shift |
| Keyboard/controller focus | Clear persistent outline, accessible action name, predictable next/previous/back; focus and hover may look related but selection remains distinct |
| Pressed | Immediate inset/darken or compression response; execute once; no long squash/bounce |
| Disabled | Readable muted treatment plus reason; cannot activate; meaningful focus explanation where needed |
| Selected | Persistent marker/check/accent; no color-only state; focus can move away without erasing selection |
| Busy/loading | Plain verb such as “Saving…”; prevent duplicate submission; only show progress when known; cancel/back policy explicit |
| Error | Preserve input where possible; useful message next to action and clear retry/back; error icon and text; no raw path/JSON |
| Cooldown | Remaining time/progress and unavailable meaning clear; feedback when available; avoid looping particles or false precision |

Current developer-panel button audit, based on source only: **S** means stock Slate interaction route exists but visual appearance/behavior was not observed; **NE** means untested/unspecified; **NA** means not meaningful for this action. No cell marked S is a pass. Source lacks a dedicated game style, explicit selected/busy/cooldown/error button variants and a rendered recovery/focus receipt.

| Existing button | Idle | Hover | Focus | Pressed | Disabled | Selected | Busy | Error | Cooldown |
|---|---|---|---|---|---|---|---|---|---|
| RESET | S | S | S | S | NE | NA | NA | NE | NA |
| SAVE | S | S | S | S | NE | NA | NA (synchronous) | NE | NA |
| LOAD | S | S | S | S | NE | NA | NA (synchronous) | NE | NA |
| CLOSE | S | S | S | S | NE | NA | NA | NA | NA |
| PROMOTE TO PROJECT DEFAULTS | S | S | S | S | NE | NA | NA (synchronous) | NE | NA |

Current tuning values use stock spinboxes, field names copied from tuning entries and equal-weight reset/save/load/close slots. They are acceptable as a developer utility, but fail the proposed player settings presentation. Current fixed 760px panel height is a source-level clipping risk on 720px viewports, not a visually tested failure. There is no evidence for player-facing default browser controls; do not invent that finding. No focus dead end or controller compatibility pass is claimed without interaction testing.

## Transition, sound and motion rules

Starting timings: focus/hover feedback on the next UI update; pressed feedback within one rendered frame; menu open/close 100–160ms, screen change 150–200ms maximum before usable controls. Reduced-motion mode uses an immediate state change or brief fade. No transition delays legal gameplay input or hides a danger signal. A single crisp navigation tick, restrained confirm sound and distinct back/error sound should fit wood/leather/steel character without turning every highlight into a sword clang. Keep UI sound below important combat information; no audio-only status meaning.

HUD resource changes and contact feedback consume the same resolved gameplay event used by animation/VFX/audio. Use one event identity to avoid duplicated text/sparks/sounds. Cosmetic cues can ease in/out, but must not report a hit on a miss or keep a riposte available after its legal window. Displayed numbers, costs and enabled state use the same underlying value; no UI-local combat clock.

## Player-readable language and recovery

All player text uses concise established terminology and a next action. Keep exceptions, paths, IDs, variable/enum names, stack traces, raw JSON and tuning units in development diagnostics. A support reference may be shown only if support can resolve it to private diagnostics. Do not promise save safety unless the implementation proves it.

| Situation | Proposed player-facing presentation | Current evidence / remaining check |
|---|---|---|
| Ready/successful action | “Parried” then “Riposte” only while actionable; or one contextual combined cue | G-FP shows overlapping PARRY/RIPOSTE; consolidated version not implemented |
| Defeat | “You’re down. Try again.” with **Try again** and **Practice options** | Current source: DOWNED - PRESS R TO RESET; new flow and rendered defeat NE |
| Loading practice | “Preparing practice…”; show tips only if loading is long enough; no invented percentage | No reviewed startup/loading flow |
| Empty training selection | “No practice opponents available.” plus return/retry only where supported | Proposed boundary, not observed behavior |
| Settings saved | “Settings saved.” | Developer source instead reports Saved: plus path |
| Save failure / permission / storage problem | “Couldn’t save settings. Your changes are still active for this session. Try again.” only after confirming session state | Source reports SAVE FAILED plus path; user-facing handling/test absent |
| Invalid saved settings | “Couldn’t load saved settings. Your current settings are unchanged.” if atomic load leaves them intact | Source builds Candidate before assignment but rendered/error scenario not exercised |
| Validation | “Choose a value from … to …” with localized range; preserve legal current value | Developer spinboxes clamp; final player controls not specified/verified |
| Slow/timeout | “This is taking longer than expected.” with actual available retry/back action; never fake timeout resolution | No async player operation demonstrated |
| Cancel/reset confirmation | “Restore default settings?” **Restore defaults / Keep changes**; identify what will change | Current reset immediately changes live values; player confirmation proposed, not added |
| Offline/reconnect | No connection-required message for local practice. If future network mode exists, state what can continue and what is retrying | Networking/reconnect NA in current lab; no save/progress guarantees invented |
| Graphics recovery | “The display was reset. Restoring the game…” only if recovery exists; otherwise helpful restart message | Context/device-loss recovery unverified; do not claim implemented support |

Verification register: success/health/parry cues have sampled-frame evidence; failure/downed, loading, empty, permission, validation, timeout, save/load recovery and cancellation have source/spec evidence only or NE. Offline/reconnect is NA for approved local scope. These gaps must be exercised from the player perspective during UI implementation; this guide does not claim they passed.

## Implementation ownership and extension

UI owner creates a shared game style/token layer and reusable button/resource/prompt components within the existing Unreal presentation boundary. Keep developer `CombatTuningPanel` separate; game-mode settings/event services return structured outcomes that player UI maps to localized text, while detailed failures go to diagnostics. Choose Slate/UMG integration based on the existing viewport route and authoring needs; a wholesale UI framework rewrite is not required by this guide. Do not add web/browser rendering.

Player menu lifecycle: one owner opens/closes the active screen, restores prior focus, manages input mode and cursor, and destroys/detaches the screen on level teardown. Save/load services own persistence and atomicity; buttons request operations and reflect their outcomes. Graphics profiles and combat simulation remain authoritative outside UI. Preserve diagnostics, user tuning and tested failure assertions. New player-facing C++ implementation requires build/affected tests and one independent review when consequential; none was changed for this guide.

Review one representative critical flow first: play → pause → settings → apply → failed-save recovery → back → resume → downed → retry. Cover every applicable button state, remapped keyboard/mouse and any confirmed controller, bright/dark background, text expansion and smallest supported viewport. Then broaden only for changed flows or specific unresolved concerns. Record missing combinations explicitly. No automated all-screen campaign for animation drafts.
