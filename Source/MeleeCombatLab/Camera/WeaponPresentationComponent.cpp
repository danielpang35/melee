#include "WeaponPresentationComponent.h"
#include "Visual/MeleePresentationPose.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "DrawDebugHelpers.h"
#include "HAL/IConsoleManager.h"

static TAutoConsoleVariable<int32> CVarMotionDebug(TEXT("mcl.MotionDebug"),0,
    TEXT("Draw authoritative blade (green), rendered blade (magenta), and arm targets (cyan)."));

mcl::Pose UWeaponPresentationComponent::RenderedBlade() const
{
    const FTransform Transform=Sword->GetComponentTransform();
    const FVector H=Transform.TransformPosition(FVector::ZeroVector);
    const FVector T=Transform.TransformPosition(FVector(0,0,103.5));
    return {{H.X,H.Y,H.Z},{T.X,T.Y,T.Z}};
}

UWeaponPresentationComponent::UWeaponPresentationComponent()
{
    PrimaryComponentTick.bCanEverTick=false;
    Sword=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("FreshSword"));
    Sword->SetupAttachment(this);
    Sword->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Sword->SetGenerateOverlapEvents(false);
    Sword->SetCastShadow(true);
}
void UWeaponPresentationComponent::BeginPlay()
{
    Super::BeginPlay();
    auto* Mesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/EXPreview/EX_v002/EXPreviewWeapon.EXPreviewWeapon"));
    ensureAlwaysMsgf(Mesh,TEXT("Fresh sword missing. Restore the approved EX asset bundle."));
    Sword->SetStaticMesh(Mesh);
}
void UWeaponPresentationComponent::Present(const mcl::Combatant& State,const mcl::Tuning& Tuning,float Dt,bool FirstPerson)
{
    auto Pose=mcl::presentation::evaluate(State,Tuning);
    const auto Desired=FirstPerson&&State.rightCut?State.view.world(State.rightCut->viewOffset(State.state)):mcl::Vec{};
    ViewOffset=mcl::lerp(ViewOffset,Desired,1.-std::exp(-double(Dt)/.035));
    // No cosmetic displacement in an active damage window or external view.
    if(!FirstPerson||State.state.phase==mcl::Phase::Release)ViewOffset={};
    Pose.blade.hilt+=ViewOffset;Pose.blade.tip+=ViewOffset;
    const auto V=[](mcl::Vec P){return FVector(P.x,P.y,P.z);};
    // Calibrated asset: blade base Z=0, tip Z=103.5 cm, broad edge along X.
    const double Scale=(V(Pose.blade.tip)-V(Pose.blade.hilt)).Size()/103.5;
    Sword->SetWorldTransform(FTransform(FRotationMatrix::MakeFromZX(V(Pose.axis),V(Pose.edge)).ToQuat(),
        V(Pose.blade.hilt),FVector(Scale)));
    const auto Rendered=RenderedBlade();
    ProjectionError=FMath::Max((Rendered.hilt-State.weapon.hilt).length(),(Rendered.tip-State.weapon.tip).length());
    ActiveBladeError=State.state.phase==mcl::Phase::Release?ProjectionError:0.;
    // Geometric render error and deliberate non-damaging projection are
    // reported separately; release must satisfy both exact-contact checks.
    BladeError=FMath::Max((Rendered.hilt-Pose.blade.hilt).length(),(Rendered.tip-Pose.blade.tip).length());
#if !UE_BUILD_SHIPPING
    if(CVarMotionDebug.GetValueOnGameThread()){
        DrawDebugLine(GetWorld(),V(State.weapon.hilt),V(State.weapon.tip),FColor::Green,false,-1,0,3);
        DrawDebugLine(GetWorld(),V(Rendered.hilt),V(Rendered.tip),FColor::Magenta,false,-1,0,1);
        for(const auto& Arm:Pose.arms){
            for(auto Point:{Arm.shoulder,Arm.elbow,Arm.hand})DrawDebugSphere(GetWorld(),V(Point),2,8,FColor::Cyan,false,-1);
            DrawDebugLine(GetWorld(),V(Arm.shoulder),V(Arm.elbow),FColor::Cyan,false,-1);
            DrawDebugLine(GetWorld(),V(Arm.elbow),V(Arm.hand),FColor::Cyan,false,-1);
        }
        DrawDebugDirectionalArrow(GetWorld(),V(Rendered.tip),V(Rendered.tip+State.tipVelocity*.02),5,FColor::Yellow,false,-1);
    }
#endif
}
