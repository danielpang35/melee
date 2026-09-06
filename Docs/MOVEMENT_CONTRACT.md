# Grounded Movement Contract

## Design goal

Locomotion must communicate input intent immediately while allowing horizontal body velocity to respond over time. The player controls where the body is trying to go on the current frame; the controller owns how an armored body gets there.

This system is intentionally not an animation controller. Camera, weapon presentation, footsteps and body animation may consume its signals later, but they must not alter authoritative capsule velocity.

## Architecture

`mcl::LocomotionModel` is the engine-independent movement law. `UMeleeCharacterMovementComponent` supplies Unreal input/collision state, executes the planar result through CharacterMovement, and exposes presentation signals.

The model is stateless. Its complete authoritative inputs are:

- current planar velocity
- current movement intent
- character forward
- grounded/crouched/sprint-request state
- combat phase and normalized release progress
- delta time
- `mcl::Tuning`

The model outputs target-resolved planar velocity plus presentation telemetry. Unreal remains responsible for collision, floor finding, stepping, slopes, depenetration, jump/fall movement and final actor translation.

## Core movement law

### Immediate intent, physical velocity

WASD intent is sampled every movement tick with no input smoothing. View yaw remains immediate. Horizontal velocity approaches a target under a bounded acceleration budget.

Acceleration authority is contextual:

- ordinary acceleration for sustained travel
- stronger precision acceleration below `PrecisionSpeedThreshold`
- stronger redirect acceleration when desired direction diverges from current velocity
- strongest reversal acceleration for true opposite-direction changes
- explicit deceleration when input is released or a lower gait target is entered

This is velocity inertia, not input latency.

### Directional speed envelope

Forward, lateral and backward speeds are separate axes. Mixed directions use an elliptical envelope, so W+D cannot gain a `sqrt(2)` speed bonus.

The directional caps are authoritative even when the camera turns. Fast circle-strafing therefore rotates intent immediately while velocity catches the new direction using redirect authority.

### Sprint

Shift requests sprint; it does not grant a speed multiplier directly.

Sprint is legal only when:
- grounded
- not crouched
- combat phase is neutral/idle
- local forward intent exceeds `SprintForwardRequirement`

The sprint target is strongest for straight-ahead input and fades toward ordinary directional speed near the forward requirement. Releasing W uses `SprintDeceleration`; releasing Shift or entering combat lowers the target and decelerates toward ordinary footwork instead of snapping speed.

Attacking therefore disengages sprint automatically without an animation lock.

### Combat footwork

Combat phases scale ordinary target velocity, not input:

- windup: small loss of travel speed
- release: stronger commitment
- recovery: modest commitment
- parry: modest commitment
- missed-parry recovery: stronger commitment
- flinch: substantial movement loss
- dead: zero target

The player keeps steering authority during these states. Reversal and redirect acceleration are still available; combat scaling changes the target, not whether movement input is accepted.

### Release drive

There is no additive lunge velocity and no attack that moves a stationary player for free.

During release, positive forward movement intent receives a small, front-loaded target-velocity bias. At default tuning this produces only footwork-scale extra displacement over the release, rather than a dash. Sideways, backward, and zero-input releases receive no forward injection.

This keeps attack spacing coupled to the same collision-resolved locomotion law used everywhere else.

### Frame-rate contract

CharacterMovement is configured for a maximum 1/120 s simulation step with up to eight iterations per frame. The pure movement law is time-based and contains no frame-count constants.

Very large hitches can still exceed that substep budget; that is an overload case, not a normal tuning target.

## Presentation signals

`FMovementPresentationSignals` exposes:

- `LocalVelocity` — cm/s in character forward/right/up axes
- `LocalAcceleration` — cm/s² in the same axes
- `BrakingIntensity` — normalized opposing acceleration
- `SpeedNormalized` — normalized gait speed
- `ReversalSeverity` — 0..1 opposite-direction demand
- `Gait` — idle, walk, sprint, crouch, airborne, disabled
- `CombatState` — neutral, windup, release, recovery, parry, parry recovery, flinch, dead
- `bGrounded`

Later camera/animation specialists should consume these signals instead of recomputing movement state from raw input.

## Collision and combat coupling

The capsule remains authoritative for world movement. `ACombatLabGameMode` continues to copy the post-movement actor position into `Combatant::frameTarget`; the 240 Hz combat simulation interpolates that collision-resolved translation through its fixed steps. Footwork therefore advances/delays actual blade contact naturally without special attack-time teleportation.

## Tuning order

Tune in this order:

1. `ForwardSpeed`, `LateralSpeed`, `BackwardSpeed`
2. `Acceleration`, `PrecisionAcceleration`
3. `Deceleration`, `SprintDeceleration`
4. `RedirectAcceleration`, `ReverseAcceleration`
5. `SprintSpeed`, `SprintForwardRequirement`
6. combat movement scales
7. `ReleaseForwardBias`

Do not tune `ReleaseForwardBias` to solve a range problem first. Weapon reach, attack trajectory, normal footwork and collision should establish spacing. Release drive is only the final physical punctuation.

## Remaining human-playtest questions

- Is ~35 cm of sprint stopping distance enough mass without harming defensive spacing?
- Is ~65–75 ms to cross zero on a hard reversal too strong for high-level A/D baiting?
- Does lateral speed need to come down relative to forward speed once real duel AI/player opposition exists?
- Should missed-parry recovery movement scale be harsher or should punishment come primarily from defense timing?
- Is the default release forward bias perceptible enough, or should it remain effectively invisible and only affect contact timing?
- Should crouch retain the same acceleration authority at its lower speed?
- Does jumping need a separate air-acceleration contract once bunny-hop/air-strafe exploits can be tested?
- Future multiplayer work must serialize sprint request and reproduce this solver in CharacterMovement prediction/saved moves; no networking contract is implemented here.
