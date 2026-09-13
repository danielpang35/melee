# Combat audio — weighted steel revision

This incorporates the user's latest request for punchier, fuller slicing /
metal-on-metal hits, even sharper higher headshots, and metallic parries that
communicate the mass of the weapons. It builds on the clean, uninterrupted
air and subtle moving armor of revision 3.

Body impacts combine a real Norse sword / katana contact, a low steel body,
a cutting steel tail, a physical punch and a restrained organic layer. Head
impacts use higher, shorter sabre / katana and seax / katana cuts, a precise
metal tick and compact underlying weight. Head loudness matches body; pitch,
transient texture and decay distinguish it. Parries have a quick pop, real
blade collision, low hilt weight and a controlled metallic bloom. Their tail
stays short enough to leave room for the next commitment.

Still North Media recordings by Ben Jaszczak and Brian Nelson supply the
actual weapon impacts. The archives, original recordings, chosen strike
times, band separation, pitch/time changes, envelopes, gains, synthesis seeds
and output hashes are preserved in `ArtSource/CombatAudio`. All recorded
sources are CC0. Processing includes onset alignment, independent layer
shaping, saturation, subsonic cleanup and oversampled peak control. Unreal
uses uncompressed PCM and inline loading for these small transient sounds.

Whooshes contain only original shaped air and recorded nonmetallic swishes.
They play their complete tail through hits and parries, following the moving
blade in 3D. Quiet chainmail, armor, cloth and leather follow body movement,
attack preparation, recovery and larger turns. Armor has separate concurrency
and a shorter falloff. All families have three variations.

`combat-audition.wav` presents clean air, parries, body/head comparisons,
quiet armor and complete overlapping exchanges at runtime gain. It is an
edited audition, not a recorded gameplay session. `timeline.json` supplies
timestamps. `sample-validation.json` and `validation-summary.json` record
technical verification; these do not certify subjective audio quality.

## Build state

The first validation used `D:/MeleeCombatLab-MEL7` while the concurrent hip-lean
integration was incomplete. The other task subsequently finished that work
and rebuilt the shared game module. Final audio verification therefore also
ran against the current combined build: all 322 native audio checks passed
with AddressSanitizer, the persisted PCM asset bank passed fresh engine
automation, and a 29-second runtime check verified real contact/armor voices
and continuing air after contact. The shared module remains selected; the
isolated audio build did not replace the newer arm/lean implementation.
See `validation-summary.json` for hashes, evidence and exact test coverage.

Restart an older Unreal session to load the new audio playback code.
Head detection uses the cosmetic upper-capsule band in the combatant's
anatomical frame, including lean; this audio revision changes no damage
rules. Notion records the current sound
direction; MEL-7 remains open for listening and paired-exchange acceptance.
