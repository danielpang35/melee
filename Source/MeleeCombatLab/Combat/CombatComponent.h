#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CombatSimulation.h"
#include "CombatComponent.generated.h"

UCLASS(ClassGroup=(Combat), meta=(BlueprintSpawnableComponent))
class MELEECOMBATLAB_API UCombatComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UCombatComponent();
    mcl::Combatant Simulation;
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    void Strike(double Angle, double RawAngle);
    void Stab();
    void Feint();
    void Parry();
    const mcl::Tuning& Tuning() const;
};
