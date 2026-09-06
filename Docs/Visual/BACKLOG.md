# Visual backlog — September 6, 2026

Current architecture and staged plan: [REHAUL.md](REHAUL.md). Earlier planned statuses were stale.

| Priority | Area | Next work / benefit | Risk | Status |
|---|---|---|---|---|
| P0 | Presentation foundation | Exact blade frame and grip contacts; shared torso/elbow targets | Extreme-pitch reach | Implemented; portable invariant suite passes |
| P0 | Material pipeline | Generate real shared materials, reject failed graph connections, enable instancing and cook assets | Shader permutations | Implemented; rendered verification required after each generator change |
| P0 | Character quality | Authored knight rig, weighted hands, clavicle/spine reach compensation | Asset creation, skinning and clipping | Missing assets; procedural fallback retained |
| P0 | Animation | Direction-specific authored load/carry poses layered under final hand IK | Must preserve authoritative weapon and timings | Adapter ready; AnimBP/Control Rig assets still missing |
| P0 | Validation | Resolve the pre-existing double-parry native failure through a separately authorized combat decision | Frozen mechanics | Recorded, untouched |
| P1 | First person | Camera-safe torso look-down mesh and finger grip articulation | Camera clipping | Full body in external views; first-person torso hidden |
| P1 | Environment | Stone trim sheet, recessed arcade modules, shaped cloth banners | Draw calls and shadow cost | Existing court extended with shallow arches, plinths and basin inlay |
| P1 | Lighting | Artist review of sunny/shaded backgrounds and reflection response | Shadow readability, GPU cost | Atmosphere skylight replaces unbuilt runtime reflection capture |
| P1 | Effects | Preserve gold parry/cyan chamber; improve fountain stream geometry | Visual competition with combat | Combat feedback preserved; fountain still basic |
| P1 | Materials | Real steel/cloth/leather normal and trim sheets | Texture budget | Generated shared micro-detail is a fallback |
| P2 | Performance | Packaged route and RTX 3060/4060-tier measurement | Hardware availability | Local RTX 5070 measurements only |
| P2 | Audio | Fountain ambience, footfalls and exertion | Cue masking | Synthesized combat placeholder retained |
