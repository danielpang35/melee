#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Combat/Attacks/AttackTypes.h"
#include "Combat/CombatTuning.h"
#include "CombatPlaytest.generated.h"

class ACombatLabGameMode;class AMeleeCharacter;class ATrainingDummy;
// Opt-in in-engine regression tour. Uses real actors, movement, world queries, rendering and feedback.
UCLASS()
class UCombatPlaytest : public UActorComponent
{
    GENERATED_BODY()
public:
    UCombatPlaytest();
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void TickComponent(float DeltaTime,ELevelTick TickType,FActorComponentTickFunction* TickFunction) override;
private:
    int Scenario=-1;
    double Age=0,ScenarioStartTime=0;
    bool bAction=false,bSnapshot=false,bObserved=false,bFinished=false;
    double FirstContact=-1,NeutralContact=-1,AccelContact=-1,DragContact=-1;
    FVector StartPosition,StopPosition;
    mcl::Tuning MovementTuning,UserTuning;
    FString UserTuningFile;bool bSavedFixture=false,bHadTuningFile=false;
    double SpeedAt=-1,StopDistance=0,BaselineSpeedAt=0,BaselineStop=0;
    TArray<FString> Results;
    void BeginScenario(ACombatLabGameMode* Lab,AMeleeCharacter* Player,ATrainingDummy* Dummy);
    void FinishScenario(ACombatLabGameMode* Lab,AMeleeCharacter* Player,ATrainingDummy* Dummy);
};
