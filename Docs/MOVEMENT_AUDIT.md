# Locomotion Audit — September 6, 2026

## What made the previous movement feel prototype-level

1. **The scalar momentum model was not body momentum.** CharacterMovement solved velocity with its stock acceleration/friction model; a separate 0..1 scalar only influenced sprint and lunge. The player therefore had two unrelated notions of momentum.

2. **Sprint depended on historical scalar state instead of one coherent gait transition.** A player who had already built the scalar could enter sprint differently from a player issuing the same current input from another history.

3. **Attack movement was layered after ordinary locomotion.** Lunge removed the previous additive term, asked stock CharacterMovement for base velocity, then added a new positive-only release velocity. Because the candidate was rejected if it made the player slower, attack movement could not participate in braking, reversals, or the same physical law as normal footwork.

4. **Directional speed and response were separate concerns.** Forward/lateral/backward caps existed, but acceleration, braking and redirection were generic stock-vector behavior. There was no explicit contract for A/D reversals, W/S reversals, circle-strafe redirection, precision taps, or sprint disengagement.

5. **Stopping was dominated by stock friction + braking.** That can be tuned to a number, but it does not express the desired authored distinction between ordinary braking, high-speed sprint braking, redirection and hard reversal.

6. **Combat states barely participated in locomotion.** Ordinary movement was deliberately preserved through attacks and lunge was purely additive. This protected agency, but it also made weapon commitment and body commitment feel disconnected.

7. **Validation was coupled to implementation details.** The rendered movement case checked `Momentum.value` and `Lunge.displacement`, rather than player-facing outcomes such as reversal response or sprint-to-combat behavior.

8. **Documentation had drifted.** README movement values no longer matched the checked-in tuning registry.

## Approaches considered

| Approach | Intent | Mass | Footwork | Stops/reversals | Combat integration | Risk |
|---|---:|---:|---:|---:|---:|---|
| Retuned stock CharacterMovement | Excellent | Fair | Good | Fair | Fair | Low |
| Critically damped target-velocity spring | Good | Excellent | Fair | Good | Good | Medium |
| Projected longitudinal/lateral momentum | Good | Excellent | Good | Good | Excellent | High |
| **Immediate intent + bounded body-velocity solver** | **Excellent** | **Excellent** | **Excellent** | **Excellent** | **Excellent** | **Medium-low** |

### 1. Retuned stock CharacterMovement

Keep stock `CalcVelocity`, adjust acceleration/friction/braking and directional `GetMaxSpeed`.

**Why it lost:** smallest code change, but it still leaves the core feel implicit inside a generic locomotion solver. It cannot cleanly distinguish precision acceleration, redirection, true reversal, sprint braking and combat target-speed changes without accumulating overrides around the stock model.

### 2. Critically damped target-velocity spring

Treat desired velocity as a spring target and solve a second-order response.

**Why it lost:** excellent mass and smoothness, but a spring introduces a continuous lag/error state precisely where competitive footwork needs explicit stop and reversal guarantees. It is also easier to make small corrections feel syrupy and harder to express deterministic stopping-distance expectations.

### 3. Projected longitudinal/lateral momentum

Decompose velocity onto current intent or body axes and preserve/bleed components independently.

**Why it lost:** powerful for surf-like or highly momentum-driven movement, but it can preserve tangential velocity too strongly during camera turns and produce ice-skating. It also creates more policy questions around basis changes than this prototype needs.

### 4. Immediate intent + bounded body-velocity solver — selected

Input establishes a target velocity immediately. Actual planar velocity moves toward that target with an acceleration budget selected from the current physical situation.

**Why it won:** it creates the intended split directly:

`immediate player intent + physical velocity response`

without filtering input. The acceleration budget can be stronger for low-speed precision, redirection and true reversals while ordinary travel remains weighty. Sprint and combat become target-velocity states inside the same law. Attack movement no longer bypasses braking/collision with an additive impulse.

## Default feel targets

- Forward: 360 cm/s
- Lateral: 315 cm/s
- Backward: 255 cm/s
- Sprint: 560 cm/s
- Forward start to ~90% target: ~100 ms
- Hard reversal crosses zero: ~65–75 ms
- Sprint release stop: roughly 34–36 cm under the 120 Hz movement substep contract
- Release drive: small forward-intent-only speed bias; roughly single-digit centimeters of extra release translation at defaults

These are starting points for human playtesting, not balance constants.
