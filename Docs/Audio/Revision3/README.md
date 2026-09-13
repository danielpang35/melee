# Combat audio — ground-up redesign

**Superseded by [Revision 4](../Revision4/README.md):** fuller metal-on-metal
hits, sharper higher headshots and more weight in the metallic parry.

This revision implements the user's clean full whoosh, slicing hit, tactile
higher headshot, quiet armor rustle and distinct poppy parry direction.
All 24 mixes are newly constructed from source recordings and original
shaped air; no previous finished cue is reused.

- **Swing/stab:** low pressure, broad moving air and a small high-frequency
  edge, supported by recorded wood/hanger swishes. No metal-contact sources.
- **Body:** wet cutting onset, fabric draw-through, contained body weight
  and a short slicing air texture.
- **Head:** a tighter, higher wet cut, dry pinpoint crack and fine fabric
  texture at the body's loudness, with a short tail and no tonal ping.
- **Parry:** a firm dry pop, compact pressure burst and tiny hard-contact
  tick. Nearly all energy ends within 100 ms; no clash or scrape recording.
- **Chamber/wall:** a short articulated catch and a damped surface bite,
  respectively, with no long ringing tail.
- **Armor:** quiet chainmail, overlapping armor, padded cloth and leather.
  About 12.5 LU below blade air in the source bank, with quieter locomotion
  playback and shorter spatial falloff than combat cues.

Whooshes play their natural tail through hits, parries, flinch and combo
transitions. Contact never fades, ducks or stops the air. Reset/removal still
cleans up voices. Armor follows attack preparation, recovery, guard changes,
distance traveled and larger turns; it stays silent at rest and on teleport.
A 240 ms minimum interval prevents rustle stacking. Armor has its own voice
pool so it cannot take a blade or impact voice.
Air sources travel with the blade and armor follows the body for spatial
movement in the game; impacts stay at their resolved contact positions.

## Audition

`combat-audition.wav` presents clean whooshes, dry parries, alternating body/
head hits, quiet armor, and combined exchanges with uninterrupted blade air.
Armor examples retain their real quiet level. `timeline.json` gives positions.
This is an edited audition using the game assets and gain, not captured gameplay.

## Build and checks

Rebuild with `python Tools/BuildCombatAudio.py --ffmpeg <executable>`, then run
`Tools/ImportCombatAudio.py` through Unreal's Python commandlet. Source archives,
recipes, seeds and credits live in `ArtSource/CombatAudio`; revision 2 is
preserved under its `Revisions/v2` directory. Restart a running editor after
building the new code.

`sample-validation.json` checks all 24 WAVs, hashes, source restrictions,
head/body balance, quiet armor, short parry tails, retained air after contact
in the audition, and headroom. `validation-summary.json` records native tests,
Unreal build/import/asset checks and runtime playback results. Numerical
measurements establish technical integrity; quality still requires listening.

The existing cosmetic head tag uses the upper part of the hurt capsule until
anatomical hit volumes exist. Damage and the combat clock are unchanged.
Notion Visual Direction records this revision's intent. MEL-7 remains open
for in-game listening and the broader paired-exchange acceptance.
