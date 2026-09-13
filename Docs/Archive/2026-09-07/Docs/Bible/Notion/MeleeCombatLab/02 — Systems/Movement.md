> Archived 7 September 2026. Historical evidence and instructions; use [the current development plan](../../../../../../../DEVELOPMENT.md) for active work.

# Movement


Current movement uses an engine-independent locomotion law applied through a custom CharacterMovement component. Input intent is immediate; acceleration, braking, redirect, and reversal resolve planar velocity. Unreal handles collision, floors, stepping, slopes, jumping, and actual translation. Combat consumes that translation. [D2]

Forward, lateral, and backward targets differ; mixed directions use an elliptical envelope to avoid a diagonal speed bonus. Sprint is a request gated by forward intent, grounded state, crouch, and neutral combat. Entering combat lowers the target without an instantaneous velocity reset or animation lock. Phase modifiers scale travel targets while retaining steering. [D2]

The later kinetic pass expands the earlier modest forward-bias model: forward-input-dependent drive peaks early and ends partway through release; inherited forward momentum partially carries and decays; reversal stops drive. One controlled fixture recorded about 17.1 cm extra displacement. That is a fixture result, not every attack's travel distance. [D3]

The movement contract's earlier release-bias prose and the original 0.7–1.1 m speculative lunge should not override the later implementation. Review source/config and actual exchanges before selecting a new distance. [S1, D2, D3]

Open: crouch acceleration, high-skill reversal balance, air-control exploits, sprint stopping feel, and networking saved-move/prediction support. These are playtest and future implementation questions, not verified deficiencies. [D2]



[Source register](../Sources.md)
