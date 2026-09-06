#pragma once
#include "CoreMinimal.h"
#include "Character/MeleeCharacter.h"
#include "TrainingPattern.h"
#include "TrainingDummy.generated.h"

class UKnightPresentation;class UStaticMeshComponent;class UTextRenderComponent;class UMaterialInstanceDynamic;
UCLASS()
class MELEECOMBATLAB_API ATrainingDummy : public AMeleeCharacter
{
    GENERATED_BODY()
public:
    ATrainingDummy(const FObjectInitializer& ObjectInitializer);
    mcl::TrainingPattern Pattern;
    bool bPassive=false;
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    void React(mcl::Resolution Result);
private:
    UPROPERTY() TObjectPtr<UKnightPresentation> Knight;
    UPROPERTY() TObjectPtr<UTextRenderComponent> Label;
    FString LastLabel;
    float Reaction=0;
};
