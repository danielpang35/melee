# MEL-17 — Unreal style implementation plan

Updated 8 September 2026. This is a planning delivery: the work packages below are proposed; no new art variant, engine import or visual acceptance is claimed. [Current evidence](UNREAL_STYLE_CHECKPOINT.md) records completed work. This plan supersedes the older Helmet_v009/USP_v011 implementation sequence and the historical contracts in [the technical handoff](UNREAL_STYLE_TECHNICAL_HANDOFF.md) wherever they differ.

## Outcome and fixed authorities

Deliver the accepted Clay_v005 helmet with the restrained Steel_v025 treatment, first demonstrated beside accepted armor in the audited source rig, then in actual Unreal daylight, movement, shade and gameplay distance.

- Shape: `ArtSource/StyleReference/MEL17/GeometryReview/Clay_v005/Helmet_Clay_v005.blend`. The checkpoint records explicit user acceptance: “Looks very nice. The shape is quite perfect.” Recorded SHA-256: `a9937b6b9cb04973a4a3b4b383f4a635c55e63c2241f737e9f573489a631c263`. Geometry acceptance is closed.
- Material: unchanged `ArtSource/StyleReference/MEL17/Steel_v025/Steel_v025.blend`; its `generator.py` supplies the accepted normal mechanism. `Saved/ArtReview/UnrealStyle/AcceptedSteelTransfer/rig_audit.json` supplies the lighting/camera audit, not the material mathematics.
- Visual reference: unchanged `ArtSource/StyleReference/MEL17/06-riot-inspired.png`, with the user's smoother, less crowded steel correction. Preserve sharp construction and readable warm/cool values; do not reintroduce paint islands, noisy facets or soft blur.
- Scope: one isolated helmet proof. Shoulder/breastplate portability, fitting, articulation, full character production and dedicated profiling remain later milestones behind existing project gates.

Live Linear MEL-17 was checked: In Progress. Its Helmet_v009 text is historical; the newer local checkpoint records Clay_v005 acceptance. This planning delivery does not change remote task state.

## What can be reused, and what must change

| Area | Existing evidence or machinery | Required next change |
|---|---|---|
| Source geometry | Accepted Clay_v005; receipt reports 15 metal objects and 61,132 evaluated metal triangles | Derive an export copy; preserve accepted construction. Old 9,488-triangle/four-slot receipts do not describe it. |
| Material | Steel_v025 blends toward connected constant plane-normal targets | Reauthor helmet-specific regions; existing additive-offset helmet fields are a different mechanism. |
| Export | Revision protection, evaluated meshes, triangulated FBX, tangent maps and receipts | Remove old assembly/slit/material-name assumptions and automatic UV regeneration during baking. |
| Unreal | Scoped importer, saved no-pawn proof map, material variants and ordinary PIE screenshots | Version the transfer contract; preserve the geometric normal foundation in the control; verify the new asset. |
| Capture | Bounded Slate callback, immutable run folders, effective settings and frame receipts | Add a compact transfer set, complete-image validation and mandatory motion continuity checks. |
| Artistic evidence | Shape accepted; earlier WorldNormal diagnostics prove old fields reached the renderer | Material fidelity, new-asset seams/handedness and motion remain open. Prior technical success is not a pass for this helmet. |

The rejected Unlit response and custom-renderer exploration are closed for this sequence. Preserve Default Lit and the existing Competitive configuration. No C++ or global renderer change is planned.

## Sequential implementation packages

### P1 — Prepare the editable helmet steel source

**Owner:** source/material agent. **Depends on:** existing accepted sources and receipts.

Add proposed `Tools/BuildHelmetSteelTransfer.py`. It loads Clay_v005 explicitly and creates a fresh `ArtSource/StyleReference/MEL17/SteelTransfer/ST_v001/` package. Proposed outputs: `Helmet_Steel_ST_v001.blend`, `regions.json`, `source_manifest.json`, and `validation.json`. Check revision availability at execution; never overwrite an existing package or either accepted source.

Preserve the editable construction stack, assembly transform, silhouette, aperture thickness, crown overlap, ridge, cheek curvature and chin returns. Include an explicit part/slot mapping and construction-protection selections. Account for the assembly's nonuniform X scale when transforming normals. Start from evaluated geometry; no decimation or broad retopology is justified by this proof.

Recreate the accepted mechanism in a declared common normal space:

`N = normalize((1 - w) * Ns + w * Nt)`

`Ns` is the underlying construction normal; `Nt` is a constant target normal within a connected region. The accepted generator uses `w = 0.4 * alpha`; use this as the starting influence, adapting layout to helmet curvature. Store named plate/region membership, boundary, target direction, influence, protected-edge mask and transition width. Keep regions attached to their plate and broad areas quiet. Do not copy the proxy's maps or region count, or select disconnected plates solely through overlapping positions.

Start with accepted linear steel RGB approximately `(.29, .285, .275)`, metallic `1`, roughness `.30`, and `.23` only for justified selective edges. Keep padding/dark materials separate. Zero influence must recover the same construction normal with unchanged geometry, color, roughness and edge treatment.

**Exit evidence:** editable material graph and region recipe; explicit included parts/materials; representative interior, edge and seam checks establishing the zero-influence result. Accepted sources remain unchanged. This establishes a source contract, not material acceptance.

### P2 — Prove the material under the accepted source rig

**Owner:** same source/material agent, with one independent art critic reused through revisions. **Depends on:** P1.

Append an unchanged accepted armor comparator into the working scene and preserve the audited reflection surroundings, light transforms and color management. Audit values include a 750 W rectangular key (`3 × .18`), 100 W rim, broad 15 W front fill, blue world at `.30`, AgX, exposure `0`, gamma `1`. Record comparator placement because position affects reflections. The clay review rig and Unreal neutral rig are separate rigs.

Use the accepted helmet view direction and projection, adjusting framing only. Render front and matched three-quarter smooth/authored pairs, the unchanged armor comparator, original portrait detail and a native-size helmet comparison. Keep lighting fixed during each A/B. Use the proven Cycles CPU route. Add a short fixed-light rotation only after still corrections are satisfactory. Add roughness variation only for a specific remaining mismatch.

Proposed evidence destination: `Saved/ArtReview/UnrealStyle/ST_v001/Review/`, including images and settings. The critic assesses steel character, restrained variation, selective edge treatment and preservation of the accepted form. Target at least 8/10 for each applicable material criterion, with no major mismatch hidden by averaging. Shape preservation is a transfer check; unchanged geometry does not require renewed shape approval.

**Exit evidence:** satisfactory source comparison and concise critic findings. If regions read as dents, camouflage or random facets, correct the region mechanism/layout before any Unreal lighting experiment. This is the next visible deliverable and permits P3; it does not establish final material acceptance.

### P3 — Finalize UVs, bake and export a scoped revision

**Owner:** engine/technical-art agent, using the source agent's accepted treatment. **Depends on:** P2.

Adapt `Tools/BuildUnrealStyleSource.py` into explicit preparation and bake steps. Preparation consumes the P1 part/slot contract and derives an evaluated export copy. Preserve construction normals; prepare plate-aware UVs, then freeze triangulation and tangent basis. Baking consumes that exact mesh and fails when the geometry/UV/tangent fingerprint differs. Do not rerun unconditional smart projection during the bake or reuse old UV-bound masks without verified identical UV identity.

Keep the existing 35 cm bottom-centered assembly as a documented proof scale, not an anatomical measurement. Preserve proportional shape and record source-to-export transforms and front/ridge/slit landmarks. Retain `-Y` forward, `Z` up and the source-verified Unreal mapping `(Bx, -By, Bz)` after normalization. Use mesh node names such as `SM_Helmet_StyleProof012`; the historical importer treats FBX node names containing `USP` as collision nodes.

**Selected normal contract:** bake `N0`, the construction-normal foundation, and `N1`, the complete authored result, against the same frozen tangent basis. The runtime material decodes each once and uses `normalize(lerp(N0, N1, Blend))`. `Blend=0` is smooth control; `Blend=1` is the faithful baked candidate. Intermediate values are diagnostic endpoint interpolation, not a promise to reproduce the source graph's intermediate influence. Author region-strength changes in the editable source and rebake. Never compose the complete authored bake with itself. A flat `N0` may replace the foundation texture only if exported/imported split normals demonstrably reproduce that foundation.

Begin with 2K DirectX tangent normals and linear packed masks: R roughness, G selective edge, B authored influence for diagnostics. The baked `N1` already includes influence: do not multiply its influence again in the runtime graph. Retain separate editable region/protection masks in the source package. Verify UV padding and seams, normal handedness, protected construction, finite unit normals and identical geometry across controls.

Proposed engine source destination: `ArtSource/StyleReference/MEL17/UnrealProof/USP_v012/`, if still unused when execution starts. Treat `USP_v012` as a proposed revision, not an existing validated output.

**Exit evidence:** source/export `.blend`, triangulated FBX, baked maps, versioned manifest and validation receipt for one immutable revision; matching mesh/UV/tangent identity across bake and export.

### P4 — Import and prove neutral transfer in Unreal

**Owner:** same engine/technical-art agent. **Depends on:** P3.

Adapt `Tools/ImportUnrealStyleProof.py` to preflight the new manifest before asset writes. Replace hard-coded source names, slot classification and height assertions with the explicit manifest contract. Preserve old revision compatibility through explicit schema handling; fail on unknown schemas or missing required fields rather than guessing.

Import only below `/Game/Visual/StyleProof/<revision>/`. Reuse disabled material/texture auto-import, imported normals+tangents, the isolated no-pawn map and existing comparison variants. Explicitly set and verify opaque Default Lit, normal-map compression with sRGB off and DirectX green convention, linear masks, preserved mesh build normals/tangents, and disabled unwanted collision/Nanite. Verify actual slots, manifest height/bounds and transformed landmarks. Initialize steel values from the transfer contract, not clay materials.

Adapt `Tools/CaptureUnrealStyleProof.py` and `Tools/UnrealStyleProof.ps1` to accept one proposed `transfer` capture set consistently across launcher/importer/capture. Use approved camera metadata; record fitted perspective FOV/transform rather than copying the source orthographic camera or assuming an old camera fits the new helmet. First capture matte import fidelity, then neutral smooth/authored front and matched three-quarter pairs. Each receipt identifies the imported manifest, actual material variants, rig, exposure and effective Competitive settings. Preserve TAA and the existing disabled SSR/GI/reflection-method settings; no hidden Lumen dependency.

**Exit evidence:** complete ordinary PIE captures, zero-control equivalence, intact silhouette/construction, clean seams/bevels and coherent directional normal response. Use one targeted WorldNormal or light-direction diagnostic if needed to locate a defect; old WorldNormal evidence does not validate the changed asset. Diagnose import, normals, roughness, lighting or tone mapping separately before altering accepted geometry.

### P5 — Validate daylight, movement, shade and distance

**Owner:** engine agent produces evidence; same independent art critic reviews. **Depends on:** P4 still transfer passing.

Capture matched reference daylight at fixed exposure, then continuous helmet rotation under fixed light, a fixed helmet with moving key, an actual lit-to-shade transition and intended gameplay screen size. Record actual output dimensions and helmet pixel height; the source reference's approximately 184-pixel crown-to-chin crop is a comparison scale, not proof of intended gameplay distance. Keep blur/DOF disabled in the proof and gameplay TAA active for final motion. Do not turn full sequences into a parameter sweep.

Strengthen the existing capture verifier: decode the complete PNG and verify dimensions/nonblank output, rather than accepting a PNG header alone. Require complete motion sequences with consecutive rendered frame evidence and recorded transforms; missing/noncontinuous frames fail the motion gate. Held-pose samples may diagnose reflections but cannot establish temporal stability. Preserve bounded timeouts and clean callback/editor shutdown on failure.

**Exit evidence:** separate scores of at least 8/10 for material character, reflection/color, and motion/distance; preserved shape; no distracting shimmer, swimming, seam catches or disappearing treatment at distance. State exactly whether motion was played or only sampled. User material review follows the completed engine evidence. Technical completion and critic scores do not imply that review has occurred.

### P6 — Package and demonstrate repeatability

**Owner:** engine agent and parent coordinator. **Depends on:** P5 technical/art gates and user material acceptance.

Use `Tools/BuildUnrealStyleReview.py` with explicit capture/source inputs to package the editable treatment, maps, accepted scene, material instances, import settings, light/camera settings, source identities and critic decision. Save only the accepted winning map/settings. Perform one controlled source-region edit, export/import it to a separate revision and verify the expected change without disturbing the accepted baseline; revert by selecting the preserved baseline.

**Exit evidence:** portable review packet, runnable winning revision and successful edit/reimport receipt. Then assess shoulder and breastplate portability subject to the existing MEL-11/full-production gates. Record proof asset costs now; dedicated profiling, deformation and full-body integration remain later work unless a concrete slowdown or integration defect calls for a focused check.

## Manifest and evidence contract

The current exporter and historical handoff describe different schemas. P3/P4 must agree on a versioned schema before import implementation:

| Field group | Required information |
|---|---|
| Identity | Schema version, revision, accepted-source references/recorded hashes, working-copy identity, file hashes and relative contained paths |
| Assembly | Explicit included parts, slot mapping and steel/nonsteel parameters; normalization, origin, scale, bounds, landmarks and axis convention |
| Bake | UV/triangle/tangent fingerprints, normal representation `base_and_final`, source recipe identity, map resolution, color space, compression and green convention |
| Masks | Channel meanings, protected-region source, padding; clear statement that final normal already contains authored influence |
| Review | Source-camera projection/transform, source-rig receipt, runtime camera/rig/settings and exact imported manifest identity |

Keep capture receipts under `Saved/ArtReview/UnrealStyle/<revision>/run_###/`. Preserve failed runs with a reason; mark completion only after evidence validation. Record technical result, critic result and human decision separately. Do not infer fresh acceptance from historical metrics or rerun unchanged authority audits.

## Execution and verification discipline

The planning subtasks were completed by two Astra High agents with self-contained context and no child agents: source/material planning and engine architecture. Execution is sequential P1 → P2 → P3 → P4 → P5 → P6, reusing each owner and one critic through acceptance. Serialize heavy source renders and engine imports/captures. Users receive images and runnable review artifacts; agents own Blender and engine operation.

For this documentation delivery, verify changed references and plan consistency; no engine build or combat test is required. During implementation, stop the affected package on an unmapped part/slot, changed construction, invalid bake identity, zero-control mismatch, import seam/handedness defect, effective-setting mismatch or incomplete motion evidence. Fix that dependency and rerun only affected checks.

Corrective efficiency decisions: replace the stale old-mesh/Unlit instructions; settle the normal foundation before importer changes; reject inconsistent capture options before launching Unreal; reuse accepted-source evidence and postpone full sequences until stills pass.
