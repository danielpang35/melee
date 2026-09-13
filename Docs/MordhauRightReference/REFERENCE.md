# Confirmed neutral RIGHT horizontal Greatsword

The new user capture resolves the prior classification gap. The user identifies the Greatsword, opening partial LEFT, subsequent combos, neutral RIGHT repetitions and final RIGHT feint. The selected complete neutral RIGHT is **native source PTS 15.775733–17.775500 seconds**, with onset bracketed by 15.747967 and 15.775733. Weapon/direction/type confidence is high with that provenance; no loadout name was independently read from pixels.

[Matching contract](reference.json) · [actual frame keys](confirmed/matching-keys.jpg) · [source-speed excerpt](confirmed/neutral-right-source-speed.mp4). Previous uncertain montage findings are retained in [PROVISIONAL_REFERENCE.md](PROVISIONAL_REFERENCE.md); they are superseded as the matching target.

Source: `C:/Users/Daniel Pang/Videos/Captures/MORDHAU   2026-09-07 12-27-58.mp4`, 34,324,182 bytes, 1920×1080. Container reports 20.84s, average36.26fps and59.94tbr; these are not an authoritative uniform frame grid. Decoded presentation timestamps in the selected interval advance about1/36s. **Use native PTS**, stored alongside all216 consecutive decoded frames from13.803533–19.775733 in `confirmed/pts.json`. The overview is sampling guidance only. Encoder timebase1/30000 avoids collapsing nearby PTS. Excerpt selects15.470167≤PTS<18.025767, preserves source PTS differences, speed, framing and all selected frames, re-encodes H264 without audio. Final key sheet preserves16:9; draft native-sheet contact pages were compressed vertically for inspection and are not measurement images.

Visible sequence:

- 15.775733: begins leaving lower-center diagonal idle toward right.
- 15.886867–15.970200: paired grip and guard move far right; much of blade and then hands leave view.
- 16.025767–16.470167: weapon/palms offscreen right, broad near sleeve held low/right. This deliberate visual absence belongs in the target.
- 16.497967–16.775733: connected hands reenter from right and travel through center to left. Guard approximately(.70,.59) at16.553500, (.53,.56) at16.609067 and(.23,.66) at16.720167. Coordinates normalized top-left origin. Blade turns from rightward through pronounced foreshortening; near sleeve occupies substantial foreground.
- 16.803533 onward: hands leave left; view clears. Do not force hands or blade to remain visible.
- 17.386800–17.775500: blade reenters from left, then guard/grip restore lower-center diagonal idle.

The earlier neutral repetition corroborates this same structure: onset around12.831333; reentry/passage13.553533–13.803533; return14.47–14.887. Opening partial LEFT, prior moving/combo section and final RIGHT feint around18.220133 are excluded. The feint returns from the right-side load without the full cross-view passage.

Stone edges, skyline and horizon remain essentially stable during selected swing. Camera movement is not the explanation for its large visible hand travel. No hidden torso/root trajectory is recovered, and no physical-realism amplitude limit should replace these visible beats. Match the frame composition and timing first.

`reference.json` contains approximate manually read screen landmarks, uncertainty±.03UV. Null means offscreen or not independently measurable, not zero. Two palms overlap: separate left-palm centers are not observable. Blade endpoint may be an edge intersection instead of a visible tip. No invented3D positions or exact hand anatomy are encoded.

Observed passage is distinct from engine release. External Mordstats Build26.1 gives575ms windup,500ms release,700ms recovery (normal strike); these can cross-check the gameplay clock but are not directly observed phase boundaries here. Exact release remains unmeasured. No animation asset or legacy project data was changed in this reference pass.
