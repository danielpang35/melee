#include "MeleeCharacterMovementComponent.h"
#include "MeleeCharacter.h"
#include "Combat/CombatComponent.h"

UMeleeCharacterMovementComponent::UMeleeCharacterMovementComponent()
{
    bOrientRotationToMovement=false;AirControl=.25f;JumpZVelocity=460.f;
    GroundFriction=6.f;BrakingFrictionFactor=1.f;MaxWalkSpeedCrouched=190.f;
    GetNavAgentPropertiesRef().bCanCrouch=true;
}
void UMeleeCharacterMovementComponent::ResetCombatMovement()
{
    StopMovementImmediately();Momentum={};Lunge={};LungedSerial=0;PreviousLunge=FVector::ZeroVector;ForwardInput=0;bSprint=false;
}
float UMeleeCharacterMovementComponent::GetMaxSpeed() const
{
    const auto* C=Cast<AMeleeCharacter>(CharacterOwner);
    if(!C||!C->Combat)return Super::GetMaxSpeed();
    const auto& T=C->Combat->Tuning();
    const FVector Desired=Acceleration.GetSafeNormal2D();
    const double Forward=FVector::DotProduct(Desired,C->GetActorForwardVector());
    double Speed=Forward>=0?FMath::Lerp(T.LateralSpeed,T.ForwardSpeed,Forward):FMath::Lerp(T.LateralSpeed,T.BackwardSpeed,-Forward);
    if(bSprint&&Forward>.7&&C->Combat->Simulation.state.phase==mcl::Phase::Idle)Speed=FMath::Lerp(Speed,T.SprintSpeed,Momentum.value);
    if(IsCrouching())Speed*=.5;
    return static_cast<float>(Speed);
}
void UMeleeCharacterMovementComponent::TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* TickFunction)
{
    if(auto* C=Cast<AMeleeCharacter>(CharacterOwner)){
        const auto& T=C->Combat->Tuning();FVector Input=GetPendingInputVector();
        Momentum.update({Velocity.X,Velocity.Y,0},{Input.X,Input.Y,0},Dt,T);
        GroundFriction=static_cast<float>(T.GroundFriction);GravityScale=static_cast<float>(T.GravityScale);JumpZVelocity=static_cast<float>(T.JumpSpeed);
        MaxAcceleration=static_cast<float>(T.Acceleration);BrakingDecelerationWalking=static_cast<float>(T.Deceleration);
        const auto& S=C->Combat->Simulation;
        if(S.state.phase!=mcl::Phase::Release)Lunge={};
        if(S.state.phase==mcl::Phase::Release&&S.state.serial!=LungedSerial){LungedSerial=S.state.serial;Lunge.begin(S.view.forward(),ForwardInput,Momentum.value,T);}
    }
    Super::TickComponent(Dt,TickType,TickFunction);
}
void UMeleeCharacterMovementComponent::CalcVelocity(float Dt,float Friction,bool bFluid,float Braking)
{
    Velocity-=PreviousLunge;PreviousLunge=FVector::ZeroVector;
    Super::CalcVelocity(Dt,Friction,bFluid,Braking);
    if(auto* C=Cast<AMeleeCharacter>(CharacterOwner)){
        if(IsMovingOnGround()){
            const auto V=Lunge.step(Dt,C->Combat->Tuning());PreviousLunge=FVector(V.x,V.y,V.z);Velocity+=PreviousLunge;
        }
    }
}
