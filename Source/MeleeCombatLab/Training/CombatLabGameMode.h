#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "Combat/CombatSimulation.h"
#include "CombatLabGameMode.generated.h"

class UCombatComponent;class ATrainingDummy;class SCombatTuningPanel;class USoundWaveProcedural;class ACameraActor;
UCLASS()
class MELEECOMBATLAB_API ACombatLabGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    ACombatLabGameMode();
    mcl::CombatSimulation Combat;
    bool bDebug=false,bTuningOpen=false,bInspection=false;
    FString TuningStatus;
    mcl::Resolution FeedbackResult=mcl::Resolution::None;
    double FeedbackUntil=0;
    struct Spark { FVector Position,Velocity; float Life; FLinearColor Color; };
    TArray<Spark> Sparks;
    UPROPERTY() TArray<TObjectPtr<UCombatComponent>> Combatants;
    UPROPERTY() TObjectPtr<ATrainingDummy> AttackingDummy;
    UPROPERTY() TObjectPtr<ATrainingDummy> PassiveDummy;
    virtual void StartPlay() override;
    virtual void Tick(float DeltaTime) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    void Register(UCombatComponent* Component);
    void Unregister(UCombatComponent* Component);
    void ResetLab();void NextPattern();void ToggleTuning();void ToggleInspection();
    bool SaveTuning(bool bPromote=false);bool LoadTuning();void ResetTuning();
    void DrawCombatDebug();
private:
    int NextId=1;
    TSharedPtr<SCombatTuningPanel> Panel;
    UPROPERTY() TArray<TObjectPtr<USoundWaveProcedural>> ActiveSounds;
    UPROPERTY() TObjectPtr<ACameraActor> InspectionCamera;
    void BuildArena();void PlayImpact(const mcl::CombatEvent& Event);
};
