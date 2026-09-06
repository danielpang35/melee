#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TournamentCourtyard.generated.h"
class UInstancedStaticMeshComponent;
UCLASS()
class MELEECOMBATLAB_API ATournamentCourtyard : public AActor
{
    GENERATED_BODY()
public:
    ATournamentCourtyard();
    virtual void BeginPlay() override;
private:
    UPROPERTY() TMap<FString,TObjectPtr<UInstancedStaticMeshComponent>> Groups;
    void Part(const FString& Kind,FVector At,FVector Size,FLinearColor Color,FRotator Rotation=FRotator::ZeroRotator,bool Collision=false,const FString& Shape=TEXT("Cube"));
    void Beam(const FString& Kind,FVector A,FVector B,float Width,float Depth,FLinearColor Color);
};
