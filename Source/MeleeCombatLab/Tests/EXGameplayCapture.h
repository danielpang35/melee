#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "EXGameplayCapture.generated.h"
// Bounded input replay/capture around the production game; owns no combat step.
UCLASS()
class UEXGameplayCapture : public UActorComponent
{
    GENERATED_BODY()
public:
    UEXGameplayCapture();
    virtual void TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* TickFunction) override;
private:
    int Frame=-90;
    bool Started=false,Riposted=false,TPProof=false,TPCompose=false,Pilot=false,TracerSmoke=false,ReadabilitySmoke=false,TPPoseReview=false;
    FString Directory,View,Rows,Events,ContactRows,TracerRows;
    UPROPERTY() TObjectPtr<class ACameraActor> ReviewCamera;
};
