#pragma once
#include "CoreMinimal.h"
#include "Components/SceneComponent.h"
#include "KnightPresentation.generated.h"
class UStaticMeshComponent;class UMaterialInstanceDynamic;
UCLASS()
class MELEECOMBATLAB_API UKnightPresentation : public USceneComponent
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    void Present(bool Blue,float Reaction,bool Dead,float Dt);
private:
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> Parts;
    UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> Cloth;
    UPROPERTY() TObjectPtr<USceneComponent> UpperBody;
    bool WasBlue=false;
    float Fall=0;
};
