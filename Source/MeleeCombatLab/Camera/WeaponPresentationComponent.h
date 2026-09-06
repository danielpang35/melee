#pragma once
#include "CoreMinimal.h"
#include "Components/SceneComponent.h"
#include "Combat/CombatSimulation.h"
#include "WeaponPresentationComponent.generated.h"

class UStaticMeshComponent;
UCLASS(ClassGroup=(Combat))
class MELEECOMBATLAB_API UWeaponPresentationComponent : public USceneComponent
{
    GENERATED_BODY()
public:
    UWeaponPresentationComponent();
    virtual void BeginPlay() override;
    void Present(const mcl::Combatant& State,const mcl::Tuning& Tuning,float DeltaTime);
    void SetArmsVisible(bool bShowArms);
private:
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Blade;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Guard;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Grip;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> Arms;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> Details;
    FVector LastVisualHilt=FVector::ZeroVector;
    bool bVisualInitialized=false;
    void Segment(UStaticMeshComponent* Mesh,FVector A,FVector B,float Width,float Depth);
};
