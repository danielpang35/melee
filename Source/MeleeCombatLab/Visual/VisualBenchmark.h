#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "VisualBenchmark.generated.h"
class ACameraActor;
UCLASS()
class MELEECOMBATLAB_API UVisualBenchmark : public UActorComponent
{
    GENERATED_BODY()
public:
    UVisualBenchmark();
    virtual void TickComponent(float Dt,ELevelTick Type,FActorComponentTickFunction* Function) override;
private:
    UPROPERTY() TObjectPtr<ACameraActor> Camera;
    double Age=0,LastClock=0;
    int Shot=0;
    bool Started=false,Finished=false;
    FString Label,Rows;
    TArray<double> Frames,Game,Render,Gpu,Draws,Primitives;
    void Finish();
};
