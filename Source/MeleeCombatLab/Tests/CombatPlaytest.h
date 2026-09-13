#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Combat/Attacks/AttackTypes.h"
#include "Combat/CombatTuning.h"
#include <functional>
#include "CombatPlaytest.generated.h"

class ACombatLabGameMode;class AMeleeCharacter;class ATrainingDummy;class AStaticMeshActor;
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
    int MotionSnapshot=0;
    int ReviewFrame=0;
    int ReviewOnlyScenario=-1;
    FString ReviewCamera,ReviewPose,ReviewOutcome,ReviewSequence;
    bool bReviewSequenceIssued=false,bReviewSequenceObserved=false;
    bool bReviewFinishPending=false;
    double ReviewAttackStartTime=-1;
    uint64 ReviewKeySerial=0;
    mcl::Phase ReviewKeyPhase=mcl::Phase::Dead;
    double ReviewLeadIn=0,ReviewPitch=0,ReviewAngle=0;
    bool bReviewPitch=false,bReviewAngle=false,bReviewAttackPending=false,bReviewKeys=false,bReviewCoreSet=false;
    bool bReviewOutcome=false,bReviewParryIssued=false,bReviewFixtureReady=true;
    int ReviewExpectedContacts=0,ReviewUnexpectedContacts=0;
    double ReviewContactTime=-1;
    mcl::Resolution ReviewContactResolution=mcl::Resolution::None;
    TWeakObjectPtr<AStaticMeshActor> ReviewWall;
    TArray<FString> ReviewContactRows;
    int ReviewKey=0;
    TArray<FString> ReviewFrameRows;
    TArray<FString> ReviewScenarioFrameRows;
    FString OutputFolder,MotionFrameFolder;
    double MaxBladeError=0,MaxProjectionError=0,MaxReleaseProjectionError=0;
    double MaxArmStretch=1.;
    double MaxArmSurfaceStretch=1.;
    std::function<void(double)> OriginalBeforeStep;
    FVector StartPosition,StopPosition;
    mcl::Tuning MovementTuning,UserTuning;
    FString UserTuningFile;bool bSavedFixture=false,bHadTuningFile=false;
    bool bPriorIgnoreInput=false;
    double SpeedAt=-1,StopDistance=0,BaselineSpeedAt=0,BaselineStop=0;
    TArray<FString> Results;
    void BeginScenario(ACombatLabGameMode* Lab,AMeleeCharacter* Player,ATrainingDummy* Dummy);
    void FinishScenario(ACombatLabGameMode* Lab,AMeleeCharacter* Player,ATrainingDummy* Dummy);
    void StartReviewAttack(AMeleeCharacter* Player);
    void UpdateReviewCamera(AMeleeCharacter* Player);
    void DestroyReviewWall();
};
