# PROJECT: SYSTEMATIC VISUAL UPGRADE FOR THE MELEE COMBAT LAB

Continue developing the existing Unreal Engine 5.8 first-person melee slasher project in the current workspace.

The selected visual direction is:

SUNLIT LOW-FANTASY TOURNAMENT

The game should feel like a grounded medieval tournament held in a maintained castle courtyard. The scene should use warm limestone and sandstone, believable steel armor, restrained heraldic colors, clear late-morning sunlight, and modest environmental wear. Aim for stylized realism rather than film-quality photorealism.

Your task is to establish a repeatable visual-development pipeline and implement the first complete version of this style.

## PRIMARY GOALS

1. Replace the blocky combatants with somewhat realistic medieval knights.
2. Replace the current testing arena with a convincing castle tournament courtyard.
3. Place a fountain at the center of the courtyard as its main visual and spatial landmark.
4. Preserve excellent first-person combat readability.
5. Maintain a realistic path toward 144 FPS at 1080p on mid-tier gaming PCs.
6. Establish a profiling and iteration loop that allows future agents to improve the graphics without gradually destroying performance.
7. Build and run the result, inspect it from the actual combat camera, and keep iterating until the visual change is concrete and reviewable.

## PERFORMANCE TARGET

Treat 144 FPS as a core design constraint.

The frame-time budget is 6.94 ms at 1080p. Use a representative mid-tier target comparable to:

- Six-core modern desktop CPU
- 16 GB system memory
- RTX 3060 / RTX 4060 or RX 6600 / RX 7600 class GPU
- 1080p resolution
- Development or packaged build measurements, with editor overhead reported separately

Create at least three graphics profiles:

- Competitive: targets 144 FPS
- High: targets 90 FPS
- Showcase: favors appearance while remaining playable

Competitive is the authoritative profile. Visual decisions must work gracefully when expensive features are disabled.

Do not claim the performance target is met based only on editor FPS or an uncapped reading on the current machine. Record the rendering settings, resolution, test camera path, frame-time measurements, and relevant hardware. If the local hardware is substantially faster than the target, use conservative scalability settings and GPU profiling to estimate risks honestly.

## VISUAL DIRECTION

The courtyard should communicate an organized low-fantasy tournament rather than a ruined battlefield.

Use:

- Warm pale sandstone and limestone
- Weathered but maintained architecture
- Muted blue and red heraldic accents
- Steel, darkened iron, leather, wood, linen, and wool
- Clear late-morning sunlight
- Cool ambient shadow color
- Small amounts of moss, dust, discoloration, and edge wear
- Strong character silhouettes against the environment
- Restrained decoration around the playable space

Avoid:

- High-fantasy glowing architecture
- Excessively dark or muddy grading
- Dense foliage that obscures attacks
- Heavy fog
- Persistent screen effects
- Excessive bloom
- Mirror-like wet surfaces
- Large numbers of dynamic lights
- Overly busy materials behind combatants
- Visual effects that conceal weapon trajectories
- Expensive detail that is invisible from the combat camera

The environment should support the duel. The player must be able to read weapon origin, attack height, body position, parry sparks, chamber sparks, and footwork immediately.

## KNIGHT ART DIRECTION

Replace all visible block characters, including training opponents, with optimized armored knights.

The knights should look grounded and functional:

- Closed or partially closed medieval helmets
- Mail, padded cloth, plate components, leather straps, gloves, and boots
- Clear torso, shoulder, arm, hand, and leg forms
- Medium-poly geometry with useful silhouettes
- Believable steel roughness rather than chrome
- Subtle wear and grime
- Muted heraldic cloth for visual identity
- No oversized fantasy armor or extreme ornamental spikes

Create at least two readable variants using shared underlying assets and materials:

- Player-aligned knight: muted blue heraldry
- Opposing knight: muted red heraldry

Use material instances and shared texture sets. Prefer trim sheets, tiling materials, masks, and vertex colors over many unique high-resolution textures.

The first-person arms, hands, weapon grip, and visible armor must match the new knight style. Do not leave the first-person presentation as block geometry while only upgrading the dummy.

Preserve the existing simulation-owned weapon trajectory. Presentation follows combat state and may not alter hit timing, blade position, collision, attack direction, turncaps, chamber rules, parry rules, or movement.

If suitable licensed knight assets already exist locally, inspect and reuse them. Do not download or redistribute unlicensed assets. If production-ready assets are unavailable, build an optimized modular knight prototype from available Unreal assets and clean procedural components, structured so a later skeletal mesh can replace it without changing combat code.

Use a proper skeletal or articulated presentation where practical. Avoid physics-driven armor that can affect combat. Secondary cloth or straps should be cosmetic, bounded, and disableable in the Competitive profile.

## COURTYARD LAYOUT

Replace the existing test map presentation with a modular courtyard while preserving useful combat-testing distances.

The layout should include:

- Central circular or octagonal fountain
- Broad walkable ring around the fountain
- Warm stone paving with subtle variation
- Castle walls or arcades defining the perimeter
- Arched entrances
- Tournament banners
- Limited benches, weapon racks, planters, crates, or training props
- Clear open duel zones
- A few strong architectural landmarks for orientation

The fountain should act as both a visual anchor and a movement obstacle. Its collision must be simple, stable, and easy to read.

Keep the arena useful for testing:

- Open space for neutral duels
- Space for circling and footwork
- Clear walls for drag and collision tests
- Predictable collision
- No decorative snag points near primary combat routes
- No narrow clutter corridors
- No props that hide lower-body attacks

Use modular pieces and instancing. Keep collision meshes much simpler than render meshes.

## FOUNTAIN

Build a convincing but inexpensive fountain.

Use:

- Modular stone basin and central feature
- Tiling stone material
- Cheap water material based primarily on animated normal maps
- Modest water jets or falling streams
- Small splash particles
- Simple looping fountain audio
- Simple collision around the basin

Avoid expensive planar reflections, dense translucent particle sheets, large translucent overdraw, and simulation-heavy water.

The Competitive profile may simplify or disable water translucency, reduce particles, and use an opaque or masked approximation.

## LIGHTING

Favor stable, inexpensive lighting.

Start with:

- One dominant directional light
- Skylight or equivalent ambient contribution
- Baked or cached lighting for static architecture where appropriate
- Reflection captures for armor and fountain readability
- Restrained contact shadows
- Minimal movable shadow-casting lights

The sunlight should create attractive armor highlights without losing detail in shadow. Keep exposure stable during combat. Disable automatic exposure changes unless there is a clear gameplay reason.

Do not make the Competitive profile depend on costly full-scene Lumen settings. If Lumen is retained for High or Showcase, provide a lower-cost fallback with comparable art direction.

Evaluate Virtual Shadow Maps, conventional shadow maps, Lumen, baked lighting, Nanite, TSR, TAA, and resolution scaling based on measured cost rather than defaults. Nanite is appropriate only where it provides a measured benefit.

## MATERIAL STRATEGY

Create a compact shared material library:

- Sandstone/limestone
- Cobblestone or stone paving
- Weathered steel
- Darkened iron
- Leather
- Painted wood
- Heraldic cloth
- Fountain water
- Moss/dirt decal or vertex blend

Expose useful parameters through material instances:

- Base color
- Roughness
- Dirt amount
- Edge wear
- Tint
- Normal intensity
- Texture scale

Avoid excessive material slots and unique draw calls. Consolidate materials on knight and courtyard assets where reasonable.

## EFFECTS AND READABILITY

Keep the recently improved parry and chamber feedback prominent.

- Parry effects should remain warm gold.
- Chamber effects should remain cyan.
- Sparks should be brief, directional, and visible in sunlight.
- Weapon trails must remain subtle and must communicate trajectory accurately.
- Do not use full-screen flashes that obscure follow-up attacks.
- Fountain particles and ambient effects must never be confused with combat sparks.
- Environmental audio must sit below weapon, impact, parry, chamber, footstep, and exertion cues.

Aesthetics may improve the presentation of combat feedback, but combat timings and mechanics are outside this task.

## IMPLEMENTATION ORDER

Work in measured stages. Complete, build, inspect, and profile each stage before adding the next.

### Stage 1: Baseline and budgets

- Inspect the current project, visual architecture, combat presentation, map construction, assets, renderer settings, and scalability settings.
- Record a baseline from a repeatable combat scene.
- Capture CPU frame, GPU frame, draw calls, primitive counts, shadow cost, translucency cost, memory use, and frame-rate statistics where available.
- Define budgets for knights, courtyard, fountain, lighting, shadows, particles, and post-processing.
- Save baseline screenshots and performance data.

### Stage 2: Courtyard blockout

- Preserve the proven combat-space dimensions.
- Replace the abstract arena presentation with the courtyard layout.
- Add the central fountain with simple collision.
- Validate navigation, line of sight, wall collision, weapon collision, and duel spacing.
- Profile before adding detail.

### Stage 3: Knight replacement

- Replace block combatants and first-person block arms.
- Preserve simulation authority and exact weapon trajectories.
- Establish blue and red variants.
- Add LODs and material instances.
- Test every attack direction, stab, combo, parry, chamber, morph, feint, crouch, jump, sprint, death, and reset behavior.
- Check for clipping from the first-person camera.

### Stage 4: Materials and lighting

- Implement the shared material library.
- Establish the sunlight, ambient fill, exposure, reflection captures, and restrained color grade.
- Verify that knights remain readable against every courtyard background.
- Profile shadow and material cost.

### Stage 5: Fountain and environmental detail

- Add optimized water motion, splash effects, sound, banners, and restrained props.
- Use instancing and LODs.
- Keep primary combat lanes clear.
- Profile translucency, particles, animation, and draw calls.

### Stage 6: Scalability and polish

- Implement Competitive, High, and Showcase profiles.
- Make expensive decorative systems disableable.
- Run the repeatable performance route on every profile.
- Fix the largest measured bottlenecks first.
- Inspect screenshots and gameplay footage for inconsistent style, clipping, lighting problems, distracting backgrounds, and weak silhouettes.

## CONTINUOUS IMPROVEMENT LOOP

Establish this loop for every future visual change:

1. Capture the current reference image and performance baseline.
2. State the visual problem being addressed.
3. Make one bounded visual change.
4. Build and run the actual game.
5. Inspect the change through the first-person combat camera.
6. Test it during movement and all relevant combat actions.
7. Profile the same repeatable scene.
8. Compare visual benefit against frame-time cost.
9. Keep, optimize, scale, or remove the change.
10. Update the visual and performance records.

Do not accumulate speculative effects before profiling. Work from the largest visible improvements to smaller polish.

Maintain a visual backlog divided into:

- Character quality
- Environment composition
- Materials
- Lighting
- Combat effects
- Animation presentation
- Audio presentation
- Optimization
- Scalability

For each backlog item, record its expected visual benefit, performance risk, implementation status, and measured result.

## TECHNICAL BOUNDARIES

Do not alter combat mechanics during this visual pass.

Preserve:

- Simulation-owned weapon poses
- Collision and trace behavior
- Attack phase timing
- Turncaps
- Combo side rules
- Chamber eligibility rules
- Parry geometry
- Movement and lunge behavior
- Existing combat tests
- Input mappings
- Tuning persistence

Presentation components may read combat state but may not become gameplay authority.

Keep runtime procedural presentation separate from the portable combat simulation. Do not introduce root-motion authority, animation-driven damage, lock-on, aim assistance, or collision based on visible cloth or armor.

Do not remove debug and inspection tools. Update them if needed so geometry remains inspectable through the new meshes.

## VALIDATION

Before considering a stage complete:

- Build the Unreal project successfully.
- Run the native combat suite.
- Run Unreal automation tests.
- Run the scripted in-engine combat tour.
- Verify all existing combat scenarios still pass.
- Inspect representative screenshots from the player camera.
- Test the courtyard in motion.
- Check knight presentation for clipping and trajectory mismatch.
- Profile the same repeatable route.
- Record observed FPS and CPU/GPU frame time.
- Report warnings and limitations honestly.

Add focused tests only where new presentation logic can regress meaningful behavior. Do not create tests that simply restate implementation details.

## REQUIRED DELIVERABLES

Produce:

1. A working sunlit low-fantasy tournament courtyard.
2. A central optimized fountain.
3. Upgraded blue and red knight presentations.
4. Matching first-person armored arms and hands.
5. Shared material instances and a restrained lighting setup.
6. Competitive, High, and Showcase graphics profiles.
7. Before-and-after screenshots from the combat camera.
8. A repeatable performance-test route.
9. A performance record containing settings, resolution, hardware, FPS, CPU/GPU frame time, and known bottlenecks.
10. A visual-style guide describing palette, materials, lighting, knight design, environmental rules, and readability requirements.
11. A prioritized visual backlog for future improvement.
12. Updated project documentation explaining how to extend the style efficiently.

## DEFINITION OF DONE

The pass is complete when:

- No visible combatant remains a block figure.
- First-person limbs visually belong to the same knight style.
- The arena reads immediately as a maintained medieval tournament courtyard.
- The fountain serves as the central landmark without dominating performance.
- All six strike origins, stabs, combos, parries, chambers, feints, morphs, movement, crouching, jumping, impacts, and resets remain visually and mechanically correct.
- Knights remain readable against the courtyard during fast combat.
- Competitive settings have a credible measured path to 144 FPS at 1080p on the target class of hardware.
- Existing combat validation passes.
- Visual improvements and performance costs are documented.
- The project is left in a buildable, runnable, reviewable state.

Begin by inspecting the existing project and recording the baseline. Then proceed autonomously through the stages. Make reasonable implementation decisions without stopping for routine confirmation. If production-quality knight assets are unavailable, implement the strongest optimized modular substitute possible and document the exact asset gap for the next pass.