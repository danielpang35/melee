#pragma once
#include "CoreMinimal.h"
#include "Components/SceneComponent.h"
#include "Combat/CombatSimulation.h"
#include "KnightPresentation.generated.h"
// Original CF presentation or the working body's independent rest-pose rig.
UCLASS()
class MELEECOMBATLAB_API UKnightPresentation : public USceneComponent
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable,Category="Fresh Character|Import")
    static bool PersistSurface(class USkeletalMesh* Mesh,class UMaterialInterface* Surface);
    virtual void BeginPlay() override;
    void Present(const mcl::Combatant& State,const mcl::Tuning& Tuning,bool Blue,float Reaction,float Dt,mcl::Vec ViewOffset={});
    void SetFirstPerson(bool Value);
    double MaxArmStretch=1.;
    bool TPSelected=false,TPActive=false,TPAuthored=false;
    FString TPRevision;
    double TPSourceTime=.30,TPPoseErrorCm=0,TPWeaponErrorCm=0,TPBladeBaseErrorCm=0,TPBladeTipErrorCm=0,TPBlendWeight=1;
    double TPGripErrorCm=0,TPArmReachScale=1;
    double TPImportPoseErrorCm=0,TPImportRotationErrorDegrees=0;
    FVector TPBladeBase=FVector::ZeroVector,TPBladeTip=FVector::ZeroVector;
    double MeasureArmSurfaceStretch() const;
    void SaveArmPoseAudit(const FString& Path) const;
    void SaveMotionTrace(const FString& Path,double SampleTime) const;
private:
    UPROPERTY() TObjectPtr<class UCombatRigMesh> Body;
    UPROPERTY() TObjectPtr<class UCombatRigMesh> KnightSkin;
    UPROPERTY() TObjectPtr<class UTPCombatPresentation> TP;
    TArray<FTransform> Reference,ComponentPose;
    TArray<int32> Parents;
    TMap<FName,int32> BoneIndices;
    mcl::Vec AuditEye;
    mcl::Orientation AuditView;
    FString MotionTrace;
    FVector LastPosition=FVector::ZeroVector;
    double Gait=0;
    bool bFirstPerson=false,Initialized=false;
    int32 Bone(FName Name) const;
    void RotateSubtree(int32 Root,FQuat Rotation,FVector Shift=FVector::ZeroVector);
    void FitLimb(int32 Upper,int32 Lower,int32 End,FVector Target,FVector Pole);
};
