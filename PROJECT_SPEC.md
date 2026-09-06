# PROJECT: BUILD A HIGH-SKILL FIRST-PERSON MELEE SLASHER COMBAT LAB

You are the lead gameplay engineer, technical designer, combat systems engineer, gameplay animator, tools engineer, and QA engineer for this project.

Your task is to CREATE A WORKING GAME PROJECT, not merely produce a design document, pseudocode, architectural suggestions, or an incomplete scaffold.

Work autonomously from beginning to end. Infer routine implementation details yourself. Do not stop to ask me questions unless continuing is literally impossible. If an implementation choice is uncertain, choose the option most consistent with the goals in this specification, implement it cleanly, expose the uncertain parameter for tuning, test it, and continue.

Persist through compilation errors, Unreal errors, broken assets, input issues, crashes, gameplay bugs, and integration problems. Diagnose and repair them yourself.

Use available terminal, filesystem, editor, browser/documentation, computer-use, Unreal Engine, MCP, debugging, build, and testing capabilities as appropriate. If Unreal Engine exposes an MCP or other editor-control interface, use it where useful. Use official Unreal Engine 5.8 documentation when engine behavior or APIs are uncertain.

Do not finish after generating files. Build the project, launch it, enter Play In Editor or the executable, verify the mechanics, exercise the important state transitions, fix obvious defects, and perform at least one polish/tuning pass.

The working title is:

**MeleeCombatLab**

The project should be designed so it can later grow into a full multiplayer melee slasher, but this version is a polished SINGLE-PLAYER COMBAT LAB. Do not implement multiplayer yet.

---

# 1. PRIMARY PRODUCT GOAL

The highest priority, overwhelmingly above everything else, is:

**COMBAT FEEL.**

The inspiration is the extraordinarily fluid, responsive, spatial, high-skill melee combat found in games such as Mordhau and the original Chivalry.

Do not clone proprietary source code, assets, sounds, animations, maps, or other copyrighted implementation material. We are reproducing high-level mechanical principles and creating our own implementation.

The game must feel like a skill-based first-person melee system rather than:

* Skyrim melee
* a Soulslike
* an animation-lock action game
* a lock-on combat game
* an FPS where a sword animation merely triggers a raycast
* a collection of canned attack montages

The long-term goal is an extremely high or effectively unbounded mechanical skill ceiling emerging from a relatively understandable ruleset.

The first version succeeds if simply moving around another character, attacking, manipulating swings, parrying, chambering, feinting, morphing, riposting, and spacing attacks feels responsive and satisfying enough that one wants to continue dueling even in an ugly gray-box arena.

Graphics, menus, progression, narrative, inventory systems, matchmaking, cosmetics, procedural levels, quests, crafting, and other conventional game features are NOT priorities.

If you must choose between spending an hour polishing combat and spending an hour adding another game system, polish combat.

---

# 2. ENGINE AND TECHNICAL FOUNDATION

Use:

**Unreal Engine 5.8**

Primary language:

**C++**

Use Blueprints only where they provide a genuine presentation/editor benefit. The authoritative combat simulation must remain understandable in C++.

Use:

* Enhanced Input
* CharacterMovementComponent as the base for a custom melee movement component
* Unreal collision/query APIs where useful
* C++ gameplay systems
* Animation Blueprint / IK / Control Rig only as presentation where useful
* Slate or C++ UI where practical for debugging/tuning
* Niagara only if it can be created reliably without distracting from the core
* Unreal Automation Tests where useful

Do NOT use Gameplay Ability System for this prototype. It adds unnecessary abstraction.

Do NOT make root-motion attack animation authoritative.

Do NOT make animation notifies authoritative for weapon damage.

Do NOT make a skeletal animation decide where the gameplay weapon exists.

The central architectural rule is:

**COMBAT SIMULATION OWNS THE WEAPON. PRESENTATION VISUALIZES THE COMBAT SIMULATION.**

The authoritative attack system calculates the weapon's gameplay pose and trajectory. First-person arms, the sword mesh, third-person presentation, camera effects, sounds, and animation follow that gameplay state.

This separation is mandatory.

---

# 3. PROJECT STRUCTURE

Create a clean modular source hierarchy broadly following this organization. Modify names if Unreal conventions require it, but preserve the separation of responsibility.

```text
MeleeCombatLab/
│
├── Config/
│
├── Content/
│   ├── Combat/
│   │   ├── Weapons/
│   │   ├── Characters/
│   │   ├── Effects/
│   │   ├── Audio/
│   │   └── Presentation/
│   ├── Maps/
│   └── UI/
│
├── Source/
│   └── MeleeCombatLab/
│       │
│       ├── Character/
│       │   ├── MeleeCharacter
│       │   ├── MeleePlayerController
│       │   └── MeleeCharacterMovementComponent
│       │
│       ├── Combat/
│       │   ├── Attacks/
│       │   │   ├── AttackStateMachine
│       │   │   ├── AttackDefinition
│       │   │   ├── AttackTrajectory
│       │   │   ├── AttackDirectionResolver
│       │   │   └── AttackTypes
│       │   │
│       │   ├── Defense/
│       │   │   ├── ParrySystem
│       │   │   ├── ParryGeometry
│       │   │   ├── ChamberSystem
│       │   │   └── DefenseTypes
│       │   │
│       │   ├── Collision/
│       │   │   ├── WeaponTraceSystem
│       │   │   ├── CombatContactResolver
│       │   │   └── HitResolver
│       │   │
│       │   ├── CombatComponent
│       │   └── CombatTypes
│       │
│       ├── Weapons/
│       │   ├── MeleeWeapon
│       │   ├── Longsword
│       │   └── WeaponDefinition
│       │
│       ├── Movement/
│       │   ├── MomentumModel
│       │   ├── LungeModel
│       │   └── MovementTuning
│       │
│       ├── Camera/
│       │   ├── CombatCameraComponent
│       │   └── WeaponPresentationComponent
│       │
│       ├── Debug/
│       │   ├── CombatDebugHUD
│       │   ├── CombatDebugDraw
│       │   └── CombatTuningPanel
│       │
│       ├── Training/
│       │   ├── TrainingDummy
│       │   ├── AttackTrainingDummy
│       │   └── CombatLabGameMode
│       │
│       └── Tests/
│
└── README.md
```

Favor explicit, understandable systems over clever abstraction.

Avoid enormous god classes.

Avoid hundreds of tiny abstraction layers.

The architecture should be sophisticated because the combat is sophisticated, not because the class hierarchy is sophisticated.

---

# 4. BOOTSTRAPPING AND ASSETS

Make the project capable of being created and run in one end-to-end pass.

If the Unreal First Person C++ template is available, it is acceptable and probably advantageous to use it as the initial project foundation so standard first-person/mannequin content exists.

Replace the template gameplay logic with this combat architecture.

Use engine primitives and template assets wherever possible rather than wasting effort sourcing art.

A simple sword mesh can initially be constructed from a primitive or generated/imported simple mesh if necessary.

The level should be a deliberately simple gray-box **Combat Lab**.

If binary `.uasset` creation is inconvenient, use Unreal editor automation, Unreal Python, MCP/editor control, programmatic generation, template assets, or runtime spawning rather than abandoning the implementation.

Do not let the inability to hand-write `.uasset` files stop the project.

The player should be able to open/run the project and immediately reach the Combat Lab.

---

# 5. COMBAT LAB

The initial environment should contain:

* flat arena floor
* simple walls/boundaries
* good neutral lighting
* player spawn
* passive damage dummy
* programmable attacking dummy
* room to practice footwork
* optionally a simple hostile dueling bot after the deterministic training dummy works
* visible reset mechanism
* debug/tuning controls

Do not spend substantial time making the level beautiful.

Do spend enough time on presentation that impacts are readable and attacks are easy to perceive.

---

# 6. FIRST-PERSON CONTROL PHILOSOPHY

The game must feel extremely responsive.

Mouse input should have minimal perceptible latency.

Do not artificially smooth the actual player's aim to the point that it feels floaty.

Do not use aim acceleration by default.

Do not use target lock.

Do not use melee aim assist.

Do not magnetically rotate the player toward enemies.

Do not magnetically redirect attacks toward enemies.

The player must be able to:

* intentionally miss
* aim around somebody
* turn an attack into an accel
* delay contact with a drag
* aim attacks at specific parts of space
* use footwork to alter contact timing

Mechanical aim is authoritative.

Presentation smoothing may make the arms and weapon visually pleasing, but it must never make collision disagree significantly with what the player sees.

---

# 7. INPUT SCHEME

Implement the following baseline input scheme.

Movement:

```text
WASD       Move
Mouse      Look
Shift      Sprint
Ctrl       Crouch
Space      Jump
```

Combat:

```text
LMB        Directional strike
MouseWheelUp or appropriate dedicated input
           Stab

RMB        Parry

Q          Feint

Attack during valid opposing attack windup:
           Morph where applicable

Attack during appropriate post-parry window:
           Riposte

Attack during combo window:
           Combo
```

Keep bindings cleanly configurable through Enhanced Input.

The eventual game will likely support user-bound individual attack directions as well, so do not entangle attack semantics with a single input device.

---

# 8. DIRECTIONAL ATTACK SYSTEM: SIX DIRECTIONS NOW, 240-FRIENDLY INTERNALLY

Do NOT implement the full continuous Mordhau-style 240-degree attack selection system yet.

Implement six strike origins:

```text
Upper Left
Upper Right

Left Horizontal
Right Horizontal

Lower Left
Lower Right
```

Interpret the name as the side the attack ORIGINATES from.

Examples:

```text
Right Horizontal:
starts on player's right and travels toward player's left

Upper Right:
starts high on player's right and travels diagonally down-left

Lower Right:
starts low on player's right and travels diagonally up-left
```

Also implement a dedicated stab.

However, the internal system MUST be future-compatible with continuous directional selection.

Do this by separating:

```text
raw attack input angle
        ↓
AttackDirectionResolver
        ↓
six-direction quantization
        ↓
AttackDefinition
```

Store the raw continuous angle even though this version quantizes it.

Later, replacing six sectors with a continuous attack angle should not require rewriting:

* hit detection
* chambers
* trajectories
* state machine
* parries
* morphs
* combo system
* networking architecture

For directional selection, sample recent mouse movement immediately surrounding/before the strike input. Maintain a short mouse-delta history, use a recency-weighted vector, apply a configurable deadzone, convert it to an angle, and quantize that angle into the six strike sectors.

Do not create a long artificial delay after LMB while waiting for direction input.

Input responsiveness takes priority.

If mouse directional intent is below deadzone, use a deterministic sensible fallback such as the most recently selected direction or Right Horizontal.

Expose the input sampling window and deadzone in tuning settings.

---

# 9. ATTACK STATE MACHINE

The fundamental attack lifecycle is:

```text
IDLE
  ↓
WINDUP
  ↓
RELEASE
  ↓
RECOVERY
  ↓
IDLE
```

Support legal branches for:

```text
WINDUP → FEINT → NEUTRAL

WINDUP → MORPH → NEW WINDUP/TRANSITION

RELEASE/late attack flow → COMBO → NEXT WINDUP

PARRY SUCCESS → RIPOSTE

MATCHED DEFENSIVE ATTACK → SUCCESSFUL CHAMBER
```

The state machine, rather than animations, determines:

* legal inputs
* attack phase
* damage activity
* chamber activity
* feint availability
* morph availability
* combo availability
* parry availability
* turn restrictions
* movement modifiers
* lunge
* hit eligibility
* recovery
* stamina costs if enabled

Make state transitions explicit and debuggable.

---

# 10. INITIAL LONGSWORD TIMINGS

Use a longsword as the only fully developed weapon initially.

Exact values are TUNING STARTING POINTS, not immutable design requirements.

Use approximately:

```text
STRIKE

Windup:          ~525 ms
Release:         ~475-500 ms
Recovery:        ~650-700 ms
Combo windup:    ~650-700 ms

STAB

Windup:          ~550-575 ms
Release:         ~325-375 ms
Recovery:        ~650-700 ms
```

Tune after actually playing.

The important behavioral property is that windup is long enough to create readable commitment and feint/chamber mindgames, while release is long enough to permit meaningful accels and drags.

Attack phases should be based on elapsed simulation time, not number of frames.

---

# 11. EARLY/LATE RELEASE AND DAMAGE WINDOW

Do not necessarily make 100% of the visual release equally damaging.

Expose:

```text
DamageWindowStart
DamageWindowEnd
```

as normalized release-phase values.

A good starting point might be approximately:

```text
Damage begins around 5-10% into release.
Damage ends around 90-95% through release.
```

The attack trajectory may continue visually before and after the damage interval.

This helps prevent pathological instant-release hits and absurd extreme late-release contacts.

Defense interaction may remain active slightly outside the damaging portion where appropriate.

These values must be data-driven.

---

# 12. PROCEDURAL / DATA-DRIVEN ATTACK TRAJECTORIES

This is a foundational requirement.

Do not implement an attack as:

```text
Play animation
Wait for notify
Perform trace
```

Instead, each attack has a normalized trajectory.

Conceptually:

```text
WeaponPose =
    F(
      AttackDefinition,
      AttackPhase,
      CombatOrientation,
      ViewManipulation,
      CharacterMovement
    )
```

An AttackDefinition should contain enough data to describe:

* windup trajectory
* release trajectory
* recovery trajectory
* local weapon position
* local weapon rotation
* timing
* turn-cap curves
* lunge curve
* damage window
* combo window
* feint lockout
* morph window

Use interpolation that produces continuous, pleasing motion.

Quaternion interpolation or another rotation representation that avoids Euler interpolation artifacts is preferred internally where appropriate.

The sword should visibly travel along a coherent physical arc.

The attack's gameplay trajectory and rendered weapon must be derived from the same state.

Use IK/procedural positioning so arms follow the gameplay weapon naturally.

Presentation can lag the gameplay solution by only a tiny amount, and only if visual mismatch remains negligible.

---

# 13. SWING MANIPULATION: ACCELS AND DRAGS

This is one of the most important mechanics in the entire project.

During attack release, the player retains meaningful control of their orientation.

The attack is defined in player-local/combat-local space.

Changing the player's orientation changes the attack's resulting WORLD-SPACE trajectory.

Therefore:

Turning INTO the strike physically causes the blade to reach the target earlier.

This is an **accel**.

Turning AWAY from the strike physically delays contact.

This is a **drag**.

Do NOT implement accels or drags by detecting mouse direction and changing animation playback speed.

Do NOT use:

```text
if turning into attack:
    AttackSpeed *= 1.4
```

Swing manipulation must arise primarily from spatial movement of the attack trajectory through world space.

Footwork must also contribute naturally.

If I step into an attack, contact happens earlier.

If I move away or rotate away, contact happens later.

This is a core source of skill expression.

---

# 14. ATTACK TURNCAPS

Unlimited rotation during release will create helicopters, spins, unreadable attacks, and degenerate exploits.

Implement phase-dependent turn-rate limits.

At minimum distinguish:

```text
Idle
Windup
Release
Recovery
Parry
```

Windup should permit substantial freedom.

Release should be meaningfully restricted.

The turn restriction may vary over normalized release phase.

Represent this with curves where practical.

Conceptually:

```text
Windup:
high turn freedom

Early Release:
moderate/high

Mid Release:
lower

Late Release:
low

Recovery:
control gradually restores
```

Yaw and pitch may have different caps.

Discard mouse movement beyond the permitted rotation rather than accumulating it and causing a camera snap afterward.

Expose all caps for live tuning.

Do not arbitrarily make the game sluggish. The player should remain strongly connected to the mouse within the permitted angular envelope.

---

# 15. ANTI-SPIN / GLANCING PROTECTION

Preserve powerful drags while preventing nonsense.

Track cumulative offensive rotation during release.

If an attack becomes an extreme spin or otherwise exceeds a tunable plausible manipulation threshold, make the attack incapable of dealing full damage or mark it as a glancing/non-damaging continuation.

Also use the configurable late-release damage cutoff.

This protection should target pathological exploits without killing ordinary:

* accels
* drags
* foot drags
* target switching
* torso manipulation

Expose the threshold.

Visualize it in debug mode.

---

# 16. WEAPON COLLISION

Do not perform a single raycast at one instant.

The weapon exists continuously in space.

Track its previous and current authoritative transforms.

Represent the sword's damaging geometry as a single conceptual blade/weapon segment with small thickness.

IMPORTANT DESIGN CONSTRAINT:

**Do not differentiate gameplay between the tip, middle, base, hilt, ricasso, inner blade, outer blade, etc.**

There is no tip damage modifier.

There is no special inner-blade parry rule.

There are no semantic sword zones.

If multiple sample points or subsegments are used internally to make collision numerically robust, they all represent the same weapon and use identical gameplay rules.

Sweep between previous and current weapon positions.

Use sufficient continuous sweep coverage that a fast blade cannot teleport through a target at low frame rates.

For curved motion and large DeltaTime values, use adaptive combat substeps based on:

* elapsed time
* weapon translation
* weapon angular displacement

Cap the number of substeps to avoid pathological performance costs.

The same attack should behave nearly identically at:

```text
30 FPS
60 FPS
120/144 FPS
240 FPS
```

Maintain a set of actors hit by the current attack so an ordinary swing cannot damage the same target repeatedly every frame.

---

# 17. COLLISION PRIORITY

When interactions happen in the same combat substep, resolve defense before ordinary body damage.

A sensible conceptual priority is:

```text
1. Valid chamber protection
2. Valid parry
3. Weapon/world interaction or clash where relevant
4. Character damage
```

Implement resolution carefully enough that outcome does not change merely because two collision callbacks happened in a different engine order.

Centralize combat contact resolution rather than spreading it across unrelated overlap callbacks.

---

# 18. PARRY SYSTEM

Parry is intentionally generous SPATIALLY and demanding TEMPORALLY.

RMB initiates a parry.

Use approximately:

```text
Active parry window: ~325-400 ms starting range
```

Choose a good initial value and expose it for tuning.

There must also be a meaningful parry recovery/punish window after a missed parry.

A successful parry should return initiative quickly enough to support ripostes and responsive defense.

The defining implementation is that parry consists of TWO protective geometries:

```text
A. Main Parry Box

B. Extended Parry Catch Region
```

These serve different purposes.

---

# 19. MAIN PARRY BOX

Create a large oriented defensive box attached to the defender's combat/guard orientation.

It protects most of the character from frontal attacks.

It should be deliberately large and forgiving.

The box must be sensitive to the player's view pitch.

This is a key mechanic.

When the player LOOKS UP while parrying, the torso/hip/guard defensive orientation should transform such that the box provides excellent full-body frontal protection, including the legs/feet.

When the player LOOKS DOWN, the defensive volume follows the torso/guard orientation in a way that can cause the lower edge of the protection to rotate upward/forward enough that the feet/lower legs become more exposed.

Therefore skilled players can optimize parry posture by looking upward appropriately.

Do not fake this with a boolean:

```text
if looking up:
    protect feet
```

Instead make it emerge from defensive geometry transformation.

Implement curves/functions such as:

```text
ViewPitch → DefensiveBoxPitch
ViewPitch → DefensiveBoxVerticalOffset
ViewPitch → DefensiveBoxForwardOffset
ViewPitch → torso/hip presentation pose
```

Tune the transform until the actual debug geometry demonstrates the desired behavior.

The box should rotate with defensive facing and therefore can be bypassed from the sides or rear.

---

# 20. EXTENDED PARRY CATCH REGION

In addition to the main box, implement a forward extended defensive region roughly shaped as a CONE or truncated cone/frustum.

This is an intentional "catch" region.

Conceptually:

```text
              ATTACKER

                  ↓

              /-------\
            /           \
          /   EXTENDED    \
        /      PARRY        \
       \      CATCH          /
         \     REGION       /
           \               /

              [PLAYER]
```

It projects forward from the defender's guard/aim direction.

Implement this mathematically if a physical cone collider is inconvenient:

Given a candidate incoming active weapon position or swept segment:

* calculate vector from guard origin
* test forward distance
* test dot product against guard forward vector
* compare angle to configurable cone half-angle
* account for weapon sweep through the region

Expose:

```text
ExtendedParryLength
ExtendedParryHalfAngle
ExtendedParryOrigin
```

This extended region exists specifically so a normal parry can "catch" manipulated swings more effectively than a chamber.

It should be generous enough that ordinary drags cannot trivially wrap around a well-aimed correctly-timed parry.

However, attacks from sufficiently far outside the player's defended frontal orientation must still be capable of bypassing it.

---

# 21. PARRY TURNCAP

Parry has its own turncap.

The defender cannot instantly flick the guard through an arbitrary angle after initiating parry.

Track:

```text
DesiredGuardOrientation
ActualGuardOrientation
```

Actual guard orientation approaches desired orientation subject to a configurable angular rate.

Both the main parry box and extended catch region use the ACTUAL guard orientation.

This makes parry aim meaningful.

After a successful parry, control may relax rapidly so target switching and riposte direction remain fluid.

Expose:

```text
ParryYawTurnRate
ParryPitchTurnRate
SuccessfulParryTurnRateModifier
```

---

# 22. CHAMBERS — CRITICAL DESIGN

Do NOT model a chamber as a normal parry.

Do NOT give chambers the extended parry cone.

Do NOT require literal sword-on-sword geometry as the central chamber criterion.

A chamber is better modeled as:

**a temporary angle-specific defensive protection state created by beginning a matching attack.**

The player throws an ordinary attack corresponding to the incoming attack angle.

During a short chamber window at the beginning of that attack, incoming attacks of the appropriate angle can be nullified/chambered.

Conceptually:

```text
Defender starts matching attack
        ↓
ChamberDefenseActive = true
        ↓
incoming attack reaches defender
        ↓
Is its attack angle within tolerance?
        ↓
YES → chamber
NO  → normal hit/other defense
```

The chambering attack itself remains a completely ordinary attack.

This distinction matters enormously.

---

# 23. CHAMBER ANGULAR MATCHING

Strike chambers should use CONTINUOUS ANGULAR COMPARISON internally.

Do not merely compare:

```text
IncomingDirectionEnum == DefenderDirectionEnum
```

Each offensive strike must expose a continuous directional/attack-plane representation.

Compare the defender's selected attack direction against the incoming attack direction.

Use an angular tolerance.

Conceptually:

```text
AngularDifference =
    acos(dot(
        Normalize(IncomingAttackDirection),
        Normalize(DefensiveAttackDirection)
    ))
```

A chamber succeeds when:

```text
AngularDifference <= ChamberAngleTolerance
```

and timing is valid.

Be careful about the orientation convention so "matching" represents the correct corresponding attack angle rather than the physically opposite world vector.

Test every attack pairing.

The six current attack sectors are merely quantized samples of an underlying continuous angular space.

This is another reason the architecture must remain 240-friendly.

For stabs:

A stab can chamber another stab based primarily on timing rather than six-direction strike-angle matching.

Expose strike chamber angular tolerance.

Start with a reasonably forgiving value, playtest it, and tune it.

---

# 24. CHAMBER TIMING AND WHY DRAGS BEAT CHAMBERS

The chamber protection window should be short.

A reasonable initial range for strike chambers is approximately:

```text
~200-250 ms
```

Tune it.

The exact number matters less than the resulting interaction:

A correctly timed ordinary strike should be chamberable.

An accel should be chamberable if the defender predicts/times it correctly.

A sufficiently delayed drag should cause the incoming blade to arrive AFTER the chamber protection window has expired.

Therefore even a small microdrag can defeat a chamber attempt.

THIS IS INTENTIONAL.

The chamber has:

```text
angle-specific protection
+
short temporal window
+
NO extended parry catch region
```

A normal parry has:

```text
large body-covering box
+
extended catch region
+
its own temporal window
```

That asymmetry is fundamental to the combat design.

Do not add a special:

```text
if AttackIsDrag:
    ChamberFails
```

It should emerge from timing.

---

# 25. CHAMBERS COUNTER FEINTS NATURALLY

A chamber attempt is an ATTACK.

Suppose the attacker begins a Right Horizontal strike.

The defender responds by beginning the appropriate Right Horizontal chamber attempt.

If the attacker FEINTS:

The defender's attack remains active.

The defender can simply commit to it and hit the attacker, forcing the original attacker to defend.

Therefore chambers naturally punish feints.

No bespoke "feint counter" flag is required.

This interaction is a cornerstone of the combat mindgame.

---

# 26. FEINTING A CHAMBER

Because a chamber is just an ordinary attack with a temporary chamber-defense window, it can be feinted exactly like any other attack.

There must be NO bespoke "Chamber Feint to Parry" action or state.

The generic rules are sufficient:

```text
chamber attempt
=
ordinary attack

ordinary attack can be feinted

feint returns player to neutral

neutral can parry immediately
```

Therefore a player can naturally perform:

```text
attempt chamber
→ realize attack is being dragged
→ Q / feint
→ neutral
→ RMB / parry
```

This should work automatically because of the state machine.

Do not create a special CHFTP implementation.

---

# 27. FEINTS

Q during a legal windup feints the attack.

Feints should be available late enough in windup to produce meaningful reads.

A good starting design is:

```text
Feint available until approximately the last 50 ms of windup.
```

Expose this.

On feint:

* attack can no longer release
* gameplay returns to neutral immediately or almost immediately
* visual weapon smoothly returns from the canceled pose
* player can immediately initiate a parry
* stamina cost may apply

Gameplay neutrality must not wait for a long cosmetic weapon-return animation.

Visual recovery and gameplay state may be separated carefully so controls stay responsive.

Feints themselves should look readable enough from third person/training-dummy perspective to avoid pure invisible state switching.

---

# 28. MORPHS

Allow attack type transitions during the appropriate portion of windup.

Core morph:

```text
Strike → Stab
Stab → Directional Strike
```

When morphing:

* cancel the original final release
* transition through a believable weapon path
* add/replace windup timing so the morph meaningfully changes impact timing
* preserve enough visual readability that an attentive defender can react
* charge stamina if stamina system is enabled

Morph eligibility should end earlier than the absolute final moment of the attack.

Expose:

```text
MorphWindow
MorphAdditionalWindup
MorphCost
```

Architect the morph system as state transition data rather than per-direction hacks.

---

# 29. COMBOS

Allow a new attack to be buffered during an appropriate portion of release/end-of-release.

If queued in the valid combo window:

```text
Current Release
→ Combo Transition
→ Next Attack Windup
```

This should bypass a substantial portion of ordinary miss recovery.

Direction may change.

The next attack may be another strike or valid stab depending on rules.

Expose combo input/buffer windows.

Input buffering must make combos feel dependable rather than requiring frame-perfect clicks.

---

# 30. PARRY AND RIPOSTE

When a defender successfully parries an attack, open a short riposte input window.

If the defender attacks within that window:

```text
Successful Parry
→ Riposte Windup
→ Release
```

The riposte should feel fast, decisive, and initiative-granting without becoming an unavoidable instant attack.

Direction selection remains available.

Do not hard-code one riposte direction.

Give successful parry strong audiovisual feedback.

Exact riposte timing should be tunable separately from ordinary attacks.

---

# 31. OPTIONAL CLASHES

After the core system is working reliably, implement a minimal clash if it can be done without destabilizing higher-priority mechanics.

If two attacks are BOTH in valid offensive release and their weapon sweep geometry genuinely intersects, a clash may occur.

A clash should:

* prevent phantom pass-through
* play a strong metallic response
* alter/cancel attack states predictably

Do not spend excessive time on clashes before:

* attacks
* drags
* accels
* parries
* chambers
* feints
* morphs
* combos
* movement

all work correctly.

---

# 32. MOVEMENT

Generic FPS movement is insufficient.

Movement is part of melee combat.

Create a custom melee movement component based on CharacterMovementComponent.

Movement should feel:

* responsive
* grounded
* predictable
* controllable
* slightly weighty
* never floaty or delayed

Implement:

```text
walking/combat movement
sprint
lateral movement
backward movement
jump
crouch
air control
landing
```

Tune forward/lateral/backward speeds independently where useful.

Do not attempt realistic human locomotion.

Gameplay responsiveness matters more than biomechanical realism.

---

# 33. MOVEMENT MOMENTUM

Implement persistent horizontal locomotion momentum.

Represent a normalized state approximately:

```text
Momentum01 = 0.0 ... 1.0
```

Momentum builds when the player moves consistently.

It contributes to sustainable movement/sprint speed.

Sudden large changes in movement direction destroy momentum.

Do NOT punish the player simply for freely looking around while continuing in roughly the same movement direction.

The primary comparison should involve:

```text
current horizontal velocity direction
versus
desired horizontal movement direction
```

and/or rate at which locomotion direction is being redirected.

A player sprinting forward who rotates the camera slightly while maintaining a coherent path should preserve momentum.

A player instantly reversing direction should lose substantial momentum.

---

# 34. MOVEMENT TURN PENALTY

Use a SOFT turn threshold and a HARD turn region rather than a binary speed switch.

Conceptually:

```text
small direction change
→ negligible penalty

moderate rapid turn
→ gradual momentum loss

hard turn
→ strong momentum loss

instant reversal
→ severe momentum loss
```

Use a continuous curve.

Initial conceptual thresholds might look something like:

```text
Below ~80-100 degrees/sec:
minimal loss

~100-160:
progressively increasing loss

~160-220:
heavy loss

Very large reversals:
severe loss
```

These are placeholders.

Tune them while playing.

The resulting velocity should bend/slow naturally rather than teleporting to zero.

Avoid the feeling of ice skating.

Expose all momentum parameters.

---

# 35. ATTACK LUNGE

Attack lunge is required.

When an attack transitions from windup into release, forward commitment can create a short controlled lunge.

This is a VELOCITY/ACCELERATION phenomenon, not target magnetism.

Never snap the player toward the enemy.

Never make lunge depend on whether a target exists.

Model:

```text
Windup → Release
        ↓
short lunge acceleration curve
```

Lunge should interact with current movement momentum.

A moving forward attacker should obtain useful reach.

A stationary/backpedaling attacker should not receive the exact same displacement as somebody sprinting into the attack unless tuning intentionally dictates it.

Start with a maximum displacement around roughly 0.7-1.1 meters for a fully realized favorable lunge, then PLAYTEST rather than blindly preserving the number.

Use collision-safe CharacterMovement behavior.

Expose:

```text
LungeStrength
LungeDuration
LungeForwardInputRequirement
LungeMomentumContribution
MaxLungeDisplacement
```

Spacing must remain a skill.

---

# 36. CAMERA AND BODY ORIENTATION

Use separate concepts for:

```text
Player desired view orientation
Combat orientation
Character/body orientation
Guard orientation
Weapon gameplay orientation
Weapon visual orientation
```

They may normally track each other closely, but separating them allows:

* attack turncaps
* parry turncaps
* body twist
* first-person weapon smoothing
* future third-person readability

Do not add huge delayed camera inertia.

The camera should remain responsive.

During states with turncaps, restrict permitted angular movement cleanly.

---

# 37. FIRST-PERSON WEAPON PRESENTATION

The authoritative weapon pose is mechanical.

The rendered weapon/arms should follow it convincingly.

Add subtle presentation effects where useful:

* tiny rotational lag
* tiny translational inertia
* procedural breathing when idle
* locomotion sway
* attack anticipation
* impact kick
* parry recoil
* chamber recoil
* footstep movement

Do not allow presentation lag to become large enough that a hit visually appears incorrect.

Use IK or procedural arm positioning where possible.

If template arms are available, use them.

Do not make arm-animation perfection a blocker for combat functionality.

---

# 38. HIT RESPONSE

Hits need immediate satisfying feedback.

Implement an initial lightweight feedback stack:

```text
clear impact sound
small directional camera impulse
weapon impact/recoil response
brief local presentation emphasis
visible hit effect
clear dummy reaction
```

Avoid giant camera shake.

Avoid global time dilation.

If using "hitstop," implement it as a very brief local presentation/weapon-response effect rather than pausing the entire game's simulation.

The combat simulation should continue consistently.

Differentiate sounds for at least:

```text
body hit
parry
chamber
wall/environment impact
```

If suitable audio assets are not readily available, generate simple legal placeholder WAVs programmatically or use permitted engine/template content rather than spending large amounts of time asset hunting.

The feedback must be functional and readable even if placeholder-quality.

---

# 39. DAMAGE

Keep damage simple in this prototype.

Use roughly:

```text
100 health
```

A longsword should require a small number of committed hits to kill a normal target.

If mannequin bones/hitboxes make it straightforward, allow broad:

```text
head
torso
legs
```

damage multipliers.

Do not waste time implementing detailed armor, limb severing, weapon-tip modifiers, material penetration, or sophisticated damage falloff.

Remember:

No differentiation between different locations ALONG THE SWORD.

---

# 40. FLINCH

A successful damaging melee hit should interrupt an opponent who is currently winding up or otherwise in an interruptible offensive state.

This is necessary to preserve initiative.

Riposte/chamber-specific exceptions may eventually exist, but keep the first implementation straightforward and data-driven.

A flinched attack must be clearly canceled.

Do not allow two players to routinely swing through direct hits simply because both clicked.

---

# 41. STAMINA

Implement a simple data-driven stamina component if it can be done without compromising core development.

Initial maximum:

```text
100 stamina
```

Potential stamina costs:

```text
Feint        ~10
Morph        ~7
Chamber      ~15
Miss         ~8
Parry        configurable based on incoming attack
```

These are initial values only.

Stamina should regenerate after a short combat delay.

For the Combat Lab, provide a debug toggle for:

```text
Infinite Stamina ON/OFF
```

Do not spend substantial time on disarming or sophisticated stamina balance in this pass.

The stamina architecture should exist primarily so feint/chamber/morph spam can later be economically balanced.

---

# 42. TRAINING DUMMY — HIGH PRIORITY

A programmable attack dummy is more important than sophisticated enemy AI.

Create a training target capable of deterministic attacks.

It should support modes such as:

```text
Passive

Repeated Right Horizontal

Repeated Left Horizontal

Repeated Upper attacks

Repeated Lower attacks

Repeated Stabs

Alternating directions

Accel test

Drag test

Microdrag test

Feint test

Morph test

Mixed test
```

Expose attack interval.

Allow it to face the player.

Allow resetting position/health.

For drag/accel test patterns, deliberately alter dummy orientation during release using the same legitimate combat turncap rules rather than secretly changing attack speed.

This dummy will let the human developer rapidly test:

* parry timing
* parry geometry
* chamber timing
* chamber angular tolerance
* microdrag behavior
* feint reads
* morph reads
* footwork
* ripostes

A sophisticated NavMesh combat AI is optional and LOWER PRIORITY.

---

# 43. COMBAT DEBUG MODE

Implement a powerful debug mode toggled with approximately:

```text
F3
```

Display real-time values including:

```text
Combat State
Attack Type
Attack Direction
Raw Input Angle
Attack Phase
Windup remaining
Release progress
Recovery remaining

Weapon world speed
Weapon angular speed

Current yaw turncap
Current pitch turncap
Mouse delta

Parry active
Parry time remaining
Guard orientation
Parry turncap

Chamber defense active
Chamber time remaining
Selected chamber angle
Incoming attack angle
Angular difference
Chamber tolerance

Combo available
Feint available
Morph available
Riposte available

Movement speed
Momentum01
Movement turn rate
Momentum loss

Lunge active
Lunge velocity contribution

Last combat resolution:
HIT / PARRY / CHAMBER / MISS / WALL / CLASH
```

Use debug drawing to visualize:

* weapon previous position
* weapon current position
* weapon swept trajectory
* damaging trajectory
* non-damaging early/late trajectory
* character hurt volume
* main parry box
* extended parry cone
* guard forward direction
* chamber active indicator
* attack angle vectors
* impact/contact point
* movement velocity
* desired movement direction

Use different debug colors if practical.

Debug visualization must correspond to ACTUAL gameplay geometry, not approximations.

---

# 44. LIVE TUNING PANEL

Implement a live combat tuning panel, approximately:

```text
F4
```

It should allow editing combat values while running whenever practical.

At minimum expose:

## STRIKE

```text
Windup
Release
Recovery
Combo timing
Damage-window start
Damage-window end
Feint lockout
Morph window
```

## SWING MANIPULATION

```text
Windup turncap
Early release turncap
Mid release turncap
Late release turncap
Pitch turncap
Anti-spin threshold
```

## PARRY

```text
Active duration
Recovery
Main box width
Main box height
Main box depth
Main box forward offset
Main box vertical offset

Extended cone length
Extended cone half-angle

Parry yaw turn rate
Parry pitch turn rate

ViewPitch→BoxPitch influence
ViewPitch→BoxZ influence
```

## CHAMBER

```text
Chamber active duration
Strike angular tolerance
Stab chamber tolerance/rules
Chamber stamina cost
```

## MOVEMENT

```text
Forward speed
Lateral speed
Backward speed
Sprint speed

Acceleration
Deceleration

Momentum build rate
Momentum loss
Soft turn threshold
Hard turn threshold
Reverse penalty
```

## LUNGE

```text
Strength
Duration
Maximum displacement
Momentum scaling
```

## PRESENTATION

```text
Weapon visual lag
Weapon visual spring
Camera hit impulse
Parry recoil
Chamber recoil
Hit emphasis
FOV
```

Provide:

```text
RESET
SAVE
LOAD
```

Save tuning to a simple human-readable format such as JSON under an appropriate Saved/Config location.

Provide an editor/development way to promote a tuned configuration to new defaults.

Sane defaults must exist even if the tuning file is missing.

---

# 45. DATA-DRIVEN DESIGN

Do not bury critical tuning numbers throughout C++.

Create coherent data structures for:

```text
AttackDefinition
WeaponDefinition
DefenseTuning
MovementTuning
CombatPresentationTuning
```

Use Unreal data assets where reliable, but maintain code/default fallbacks and/or human-readable configuration so the project is not dependent on fragile binary asset generation.

Every timing and geometry value likely to require playtesting should be centralized.

---

# 46. FRAME-RATE INDEPENDENCE

Combat correctness must not depend on frame rate.

Attack phase advancement uses DeltaSeconds.

Swept collision spans previous to current weapon pose.

Substep large angular/positional movement.

Movement momentum uses time-based rates.

Parry and chamber windows use actual elapsed simulation time.

Create automated or scripted tests at multiple effective frame rates where practical.

An attack should not become significantly faster, slower, easier to chamber, or more likely to tunnel merely because the game runs at 30 FPS instead of 144 FPS.

---

# 47. FUTURE MULTIPLAYER ARCHITECTURE

Do NOT implement networking now.

However, avoid architectural decisions that would make server-authoritative multiplayer impossible.

Keep clear boundaries between:

```text
input intent
combat state
authoritative attack simulation
combat resolution
visual presentation
```

Combat events should be represented cleanly enough that future networking can replicate/reconcile:

```text
attack start
attack direction
feint
morph
parry
chamber
hit
movement state
```

Do not use global time dilation for combat effects.

Do not make core combat depend on client-only animation state.

Do not implement actual rollback/prediction yet.

---

# 48. POLISH PRIORITY

After all mechanics work, spend remaining development effort primarily on making these actions feel excellent:

```text
mouse look
movement acceleration
sprinting
stopping
direction changes

attack startup
weapon arc
accel
drag
lunge

successful body hit

parry
parry recoil
riposte

chamber

feint
morph
combo
```

A beautiful main menu is worthless compared with another meaningful combat-polish pass.

---

# 49. THINGS YOU MUST NOT DO

Do not substitute implementation with a design document.

Do not stop after scaffolding.

Do not create only pseudocode.

Do not make the sword collision a single raycast fired by an animation notify.

Do not make attack animation authoritative.

Do not use root motion as the combat authority.

Do not implement lock-on.

Do not implement melee aim assist.

Do not magnetize attacks to opponents.

Do not artificially change attack playback speed to create accels and drags.

Do not give chambers the extended parry cone.

Do not create a bespoke CHFTP mechanic.

Do not differentiate tip/middle/base sword gameplay.

Do not implement 240 selection yet.

Do not make six discrete directions impossible to replace with continuous directions later.

Do not implement multiplayer yet.

Do not spend time on inventory systems.

Do not build progression.

Do not build matchmaking.

Do not build cosmetics.

Do not build elaborate menus.

Do not source expensive art packs.

Do not copy Mordhau or Chivalry code/assets.

Do not hide important tuning values inside random source files.

Do not claim something works merely because it compiles.

---

# 50. DEVELOPMENT ORDER

Work continuously through the entire task without asking for approval between stages.

Use approximately this implementation order:

```text
1. Inspect environment and Unreal installation/tooling.

2. Create/initialize UE 5.8 C++ project.

3. Establish buildable modular source architecture.

4. Create Combat Lab and first-person character.

5. Implement responsive movement.

6. Implement procedural longsword pose/trajectory system.

7. Implement attack state machine.

8. Implement six-direction input resolver + stab.

9. Implement continuous swept weapon collision.

10. Implement damage/flinch.

11. Implement accels/drags through world-space orientation.

12. Implement attack turncaps.

13. Implement movement momentum and turn penalties.

14. Implement lunge.

15. Implement main parry box.

16. Implement pitch-dependent parry coverage.

17. Implement extended parry cone.

18. Implement parry turncap.

19. Implement angular/timed chamber defense.

20. Verify microdrags beat chambers more readily than parries.

21. Implement feints.

22. Verify chamber attempts can be feinted generically.

23. Implement morphs.

24. Implement combos.

25. Implement ripostes.

26. Implement stamina if appropriate.

27. Implement programmable training dummy.

28. Implement debug visualization/HUD.

29. Implement live tuning panel.

30. Add hit/parry/chamber audiovisual feedback.

31. Add first-person procedural/IK presentation polish.

32. Add automated tests.

33. Compile.

34. Launch.

35. Playtest.

36. Fix.

37. Playtest again.

38. Tune combat.

39. Verify every acceptance criterion.

40. Write concise README and final report.
```

This is an execution sequence, not a request to stop after each phase.

---

# 51. AUTOMATED / PROGRAMMATIC TESTS

Create tests where they add real confidence.

Important cases include:

### STATE MACHINE

Verify:

```text
Idle → Windup → Release → Recovery → Idle

Windup → Feint → Neutral

Windup → Morph

Release → Combo

Successful Parry → Riposte
```

### CHAMBERS

Verify:

```text
matching horizontal angle inside tolerance succeeds

angle outside tolerance fails

correct angle outside chamber time fails

stab chambers stab

strike does not chamber stab

chamber attack can be feinted

feint returns neutral

parry is immediately possible after feint
```

### PARRY

Verify:

```text
front attack inside active time blocks

attack after active time does not block

rear attack is not magically blocked

extended cone catches intended forward attacks

parry guard turncap is enforced

view pitch actually changes lower-body parry coverage
```

### SWING MANIPULATION

Verify:

```text
turning into release advances world-space contact time

turning away delays world-space contact time

attack duration itself remains logically consistent

extreme rotation triggers anti-spin protection
```

### FRAME RATE

Run representative attack/collision simulations with coarse and fine timesteps and ensure outcomes remain equivalent within a small tolerance.

---

# 52. MANUAL PLAYTEST SCENARIOS YOU MUST EXECUTE

Use PIE or the built executable and actually exercise these situations.

### TEST A — BASIC SWING

Stand at proper range.

Perform all six strikes and stab.

Verify:

* each begins from correct side
* paths look coherent
* contact matches sword
* no obvious clipping-through-target
* hit feedback is immediate

### TEST B — ACCEL

Place dummy near attack path.

Perform Right Horizontal.

Rotate into the swing.

Verify contact happens noticeably earlier in world space without modifying the attack timer artificially.

### TEST C — DRAG

Repeat but rotate away from the swing.

Verify contact can happen significantly later.

### TEST D — PARRY

Have dummy repeatedly attack.

Parry late enough to block.

Verify the main box visibly corresponds to successful defense.

### TEST E — PARRY PITCH

Enable parry debug geometry.

Look upward and parry.

Verify the transformed box covers the full frontal body/feet well.

Look downward and parry.

Verify lower protection shifts so feet/lower legs can become more vulnerable.

Do not merely assume the transform works.

### TEST F — EXTENDED PARRY

Use a manipulated incoming attack.

Verify the forward cone can catch an active attack that would be considerably harder to defend using only body-box intersection.

### TEST G — CHAMBER

Set dummy to predictable Right Horizontal attacks.

Perform matching chamber.

Verify successful protection.

Attempt the wrong attack angle.

Verify failure.

### TEST H — MICRODRAG VS CHAMBER

Configure dummy to perform a small legal drag.

Attempt a chamber at accel/normal timing.

Verify the delayed attack can arrive after the chamber window and hit.

### TEST I — MICRODRAG VS PARRY

Perform a correctly timed normal parry against the same manipulated attack.

Verify the extended catch geometry makes the ordinary parry substantially more robust than the chamber.

This relationship is REQUIRED.

### TEST J — FEINT VS PARRY

Have dummy feint.

Verify an early parry can be baited and punished by recovery.

### TEST K — CHAMBER VS FEINT

Dummy begins an attack and feints.

Begin the correct chamber attempt.

Because your chamber attempt is itself a real attack, verify it continues and threatens the feinting attacker.

### TEST L — FEINT CHAMBER ATTEMPT INTO PARRY

Begin a chamber attempt.

Feint with Q.

Immediately parry with RMB.

Verify this works through generic state rules with no special CHFTP code.

### TEST M — MOVEMENT MOMENTUM

Sprint in one direction.

Maintain direction and verify momentum builds.

Make a gentle curve and verify most momentum remains.

Perform an abrupt reversal and verify speed/momentum falls.

Verify normal camera look does not arbitrarily destroy locomotion momentum.

### TEST N — LUNGE

Attack while moving forward.

Verify a controlled velocity-based lunge improves reach.

Attack backward/stationary.

Verify behavior differs appropriately and there is no target magnetism.

---

# 53. INITIAL SUCCESS CRITERIA

Do not consider the task complete until all of these are true:

The project builds without compilation errors.

The project launches.

The Combat Lab opens.

The player can move, sprint, crouch, jump, and look smoothly.

The player can attack from six strike directions.

The player can stab.

Attacks have distinct windup, release, and recovery.

The weapon path is mechanically authoritative.

Collision tracks the moving weapon continuously.

Attacks work at different frame rates without obvious tunneling.

Accels occur through spatial rotation.

Drags occur through spatial rotation.

Attack release turncaps prevent pathological spinning.

Lunge works without target magnetism.

Movement momentum exists.

Sharp movement turns reduce momentum.

Normal look movement does not arbitrarily kill momentum.

Parry has a large main body-covering box.

Parry coverage meaningfully changes with view pitch.

Looking upward creates strong full-body frontal coverage.

Looking downward can expose lower body/feet.

Parry has a separate extended forward catch cone.

Parry orientation has its own turncap.

Chambers are timed angle-specific defense attached to ordinary attacks.

Chambers have no extended cone.

Correct attack angle chambers.

Incorrect angle does not.

Small legal drags can defeat chamber timing.

Normal parry is more robust against those drags.

Chambers naturally punish feints.

Any chamber attempt can be generically feinted.

Feint returns the player to neutral.

Parry can immediately follow a feint.

No special CHFTP state exists.

Morphs work.

Combos work.

Ripostes work.

Hits flinch interruptible opponents.

Training dummy can produce repeatable scenarios.

Debug visualization displays ACTUAL attack/parry/chamber geometry.

Live tuning controls work.

Tuning can be saved.

Hits feel meaningfully satisfying.

Parries feel strong and immediate.

Chambers are clearly recognizable.

The game is sufficiently stable to hand to a human for actual combat-feel tuning.

---

# 54. POLISH PASS

Once everything above works, do not immediately stop.

Perform one deliberate combat polish pass.

Focus on:

* input latency
* mouse responsiveness
* weapon arc continuity
* visual/contact synchronization
* attack anticipation
* release readability
* accel potential
* drag potential
* parry timing
* parry recoil
* chamber feedback
* movement acceleration
* movement direction changes
* lunge strength
* hit sound timing
* camera impulse
* viewmodel spring
* dummy readability

Use your own testing observations to adjust obviously poor defaults.

Do not aggressively tune away depth merely because one mechanic initially appears exploitable. Prefer controlled turncaps and time windows over removing player control.

---

# 55. CODE QUALITY

Use modern idiomatic Unreal C++.

Use:

* Unreal reflection appropriately
* `UPROPERTY` / `UFUNCTION` where needed
* correct ownership/lifetime patterns
* weak references where appropriate
* const correctness
* clear types
* descriptive names
* minimal unnecessary Tick usage
* event-driven behavior where practical
* debug-only code guarded appropriately for shipping later

Avoid premature optimization, but instrument the weapon trace subsystem sufficiently to detect pathological cost.

Document the non-obvious mathematics and state-machine invariants.

Do not fill files with commentary explaining trivial C++.

---

# 56. README

At completion, create a useful concise README containing:

```text
Project purpose

Required Unreal Engine version

How to build

How to launch

Controls

Combat mechanics

Debug controls

Tuning controls

Architecture overview

Where combat timing data lives

Where movement tuning lives

How six-direction selection can later become 240

Current known limitations

Recommended next steps toward multiplayer
```

Include the exact keys for debug/tuning modes.

---

# 57. FINAL REPORT

Only AFTER implementation, compilation, launch, testing, and repairs are complete, give me a concise final report.

Report:

```text
What you built

Where the project is located

How to launch it

Important controls

Which acceptance tests passed

Any remaining known defects

Any mechanic whose exact feel still requires human tuning

The five or so parameters I should tune first after playing it
```

Do not bury known failures.

If something could not be completed despite serious attempts, state exactly what failed, why, and leave the rest of the project in the most functional state possible.

---

# 58. FINAL DESIGN PRINCIPLES

When uncertain, preserve these principles above everything else:

**Combat simulation owns the weapon.**

**Animation follows combat.**

**What you see should agree with what can hit you.**

**Player rotation physically manipulates swing timing.**

**Accels and drags are spatial rather than playback-speed tricks.**

**Parry is a generous spatial defense with a main box and extended catch region.**

**Chamber is a short angle-specific defensive window attached to an ordinary attack.**

**Chamber has no extended catch region.**

**Therefore drags naturally threaten chambers more than parries.**

**Chambers naturally punish feints because the chamber attempt remains an attack.**

**A chamber can be feinted because every ordinary attack can be feinted.**

**Feint returns to neutral, and neutral may parry immediately.**

**Six attack sectors are temporary; the underlying representation remains continuous-angle friendly.**

**Movement and footwork alter combat timing.**

**Lunge increases commitment/reach without target magnetism.**

**Sharp locomotion turns destroy momentum rather than allowing instantaneous full-speed reversals.**

**Turncaps constrain pathological manipulation without removing meaningful manipulation.**

**Every important balance value is tunable.**

**Debug geometry represents the real mechanics.**

**Combat feel is more important than feature count.**

**A small Combat Lab that feels excellent is preferable to a large game that feels mediocre.**

Now take ownership of the project and build it from beginning to end.
