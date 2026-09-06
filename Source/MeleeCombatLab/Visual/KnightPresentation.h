#pragma once
#include "CoreMinimal.h"
#include "Components/SceneComponent.h"
#include "Combat/CombatSimulation.h"
#include "KnightPresentation.generated.h"
class UCombatRigMesh;
class UMaterialInstanceDynamic;
UCLASS()
class MELEECOMBATLAB_API UKnightPresentation : public USceneComponent
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    void Present(const mcl::Combatant& State,const mcl::Tuning& Tuning,bool Blue,float Reaction,float Dt);
    void SetFirstPerson(bool Value);
private:
    UPROPERTY() TObjectPtr<UCombatRigMesh> Body;
    UPROPERTY() TObjectPtr<UCombatRigMesh> FirstPerson;
    UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> Alloy;
    TArray<FTransform> Reference,LocalPose,ComponentPose;
    TMap<FName,int32> BoneIndices;
    TArray<int32> Parents;
    FVector LastPosition=FVector::ZeroVector;
    float Gait=0,Travel=0,Fall=0;
    bool Initialized=false,bFirstPerson=false,bBlue=false;
    int32 Bone(FName Name) const;
    void BuildComponentPose();
};
