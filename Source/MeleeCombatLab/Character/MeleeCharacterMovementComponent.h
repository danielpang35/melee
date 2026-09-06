#pragma once
#include "CoreMinimal.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Movement/LocomotionModel.h"
#include "MeleeCharacterMovementComponent.generated.h"

UENUM(BlueprintType)
enum class EMeleeGait : uint8
{
    Idle,
    Walk,
    Sprint,
    Crouch,
    Airborne,
    Disabled
};

UENUM(BlueprintType)
enum class EMeleeCombatMovementState : uint8
{
    Neutral,
    Windup,
    Release,
    Recovery,
    Parry,
    ParryRecovery,
    Flinch,
    Dead
};

USTRUCT(BlueprintType)
struct FMovementPresentationSignals
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly,Category="Movement|Presentation")
    FVector LocalVelocity=FVector::ZeroVector;

    UPROPERTY(BlueprintReadOnly,Category="Movement|Presentation")
    FVector LocalAcceleration=FVector::ZeroVector;

    UPROPERTY(BlueprintReadOnly,Category="Movement|Presentation")
    float BrakingIntensity=0;

    UPROPERTY(BlueprintReadOnly,Category="Movement|Presentation")
    float SpeedNormalized=0;

    UPROPERTY(BlueprintReadOnly,Category="Movement|Presentation")
    float ReversalSeverity=0;

    UPROPERTY(BlueprintReadOnly,Category="Movement|Presentation")
    EMeleeGait Gait=EMeleeGait::Idle;

    UPROPERTY(BlueprintReadOnly,Category="Movement|Presentation")
    EMeleeCombatMovementState CombatState=EMeleeCombatMovementState::Neutral;

    UPROPERTY(BlueprintReadOnly,Category="Movement|Presentation")
    bool bGrounded=false;
};

// Transitional read-only compatibility telemetry for older debug/playtest code.
// These fields no longer drive authoritative movement.
struct FLegacyMomentumTelemetry
{
    double value=0,turnRate=0,loss=0;
};

struct FLegacyLungeTelemetry
{
    double velocity=0,displacement=0;
};

UCLASS()
class MELEECOMBATLAB_API UMeleeCharacterMovementComponent : public UCharacterMovementComponent
{
    GENERATED_BODY()
public:
    UMeleeCharacterMovementComponent();

    bool bSprintRequested=false;

    // Legacy API shims: retained so locally edited character/debug/playtest code
    // can compile while the new locomotion solver becomes authoritative.
    bool bSprint=false;
    double ForwardInput=0;
    FLegacyMomentumTelemetry Momentum;
    FLegacyLungeTelemetry Lunge;

    UPROPERTY(BlueprintReadOnly,Category="Movement|Presentation")
    FMovementPresentationSignals MovementSignals;

    void ResetCombatMovement();
    virtual float GetMaxSpeed() const override;
    virtual void TickComponent(float DeltaTime,ELevelTick TickType,FActorComponentTickFunction* ThisTickFunction) override;
    virtual void CalcVelocity(float DeltaTime,float Friction,bool bFluid,float BrakingDeceleration) override;

private:
    FVector InputIntent=FVector::ZeroVector;
    void UpdateFallbackSignals(const FVector& PreviousVelocity,float DeltaTime);
};
