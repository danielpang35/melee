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
private:
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Sword;
};
