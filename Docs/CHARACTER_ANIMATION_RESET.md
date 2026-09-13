# Character and animation reset — 7 September 2026

> Historical reset brief. CF_v001 and accepted EX_v002 now exist; do not restart the character foundation. [Current development](DEVELOPMENT.md) supersedes its first-delivery ordering.

The user rejected the current animation/modeling approach as nowhere near Mordhau and not converging. Stop refining its local offsets and fittings. Start the character and animation foundation afresh; retain design goals, not implementation assumptions.

## Priority and retained design

Animation quality comes first. Realism, physical simulation and production speed are tools serving that quality. Swings should feel weighty, satisfying and responsive. First-person and third-person animation may differ when useful. Readable contact and player control remain design requirements. The medieval visual direction remains relevant for later armor and materials.

Brief deformation in ripostes is acceptable when the performance reads well. This does not excuse broken proportions or persistent disconnected-looking shoulders. Numeric blade/grip checks do not establish animation quality.

## What is being replaced

No requirement to retain the old Citadel mesh, skeleton, bone proportions, hand offsets, oversized weapon fittings, trajectories, clip dimensions or stack of runtime corrections. All old candidates are preserved for historical comparison. The interrupted pommel iteration made no asset change.

The assessment is that weapon-led posing, multiple layers reshaping the final performance, bad relative asset scale and excessive reliance on metrics/frame inspection contributed to the failed result. This is an engineering/artistic assessment, not proof that physics caused the problem. The previous path used procedural/authored curves and IK; a finished AutoPhysics performance was not evaluated.

## First delivery

[MEL-25](https://linear.app/meleeslasher/issue/MEL-25) owns the new anatomical character and shoulder rig. Build coherent adult proportions with continuous chest/back/deltoid/armpit surfaces, meaningful hand anatomy and a shoulder girdle that moves with arm elevation and reach. Plain materials expose the body before armor. Produce editable source and actual front/side/back and deformation renders.

The CF_v001 study uses CC0 MakeHuman Community/MPFB graphic topology, morph, anatomical landmark and weight data as raw material. It is independently assembled and proportioned, not vertex-by-vertex original sculpting. It imports no old character or combat module. Pin and hash the upstream assets and preserve their license. That source choice is revisable after visual review.

The new setup gives upper arms approximately 30.4 cm, forearms 26.0 cm and wrist-to-middle-fingertip distance 19.4 cm at 180 cm stature. These are chosen character dimensions, not claimed population averages or a universal human standard. Use a coherent whole-body silhouette rather than combining unrelated percentile extremes. [NASA anthropometry guidance](https://www.nasa.gov/reference/4-0-physical-characteristics-and-capabilities-vol-2/) is background guidance, not a calibration certificate for this character.

Review the actual deformation using linear skinning. Blender's optional dual-quaternion preserve-volume setting has different deformation behavior and should not silently make a source-only improvement that disappears in the engine. [Blender armature documentation](https://docs.blender.org/manual/en/latest/modeling/modifiers/deform/armature.html).

## Next after character review

Author body, arms, hands and weapon together through idle → parry → riposte → carry → return. Extract the canonical weapon motion from the authored performance for contact evaluation. Preserve intended source motion through a minimal preview consumer; add aim, movement and interruption behavior only after basic motion is convincing. Reconsider authoring tools and controls on the evidence. Do not recreate the rejected corrective stack by habit.

CF_v001 is a character and deformation study. It is not final armor, a finished animation, a proven game export or artistic acceptance. Normal-speed review against Mordhau remains necessary when attacks are authored.
