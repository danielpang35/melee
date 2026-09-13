#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Combat/CombatSimulation.h"
#include "EXCombatPresentation.generated.h"
UCLASS()
class MELEECOMBATLAB_API UEXCombatPresentation : public UActorComponent
{
    GENERATED_BODY()
public:
    UEXCombatPresentation();
    virtual void BeginPlay() override;
    bool Present(mcl::Combatant& State,float Dt,bool FirstPerson);
    FString Revision;
    TMap<FName,FTransform> HandBinding;
    static FName BindingName(FName Name){FString S=Name.ToString().ToLower();S.ReplaceInline(TEXT("."),TEXT("_"));S.ReplaceInline(TEXT("-"),TEXT("_"));return FName(*S);}
    double BladeError=0,PoseError=0;
    double BranchGripError=0,BranchAnchorError=0,BranchReachScale=1;
    bool Ready() const {return !Meshes.IsEmpty();}
    void SetWeaponVisible(bool Visible);
    bool GetVisibleBlade(FVector& Base,FVector& Tip) const;
private:
    bool Reload(mcl::Combatant& State);
    UPROPERTY() TArray<TObjectPtr<class USkeletalMeshComponent>> Meshes;
    UPROPERTY() TArray<TObjectPtr<class UCombatRigMesh>> Outputs;
    UPROPERTY() TObjectPtr<class UStaticMeshComponent> Weapon;
    TArray<FTransform> WeaponFrames,LastPose,FromPose;
    TArray<FTransform> LastCameraPose,FromCameraPose;
    FString SelectionText;
    double Poll=0,TransitionAge=1;
    mcl::Phase LastPhase=mcl::Phase::Idle;
    uint64 LastSerial=0;
    bool LastAuthored=false;
};
