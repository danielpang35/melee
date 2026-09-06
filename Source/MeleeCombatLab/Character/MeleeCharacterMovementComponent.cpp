#include "MeleeCharacterMovementComponent.h"
#include "MeleeCharacter.h"
#include "Combat/CombatComponent.h"

namespace
{
EMeleeGait ToUnrealGait(mcl::Gait Gait)
{
    switch(Gait){
    case mcl::Gait::Walk:return EMeleeGait::Walk;
    case mcl::Gait::Sprint:return EMeleeGait::Sprint;
    case mcl::Gait::Crouch:return EMeleeGait::Crouch;
    case mcl::Gait::Airborne:return EMeleeGait::Airborne;
    case mcl::Gait::Disabled:return EMeleeGait::Disabled;
    default:return EMeleeGait::Idle;
    }
}

EMeleeCombatMovementState ToUnrealCombatState(mcl::CombatMovementState State)
{
    switch(State){
    case mcl::CombatMovementState::Windup:return EMeleeCombatMovementState::Windup;
    case mcl::CombatMovementState::Release:return EMeleeCombatMovementState::Release;
    case mcl::CombatMovementState::Recovery:return EMeleeCombatMovementState::Recovery;
    case mcl::CombatMovementState::Parry:return EMeleeCombatMovementState::Parry;
    case mcl::CombatMovementState::ParryRecovery:return EMeleeCombatMovementState::ParryRecovery;
    case mcl::CombatMovementState::Flinch:return EMeleeCombatMovementState::Flinch;
    case mcl::CombatMovementState::Dead:return EMeleeCombatMovementState::Dead;
    default:return EMeleeCombatMovementState::Neutral;
    }
}
}

UMeleeCharacterMovementComponent::UMeleeCharacterMovementComponent()
{
    bOrientRotationToMovement=false;
    AirControl=.25f;
    JumpZVelocity=500.f;
    GroundFriction=8.f;
    BrakingFrictionFactor=1.f;
    MaxWalkSpeedCrouched=210.f;
    MaxSimulationTimeStep=static_cast<float>(mcl::LocomotionModel::MaxSimulationStep);
    MaxSimulationIterations=8;
    GetNavAgentPropertiesRef().bCanCrouch=true;
}

void UMeleeCharacterMovementComponent::ResetCombatMovement()
{
    StopMovementImmediately();
    InputIntent=FVector::ZeroVector;
    bSprintRequested=false;
    bSprint=false;
    ForwardInput=0;
    Momentum={};
    Lunge={};
    MovementSignals={};
}

float UMeleeCharacterMovementComponent::GetMaxSpeed() const
{
    const auto* C=Cast<AMeleeCharacter>(CharacterOwner);
    if(!C||!C->Combat)return Super::GetMaxSpeed();

    const auto& T=C->Combat->Tuning();
    const auto Phase=C->Combat->Simulation.state.phase;
    if(Phase==mcl::Phase::Dead)return 0;

    // The grounded solver owns the real directional cap. Return its absolute ceiling
    // here so CharacterMovement never clips the release bias after CalcVelocity.
    if(IsMovingOnGround()){
        return static_cast<float>(std::max({T.ForwardSpeed,T.LateralSpeed,T.BackwardSpeed,T.SprintSpeed})+
            T.ReleaseForwardBias);
    }

    const FVector Desired=Acceleration.GetSafeNormal2D();
    if(Desired.IsNearlyZero())return static_cast<float>(T.ForwardSpeed);
    const FVector Forward=C->GetActorForwardVector().GetSafeNormal2D();
    const mcl::Vec D{Desired.X,Desired.Y,0},F{Forward.X,Forward.Y,0};
    const mcl::Vec Local=mcl::LocomotionModel::local(D,F);
    double Speed=mcl::LocomotionModel::directionalSpeed(Local,T)*mcl::LocomotionModel::phaseScale(Phase,T);
    if((bSprintRequested||bSprint)&&Phase==mcl::Phase::Idle&&Local.x>=T.SprintForwardRequirement){
        const double Alpha=mcl::clamp((Local.x-T.SprintForwardRequirement)/
            std::max(1e-6,1.-T.SprintForwardRequirement),0.,1.);
        Speed=mcl::mix(Speed,T.SprintSpeed,Alpha);
    }
    if(IsCrouching())Speed*=T.CrouchMoveScale;
    return static_cast<float>(Speed);
}

void UMeleeCharacterMovementComponent::TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* TickFunction)
{
    InputIntent=GetPendingInputVector();
    InputIntent.Z=0;
    InputIntent=InputIntent.GetClampedToMaxSize(1.f);

    if(auto* C=Cast<AMeleeCharacter>(CharacterOwner);C&&C->Combat){
        const auto& T=C->Combat->Tuning();
        GravityScale=static_cast<float>(T.GravityScale);
        JumpZVelocity=static_cast<float>(T.JumpSpeed);
        MaxAcceleration=static_cast<float>(T.PrecisionAcceleration);
        BrakingDecelerationWalking=static_cast<float>(T.Deceleration);
        MaxWalkSpeedCrouched=static_cast<float>(T.ForwardSpeed*T.CrouchMoveScale);
    }
    Super::TickComponent(Dt,TickType,TickFunction);
}

void UMeleeCharacterMovementComponent::CalcVelocity(float Dt,float Friction,bool bFluid,float Braking)
{
    const FVector PreviousVelocity=Velocity;
    auto* C=Cast<AMeleeCharacter>(CharacterOwner);
    if(Dt<=SMALL_NUMBER||!C||!C->Combat||!IsMovingOnGround()){
        Super::CalcVelocity(Dt,Friction,bFluid,Braking);
        UpdateFallbackSignals(PreviousVelocity,Dt);
        return;
    }

    const auto& T=C->Combat->Tuning();
    const auto& State=C->Combat->Simulation.state;
    const FVector Forward=C->GetActorForwardVector().GetSafeNormal2D();

    mcl::LocomotionInput In;
    In.velocity={Velocity.X,Velocity.Y,Velocity.Z};
    In.intent={InputIntent.X,InputIntent.Y,0};
    In.forward={Forward.X,Forward.Y,0};
    In.dt=Dt;
    In.attackProgress=State.phase==mcl::Phase::Release?State.progress():0;
    In.sprintRequested=bSprintRequested||bSprint;
    In.crouched=IsCrouching();
    In.grounded=true;
    In.phase=State.phase;

    const auto Out=mcl::LocomotionModel::step(In,T);
    Velocity.X=static_cast<float>(Out.velocity.x);
    Velocity.Y=static_cast<float>(Out.velocity.y);

    MovementSignals.LocalVelocity=FVector(
        static_cast<float>(Out.localVelocity.x),
        static_cast<float>(Out.localVelocity.y),
        static_cast<float>(Out.localVelocity.z));
    MovementSignals.LocalAcceleration=FVector(
        static_cast<float>(Out.localAcceleration.x),
        static_cast<float>(Out.localAcceleration.y),
        static_cast<float>(Out.localAcceleration.z));
    MovementSignals.BrakingIntensity=static_cast<float>(Out.brakingIntensity);
    MovementSignals.SpeedNormalized=static_cast<float>(Out.speedNormalized);
    MovementSignals.ReversalSeverity=static_cast<float>(Out.reversalSeverity);
    MovementSignals.Gait=ToUnrealGait(Out.gait);
    MovementSignals.CombatState=ToUnrealCombatState(Out.combatState);
    MovementSignals.bGrounded=true;

    // Keep legacy diagnostics/playtest probes alive without letting them influence movement.
    Momentum.value=MovementSignals.SpeedNormalized;
    Momentum.turnRate=MovementSignals.ReversalSeverity*180.;
    Momentum.loss=MovementSignals.BrakingIntensity;
    if(State.phase==mcl::Phase::Release){
        Lunge.velocity=FMath::Max(0.f,FVector::DotProduct(Velocity,Forward));
        Lunge.displacement+=Lunge.velocity*Dt;
    }else Lunge={};
}

void UMeleeCharacterMovementComponent::UpdateFallbackSignals(const FVector& PreviousVelocity,float Dt)
{
    auto* C=Cast<AMeleeCharacter>(CharacterOwner);
    if(!C||!C->Combat)return;

    const FRotator Yaw(0,C->GetActorRotation().Yaw,0);
    const FVector Accel=Dt>SMALL_NUMBER?(Velocity-PreviousVelocity)/Dt:FVector::ZeroVector;
    MovementSignals.LocalVelocity=Yaw.UnrotateVector(Velocity);
    MovementSignals.LocalAcceleration=Yaw.UnrotateVector(Accel);
    MovementSignals.BrakingIntensity=0;
    MovementSignals.ReversalSeverity=0;
    MovementSignals.SpeedNormalized=FMath::Clamp(
        Velocity.Size2D()/static_cast<float>(FMath::Max(1.,C->Combat->Tuning().SprintSpeed)),0.f,1.f);
    MovementSignals.Gait=C->Combat->Simulation.state.phase==mcl::Phase::Dead?
        EMeleeGait::Disabled:EMeleeGait::Airborne;
    MovementSignals.CombatState=ToUnrealCombatState(
        mcl::LocomotionModel::combatState(C->Combat->Simulation.state.phase));
    MovementSignals.bGrounded=IsMovingOnGround();
}
