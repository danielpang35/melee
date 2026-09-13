# Tuning provenance and reproducible benchmark

Current pilot reference (12 September): [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) owns the corrected selection and verified launch. Its engine receipt identifies `sha1:e8d0f4b5966efaa710c7906b2ad9484f752f8983` after the later user-directed swing-feel changes. Exact live values belong to configuration/engine receipts, not this loader-history record. The identity in the 11 September completion below describes that earlier tested configuration; the four-test loader result remains valid at its recorded scope.

11 September completion: all four `MeleeCombatLab.Tuning` automation tests passed
in the recovered checkout. The clean-stage right-horizontal pilot loaded defaults
successfully, skipped Saved overrides, and its effective values match project JSON.
Effective identity: `sha1:4414136f87f2f237f72e3f565e6e786bbd6373ef`.
See `Saved/RightHorizontalPilot/TuningTests/index.json` and the pilot's actual
`engine-tuning.json` recorded by `Docs/THIRD_PERSON_CHECKPOINT.md`. The historical
runtime-pending state below is superseded. No double-parry checks were run.

9 September 2026. Policy MCL-DEV-2026-09-08. Workstream: [MEL-41](https://linear.app/meleeslasher/issue/MEL-41). Selected because current Saved overrides change windup, blade length and radius, obscuring the settings used for the next playable comparison. Motion source selection remains owned by the [TP checkpoint](THIRD_PERSON_CHECKPOINT.md).

Plan: preserve normal loading and atomic failure behavior; expose effective-value identity and source outcomes in developer diagnostics; add explicit defaults-only loading from a benchmark snapshot; build changed C++, run isolated loader cases, independently review the change and verify an actual engine receipt. No animation or contact changes.

Implemented `FCombatTuningPersistence`, GameMode/F4 bindings and `PlayBenchmark.ps1 -DefaultsOnly`. Normal load overlays built-ins, project and Saved; malformed JSON or invalid known values fail atomically. Missing optional files use fallback. Explicit snapshot paths are required inputs. Defaults-only skips Saved on every reload; RESET restores built-ins and promotion still targets canonical project defaults. Active source records are separate from the most recent load attempt.

Engine receipts include effective values, their identity, startup identity, operation sequence, source paths/outcomes and content identities. Identity v1 uses SHA-1 of registry-order name/value lines with 17 significant digits; source content identity uses decoded text re-encoded as UTF-8 without BOM. These differ deliberately from the launcher's raw-file SHA-256 hashes. The receipt describes the latest operation; it is not an event history. F4 edits/reset remain possible, and SAVE/PROMOTE retain their explicit write behavior.

Verification so far: normal/defaults-only prepare checks passed; independent review found no actionable correctness findings; Development Editor build passed in 176.16 seconds after one transient UBA allocation retry. Four isolated automation cases under `MeleeCombatLab.Tuning` are implemented. Engine test startup stalled under system memory pressure; observed OneDrive private memory was about 40 GB. Runtime test and benchmark receipt verification remain pending. No runtime test pass is claimed from a successful build.

Evidence is retained under `Saved/MEL41/`: `launcher-check.json`, `independent-review.md`, `build.log`, `tests.log`, `protected-before.json` and the reproducible `VerifyBenchmark.ps1`. Prepared launch identities and engine-loaded values are separate evidence. Protected EX/config/contact behavior and unrelated dirty documents remain outside this change.
