#include "EXCombatPresentation.h"
#include "CombatRigMesh.h"
#include "MeleePresentationPose.h"
#include "Character/MeleeCharacter.h"
#include "Combat/CombatComponent.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "Dom/JsonObject.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
namespace {FVector V(mcl::Vec P){return {P.x,P.y,P.z};}}
UEXCombatPresentation::UEXCombatPresentation(){PrimaryComponentTick.bCanEverTick=false;}
void UEXCombatPresentation::BeginPlay()
{
    Super::BeginPlay();
    if(auto* C=Cast<AMeleeCharacter>(GetOwner())){
        if(Reload(C->Combat->Simulation)){
            auto& S=C->Combat->Simulation;S.reset(S.position,S.view,C->Combat->Tuning());
        }else UE_LOG(LogTemp,Error,TEXT("EXGAMEPLAY selection failed; fresh gameplay unavailable; approved EX assets are required"));
    }
}
bool UEXCombatPresentation::Reload(mcl::Combatant& State)
{
    FString Text,SelectionPath;
    const bool Override=FParse::Value(FCommandLine::Get(),TEXT("EXPreview="),SelectionPath);
    if(!Override)SelectionPath=FPaths::ProjectConfigDir()/TEXT("EXPreview.json");
    else if(FPaths::IsRelative(SelectionPath))SelectionPath=FPaths::ProjectDir()/SelectionPath;
    if (!FFileHelper::LoadFileToString(Text, *SelectionPath) || Text == SelectionText) return false;
    TSharedPtr<FJsonObject> Json;
    if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text), Json) || !Json.IsValid()) return false;
    FString NewRevision;
    const TArray<TSharedPtr<FJsonValue>>* Entries;
    if (!Json->TryGetStringField(TEXT("revision"), NewRevision) || NewRevision.IsEmpty() ||
        !Json->TryGetArrayField(TEXT("assets"), Entries) || Entries->Num()!=1) return false;
    TArray<USkeletalMesh*> NewMeshes;
    TArray<UAnimSequence*> NewAnimations;
    FString WeaponPath, WeaponText;
    TSharedPtr<FJsonObject> Motion;
    if (!Json->TryGetStringField(TEXT("weapon_motion"), WeaponPath) ||
        !FFileHelper::LoadFileToString(WeaponText, *(FPaths::ProjectDir()/WeaponPath)) ||
        !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(WeaponText), Motion)) return false;
    if(Override){
        FString ApprovedText,ApprovedMotion;TSharedPtr<FJsonObject> Approved;
        if(!FFileHelper::LoadFileToString(ApprovedText,*(FPaths::ProjectConfigDir()/TEXT("EXPreview.json")))||
            !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(ApprovedText),Approved)||!Approved.IsValid()||
            !Approved->TryGetStringField(TEXT("weapon_motion"),ApprovedMotion)||ApprovedMotion!=WeaponPath){
            UE_LOG(LogTemp,Error,TEXT("EXGAMEPLAY presentation override must retain approved weapon motion"));return false;
        }
    }
    const TArray<TSharedPtr<FJsonValue>>* Samples;
    double Rate;
    if (!Motion.IsValid() || !Motion->TryGetNumberField(TEXT("fps"),Rate) || Rate!=60. ||
        !Motion->TryGetArrayField(TEXT("samples"),Samples) || Samples->Num()!=154) return false;
    TArray<FTransform> NewWeaponFrames;
    mcl::EXWeaponMotion NewContactMotion;
    for (const auto& Sample : *Samples)
    {
        const TSharedPtr<FJsonObject>* Transform;
        const TArray<TSharedPtr<FJsonValue>> *Position, *Quaternion;
        const auto Object=Sample->AsObject();
        if(!Object.IsValid() || !Object->TryGetObjectField(TEXT("weapon_world"),Transform) ||
            !(*Transform)->TryGetArrayField(TEXT("translation_m"),Position) ||
            !(*Transform)->TryGetArrayField(TEXT("quaternion_wxyz"),Quaternion) || Position->Num()!=3 || Quaternion->Num()!=4) return false;
        const auto& P=*Position;const auto& Q=*Quaternion;
        for(const auto& Value:P) {double Number;if(!Value->TryGetNumber(Number)||!FMath::IsFinite(Number))return false;}
        for(const auto& Value:Q) {double Number;if(!Value->TryGetNumber(Number)||!FMath::IsFinite(Number))return false;}
        const FQuat Rotation(-Q[1]->AsNumber(),Q[2]->AsNumber(),-Q[3]->AsNumber(),Q[0]->AsNumber());
        if(FMath::Abs(Rotation.SizeSquared()-1.)>.001)return false;
        // Same handedness conversion as FFbxDataConverter: reflect Y, meters to cm.
        NewWeaponFrames.Add(FTransform(Rotation,
            FVector(P[0]->AsNumber()*100.,-P[1]->AsNumber()*100.,P[2]->AsNumber()*100.)));
        if(true)
        {
            const TSharedPtr<FJsonObject>* Rig;
            const TArray<TSharedPtr<FJsonValue>> *Base,*Tip,*RQ;
            if(!Object->TryGetObjectField(TEXT("weapon_rig_space"),Rig)||
                !(*Rig)->TryGetArrayField(TEXT("quaternion_wxyz"),RQ)||RQ->Num()!=4||
                !Object->TryGetArrayField(TEXT("blade_base_rig_space_m"),Base)||Base->Num()!=3||
                !Object->TryGetArrayField(TEXT("blade_tip_rig_space_m"),Tip)||Tip->Num()!=3)return false;
            for(const auto* Values:{Base,Tip,RQ})for(const auto& Value:*Values){double N;if(!Value->TryGetNumber(N)||!FMath::IsFinite(N))return false;}
            const mcl::Vec B{(*Base)[0]->AsNumber(),(*Base)[1]->AsNumber(),(*Base)[2]->AsNumber()};
            const mcl::Vec T{(*Tip)[0]->AsNumber(),(*Tip)[1]->AsNumber(),(*Tip)[2]->AsNumber()};
            mcl::EXWeaponMotion::Quaternion Qr{(*RQ)[0]->AsNumber(),(*RQ)[1]->AsNumber(),(*RQ)[2]->AsNumber(),(*RQ)[3]->AsNumber()};
            if(FMath::Abs(Qr.dot(Qr)-1.)>.001||FMath::Abs((T-B).length()*100.-103.5)>.01)return false;
            Qr=Qr*(1./FMath::Sqrt(Qr.dot(Qr)));
            if((B+Qr.rotate({0,0,1})*(T-B).length()-T).length()*100.>.001)return false;
            // The accepted viewer consumes world transforms. Refuse a candidate whose
            // rig-space contact motion would disagree with that same visible blade.
            const auto& Native=NewWeaponFrames.Last();
            const FVector ExpectedBase(B.x*100.,-B.y*100.,B.z*100.);
            const FVector ExpectedTip(T.x*100.,-T.y*100.,T.z*100.);
            const FVector RigEdge(Qr.rotate({1,0,0}).x,-Qr.rotate({1,0,0}).y,Qr.rotate({1,0,0}).z);
            if(FVector::Distance(Native.TransformVectorNoScale(FVector(1,0,0)),RigEdge)>.00001)return false;
            if(FVector::Distance(Native.GetLocation(),ExpectedBase)>.001 ||
                FVector::Distance(Native.TransformPosition(FVector(0,0,(T-B).length()*100.)),ExpectedTip)>.001)return false;
            NewContactMotion.frames.push_back({mcl::EXWeaponMotion::basis(B)*100.,Qr,(T-B).length()*100.});
        }
    }
    for (const auto& Entry : *Entries)
    {
        const auto Obj = Entry->AsObject();
        FString MeshPath, AnimationPath;
        if (!Obj.IsValid() || !Obj->TryGetStringField(TEXT("mesh"), MeshPath) || !Obj->TryGetStringField(TEXT("animation"), AnimationPath)) return false;
        auto* Mesh = LoadObject<USkeletalMesh>(nullptr, *MeshPath);
        auto* Animation = LoadObject<UAnimSequence>(nullptr, *AnimationPath);
        if (!Mesh || !Animation || Mesh->GetSkeleton() != Animation->GetSkeleton() ||
            FMath::Abs(Animation->GetPlayLength()-2.55) > .02) return false;
        const auto& Ref=Mesh->GetRefSkeleton();TMap<FName,int32> Joints;
        for(int32 J=0;J<Ref.GetNum();++J)Joints.Add(BindingName(Ref.GetBoneName(J)),J);
        for(const TCHAR* Side:{TEXT("r"),TEXT("l")}){
            int32 Chain[3];int32 K=0;
            for(const TCHAR* Prefix:{TEXT("upperarm01_"),TEXT("lowerarm01_"),TEXT("wrist_")}){
                const auto* Joint=Joints.Find(FName(*(FString(Prefix)+Side)));if(!Joint)return false;Chain[K++]=*Joint;
            }
            for(int32 C=1;C<3;++C){int32 Parent=Ref.GetParentIndex(Chain[C]);
                while(Parent!=INDEX_NONE&&Parent!=Chain[C-1])Parent=Ref.GetParentIndex(Parent);
                if(Parent==INDEX_NONE)return false;}
        }
        NewMeshes.Add(Mesh); NewAnimations.Add(Animation);
    }

    auto* WeaponAsset=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/EXPreview/EX_v002/EXPreviewWeapon.EXPreviewWeapon"));
    auto* ArmsMaterial=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/EXPreview/EX_v002/Study_WarmClay.Study_WarmClay"));
    auto* SteelMaterial=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/EXPreview/EX_v002/EX_Steel.EX_Steel"));
    if(!WeaponAsset||!ArmsMaterial||!SteelMaterial)return false;
    for(USkeletalMeshComponent* Mesh:Meshes)Mesh->DestroyComponent();
    for(UCombatRigMesh* Output:Outputs)Output->DestroyComponent();
    Meshes.Empty();Outputs.Empty();LastPose.Empty();FromPose.Empty();LastCameraPose.Empty();FromCameraPose.Empty();
    for(int32 I=0;I<NewMeshes.Num();++I){
        auto* Mesh=NewObject<USkeletalMeshComponent>(GetOwner());
        Mesh->SetSkeletalMeshAsset(NewMeshes[I]);Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Mesh->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
        Mesh->RegisterComponent();Mesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);
        Mesh->SetAnimation(NewAnimations[I]);Mesh->SetComponentTickEnabled(false);
        Mesh->SetVisibility(false);Mesh->SetCastShadow(false);Meshes.Add(Mesh);
        auto* Output=NewObject<UCombatRigMesh>(GetOwner());
        Output->SetSkinnedAssetAndUpdate(NewMeshes[I]);Output->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Output->SetGenerateOverlapEvents(false);Output->SetBoundsScale(5.f);
        Output->SetMaterial(0,ArmsMaterial);
        Output->SetCastShadow(false);Output->RegisterComponent();Outputs.Add(Output);
    }
    if(!Weapon){Weapon=NewObject<UStaticMeshComponent>(GetOwner());
        Weapon->SetStaticMesh(WeaponAsset);
        Weapon->SetMaterial(0,SteelMaterial);
        Weapon->SetCollisionEnabled(ECollisionEnabled::NoCollision);Weapon->SetGenerateOverlapEvents(false);Weapon->RegisterComponent();}
    if(!Weapon->GetStaticMesh())return false;
    State.exMotion=std::make_shared<const mcl::EXWeaponMotion>(std::move(NewContactMotion));
    State.state.exEnabled=true;
    WeaponFrames=MoveTemp(NewWeaponFrames);SelectionText=Text;Revision=NewRevision;
    UE_LOG(LogTemp,Display,TEXT("EXGAMEPLAY selected=%s source=%s animation=%s; neutral=1x branches=provisional external=fresh-CF-body-candidate"),
        *Revision,*WeaponPath,*NewAnimations[0]->GetPathName());
    return true;
}
bool UEXCombatPresentation::Present(mcl::Combatant& State,float Dt,bool FirstPerson)
{
    BranchGripError=BranchAnchorError=0.;BranchReachScale=1.;
    if(!Ready())return false;
    SetWeaponVisible(true);
    Poll+=Dt;
    if(Poll>=1.&&State.state.phase==mcl::Phase::Idle&&State.returnAge>.25){Poll=0.;Reload(State);}
    const auto& S=State.state;
    const bool Authored=S.exActive&&(S.phase==mcl::Phase::Windup||S.phase==mcl::Phase::Release||
        (S.phase==mcl::Phase::Recovery&&S.last!=mcl::Resolution::Wall&&S.last!=mcl::Resolution::Parry));
    // Branch candidates reuse a grip pose, driven by the canonical weapon. They
    // never play the accepted neutral action at a legacy attack rate.
    // Ready is a compact neutral grip. Transferring the loaded windup pose to
    // the parry blade carries the upper arm across the first-person camera.
    const double Time=Authored?State.exSourceTime:mcl::EXWeaponMotion::Start;
    const double Frame=FMath::Clamp(Time*60.,0.,153.);const int32 A=int32(Frame),B=FMath::Min(A+1,153);
    FTransform NativeWeapon;NativeWeapon.Blend(WeaponFrames[A],WeaponFrames[B],Frame-A);
    const auto& P=State.weapon;
    const FVector Axis=V(P.tip-P.hilt).GetSafeNormal();
    const FVector Edge=P.edge.length()>.5?V(P.edge):V(mcl::weaponEdge(P.tip-P.hilt,State.view));
    const FTransform Canonical(FRotationMatrix::MakeFromZX(Axis,Edge).ToQuat(),V(P.hilt));
    const FTransform CameraWorld(FRotator(State.exSampleView.pitch,State.exSampleView.yaw,0),V(State.exSampleEye));
    Weapon->SetWorldTransform(FTransform(Canonical.GetRotation(),Canonical.GetLocation(),FVector(1,1,(P.tip-P.hilt).length()/103.5)));
    BladeError=FVector::Distance(Weapon->GetComponentTransform().TransformPosition(FVector(0,0,103.5)),V(P.tip));
    if(S.phase!=LastPhase||S.serial!=LastSerial||Authored!=LastAuthored){
        FromPose=LastPose;FromCameraPose=LastCameraPose;TransitionAge=0;LastPhase=S.phase;LastSerial=S.serial;LastAuthored=Authored;
    }
    TransitionAge=State.exTransitionAge;
    // The provisional ready grip differs from the authored clip: bridge entry
    // so its corrected left hand does not flip when the attack starts.
    const double Weight=Authored&&S.phase!=mcl::Phase::Windup?1.:
        mcl::smooth((Authored?S.elapsed:TransitionAge)/ (Authored?.10:.18));
    for(int32 I=0;I<Meshes.Num();++I){
        auto* Mesh=Meshes[I].Get();Mesh->SetPosition(float(Time),false);Mesh->TickAnimation(0.f,false);Mesh->RefreshBoneTransforms();
        const auto& SourcePose=Mesh->GetComponentSpaceTransforms();
        const auto& Ref=Mesh->GetSkeletalMeshAsset()->GetRefSkeleton();
        int32 LeftWrist=INDEX_NONE;
        for(int32 J=0;J<Ref.GetNum();++J)if(BindingName(Ref.GetBoneName(J))==FName(TEXT("wrist_l"))){LeftWrist=J;break;}
        const auto IsLeftHand=[&](int32 Joint){
            if(LeftWrist==INDEX_NONE)return false;
            while(Joint!=INDEX_NONE&&Joint!=LeftWrist)Joint=Ref.GetParentIndex(Joint);
            return Joint==LeftWrist;
        };
        constexpr double ProvisionalLeftWristRollDeg=180.;
        const FQuat ReadyLeftRoll(FVector::UpVector,FMath::DegreesToRadians(ProvisionalLeftWristRollDeg));
        const FVector LeftGripPivot=LeftWrist==INDEX_NONE?FVector::ZeroVector:
            FVector(0,0,NativeWeapon.InverseTransformPosition(SourcePose[LeftWrist].GetLocation()).Z);
        TArray<FTransform> Pose;Pose.SetNum(SourcePose.Num());
        for(int32 J=0;J<Pose.Num();++J){
            // Weapon-relative pose transfer keeps the native grip, full roll and
            // animated joint translations. Approved motion is exact at weight 1.
            FTransform Target=SourcePose[J].GetRelativeTransform(NativeWeapon);
            // Correct the provisional left-hand target in weapon space before
            // blending and before HandGoals are made. Authored targets stay native.
            if(!Authored&&IsLeftHand(J)){
                Target.SetLocation(LeftGripPivot+ReadyLeftRoll.RotateVector(Target.GetLocation()-LeftGripPivot));
                Target.SetRotation((ReadyLeftRoll*Target.GetRotation()).GetNormalized());
            }
            if(Weight<1.&&FromPose.Num()==Pose.Num())Pose[J].Blend(FromPose[J],Target,Weight);else Pose[J]=Target;
        }
        TMap<int32,FVector> AnchorGoals,GripGoals;
        if(!Authored){
            // Source UE +Y forward becomes camera +X; the source camera pivot
            // is (11.5,0,168) in that basis. Shoulders follow this sampled camera,
            // while hands retain the existing canonical weapon-relative goals.
            const FTransform NativeToCamera(FRotator(0,-90,0),FVector(-11.5,0,-168));
            TArray<FTransform> ReadyPose,CameraPose,HandGoals;
            ReadyPose.SetNum(Pose.Num());CameraPose.SetNum(Pose.Num());HandGoals.SetNum(Pose.Num());
            TMap<FName,int32> Indices;
            for(int32 J=0;J<Pose.Num();++J){
                Indices.Add(BindingName(Ref.GetBoneName(J)),J);
                ReadyPose[J]=SourcePose[J]*NativeToCamera;
                HandGoals[J]=(Pose[J]*Canonical).GetRelativeTransform(CameraWorld);
            }
            for(int32 J=0;J<Pose.Num();++J){
                if(Weight<1.&&FromCameraPose.Num()==Pose.Num())CameraPose[J].Blend(FromCameraPose[J],ReadyPose[J],Weight);
                else CameraPose[J]=ReadyPose[J];
            }
            const auto Descendant=[&](int32 Joint,int32 Root){
                while(Joint!=INDEX_NONE&&Joint!=Root)Joint=Ref.GetParentIndex(Joint);
                return Joint==Root;
            };
            const auto MoveChain=[&](int32 Root,FQuat Rotation,double Scale){
                const FVector Pivot=CameraPose[Root].GetLocation();
                for(int32 J=0;J<CameraPose.Num();++J)if(Descendant(J,Root)){
                    CameraPose[J].SetLocation(Pivot+Rotation.RotateVector(CameraPose[J].GetLocation()-Pivot)*Scale);
                    CameraPose[J].SetRotation((Rotation*CameraPose[J].GetRotation()).GetNormalized());
                }
            };
            const auto M=[](FVector Point){return mcl::Vec{Point.X,Point.Y,Point.Z};};
            for(const TCHAR* Side:{TEXT("r"),TEXT("l")}){
                const auto Find=[&](const TCHAR* Prefix){const auto* Index=Indices.Find(FName(*(FString(Prefix)+Side)));return Index?*Index:INDEX_NONE;};
                const int32 Upper=Find(TEXT("upperarm01_")),Lower=Find(TEXT("lowerarm01_")),Wrist=Find(TEXT("wrist_"));
                if(Upper==INDEX_NONE||Lower==INDEX_NONE||Wrist==INDEX_NONE)continue;
                const FVector Shoulder=CameraPose[Upper].GetLocation(),Goal=HandGoals[Wrist].GetLocation();
                AnchorGoals.Add(Upper,CameraWorld.TransformPosition(Shoulder));
                GripGoals.Add(Wrist,CameraWorld.TransformPosition(Goal));
                const auto Length=[&](int32 First,int32 Second){
                    const double ReadyLength=FVector::Distance(ReadyPose[First].GetLocation(),ReadyPose[Second].GetLocation());
                    return FromCameraPose.Num()==Pose.Num()?FMath::Lerp(FVector::Distance(FromCameraPose[First].GetLocation(),FromCameraPose[Second].GetLocation()),ReadyLength,Weight):ReadyLength;
                };
                // Source-derived lengths and the blended elbow plane preserve
                // entry continuity. Any unreachable grip stretches only this
                // provisional mesh; split segment translations share that fit.
                const auto Fit=mcl::presentation::solveArm(M(Shoulder),M(Goal),M(CameraPose[Lower].GetLocation()-Shoulder),Length(Upper,Lower),Length(Lower,Wrist));
                BranchReachScale=FMath::Max(BranchReachScale,Fit.reachScale);
                const FVector Elbow=V(Fit.elbow);
                FVector Before=CameraPose[Lower].GetLocation()-Shoulder,After=Elbow-Shoulder;
                MoveChain(Upper,FQuat::FindBetweenVectors(Before,After),After.Size()/FMath::Max(Before.Size(),1.e-6));
                Before=CameraPose[Wrist].GetLocation()-CameraPose[Lower].GetLocation();After=Goal-CameraPose[Lower].GetLocation();
                MoveChain(Lower,FQuat::FindBetweenVectors(Before,After),After.Size()/FMath::Max(Before.Size(),1.e-6));
                for(int32 J=0;J<CameraPose.Num();++J)if(Descendant(J,Wrist))CameraPose[J]=HandGoals[J];
            }
            for(int32 J=0;J<Pose.Num();++J)Pose[J]=(CameraPose[J]*CameraWorld).GetRelativeTransform(Canonical);
        }
        LastPose=Pose;LastCameraPose.SetNum(Pose.Num());HandBinding.Empty();
        for(int32 J=0;J<Pose.Num();++J)LastCameraPose[J]=(Pose[J]*Canonical).GetRelativeTransform(CameraWorld);
        for(int32 J=0;J<Pose.Num();++J){const auto Name=BindingName(Ref.GetBoneName(J));const FString N=Name.ToString();
            if(N.StartsWith(TEXT("wrist"))||N.StartsWith(TEXT("finger"))||N.StartsWith(TEXT("metacarpal")))HandBinding.Add(Name,Pose[J]);}

        Outputs[I]->SetWorldTransform(Canonical);
        Outputs[I]->CommitComponentPose(Pose);Outputs[I]->SetVisibility(FirstPerson);
        for(const auto& Goal:AnchorGoals)BranchAnchorError=FMath::Max(BranchAnchorError,FVector::Distance(Outputs[I]->GetBoneTransform(Goal.Key).GetLocation(),Goal.Value));
        for(const auto& Goal:GripGoals)BranchGripError=FMath::Max(BranchGripError,FVector::Distance(Outputs[I]->GetBoneTransform(Goal.Key).GetLocation(),Goal.Value));
        PoseError=0.;
        if(Authored&&Weight>=1.)for(int32 J=0;J<Pose.Num();++J){
            const FVector Expected=Canonical.TransformPosition(NativeWeapon.InverseTransformPosition(SourcePose[J].GetLocation()));
            PoseError=FMath::Max(PoseError,FVector::Distance(Outputs[I]->GetBoneTransform(J).GetLocation(),Expected));
        }
    }
    return true;
}
void UEXCombatPresentation::SetWeaponVisible(bool Visible){if(Weapon)Weapon->SetVisibility(Visible);}

bool UEXCombatPresentation::GetVisibleBlade(FVector& Base,FVector& Tip) const
{
    if(!Weapon||!Weapon->IsVisible())return false;
    const FTransform Transform=Weapon->GetComponentTransform();
    Base=Transform.GetLocation();Tip=Transform.TransformPosition(FVector(0,0,103.5));return true;
}
