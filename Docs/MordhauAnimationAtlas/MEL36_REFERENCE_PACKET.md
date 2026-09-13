# MEL-36 reference performance packet

9 September 2026 · policy MCL-DEV-2026-09-08 · observation mode `sampled_frames`.

[Open the annotated comparison](../../ArtSource/AnimationLab/MEL36_reference/index.html). It contains two compact full-frame source-speed excerpts, live source-frame timestamps and event annotations, an uncertainty table, three screen-space studies, and the saved defender-camera specification. No new swing is authored or selected.

## Bounded implementation

Use the tutorial yellow-mask actor for neutral right-horizontal identity and supplementary B for the clearer collected-load → projected-hands → high-carry gesture. Preserve every selected native frame and its PTS interval; shift time by a constant only for playback. Align the midpoint of first-visible-departure brackets, since an exact shared launch/impact event is not established. Keep unknown events empty, inspect a small visible sample, then hand this packet to the editable CF control proof. Existing accepted EX, CF foundation, production TP, attack clock and contact behavior are outside this work.

The implemented packet owns [editable data](../../ArtSource/AnimationLab/MEL36_reference/packet.json), [builder](../../ArtSource/AnimationLab/MEL36_reference/build_packet.py), [viewer template](../../ArtSource/AnimationLab/MEL36_reference/viewer.template.html), two MP4s and a three-frame annotated sheet. The separately implemented [camera specification](../../ArtSource/AnimationLab/MEL36_reference/camera-spec.json), [static preview](../../ArtSource/AnimationLab/MEL36_reference/camera-preview.png) and [receipt](../../ArtSource/AnimationLab/MEL36_reference/camera-receipt.md) define the later comparison view; the ready pose is a framing check, not a new animation candidate.

## Source identity, roles and limits

| Source | Actor, view, weapon and action confidence | Use and exclusions |
|---|---|---|
| [N-RH excerpt](../../ArtSource/AnimationLab/MEL36_reference/neutral-source-speed.mp4), original PTS 30.000000–31.500000s | Yellow-mask nbc initiator, high confidence; external actor inside tutorial view labelled “Attacker POV.” Foreground hands belong to the partner/parrier. Two-handed sword; exact model unverified. Neutral RH identity high; manipulation/input details unavailable. | Ready and lateral preparation/direction. Foreground parry occludes the initiator around 30.8–31.1; camera tilts/rotates. The 1.5s sample span does not establish complete attack duration or a clean recovery. |
| [B excerpt](../../ArtSource/AnimationLab/MEL36_reference/B-source-speed.mp4), original PTS 0.456066667–2.094866667s | Armored tutorial trainer seen by player FP, high confidence; Training Sword user-confirmed. Right-origin lateral cycle visible; exact neutral/riposte inputs unconfirmed. Separate performance from N-RH. | Clear compact load and outward hand projection, then high carry/return. Armor masks joints. Damage/chromatic distortion and camera displacement from about 1.478267 contaminate later observations. No synchronized alternate view, neutral-clock extraction or calibrated target plane. |

Original paths, byte sizes and SHA-256 identities are retained in `packet.json`, verified against the reused [integrity receipt](../../Saved/MordhauPolishReview/integrity.json). The earlier complete-stream decode findings remain authoritative; this work decoded only the selected neighborhoods and the new compact outputs. Source-speed here means preserving the supplied recording's encoded timeline, not proving game frames were never dropped or that an upstream edit never changed speed.

## Event score and uncertainty

The HTML table includes original PTS and event-relative values. Comparison zero is N-RH **30.150000s ±0.050000s** and B **0.583850s ±0.044450s**, the midpoints of visually bracketed first departure. This aligns one observable preparation proxy only; maximum load, launch and passage are not forced to coincide. The cumulative cross-source proxy uncertainty can be up to 94.45ms even before browser scheduling.

| Event | N-RH | B |
|---|---|---|
| Preparation begins | 30.1–30.2, bracketed departure from ready | 0.539400–0.628300, bracketed departure from ready |
| Maximum load | Unknown; load visible 30.2–30.7 | Exact maximum unknown; collected/apparent apex region 0.978267–1.144933 |
| Hand launch | Unknown; no isolated onset | Apparent onset bracket 1.144933–1.228233 |
| First target-plane passage | Unknown; parry cues about 30.8–30.9 amid occlusion | Unknown; crossing/carry observed 1.478267–1.728267 amid effects; exact contact not measured |
| Maximum extension | Unknown | Exact maximum unknown; strong projected delivery visible 1.311567–1.394867 |
| Carry | Unknown/occluded | High opposite-shoulder wrap observed 1.644933–1.728267 |
| Braking | Unknown | Unknown; no isolated deceleration measurement |
| Return | Complete route unknown; actor reappears later | Visible unwind/down/in 1.817167–2.067100; camera remains a confound |

These observations reuse the [art audit](../../Saved/MordhauPolishReview/architecture-audit-art.md) and [reference-role index](../MORDHAU_REFERENCE_INDEX.md). Direct image inspection here covered the neutral 16-beat sheet, B's two 20-beat sheets, original B frames 7/12/15 and the generated annotation sheet. There was no uninterrupted playback judgment, frame-by-frame event search or inferred hidden 3D motion.

[Three screen-space studies](../../ArtSource/AnimationLab/MEL36_reference/B-screen-observations.jpg) mark approximate paired-hand center, hilt, visible shoulder/elbow silhouettes, body axis and blade tip at B 0.978267/1.394867/1.644933. Original 1920×1080 pixels and normalized image coordinates are editable in `packet.json`; unknown points are null. The fixed crop is (500,400)–(1450,1000). It is neither tracked/recentered nor stabilized. Sparse shape marks do not measure world reach, hand acceleration or force; no trajectory is interpolated between them. In particular, the delivery blade leaves the left frame edge and the far elbow remains unresolved.

## Playback and minimal verification

Both videos use 960×540 H.264 with audio omitted. The combined media size is 2,142,681 bytes. HTML embeds its data and uses relative local media paths; it needs no data fetch/server. Controls wait for metadata and report failed media loads. Playing from a comparison position preserves native rate 1×, with start offsets only. Scrubbing explicitly pauses; later evidence is masked as ended instead of presenting a held final frame as continuing recovery. Browser start scheduling/buffering can introduce skew; no playback-rate drift correction disguises it. Actual browser playback is not independently certified here.

| Check | N-RH | B |
|---|---|---|
| Native timebase | 1/15360s | 1/30000s |
| Input/output selected frame count | 91 / 91 | 59 / 59 |
| Maximum output PTS error after constant rebase | 0s | 0s |
| Strictly increasing output PTS | Yes | Yes |
| Original final-frame display duration retained | 0.016666667s | 0.033366667s |
| Media duration including final display interval | 1.516666667s | 1.672166667s |

The source window selects through its final frame; its original terminal display interval is retained even when that interval extends past the requested endpoint. B's final evidence frame begins at 2.094866667s and its retained display interval ends at 2.128233333s. This is an encoded display hold, not a newly observed event.

The initial FFmpeg native-timebase encode exposed a zero-duration terminal packet that an MP4 edit list hid. The builder disables that edit list and stream-copies a final-packet duration equal to the original decoded duration. It then checks every decoded output PTS and the terminal duration against the original values. No frame duplication, interpolation, rate conversion or rounded nominal 60Hz grid is used. The check tolerance is 1e-8 seconds; actual observed PTS error was zero.

Rebuild from the repository root with `python ArtSource/AnimationLab/MEL36_reference/build_packet.py`. It verifies only these two original source hashes, serially creates the two small videos, validates their timestamps, redraws the three-frame sheet and writes data/viewer. It writes only packet-owned outputs; the temporary encode is removed after a validated final remux. Rebuilding replaces reproducible derivatives of the stated identities, never the originals or unique source evidence. For a viewer-only change, use `python ArtSource/AnimationLab/MEL36_reference/build_packet.py --refresh-viewer` to reuse the verified media and data. The separately owned camera files are not rebuilt or overwritten.

Next useful action: use this gesture/event vocabulary and saved defender camera for the bounded editable-control proof, then three complete motion hypotheses. Neutral timing, exact passage/reach and any significant FP/TP contract disagreement require explicit later integration decisions. Human source-speed review and animation acceptance remain open.
