#include "WeaponPresentationComponent.h"
#include "Visual/MeleePresentationPose.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"

UWeaponPresentationComponent::UWeaponPresentationComponent()
{
    PrimaryComponentTick.bCanEverTick=false;
    Sword=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CitadelSword"));
    Sword->SetupAttachment(this);
    Sword->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Sword->SetGenerateOverlapEvents(false);
    Sword->SetCastShadow(true);
}
void UWeaponPresentationComponent::BeginPlay()
{
    Super::BeginPlay();
    auto* Mesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Visual/Citadel/Meshes/SM_CitadelSword.SM_CitadelSword"));
    ensureAlwaysMsgf(Mesh,TEXT("Citadel sword missing. Run Tools/ImportCitadelArt.py."));
    Sword->SetStaticMesh(Mesh);
}
void UWeaponPresentationComponent::Present(const mcl::Combatant& State,const mcl::Tuning& Tuning,float)
{
    const auto Pose=mcl::presentation::evaluate(State,Tuning);
    const auto V=[](mcl::Vec P){return FVector(P.x,P.y,P.z);};
    // Calibrated asset: blade base Z=0, tip Z=100 cm, broad edge along X.
    const double Scale=(V(Pose.blade.tip)-V(Pose.blade.hilt)).Size()/100.;
    Sword->SetWorldTransform(FTransform(FRotationMatrix::MakeFromZX(V(Pose.axis),V(Pose.edge)).ToQuat(),
        V(Pose.blade.hilt),FVector(Scale)));
}
