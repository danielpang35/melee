# MEL-7 — first combat audio pass

**Superseded:** the user rejected this selection on 6 September 2026.
The current bank, audition and validation are documented in
[Revision 2](Revision2/README.md). The notes below describe the first pass only.

Replaces the default runtime noise/tone impacts with 18 imported, layered CC0
samples: three variants each for swing, stab, body hit, parry, chamber and wall.
The samples come from [Kenney RPG Audio](https://kenney.nl/assets/rpg-audio)
and [Impact Sounds](https://kenney.nl/assets/impact-sounds); provenance, original
licenses and reproducible sources are in `ArtSource/CombatAudio`.

Release air is triggered once from the existing 240 Hz simulation observation
callback, before contacts resolve. A feint or windup morph emits no committed
swing cue. The release uses the final strike/stab family; ripostes follow the
same rule at their own release onset. Resolved contact routes the appropriate
impact at its actual position, scales gain by contact energy and damps the
attacker's air tail. A miss retains its air passage and has no fabricated hit.
No combat clock, trajectory, damage or movement rule changes.

All cues are mono spatial sources with a 160 cm full-volume radius and 1800 cm
falloff. Three variants cycle per family without random pitch shifts. Contact
voices and swing voices use separate concurrency pools. The bank is cooked by
the existing `/Game/Visual` packaging rule.

## Review

Build with `Tools/Build.ps1` and restart the editor to load the new code. Normal
play uses the sample bank. Launch with `-LegacyCombatAudio` for the prior
synthesized impact audio; that baseline has no release air sound.

`cue-preview.wav` presents one dry variant of each family in this order:
**swing, stab, body, parry, chamber, wall**. The accompanying JSON records cue
times. This is a sample audition, not a recorded gameplay comparison.

For gameplay, review both horizontal origins against the passive target,
in empty air, and against parry/riposte. Check audible onset against contact,
opponent localization and whether metallic tails obscure the next commitment.
`-CombatAudioLog` logs cue selection/variation for diagnosis.

## Checks and remaining scope

- `Tools/TestCombatAudio.ps1 -Sanitize`: 296 checks passed. Both horizontal
  origins produce one release cue and unchanged damage/contact timing across
  30, 60, 120, 144 and 240 fps. Covers repeated release samples, reset,
  combo serial changes, morph family selection and non-contact routing.
- All 18 source WAVs checked against the manifest hashes, mono PCM format,
  nonzero signal and peak headroom. See `sample-validation.json`.
- Isolated Unreal editor build and final link passed. The last two translation
  units were compiled with the same generated definitions/includes, without
  the precompiled header after the incremental build stopped progressing.
- Audio import: 18 SoundWaves, zero errors/warnings. Fresh-process
  `MeleeCombatLab.Audio.AssetBank`: passed, zero warnings/failures; checks all
  assets, mono format, duration and persisted inline loading.
- Eight-second headless game smoke: clean exit, active audio device and three
  real swing voices cycling variants 0/1/2. This validates runtime release
  playback; it does not substitute for contact-mix listening or rendered play.
  Logs are in `Saved/CombatAudio/Validation`; compact results are in
  `validation-summary.json`. The validation checkout is
  `D:/MeleeCombatLab-MEL7`; the shared project's executable was not replaced.

MEL-7 remains in progress. Exertion/footsteps, final sound selection/mix and
paired first-person/opponent listening and motion review remain. The broader
horizontal exchange acceptance still depends on MEL-6. This work does not
certify the arm deformation repair or the quality of the complete exchange.

Dedicated performance work is deferred per the user's 6 September 2026
decision recorded in Notion; no profiling was performed for this pass.
