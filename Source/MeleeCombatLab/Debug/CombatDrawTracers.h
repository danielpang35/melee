#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Combat/CombatSimulation.h"
#include <deque>
#include "CombatDrawTracers.generated.h"

// Read-only diagnostic: simulation samples and rendered poses keep separate clocks.
UCLASS()
class MELEECOMBATLAB_API UCombatDrawTracers : public UActorComponent
{
    GENERATED_BODY()
public:
    UCombatDrawTracers();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void TickComponent(float Dt,ELevelTick Type,FActorComponentTickFunction* Tick) override;
    void Sample(const mcl::Combatant& State,double Time);
    void Clear();
    void Toggle();
    bool Enabled() const;
    int32 LineCount() const { return static_cast<int32>(History.size()); }
    double MaxGapCm=0;
    int32 VisibleActors=0;
private:
    struct Line { FVector A,B; FColor Color; double Time; float Width; };
    std::deque<Line> History;
    UPROPERTY() TObjectPtr<class ULineBatchComponent> Lines;
    TWeakObjectPtr<AActor> ViewTarget;
    bool WasEnabled=false;
    void Add(FVector A,FVector B,FColor Color,double Time,float Width);
};
