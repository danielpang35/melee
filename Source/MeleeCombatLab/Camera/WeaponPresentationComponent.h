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
    void Present(const mcl::Combatant& State,const mcl::Tuning& Tuning,float DeltaTime,bool FirstPerson=false);
    mcl::Pose RenderedBlade() const;
    double BladeError=0;
    double ProjectionError=0,ActiveBladeError=0;
    mcl::Vec ViewOffset;
private:
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Sword;
};
