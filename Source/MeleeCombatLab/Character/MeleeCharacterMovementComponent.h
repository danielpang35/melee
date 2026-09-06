#pragma once
#include "CoreMinimal.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Movement/MomentumModel.h"
#include "Movement/LungeModel.h"
#include "MeleeCharacterMovementComponent.generated.h"

UCLASS()
class MELEECOMBATLAB_API UMeleeCharacterMovementComponent : public UCharacterMovementComponent
{
    GENERATED_BODY()
public:
    UMeleeCharacterMovementComponent();
    mcl::MomentumModel Momentum;
    mcl::LungeModel Lunge;
    bool bSprint=false;
    double ForwardInput=0;
    void ResetCombatMovement();
    virtual float GetMaxSpeed() const override;
    virtual void TickComponent(float DeltaTime,ELevelTick TickType,FActorComponentTickFunction* ThisTickFunction) override;
    virtual void CalcVelocity(float DeltaTime,float Friction,bool bFluid,float BrakingDeceleration) override;
private:
    uint64 LungedSerial=0;
    FVector PreviousLunge=FVector::ZeroVector;
};
