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
        Mesh->SetStaticMesh(Cube.Object);Mesh->SetMaterial(0,BaseMaterial.Object);
        Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);Mesh->SetCastShadow(false);return Mesh;};
    Blade=Make(TEXT("Blade"));Guard=Make(TEXT("Crossguard"));Grip=Make(TEXT("Grip"));
    Arms.Add(Make(TEXT("RightUpperArm")));Arms.Add(Make(TEXT("RightForearm")));
    Arms.Add(Make(TEXT("LeftUpperArm")));Arms.Add(Make(TEXT("LeftForearm")));
    Details.Add(Make(TEXT("RightPauldron")));Details.Add(Make(TEXT("LeftPauldron")));
    Details.Add(Make(TEXT("RightGauntlet")));Details.Add(Make(TEXT("LeftGauntlet")));
    Details.Add(Make(TEXT("Pommel")));
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
void UWeaponPresentationComponent::SetArmsVisible(bool bShowArms)
{
    for(const auto& Arm:Arms)Arm->SetVisibility(bShowArms);
    for(int I=0;I<4;++I)Details[I]->SetVisibility(bShowArms);
}
void UWeaponPresentationComponent::Present(const mcl::Combatant& S,const mcl::Tuning& T,float Dt)
{
    FVector H=V(S.weapon.hilt),Tip=V(S.weapon.tip);
    if(bVisualInitialized&&S.state.phase!=mcl::Phase::Release&&T.WeaponVisualLag>0){
        const float Alpha=1.f-FMath::Exp(-Dt*static_cast<float>(T.WeaponVisualSpring));
        const FVector Offset=(FMath::Lerp(LastVisualHilt,H,Alpha)-H)
            .GetClampedToMaxSize(FMath::Min(.75,T.WeaponVisualLag*125.));
        H+=Offset;Tip+=Offset;
    }

    LastVisualHilt=H;bVisualInitialized=true;
    const FVector D=(Tip-H).GetSafeNormal();
    Segment(Blade,H,Tip,3.2f,1.25f);

    const mcl::BodyMotion Motion=mcl::AttackTrajectory::body(S.state,T);
    FVector Side=FVector::CrossProduct(D,V(S.view.up())).GetSafeNormal();
    if(Side.IsNearlyZero())Side=V(S.view.right());

    // Roll the crossguard/grip around the exact blade axis. This improves edge/wrist
    // readability while the visible blade endpoints remain identical to collision.
    if(FMath::Abs(Motion.gripRoll)>.001){
        const float Roll=static_cast<float>(Motion.gripRoll*mcl::Rad);
        Side=(Side*FMath::Cos(Roll)+FVector::CrossProduct(D,Side)*FMath::Sin(Roll)+
            D*FVector::DotProduct(D,Side)*(1.f-FMath::Cos(Roll))).GetSafeNormal();
    }

    Segment(Guard,H-Side*14,H+Side*14,2.5f,2.5f);
    Segment(Grip,H-D*19,H,2.8f,2.8f);
    Details[4]->SetWorldLocation(H-D*22);
    Details[4]->SetWorldScale3D(FVector(.052,.052,.07));

    const double ChestYaw=Motion.chestYaw*mcl::Rad;
    const double C=std::cos(ChestYaw),Sin=std::sin(ChestYaw);

    for(int SideIndex=0;SideIndex<2;++SideIndex){
        const double Sign=SideIndex==0?1.:-1.;
        const double ShoulderDrive=SideIndex==0?Motion.rightShoulderX:Motion.leftShoulderX;
        const double ElbowOut=SideIndex==0?Motion.rightElbowOut:Motion.leftElbowOut;
        const double ElbowLift=SideIndex==0?Motion.rightElbowLift:Motion.leftElbowLift;

        double LocalX=-10.+ShoulderDrive+Motion.forwardLean;
        double LocalY=Sign*21.;
        const double RotX=LocalX*C-LocalY*Sin;
        const double RotY=LocalX*Sin+LocalY*C;
        FVector Shoulder=V(S.position+S.view.world({RotX,RotY,39.+Motion.chestPitch*.10}));

        FVector Hand=H-D*(SideIndex==0?5:15);
        FVector Axis=(Hand-Shoulder).GetSafeNormal();
        double Distance=FMath::Min((Hand-Shoulder).Size(),79.);

        double RipostePose=S.state.isRiposte?1.:0.;
        if(S.state.phase==mcl::Phase::Windup)RipostePose*=mcl::smooth(S.state.elapsed/.06);
        if(S.state.phase==mcl::Phase::Recovery)RipostePose*=1.-mcl::smooth(S.state.progress()/.3);

        const FVector Right=V(S.view.right());
        const FVector Up=V(S.view.up());
        FVector Pole=(Right*Sign*(1.+ElbowOut*.035)+
            Up*(mcl::mix(-.8,-.2,RipostePose)+ElbowLift*.045)).GetSafeNormal();
        Pole=(Pole-Axis*FVector::DotProduct(Pole,Axis)).GetSafeNormal();

        FVector Elbow=(Shoulder+Hand)*.5+
            Pole*FMath::Sqrt(FMath::Max(0.,40.*40.-Distance*Distance*.25));
        if(RipostePose>0){
            const double Above=FVector::DotProduct(Elbow-V(S.position),Up)-(S.eyeHeight-24.);
            if(Above>0)Elbow-=Up*Above;
        }

        Segment(Arms[SideIndex*2],Shoulder,Elbow,8.2f,7.4f);
        Segment(Arms[SideIndex*2+1],Elbow,Hand,6.8f,6.2f);

        Details[SideIndex]->SetWorldLocation(Shoulder+Axis*6);
        Details[SideIndex]->SetWorldRotation(Axis.Rotation());
        Details[SideIndex]->SetWorldScale3D(FVector(.15,.14,.11));

        Details[SideIndex+2]->SetWorldLocation(Hand);
        Details[SideIndex+2]->SetWorldRotation(D.Rotation());
        Details[SideIndex+2]->SetWorldScale3D(FVector(.085,.065,.055));
    }
}
