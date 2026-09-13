# Combat audio revision 2

**Superseded by [Revision 3](../Revision3/README.md):** the user requested a
ground-up redesign with clean air, no hit cutoff, subtle armor and a poppy parry.

The user's direction is a full blade whoosh, satisfying slicing contact,
a higher-pitched tactile headshot, and a balanced exchange in which no one
cue dominates. This replaces the rejected first sample selection. The same
direction is recorded in the Notion Visual Direction page.

The bank contains 21 edited mono 48 kHz SoundWaves, three variants each:

| Cue | Texture |
| --- | --- |
| Swing | Slowed recorded swish for low air body, broad sword passage, restrained high blade edge, sleeve texture |
| Stab | Shorter, focused blade passage with low thrust weight |
| Body | Wet cutting transient, blade draw-through, fabric texture, damped low impact |
| Head | Tighter and higher-pitched cutting crack, short tactile snap, compact weight |
| Parry | Recorded steel clash with weapon weight and a short scrape |
| Chamber | Short steel catch with an outward blade slip |
| Wall | Hard surface impact and damped steel edge |

The head cue replaces body audio. It has the same runtime gain and matched
measured loudness, rather than adding a second impact voice. Body/head pairs
are within 0.07 LU on the standardized audition train. All 21 cues span
1.10 LU; their true peaks stay below -3.5 dBTP. Recorded layers are filtered,
trimmed, repitched, shaped and mixed before gentle saturation and oversampled
peak limiting. These measurements support balance and headroom; they do not
establish subjective quality or replace listening in the game.

Release still fires once from the fixed simulation sample, with final
strike/stab routing. Windups and feints stay quiet. The attacker's air tail
fades over 80 ms at contact. All families use base gain 0.68; contact energy
changes level by at most 1 dB. Short tails and separate eight-voice contact/air
pools keep repeated exchanges readable. Samples cycle through three variants.

The simulation currently has one hurt capsule. A cosmetic head tag is captured
from contact height in its upper 26 cm (capped by capsule radius/half-height),
following the defender's current position and capsule dimensions. This is an
approximation until anatomical hit volumes exist. It changes neither damage
nor collision priority. The event preserves the tag even if the target moves
before playback.

## Audition and rebuild

`combat-audition.wav` uses the actual masters at runtime gain. It presents two
whooshes, alternating body/head hits, then swing/body, swing/head, parry,
chamber, follow-up body and stab/head. `timeline.json` gives exact timestamps.
This is an edited audition with the runtime contact fade, not captured gameplay.

`python Tools/BuildCombatAudio.py --ffmpeg <ffmpeg executable>` rebuilds the
masters and audition from preserved CC0 source archives. NumPy is required;
py7zr is needed only to extract missing towel originals. Provenance, licenses,
layer recipes and hashes are in `ArtSource/CombatAudio`. The first selection
is preserved under `ArtSource/CombatAudio/Revisions/v1`.

Import using `Tools/ImportCombatAudio.py` in Unreal's Python commandlet.
Restart an already-open editor after building to load the new head routing
and mix code. Normal play uses the new bank. `-LegacyCombatAudio` selects the
original synthesized impacts, not the rejected first sample bank.

## Validation

See `sample-validation.json` for all 21 WAV hashes, mono PCM format, short
duration, endpoint continuity, negligible DC, loudness and headroom checks.
Head spectra are at least 20% brighter in centroid than corresponding body
cues at matched loudness. The combined audition peaks at -5.50 dBTP.
Native and Unreal build/import results are recorded in `validation-summary.json`.

MEL-7 remains in progress for listening in first-person and opponent contexts,
motion/audio synchronization review, and the broader horizontal exchange.
Footsteps/exertion remain outside this revision. Dedicated performance work
remains deferred per the user's decision; no profiling was added.
