#include "KnightPresentation.h"
#include "CombatRigMesh.h"
#include "MeleePresentationPose.h"
#include "Engine/SkeletalMesh.h"
#include "Materials/MaterialInstanceDynamic.h"

namespace {FVector V(mcl::Vec P){return {P.x,P.y,P.z};}}
int32 UKnightPresentation::Bone(FName Name) const {const auto* Index=BoneIndices.Find(Name);return Index?*Index:INDEX_NONE;}
void UKnightPresentation::BeginPlay()
{
    Super::BeginPlay();
    auto Make=[&](const TCHAR* Name,const TCHAR* Path){
        auto* Mesh=NewObject<UCombatRigMesh>(GetOwner(),Name);Mesh->SetupAttachment(this);
        Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);Mesh->SetGenerateOverlapEvents(false);
        auto* Asset=LoadObject<USkeletalMesh>(nullptr,Path);
        if(ensureAlwaysMsgf(Asset&&Asset->GetSkeleton(),TEXT("Citadel mesh or skeleton missing: %s"),Path))Mesh->SetSkinnedAssetAndUpdate(Asset);
        Mesh->SetRelativeLocation(FVector(0,0,-88));
        Mesh->SetBoundsScale(2.f);Mesh->RegisterComponent();return Mesh;
    };
    Body=Make(TEXT("CitadelDuelist"),TEXT("/Game/Visual/Citadel/Meshes/SK_CitadelKnight.SK_CitadelKnight"));
    FirstPerson=Make(TEXT("CitadelArms"),TEXT("/Game/Visual/Citadel/Meshes/SK_CitadelArms.SK_CitadelArms"));
    FirstPerson->SetCastShadow(false);FirstPerson->SetVisibility(false);
    if(!ensureAlwaysMsgf(Body->GetSkinnedAsset(),TEXT("Citadel knight missing. Run Tools/ImportCitadelArt.py.")))return;
    const auto& Ref=Body->GetSkinnedAsset()->GetRefSkeleton();
    LocalPose=Ref.GetRefBonePose();Parents.SetNum(Ref.GetNum());
    for(int32 I=0;I<Ref.GetNum();++I){Parents[I]=Ref.GetParentIndex(I);BoneIndices.Add(Ref.GetBoneName(I),I);}
    BuildComponentPose();Reference=ComponentPose;
    for(const TCHAR* Name:{TEXT("upperarm_r"),TEXT("lowerarm_r"),TEXT("hand_r")}){
        const int32 Index=Bone(Name);if(Index!=INDEX_NONE)UE_LOG(LogTemp,Display,TEXT("CITADEL RIG %s %s"),Name,*Reference[Index].GetLocation().ToString());
    }
    Alloy=Body->CreateDynamicMaterialInstance(0);
    if(Alloy)FirstPerson->SetMaterial(0,Alloy);
}
void UKnightPresentation::SetFirstPerson(bool Value)
{
    if(bFirstPerson==Value||!Body||!FirstPerson)return;
    bFirstPerson=Value;Body->SetVisibility(!Value);FirstPerson->SetVisibility(Value);
}
void UKnightPresentation::BuildComponentPose()
{
    ComponentPose.SetNum(LocalPose.Num());
    for(int32 I=0;I<LocalPose.Num();++I)
        ComponentPose[I]=Parents[I]==INDEX_NONE?LocalPose[I]:LocalPose[I]*ComponentPose[Parents[I]];
}
void UKnightPresentation::Present(const mcl::Combatant& State,const mcl::Tuning& Tuning,bool Blue,float Reaction,float Dt)
{
    if(!Body||Reference.IsEmpty())return;
    if(Alloy&&Blue!=bBlue){bBlue=Blue;Alloy->SetVectorParameterValue(TEXT("BaseColor"),Blue?FLinearColor(.66f,.78f,.91f):FLinearColor(.91f,.82f,.70f));}
    const auto Pose=mcl::presentation::evaluate(State,Tuning);
    const FVector Position=V(State.position);
    FVector MoveDirection=Initialized?GetComponentTransform().InverseTransformVectorNoScale(Position-LastPosition).GetSafeNormal2D():FVector::ForwardVector;
    if(MoveDirection.IsNearlyZero())MoveDirection=FVector::ForwardVector;
    const double Distance=Initialized?FVector::Dist2D(Position,LastPosition):0.;
    Initialized=true;LastPosition=Position;
    const float Speed=Dt>SMALL_NUMBER?static_cast<float>(Distance/Dt):0.f;
    Travel=FMath::FInterpTo(Travel,Distance>200?0.f:FMath::Clamp(Speed/300.f,0.f,1.f),Dt,10.f);
    if(Distance<200)Gait+=static_cast<float>(Distance*.048);
    Fall=FMath::FInterpTo(Fall,State.health<=0?1.f:0.f,Dt,4.f);
    SetRelativeRotation(FRotator(Fall*83,0,Fall*12));SetRelativeLocation(FVector(0,0,-Fall*64));
    Body->SetRelativeLocation(FVector(0,0,-State.bodyHalfHeight));
    FirstPerson->SetRelativeLocation(FVector(0,0,-State.bodyHalfHeight));
    LocalPose=Body->GetSkinnedAsset()->GetRefSkeleton().GetRefBonePose();
    BuildComponentPose();
    auto RotateSubtree=[&](FName Name,FQuat Delta,FVector Shift=FVector::ZeroVector){
        const int32 Root=Bone(Name);if(Root==INDEX_NONE)return;
        const FVector Pivot=ComponentPose[Root].GetLocation();
        for(int32 I=Root;I<ComponentPose.Num();++I){
            int32 Parent=I;while(Parent!=INDEX_NONE&&Parent!=Root)Parent=Parents[Parent];
            if(Parent!=Root)continue;
            ComponentPose[I].SetLocation(Pivot+Delta.RotateVector(ComponentPose[I].GetLocation()-Pivot)+Shift);
            ComponentPose[I].SetRotation(Delta*ComponentPose[I].GetRotation());
        }
    };
    const float Bob=Travel*(FMath::Abs(FMath::Sin(Gait))*1.8f-1.8f);
    const double Crouch=FMath::Max(0.,88.-State.bodyHalfHeight);
    RotateSubtree(TEXT("pelvis"),FRotator(0,Pose.body.chestYaw*.18,0).Quaternion(),FVector(Pose.body.forwardLean*.35,0,State.eyeHeight-64.+Bob-Crouch));
    RotateSubtree(TEXT("spine_01"),FRotator(Pose.body.chestPitch*.4+Reaction*3,Pose.body.chestYaw*.35,0).Quaternion());
    RotateSubtree(TEXT("spine_02"),FRotator(Pose.body.chestPitch*.6+Reaction*5,Pose.body.chestYaw*.47,0).Quaternion(),FVector(Pose.body.forwardLean*.65,0,0));
    RotateSubtree(TEXT("head"),FRotator(State.view.pitch*.32,-Pose.body.chestYaw*.6,0).Quaternion());
    for(int32 Side=0;Side<2;++Side){
        const FString Suffix=Side==0?TEXT("r"):TEXT("l");
        const float Step=FMath::Sin(Gait+Side*PI)*Travel;
        RotateSubtree(FName(TEXT("thigh_")+Suffix),FRotator(Step*24,0,0).Quaternion());
        RotateSubtree(FName(TEXT("calf_")+Suffix),FRotator(-FMath::Max(0.f,-Step)*32,0,0).Quaternion());
        const int32 Upper=Bone(FName(TEXT("upperarm_")+Suffix)),Lower=Bone(FName(TEXT("lowerarm_")+Suffix)),Hand=Bone(FName(TEXT("hand_")+Suffix));
        if(Upper==INDEX_NONE||Lower==INDEX_NONE||Hand==INDEX_NONE)continue;
        const FTransform World=Body->GetComponentTransform();
        FVector Shoulder=ComponentPose[Upper].GetLocation();
        const FVector Grip=World.InverseTransformPosition(V(Pose.arms[Side].hand));
        const FVector RefUpper=Reference[Lower].GetLocation()-Reference[Upper].GetLocation();
        const FVector RefLower=Reference[Hand].GetLocation()-Reference[Lower].GetLocation();
        const FVector GripAxis=World.InverseTransformVectorNoScale(V(Pose.axis));
        const FVector GripEdge=World.InverseTransformVectorNoScale(V(Pose.edge));
        const FVector RestEdge=(RefUpper+RefLower).GetSafeNormal2D();
        const FQuat SourceFrame=FRotationMatrix::MakeFromZX(FVector::UpVector,RestEdge).ToQuat();
        const FQuat TargetFrame=FRotationMatrix::MakeFromZX(GripAxis,GripEdge*(Side==0?1.:-1.)).ToQuat();
        const FQuat HandDelta=TargetFrame*SourceFrame.Inverse();
        // Calibrate palm centre, not the wrist pivot, onto each grip contact.
        const FVector PalmOffset=RefLower.GetSafeNormal()*4.;
        const FVector Target=Grip-HandDelta.RotateVector(PalmOffset);
        const double Protraction=FMath::Clamp((Target-Shoulder).Size()-57.,0.,8.);
        Shoulder+=(Target-Shoulder).GetSafeNormal()*Protraction;
        const int32 Clavicle=Bone(FName(TEXT("clavicle_")+Suffix));
        if(Clavicle!=INDEX_NONE){
            const FVector Start=ComponentPose[Clavicle].GetLocation();
            const FVector Rest=Reference[Upper].GetLocation()-Reference[Clavicle].GetLocation();
            ComponentPose[Clavicle].SetRotation(FQuat::FindBetweenNormals(Rest.GetSafeNormal(),(Shoulder-Start).GetSafeNormal())*Reference[Clavicle].GetRotation());
        }
        const FVector Pole=World.InverseTransformVectorNoScale(V(Pose.arms[Side].elbow-Pose.arms[Side].shoulder));
        const auto M=[](FVector P){return mcl::Vec{P.X,P.Y,P.Z};};
        const auto Arm=mcl::presentation::solveArm(M(Shoulder),M(Target),M(Pole),32.,28.);
        const FVector Elbow=V(Arm.elbow);
        auto Link=[&](int32 Index,FVector Start,FVector End,FVector RestDirection){
            const FQuat Delta=FQuat::FindBetweenNormals(RestDirection.GetSafeNormal(),(End-Start).GetSafeNormal());
            ComponentPose[Index]=FTransform(Delta*Reference[Index].GetRotation(),Start,Reference[Index].GetScale3D());
            FVector Scale=Reference[Index].GetScale3D();const FVector Axis=Reference[Index].GetRotation().UnrotateVector(RestDirection).GetAbs();
            const int32 Major=Axis.X>Axis.Y?(Axis.X>Axis.Z?0:2):(Axis.Y>Axis.Z?1:2);
            Scale[Major]*=(End-Start).Size()/RestDirection.Size();ComponentPose[Index].SetScale3D(Scale);
        };
        Link(Upper,Shoulder,Elbow,RefUpper);Link(Lower,Elbow,Target,RefLower);
        ComponentPose[Hand]=FTransform(HandDelta*Reference[Hand].GetRotation(),Target,Reference[Hand].GetScale3D());
    }
    // Final leg IK preserves sole height as pelvis loading and crouch compress
    // the body. The courtyard has a flat gameplay floor; airborne characters
    // retain their own capsule-relative feet rather than snapping to the floor.
    if(State.health>0)for(int32 Side=0;Side<2;++Side){
        const FString Suffix=Side==0?TEXT("r"):TEXT("l");
        const int32 Thigh=Bone(FName(TEXT("thigh_")+Suffix)),Calf=Bone(FName(TEXT("calf_")+Suffix)),Foot=Bone(FName(TEXT("foot_")+Suffix));
        if(Thigh==INDEX_NONE||Calf==INDEX_NONE||Foot==INDEX_NONE)continue;
        const float Step=FMath::Sin(Gait+Side*PI);
        const FVector Hip=ComponentPose[Thigh].GetLocation();
        const FVector Ankle=Reference[Foot].GetLocation()+MoveDirection*(Step*19.*Travel)+FVector(0,0,FMath::Max(0.f,Step)*9.*Travel);
        const FVector Upper=Reference[Calf].GetLocation()-Reference[Thigh].GetLocation(),Lower=Reference[Foot].GetLocation()-Reference[Calf].GetLocation();
        const auto M=[](FVector P){return mcl::Vec{P.X,P.Y,P.Z};};
        const auto Leg=mcl::presentation::solveArm(M(Hip),M(Ankle),{1,Side==0?.15:-.15,0},Upper.Size(),Lower.Size());
        const FVector Knee=V(Leg.elbow);
        ComponentPose[Thigh]=FTransform(FQuat::FindBetweenNormals(Upper.GetSafeNormal(),(Knee-Hip).GetSafeNormal())*Reference[Thigh].GetRotation(),Hip,Reference[Thigh].GetScale3D());
        ComponentPose[Calf]=FTransform(FQuat::FindBetweenNormals(Lower.GetSafeNormal(),(Ankle-Knee).GetSafeNormal())*Reference[Calf].GetRotation(),Knee,Reference[Calf].GetScale3D());
        ComponentPose[Foot]=FTransform(Reference[Foot].GetRotation(),Ankle,Reference[Foot].GetScale3D());
    }
    Body->CommitComponentPose(ComponentPose);
    FirstPerson->CommitComponentPose(ComponentPose);
}
