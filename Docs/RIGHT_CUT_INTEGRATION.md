> **Rejected / superseded — 7 September 2026.** The user rejected the overall modeling/animation approach. This retained record describes historical technical evidence; any acceptance-pending or next-refinement text below is historical. Preserve the runnable bundle for comparison only. The fresh character/whole-exchange plan owns active work.

> Dated evidence and assignments below are superseded for current execution by [DEVELOPMENT](DEVELOPMENT.md) and the [TP checkpoint](THIRD_PERSON_CHECKPOINT.md). See [documentation ownership](DOCUMENTATION_OWNERSHIP.md). Historical timing, candidate and issue status are not live values or authorization to resume deferred work.

# Authored right-cut pilot — RC_v008

This revision implements the Astra High prompt. Artistic acceptance remains pending. The candidate review lives in `ArtSource/Cascadeur/Candidates/RC_v008/REVIEW.md`.

## Play and reload

Run `Tools/PlayRightCut.ps1` (or start the project game with `-CascadeurPreview`). Press **1** for the right horizontal pilot, **RMB** to parry, and **R** to reset. `Config/RightCutCandidate.txt` selects the candidate folder. Ordinary launches retain the existing procedural attacks; this is an opt-in playable pilot.

Each candidate contains a saved external Cascadeur scene and baked FBX, a separately saved first-person scene and FBX, and four data tracks:

- `RightCutWeapon.csv`: authoritative local hilt and blade direction.
- `RightCutView.csv`: bounded first-person translation, exactly zero at every release sample.
- `CascadeurPreview.csv`: baked external skeleton.
- `CascadeurFirstPerson.csv`: baked first-person skeleton.

All tracks use 271 samples at 120 fps. Windup maps to .250–.825 seconds, release to .825–1.325, recovery to 1.325–2.000. Frames 240–270 hold the frame-zero rest. Phase timing still comes from the attack state machine; source time never grants damage or legal input.

Author each edit into a new candidate. Convert its external FBX with `--output <candidate>/CascadeurPreview.csv` and its first-person FBX with `--output <candidate>/CascadeurFirstPerson.csv`. Save weapon and view data alongside them. Then run:

```powershell
python Tools/PublishRightCutCandidate.py RC_v008
```

Publishing verifies the complete files and atomically changes one selector. The game validates all four tracks before adopting the candidate. Combatants adopt a new candidate while idle; an ongoing exchange retains its weapon and skeletal revision. Do not edit a published candidate in place. Subsequent artistic changes require conversion and publication, not compilation. The old loose `Config/CascadeurPreview.csv` remains the `-CascadeurLoop` technical fallback and is no longer the playable candidate selector.

## Authority and perspectives

The pilot applies only to the exact right horizontal strike (angle zero, modulo 360). Other directions use the existing evaluator. Authoring may change the full hilt path and blade orientation. Gameplay still projects the path into its reach envelope, applies legal view rotation and footwork, sweeps collision, and resolves single-hit damage. Resample the actual evaluator with `Tools/ResampleRightCut.ps1` after a weapon edit; use its guides for Cascadeur posing.

Normal windup joins the authored track from the current pose and velocity. Riposte/combo entries therefore begin at their actual incoming guard. Contact slowdown, parry, wall rebound, feint, flinch and return retain the existing simulation branches. The baked preview no longer forces those branches to source time zero: it blends to the existing defensive body performance and attaches both hands to the resolved sword.

Each perspective samples its own full skeleton. The final attachment retains its elbow plane and glove pronation, then places the palm contacts on that view's visible handle. First person additionally uses authored framing during idle, windup and return, with a short cosmetic blend for interruptions. Release forcibly uses zero displacement. The first-person blade and hand targets share the exact same offset; external presentation has no offset.

Engine review reports geometric render error separately from maximum cosmetic projection displacement and maximum release projection error. The release check still requires less than .01 cm, and the non-damaging view displacement is bounded below 35 cm. This explicitly records the perspective change instead of hiding it inside the old blade-error statistic.

## Boundaries

Follow-up module 1019 lowers standard ripostes by removing their extra vertical lift while retaining the inherited parry pose/velocity and existing transition. The RC_v008 authored horizontal files are unchanged. See [riposte height review](RIPOSTE_HEIGHT_REVIEW.md) for matched captures, contact timing impact and the user's acceptance of brief riposte deformation.

No engine-source, modeling, skinning, material, audio, attack-clock or saved user-tuning changes were needed. The new trajectory changes the spatial threat and must be judged for feel; preserved clocks do not prove preserved weight or responsiveness.

The source author uses calibrated point controls and exports the actual Cascadeur solve. It is not an AutoPhysics result. Solver control error and rigid grips cannot establish good anatomy or animation quality. The remaining wrist/carry and first-person visibility concerns belong in the candidate review.
