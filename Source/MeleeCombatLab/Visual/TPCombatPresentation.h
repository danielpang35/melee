#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Combat/CombatSimulation.h"
#include "TPSourceBinding.h"
#include "TPCombatPresentation.generated.h"

// Explicit opt-in source proof. Never owns or updates simulation weapon data.
UCLASS()
class MELEECOMBATLAB_API UTPCombatPresentation : public UActorComponent
{
    GENERATED_BODY()
public:
    void Initialize(class USkeletalMesh* FallbackMesh);
    bool Present(const mcl::Combatant& State,float Dt,const TArray<FTransform>& FallbackPose,const FTransform& BodyWorld);
    void Hide();
    bool Selected=false,Active=false,Authored=false;
    FString Revision;
    double SourceTime=.30,PoseErrorCm=0,WeaponErrorCm=0,BladeBaseErrorCm=0,BladeTipErrorCm=0,BlendWeight=1;
    double ImportPoseErrorCm=0,ImportRotationErrorDegrees=0;
    FVector VisibleBladeBase=FVector::ZeroVector,VisibleBladeTip=FVector::ZeroVector;
    double GripErrorCm=0,ArmReachScale=1;
private:
    bool Reload();
    void BindContactPose(TArray<FTransform>& Pose,const FTransform& NativeWeapon,FTransform& TargetWeapon,
        const FTransform& BodyWorld,const mcl::Combatant& State);
    void FitContactArms(TArray<FTransform>& Pose,const TArray<FTransform>& NativePose,
        const FTransform& NativeWeapon,const FTransform& TargetWeapon);
    UPROPERTY() TObjectPtr<class USkeletalMeshComponent> Sampler;
    UPROPERTY() TObjectPtr<class UCombatRigMesh> Output;
    UPROPERTY() TObjectPtr<class UStaticMeshComponent> Weapon;
    UPROPERTY() TObjectPtr<class USkeletalMesh> Fallback;
    FString SelectionPath,SelectionText,RejectedText;
    TArray<FTransform> WeaponFrames,LastPose,FromPose;
    TArray<int32> FallbackIndices;
    TArray<FQuat> GaitRotations;
    FVector LastBodyPosition=FVector::ZeroVector;
    bool GaitValid=false;
    FTransform LastWeapon,FromWeapon;
    double Poll=0;
    mcl::TPSourceBinding SourceBinding;
    bool Initialized=false,LastNative=false,Transition=false;
    bool ContactBinding=false;
    mcl::Phase LastPhase=mcl::Phase::Idle;
    uint64 LastSerial=0;
};
