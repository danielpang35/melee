# Mordhau animation reference — corrected action and frame catalogue

9 September 2026. Source confirmed by Daniel: **the 7:32 courtyard tutorial**, [Mordhau Advanced swing manipulation — Visceral Wankur](https://www.youtube.com/watch?v=KMA2nf278No), video ID `KMA2nf278No`. This replaces the **classification and pose-selection guidance** of the 8 September SWING-01 atlas. It does not replace the approved EX_v002 performance or claim acceptance of any project animation.

## What was wrong

The previous fifteen labels described tutorial chapters, not every action inside their captures. Four-second sheets often contain the end of one exchange, ready, another opening strike, a parry, a riposte and a return. Treating an entire sheet as a single attack obscures those distinctions. In particular, the former RH-A “high load” at **156.50 s** belongs to the **parry/transition sequence**; it is not a neutral right-horizontal windup reference. The prior atlas was also stored under ignored `Saved/`, leaving no canonical categorized reference in `Docs/`.

The corrected catalogue separates **actor → neutral/riposte → attack family → anatomical origin → preceding parry side → manipulation → visible beat**. It includes 240 relabelled legacy captures and 32 newly extracted neutral-horizontal captures, with **17 annotated sheets** and [per-frame records](frame-catalogue.json). Original images and receipts remain intact.

## Terminology and coverage

**Neutral means an attack initiated without that actor first parrying in the exchange.** It does not mean idle, a stationary camera, an unmanipulated-looking frame, or the preparation of a riposte. “Riposte” here describes the tutorial's immediate parry-to-answer sequence; exact engine flags/windows were not extracted. An accel/drag label describes the demonstrator's manipulation, not a separate recovered animation asset.

The on-screen **Attacker POV** belongs to the black/red fighter performing the demonstrated riposte. The externally visible yellow-mask `nbc (Paid Actor)` supplies the neutral opening attack. In **Defender POV**, that opening actor owns the foreground hands and the black/red `240 Turbo Wanker` fighter is externally visible. Thus a foreground weapon pose and the opponent's body pose in the same image can belong to **different actions**. Left/right follows each acting character's anatomical side, not the viewer's screen.

| Attack origin/family | Neutral initiation in this video | After left-side parry | After right-side parry |
|---|---|---|---|
| Left horizontal | Verified yellow-mask opener, e.g. 172.3–173.8 s; recovery partly obscured | LH-A, LH-D | Not identified |
| Right horizontal | Verified yellow-mask opener, e.g. 30.0–31.5 s; recovery partly obscured | Not identified | RH-A, RH-D |
| Left overhead | **Not independently verified as neutral** | LO-A | XL-A, XL-D |
| Right overhead | **Not independently verified as neutral** | XR-A, XR-B | RO-A, RO-D |
| Left underhand | **Not independently verified as neutral** | LU-A, LU-D | Not identified |
| Right underhand | **Not independently verified as neutral** | Not identified | RU-A, RU-D |

There are **six demonstrated riposte directions, eight observed parry-side/attack-direction pairings and fifteen tutorial demonstrations**. They are not fifteen base animations, nor a complete six-by-three neutral/left-parry/right-parry library. All fifteen attacker-side replay windows were checked for the opening actor; the identified opening strikes are lateral horizontals. This pass did **not** establish neutral overhead/underhand exemplars. Those categories remain explicit gaps rather than being filled with mislabeled riposte frames. The closing card also describes the tutorial as a selection. This does not establish that an unobserved combination is illegal or unavailable in Mordhau.

## Categorized captures

Each sheet names its subject and entry. Each tile separately marks ready, parry, parry-to-riposte transition, riposte preparation, delivery/passage, hit feedback/carry, return or edit. These are **approximate visual landmarks**, not measured engine windup/release/recovery boundaries. Context fields in the JSON are not claims that every tile depicts an attack: ready/parry/edit tiles have no `depicted_attack_type`.

| ID | Preceding parry → riposte | Manipulation | Legacy source samples | Corrected sheet |
|---|---|---|---|---|
| LH-A | Left → left horizontal | Accel | 38.00–41.75 s | [LH-A](categorized/LH-A.jpg) |
| LH-D | Left → left horizontal | Drag | 66.00–69.75 s | [LH-D](categorized/LH-D.jpg) |
| XR-A | Left → right overhead | Unlabelled example A | 92.00–95.75 s | [XR-A](categorized/XR-A.jpg) |
| XR-B | Left → right overhead | Unlabelled example B | 122.00–125.75 s | [XR-B](categorized/XR-B.jpg) |
| RH-A | Right → right horizontal | Accel | 154.00–157.75 s | [RH-A](categorized/RH-A.jpg) |
| RH-D | Right → right horizontal | Drag | 178.00–181.75 s | [RH-D](categorized/RH-D.jpg) |
| RO-A | Right → right overhead | Accel | 208.00–211.75 s | [RO-A](categorized/RO-A.jpg) |
| RO-D | Right → right overhead | Drag | 238.00–241.75 s | [RO-D](categorized/RO-D.jpg) |
| LO-A | Left → left overhead | Accel | 266.00–269.75 s | [LO-A](categorized/LO-A.jpg) |
| XL-A | Right → left overhead | Accel | 292.00–295.75 s | [XL-A](categorized/XL-A.jpg) |
| XL-D | Right → left overhead | Drag | 322.00–325.75 s | [XL-D](categorized/XL-D.jpg) |
| RU-A | Right → right underhand | Accel | 350.00–353.75 s | [RU-A](categorized/RU-A.jpg) |
| RU-D | Right → right underhand | Drag | 378.00–381.75 s | [RU-D](categorized/RU-D.jpg) |
| LU-A | Left → left underhand | Accel | 410.00–413.75 s | [LU-A](categorized/LU-A.jpg) |
| LU-D | Left → left underhand | Drag | 442.00–445.75 s | [LU-D](categorized/LU-D.jpg) |
| N-RH | Yellow-mask actor: neutral right horizontal | Not isolated/measured | 30.00–31.50 s | [Neutral RH](categorized/neutral-RH.jpg) |
| N-LH | Yellow-mask actor: neutral left horizontal | Not isolated/measured | 172.30–173.80 s | [Neutral LH](categorized/neutral-LH.jpg) |

XR-A/XR-B retain analyst identifiers: the sampled chapter cards do not explicitly name accel/drag. The captions and motion distinguish a sharp downward finish from a slower curved return, but do not justify silently upgrading those labels to confirmed categories.

## How to read the motion

**Neutral horizontals:** the yellow-mask actor leaves ready, opens the hands toward the originating shoulder, bends into the load and delivers laterally into the partner's parry. At 30.2–30.7 s the right-origin neutral preparation is visible; by 30.8–31.0 s foreground parry hands obscure contact and part of the return. At 172.5–173.1 s the opposite-side preparation is visible, with the partner's parry around 173.2–173.3 s. The foreground hands after those contacts belong to the **riposter**, not a continuation of the yellow-mask neutral swing. Do not splice them into one motion.

**Horizontal ripostes:** LH and RH show a defensive entry followed by lateral hilt transport and blade passage. The raised entry can resemble an overhead when frozen. In the denser [RH-A sequence](review/RH-A-detail/sheet-04.jpg), 156.267–156.533 s covers the defensive/returning-attack transition; 156.667–156.933 s opens toward lateral delivery; 157.067 s shows passage with damage feedback; 157.2–157.733 s carries and returns. Exact parry-to-attack phase separation remains uncertain. This is an example of why the previous neutral-load interpretation was misleading.

**Overhead ripostes:** the blade descends after the defensive entry. Compare **XR versus RO** for the same right-origin overhead following different parry sides, and **LO versus XL** for the left-origin overhead. Entry history changes the hand/blade path; the matching attack angle does not make the whole action interchangeable. XR-A 93.0–94.25 s and XL-D 323.5–325.25 s show contrasting high-to-low routes with substantial lean and close-range occlusion. Do not infer a clean neutral overhead from either.

**Underhand ripostes:** RU and LU reorganize from the parry into a low delivery and rising carry. RU-A 350.75–351.75 s and LU-A 412.25–413.5 s show the low passage followed by raised hands. The high ending is **underhand follow-through**, not an overhead preparation. LU-D 444.25 s still shows a low extended weapon before feedback at 444.5 s; by 445.0 s the picture fades, and 445.25–445.75 s are outro cards. Those last four samples are excluded from pose matching.

**Manipulation:** compare complete ordered actions within the same family and entry. Accel/drag examples differ in aim, lean, stepping and target-relative passage. They do not disclose the underlying source animation or prove changed playback speed. The previous caption recipes remain useful replay-input references, but their camera/footwork paths must stay separate from neutral authoring controls.

## Application to MeleeCombatLab

- For a neutral candidate, choose a verified neutral **actor/action** reference. Do not use RH-A's defensive entry as the required neutral load or borrow an underhand carry as an overhead windup.
- For a riposte candidate, choose **both** parry presentation side and attack origin. Keep the defensive contact, transition, delivery and carry connected; no forced visit to idle.
- Maintain separate base motion, entry transition and aim/footwork recipe records. FP and TP may use different arm/body shapes while communicating compatible phase, direction, reach and authoritative contact.
- Preserve `EX_v002-source-1615b76b-FBX-6a34514c-native-unreduced-v1` and `Config/EXPreview.json`. This catalogue changes reference guidance only. It does not authorize automatic promotion, a six-angle implementation expansion or changes to accepted gameplay.

## Evidence and reproduction

Review was **ordered frame-sequence inspection, not continuous audiovisual playback**. Reused and visually inspected all five prior overview sheets, all three title sheets and all fifteen defender sheets; extracted and inspected fifteen attacker-side replay overviews at 0.5 s spacing, two neutral sequences at 0.1 s, and a denser RH-A transition sequence. The latter requests a minimum 0.125 s step; the 60 fps grid produces actual 0.133333 s intervals. JSON contains actual decoded PTS for new samples. The prior 240 samples retain their original 0.25 s timestamp basis; none are game clocks.

Source identity: [receipt](source-receipt.json). Source pixels show motion and captions; they do not expose engine attack flags, exact contact time, authored bone transforms, world-space hand heights or synchronized FP/TP frame correspondence. Neutral opener recoveries are obscured by the responding weapon. Some legacy windows span multiple repetitions or truncate the entry/return; use the source and broader replay context when selecting a complete action.

`python Docs/MordhauAnimationAtlas/extract_review.py` rebuilds the fifteen context windows. Its optional arguments are `name start end minimum_step`. `python Docs/MordhauAnimationAtlas/build_catalogue.py` rebuilds annotations from preserved legacy captures and the two new neutral sequences. No source video, animation asset, runtime, import, build or gameplay test was changed for this documentation task.

Notion: [SWING-01 reference](https://app.notion.com/p/3d52e3c3f8f88192ababd9338ad3797b). [Checkpoint](CHECKPOINT.md) records publication/verification status.
