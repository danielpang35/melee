#include "WeaponPresentationComponent.h"
#include "Visual/TournamentAssets.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"

namespace { FVector V(mcl::Vec P){return {P.x,P.y,P.z};} }
UWeaponPresentationComponent::UWeaponPresentationComponent()
{
    PrimaryComponentTick.bCanEverTick=false;
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> BaseMaterial(TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
    auto Make=[&](FName Name){auto* Mesh=CreateDefaultSubobject<UStaticMeshComponent>(Name);Mesh->SetupAttachment(this);
        Mesh->SetStaticMesh(Cube.Object);Mesh->SetMaterial(0,BaseMaterial.Object);Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);Mesh->SetCastShadow(false);return Mesh;};
    Blade=Make(TEXT("Blade"));Guard=Make(TEXT("Crossguard"));Grip=Make(TEXT("Grip"));
    Arms.Add(Make(TEXT("RightUpperArm")));Arms.Add(Make(TEXT("RightForearm")));
    Arms.Add(Make(TEXT("LeftUpperArm")));Arms.Add(Make(TEXT("LeftForearm")));
    Details.Add(Make(TEXT("RightPauldron")));Details.Add(Make(TEXT("LeftPauldron")));Details.Add(Make(TEXT("RightGauntlet")));Details.Add(Make(TEXT("LeftGauntlet")));Details.Add(Make(TEXT("Pommel")));
}
void UWeaponPresentationComponent::BeginPlay()
{
    Super::BeginPlay();
    auto* Steel=TournamentAssets::Material(this,TEXT("Steel"),FLinearColor(.38f,.43f,.47f));
    auto* Leather=TournamentAssets::Material(this,TEXT("Leather"),FLinearColor(.10f,.055f,.028f));
    Blade->SetStaticMesh(TournamentAssets::Mesh(TEXT("Blade")));Blade->SetMaterial(0,Steel);
    Guard->SetStaticMesh(TournamentAssets::Mesh(TEXT("Grip")));Guard->SetMaterial(0,Steel);
    Grip->SetStaticMesh(TournamentAssets::Mesh(TEXT("Grip")));Grip->SetMaterial(0,Leather);
    for(const auto& Arm:Arms){Arm->SetStaticMesh(TournamentAssets::Mesh(TEXT("Arm")));Arm->SetMaterial(0,Steel);}
    for(const auto& Detail:Details){Detail->SetStaticMesh(TournamentAssets::Mesh(TEXT("Orb")));Detail->SetMaterial(0,Steel);}

}
void UWeaponPresentationComponent::Segment(UStaticMeshComponent* Mesh,FVector A,FVector B,float Width,float Depth)
{
    const FVector D=B-A;Mesh->SetWorldLocation((A+B)*.5);Mesh->SetWorldRotation(D.Rotation());
    Mesh->SetWorldScale3D(FVector(D.Size()/100.,Width/100.,Depth/100.));
}
void UWeaponPresentationComponent::SetArmsVisible(bool bShowArms){for(const auto& Arm:Arms)Arm->SetVisibility(bShowArms);for(int I=0;I<4;++I)Details[I]->SetVisibility(bShowArms);}
void UWeaponPresentationComponent::Present(const mcl::Combatant& S,const mcl::Tuning& T,float Dt)
{
    // Blade has zero visual lag while offensive: rendering and collision share these exact endpoints.
    FVector H=V(S.weapon.hilt),Tip=V(S.weapon.tip);
    if(bVisualInitialized&&S.state.phase!=mcl::Phase::Release&&T.WeaponVisualLag>0){
        const float Alpha=1.f-FMath::Exp(-Dt*static_cast<float>(T.WeaponVisualSpring));
        const FVector Offset=(FMath::Lerp(LastVisualHilt,H,Alpha)-H).GetClampedToMaxSize(FMath::Min(.75,T.WeaponVisualLag*125.));
        H+=Offset;Tip+=Offset;
    }
    LastVisualHilt=H;bVisualInitialized=true;const FVector D=(Tip-H).GetSafeNormal();
    Segment(Blade,H,Tip,4.f,1.5f);
    FVector Side=FVector::CrossProduct(D,V(S.view.up())).GetSafeNormal();if(Side.IsNearlyZero())Side=V(S.view.right());
    Segment(Guard,H-Side*14,H+Side*14,3.f,3.f);Segment(Grip,H-D*19,H,3.5f,3.5f);
    Details[4]->SetWorldLocation(H-D*22);Details[4]->SetWorldScale3D(FVector(.065,.065,.085));
    // Simple two-link procedural arms follow the authoritative hands, with pole vectors at the elbows.
    for(int SideIndex=0;SideIndex<2;++SideIndex){
        const double Sign=SideIndex==0?1.:-1.;
        FVector Shoulder=V(S.position+S.view.world({-8,Sign*22,40}));
        FVector Hand=H-D*(SideIndex==0?5:15);
        FVector Axis=(Hand-Shoulder).GetSafeNormal();double Distance=FMath::Min((Hand-Shoulder).Size(),79.);
        double RipostePose=S.state.isRiposte?1.:0.;
        if(S.state.phase==mcl::Phase::Windup)RipostePose*=mcl::smooth(S.state.elapsed/.06);
        if(S.state.phase==mcl::Phase::Recovery)RipostePose*=1.-mcl::smooth(S.state.progress()/.3);
        FVector Pole=(V(S.view.right())*Sign+FVector::UpVector*mcl::mix(-.8,-.2,RipostePose)).GetSafeNormal();Pole=(Pole-Axis*FVector::DotProduct(Pole,Axis)).GetSafeNormal();
        FVector Elbow=(Shoulder+Hand)*.5+Pole*FMath::Sqrt(FMath::Max(0.,40.*40.-Distance*Distance*.25));
        if(RipostePose>0){
            const double Above=FVector::DotProduct(Elbow-V(S.position),V(S.view.up()))-(S.eyeHeight-24.);
            if(Above>0)Elbow-=V(S.view.up())*Above;
        }
        Segment(Arms[SideIndex*2],Shoulder,Elbow,12,11);Segment(Arms[SideIndex*2+1],Elbow,Hand,9,8);
        Details[SideIndex]->SetWorldLocation(Shoulder+Axis*7);Details[SideIndex]->SetWorldRotation(Axis.Rotation());Details[SideIndex]->SetWorldScale3D(FVector(.22,.20,.15));
        Details[SideIndex+2]->SetWorldLocation(Hand);Details[SideIndex+2]->SetWorldRotation(D.Rotation());Details[SideIndex+2]->SetWorldScale3D(FVector(.12,.085,.07));
    }
}
