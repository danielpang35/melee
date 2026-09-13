#include "TPCombatPresentation.h"
#include "TPPresentationPolicy.h"
#include "MeleePresentationPose.h"
#include "CombatRigMesh.h"
#include "EXCombatPresentation.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Serialization/JsonSerializer.h"
#include "Dom/JsonObject.h"

namespace {
FVector TPVec(mcl::Vec P){return {P.x,P.y,P.z};}
bool Numbers(const TSharedPtr<FJsonObject>& Object,const TCHAR* Key,int32 Count,TArray<double>& Out)
{
    const TArray<TSharedPtr<FJsonValue>>* Values=nullptr;
    if(!Object.IsValid()||!Object->TryGetArrayField(Key,Values)||Values->Num()!=Count)return false;
    Out.Empty();for(const auto& Value:*Values){double N;if(!Value->TryGetNumber(N)||!FMath::IsFinite(N))return false;Out.Add(N);}return true;
}
bool ReadJson(const FString& Path,TSharedPtr<FJsonObject>& Object)
{
    FString Text;return FFileHelper::LoadFileToString(Text,*Path)&&FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text),Object)&&Object.IsValid();
}
FVector Point(const TArray<double>& P){return FVector(P[0]*100.,-P[1]*100.,P[2]*100.);}
FQuat Rotation(const TArray<double>& Q){return FQuat(-Q[1],Q[2],-Q[3],Q[0]);}
FString ProjectFile(FString Path){return FPaths::IsRelative(Path)?FPaths::ConvertRelativePathToFull(FPaths::ProjectDir()/Path):Path;}
}

void UTPCombatPresentation::Initialize(USkeletalMesh* FallbackMesh)
{
    Fallback=FallbackMesh;
    if(!FParse::Value(FCommandLine::Get(),TEXT("TPPreview="),SelectionPath))return;
    SelectionPath=ProjectFile(SelectionPath);Reload();
}
bool UTPCombatPresentation::Reload()
{
    FString Text;
    if(SelectionPath.IsEmpty()||!FFileHelper::LoadFileToString(Text,*SelectionPath))return false;
    if(Text==SelectionText||Text==RejectedText)return false;
    const auto Reject=[&](const TCHAR* Reason){RejectedText=Text;UE_LOG(LogTemp,Error,TEXT("TPPROOF rejected %s: %s; previous selection retained"),*SelectionPath,Reason);return false;};
    TSharedPtr<FJsonObject> Json;
    if(!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text),Json)||!Json.IsValid())return Reject(TEXT("invalid selection JSON"));
    FString NewRevision,MeshPath,AnimationPath,MotionPath,SkeletonPath,WeaponMeshPath;
    if(!Json->TryGetStringField(TEXT("revision"),NewRevision)||NewRevision.IsEmpty()||
        !Json->TryGetStringField(TEXT("mesh"),MeshPath)||!Json->TryGetStringField(TEXT("animation"),AnimationPath)||
        !Json->TryGetStringField(TEXT("weapon_motion"),MotionPath)||!Json->TryGetStringField(TEXT("skeleton_motion"),SkeletonPath)||
        !Json->TryGetStringField(TEXT("weapon_mesh"),WeaponMeshPath))return Reject(TEXT("missing selection field"));
    mcl::TPSourceBinding NewBinding;
    bool NewContactBinding=false;
    if(Json->HasField(TEXT("contact_binding"))&&!Json->TryGetBoolField(TEXT("contact_binding"),NewContactBinding))return Reject(TEXT("invalid contact binding"));
    if(Json->HasField(TEXT("profile"))){
        FString Profile;
        if(!Json->TryGetStringField(TEXT("profile"),Profile)||Profile!=TEXT("TP_native_attack_age_v1"))return Reject(TEXT("unsupported source binding profile"));
        NewBinding.attackAge=true;
        if(!Json->TryGetNumberField(TEXT("fps"),NewBinding.rate)||
            !Json->TryGetNumberField(TEXT("duration_s"),NewBinding.duration)||
            !Json->TryGetNumberField(TEXT("idle_source_s"),NewBinding.idle)||!NewBinding.valid())return Reject(TEXT("invalid source binding metadata"));
    }else if(Json->HasField(TEXT("fps"))||Json->HasField(TEXT("duration_s"))||Json->HasField(TEXT("idle_source_s")))return Reject(TEXT("source binding metadata requires explicit profile"));
    const int32 FrameCount=NewBinding.frames();
    TSharedPtr<FJsonObject> Motion,Source;
    if(!ReadJson(ProjectFile(MotionPath),Motion)||!ReadJson(ProjectFile(SkeletonPath),Source))return Reject(TEXT("missing source samples"));
    double Rate=0;const TArray<TSharedPtr<FJsonValue>>* Samples=nullptr;
    if(!Motion->TryGetNumberField(TEXT("fps"),Rate)||Rate!=NewBinding.rate||!Motion->TryGetArrayField(TEXT("samples"),Samples)||Samples->Num()!=FrameCount)return Reject(TEXT("weapon sample count/rate differs from binding"));
    TArray<FTransform> NewFrames;
    for(int32 I=0;I<Samples->Num();++I){
        const auto Row=(*Samples)[I]->AsObject();const TSharedPtr<FJsonObject>* W=nullptr;
        double Time=0;TArray<double> P,Q,Scale,Base,Tip;
        if(!Row.IsValid()||!Row->TryGetNumberField(TEXT("time_s"),Time)||!FMath::IsFinite(Time)||FMath::Abs(Time-I/NewBinding.rate)>1.e-8||
            !Row->TryGetObjectField(TEXT("weapon_world"),W)||!Numbers(*W,TEXT("translation_m"),3,P)||
            !Numbers(*W,TEXT("quaternion_wxyz"),4,Q)||!Numbers(*W,TEXT("scale"),3,Scale)||
            !Numbers(Row,TEXT("blade_base_world_m"),3,Base)||!Numbers(Row,TEXT("blade_tip_world_m"),3,Tip))return Reject(TEXT("invalid weapon sample"));
        const FQuat R=Rotation(Q);
        if(FMath::Abs(R.SizeSquared()-1.)>.001||FMath::Abs(Scale[0]-1.)>1.e-5||FMath::Abs(Scale[1]-1.)>1.e-5||FMath::Abs(Scale[2]-1.)>1.e-5)return Reject(TEXT("weapon rotation or scale contract"));
        const FTransform Transform(R.GetNormalized(),Point(P));
        if(FVector::Distance(Transform.GetLocation(),Point(Base))>.001||FVector::Distance(Transform.TransformPosition(FVector(0,0,103.5)),Point(Tip))>.001)return Reject(TEXT("weapon origin/+Z/103.5cm marker mismatch"));
        NewFrames.Add(Transform);
    }
    auto* Mesh=LoadObject<USkeletalMesh>(nullptr,*MeshPath);
    auto* Animation=LoadObject<UAnimSequence>(nullptr,*AnimationPath);
    auto* WeaponAsset=LoadObject<UStaticMesh>(nullptr,*WeaponMeshPath);
    auto* Surface=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/CharacterReset/CF_v001/CF_StudySurface.CF_StudySurface"));
    if(!Fallback||!Mesh||!Animation||!Mesh->GetSkeleton()||Mesh->GetSkeleton()!=Animation->GetSkeleton()||
        FMath::Abs(Animation->GetPlayLength()-NewBinding.duration)>.0001||!WeaponAsset||!Surface)return Reject(TEXT("native asset/skeleton/duration/material mismatch"));
    const auto& Ref=Mesh->GetRefSkeleton();const auto& FallbackRef=Fallback->GetRefSkeleton();
    // KN and CF share the102 deform-bone hierarchy; only the exported armature
    // object root has a different name. This explicit alias does not retarget.
    const auto NativeName=[&](int32 Index){
        const FName Name=UEXCombatPresentation::BindingName(Ref.GetBoneName(Index));
        return NewBinding.attackAge&&Ref.GetParentIndex(Index)==INDEX_NONE&&Name==FName(TEXT("kn01_rig"))
            ? FName(TEXT("cf01_characterrig")):Name;
    };
    TMap<FName,int32> NativeNames,FallbackNames;TArray<int32> NewFallbackIndices;
    for(int32 I=0;I<FallbackRef.GetNum();++I)FallbackNames.Add(UEXCombatPresentation::BindingName(FallbackRef.GetBoneName(I)),I);
    TArray<FTransform> Rest=Ref.GetRefBonePose();
    for(int32 I=0;I<Ref.GetNum();++I){
        const FName Name=NativeName(I);NativeNames.Add(Name,I);
        const int32* Other=FallbackNames.Find(Name);if(!Other)return Reject(TEXT("TP hierarchy differs from CF fallback"));
        const int32 Parent=Ref.GetParentIndex(I),OtherParent=FallbackRef.GetParentIndex(*Other);
        if((Parent==INDEX_NONE)!=(OtherParent==INDEX_NONE)||
            (Parent!=INDEX_NONE&&NativeName(Parent)!=UEXCombatPresentation::BindingName(FallbackRef.GetBoneName(OtherParent))))return Reject(TEXT("TP parent hierarchy differs from CF"));
        NewFallbackIndices.Add(*Other);if(Parent!=INDEX_NONE)Rest[I]=Rest[I]*Rest[Parent];
    }
    if(NewContactBinding){
        if(!NewBinding.attackAge)return Reject(TEXT("contact binding requires attack-age source"));
        for(const TCHAR* Name:{TEXT("spine05"),TEXT("upperarm01_r"),TEXT("lowerarm01_r"),TEXT("wrist_r"),TEXT("upperarm01_l"),TEXT("lowerarm01_l"),TEXT("wrist_l")})
            if(!NativeNames.Contains(FName(Name)))return Reject(TEXT("contact binding requires complete arm chains and spine"));
    }
    const TArray<TSharedPtr<FJsonValue>>* SourceSamples=nullptr;
    if(!Source->TryGetNumberField(TEXT("fps"),Rate)||Rate!=NewBinding.rate||!Source->TryGetArrayField(TEXT("samples"),SourceSamples)||SourceSamples->Num()!=FrameCount)return Reject(TEXT("source fidelity sample count/rate differs from binding"));
    auto* NewSampler=NewObject<USkeletalMeshComponent>(GetOwner());
    NewSampler->SetSkeletalMeshAsset(Mesh);NewSampler->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    NewSampler->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    NewSampler->RegisterComponent();NewSampler->SetAnimationMode(EAnimationMode::AnimationSingleNode);
    NewSampler->SetAnimation(Animation);NewSampler->SetComponentTickEnabled(false);NewSampler->SetVisibility(false);NewSampler->SetCastShadow(false);
    double MaxPosition=0,MaxRotation=0;
    bool SourceValid=true;
    for(int32 I=0;I<FrameCount&&SourceValid;++I){
        const auto Row=(*SourceSamples)[I]->AsObject();const TSharedPtr<FJsonObject>* Bones=nullptr;double Time=0;
        if(!Row.IsValid()||!Row->TryGetNumberField(TEXT("time_s"),Time)||!FMath::IsFinite(Time)||FMath::Abs(Time-I/NewBinding.rate)>1.e-8||!Row->TryGetObjectField(TEXT("bones"),Bones)||(*Bones)->Values.Num()!=102){SourceValid=false;break;}
        NewSampler->SetPosition(float(I/NewBinding.rate),false);NewSampler->TickAnimation(0.f,false);NewSampler->RefreshBoneTransforms();
        const auto& Pose=NewSampler->GetComponentSpaceTransforms();
        if(Pose.Num()!=Ref.GetNum()){SourceValid=false;break;}
        for(const auto& Entry:(*Bones)->Values){
            const auto Bone=Entry.Value->AsObject();TArray<double> P,Q;
            const int32* J=NativeNames.Find(UEXCombatPresentation::BindingName(FName(*Entry.Key)));
            if(!J||!Numbers(Bone,TEXT("head_world_m"),3,P)||!Numbers(Bone,TEXT("deformation_quaternion_wxyz"),4,Q)||Pose[*J].ContainsNaN()){SourceValid=false;break;}
            const FQuat Expected=Rotation(Q),Actual=(Pose[*J].GetRotation()*Rest[*J].GetRotation().Inverse()).GetNormalized();
            if(FMath::Abs(Expected.SizeSquared()-1.)>.001){SourceValid=false;break;}
            MaxPosition=FMath::Max(MaxPosition,FVector::Distance(Pose[*J].GetLocation(),Point(P)));
            MaxRotation=FMath::Max(MaxRotation,FMath::RadiansToDegrees(Actual.AngularDistance(Expected.GetNormalized())));
        }
    }
    if(!SourceValid||MaxPosition>.10||MaxRotation>.15){NewSampler->DestroyComponent();UE_LOG(LogTemp,Error,TEXT("TPPROOF native fidelity position_cm=%.9f rotation_deg=%.9f"),MaxPosition,MaxRotation);return Reject(TEXT("source-to-native fidelity failed"));}
    if(Sampler)Sampler->DestroyComponent();if(Output)Output->DestroyComponent();
    Sampler=NewSampler;Output=NewObject<UCombatRigMesh>(GetOwner());Output->SetSkinnedAssetAndUpdate(Mesh);
    Output->SetCollisionEnabled(ECollisionEnabled::NoCollision);Output->SetGenerateOverlapEvents(false);Output->SetBoundsScale(4.f);
    Output->SetMaterial(0,Surface);Output->RegisterComponent();Output->SetVisibility(false);
    if(!Weapon){Weapon=NewObject<UStaticMeshComponent>(GetOwner());
        Weapon->SetCollisionEnabled(ECollisionEnabled::NoCollision);Weapon->SetGenerateOverlapEvents(false);Weapon->RegisterComponent();}
    Weapon->SetStaticMesh(WeaponAsset);
    Weapon->SetVisibility(false);
    WeaponFrames=MoveTemp(NewFrames);FallbackIndices=MoveTemp(NewFallbackIndices);Revision=NewRevision;SelectionText=Text;RejectedText.Empty();
    SourceBinding=NewBinding;
    GaitRotations.Empty();
    GaitValid=false;
    ContactBinding=NewContactBinding;
    ImportPoseErrorCm=MaxPosition;ImportRotationErrorDegrees=MaxRotation;Selected=true;Initialized=false;Transition=false;
    UE_LOG(LogTemp,Display,TEXT("TPPROOF selected=%s native_position_cm=%.9f native_rotation_deg=%.9f attack_age=%d fps=%.6f duration=%.9f; simulation unchanged"),*Revision,MaxPosition,MaxRotation,SourceBinding.attackAge,SourceBinding.rate,SourceBinding.duration);
    return true;
}
void UTPCombatPresentation::Hide(){Active=false;GaitValid=false;if(Output)Output->SetVisibility(false);if(Weapon)Weapon->SetVisibility(false);}
bool UTPCombatPresentation::Present(const mcl::Combatant& State,float Dt,const TArray<FTransform>& FallbackPose,const FTransform& BodyWorld)
{
    Poll+=Dt;if(!SelectionPath.IsEmpty()&&Poll>=1.&&State.state.phase==mcl::Phase::Idle&&State.exTransitionAge>.25){Poll=0;Reload();}
    if(!Selected||!Sampler||!Output||FallbackPose.IsEmpty()){Hide();return false;}
    const auto& S=State.state;
    const auto Sample=SourceBinding.sample(S,State.exSourceTime,State.exTransitionAge);
    Authored=Sample.authored;
    const bool Native=Authored||S.phase==mcl::Phase::Idle;
    SourceTime=Sample.time;
    Sampler->SetPosition(float(SourceTime),false);Sampler->TickAnimation(0.f,false);Sampler->RefreshBoneTransforms();
    const auto& NativePose=Sampler->GetComponentSpaceTransforms();
    const int32 LastFrame=WeaponFrames.Num()-1;
    const double Frame=FMath::Clamp(SourceTime*SourceBinding.rate,0.,double(LastFrame));const int32 A=int32(Frame),B=FMath::Min(A+1,LastFrame);
    FTransform NativeWeapon;NativeWeapon.Blend(WeaponFrames[A],WeaponFrames[B],Frame-A);
    const auto& P=State.weapon;
    const FVector Axis=TPVec(P.tip-P.hilt).GetSafeNormal();
    const FVector Edge=P.edge.length()>.5?TPVec(P.edge):TPVec(mcl::weaponEdge(P.tip-P.hilt,State.exSampleView));
    const FTransform Canonical(FRotationMatrix::MakeFromZX(Axis,Edge).ToQuat(),TPVec(P.hilt),FVector(1,1,(P.tip-P.hilt).length()/103.5));
    TArray<FTransform> Target=NativePose;
    if(!Native)for(int32 I=0;I<Target.Num();++I){if(!FallbackIndices.IsValidIndex(I)||!FallbackPose.IsValidIndex(FallbackIndices[I])){Hide();return false;}Target[I]=FallbackPose[FallbackIndices[I]];}
    FTransform TargetWeapon=Native?NativeWeapon:Canonical.GetRelativeTransform(BodyWorld);
    GripErrorCm=0;ArmReachScale=1;
    if(ContactBinding&&Native)BindContactPose(Target,NativeWeapon,TargetWeapon,BodyWorld,State);
    if(ContactBinding&&Native){
        // Add the existing gait in parent-local space; retain native pelvis/stance.
        // Filtering the delta lets steps settle instead of freezing at key release.
        const auto& Ref=Sampler->GetSkeletalMeshAsset()->GetRefSkeleton();
        const auto& FallbackRef=Fallback->GetRefSkeleton();
        const TArray<FTransform> BasePose=Target;
        const double Travel=GaitValid?FVector::Dist2D(BodyWorld.GetLocation(),LastBodyPosition):0.;
        if(!GaitValid||Travel>=100.||(LastSerial!=0&&S.serial==0))GaitRotations.Empty();
        const bool Moving=GaitValid&&Travel>.01&&Travel<100.;
        LastBodyPosition=BodyWorld.GetLocation();GaitValid=true;
        if(GaitRotations.Num()!=Target.Num())GaitRotations.Init(FQuat::Identity,Target.Num());
        for(int32 I=0;I<Target.Num();++I){
            bool Leg=false;
            for(int32 J=I;J!=INDEX_NONE;J=Ref.GetParentIndex(J)){
                const FName Name=UEXCombatPresentation::BindingName(Ref.GetBoneName(J));
                if(Name==FName(TEXT("upperleg01_r"))||Name==FName(TEXT("upperleg01_l"))){Leg=true;break;}
            }
            if(!Leg)continue;
            const int32 Parent=Ref.GetParentIndex(I),Other=FallbackIndices[I],OtherParent=FallbackRef.GetParentIndex(Other);
            if(Parent==INDEX_NONE||OtherParent==INDEX_NONE)continue;
            const FTransform Local=FallbackPose[Other].GetRelativeTransform(FallbackPose[OtherParent]);
            const FQuat Delta=Moving?(Local.GetRotation()*FallbackRef.GetRefBonePose()[Other].GetRotation().Inverse()).GetNormalized():FQuat::Identity;
            GaitRotations[I]=FQuat::Slerp(GaitRotations[I],Delta,1.-FMath::Exp(-12.*Dt)).GetNormalized();
            FTransform NativeLocal=BasePose[I].GetRelativeTransform(BasePose[Parent]);
            NativeLocal.SetRotation((GaitRotations[I]*NativeLocal.GetRotation()).GetNormalized());
            Target[I]=NativeLocal*Target[Parent];
        }
    }
    if(Initialized&&(Native!=LastNative||(S.phase==mcl::Phase::Idle&&LastPhase!=mcl::Phase::Idle&&!Sample.tail)||
        (Authored&&S.serial!=LastSerial&&(State.exEntryBridge||ContactBinding)))){FromPose=LastPose;FromWeapon=LastWeapon;Transition=true;}
    // A release always uses the selected target pose. Entry/return are cosmetic and share
    // the simulation transition age; no independent animation timer exists.
    if((Authored&&S.phase==mcl::Phase::Release)||Sample.tail)Transition=false;
    BlendWeight=Transition?mcl::smooth((Authored?S.elapsed:State.exTransitionAge)/(Authored?.10:.18)):1.;
    TArray<FTransform> Pose=Target;FTransform VisibleWeapon=TargetWeapon;
    if(Transition&&FromPose.Num()==Pose.Num()){
        for(int32 I=0;I<Pose.Num();++I)Pose[I].Blend(FromPose[I],Target[I],BlendWeight);
        VisibleWeapon.Blend(FromWeapon,TargetWeapon,BlendWeight);
        // Blending bones and the weapon separately does not preserve their grasp.
        // Close cosmetic arms against the actual blended weapon before rendering.
        if(ContactBinding)FitContactArms(Pose,Target,TargetWeapon,VisibleWeapon);
    }
    if(BlendWeight>=1.)Transition=false;
    Initialized=true;LastNative=Native;LastPhase=S.phase;LastSerial=S.serial;LastPose=Pose;LastWeapon=VisibleWeapon;
    if(!Native&&!Transition){Hide();return false;}
    Output->SetWorldTransform(BodyWorld);Output->CommitComponentPose(Pose);Output->SetVisibility(true);
    Weapon->SetWorldTransform(VisibleWeapon*BodyWorld);Weapon->SetVisibility(true);Active=true;
    if(ContactBinding){
        const auto& Ref=Sampler->GetSkeletalMeshAsset()->GetRefSkeleton();
        GripErrorCm=0;
        for(int32 I=0;I<Ref.GetNum();++I){
            const FName Name=UEXCombatPresentation::BindingName(Ref.GetBoneName(I));
            if(Name==FName(TEXT("wrist_r"))||Name==FName(TEXT("wrist_l"))){
                const FTransform Goal=Target[I].GetRelativeTransform(TargetWeapon)*Weapon->GetComponentTransform();
                GripErrorCm=FMath::Max(GripErrorCm,FVector::Distance(Output->GetBoneTransform(I).GetLocation(),Goal.GetLocation()));
            }
        }
    }
    PoseErrorCm=0;for(int32 I=0;I<Pose.Num();++I)PoseErrorCm=FMath::Max(PoseErrorCm,FVector::Distance(Output->GetBoneTransform(I).GetLocation(),BodyWorld.TransformPosition(NativePose[I].GetLocation())));
    const FVector Base=Weapon->GetComponentTransform().GetLocation(),Tip=Weapon->GetComponentTransform().TransformPosition(FVector(0,0,103.5));
    VisibleBladeBase=Base;VisibleBladeTip=Tip;
    const FTransform Expected=NativeWeapon*BodyWorld;
    WeaponErrorCm=FMath::Max(FVector::Distance(Base,Expected.GetLocation()),FVector::Distance(Tip,Expected.TransformPosition(FVector(0,0,103.5))));
    BladeBaseErrorCm=FVector::Distance(Base,TPVec(P.hilt));BladeTipErrorCm=FVector::Distance(Tip,TPVec(P.tip));
    return true;
}

// The authored torso and elbow planes supply style. The simulation supplies the
// active blade; grip closure moves only cosmetic arms and never feeds back.
void UTPCombatPresentation::BindContactPose(TArray<FTransform>& Pose,const FTransform& NativeWeapon,
    FTransform& TargetWeapon,const FTransform& BodyWorld,const mcl::Combatant& State)
{
    const auto& Ref=Sampler->GetSkeletalMeshAsset()->GetRefSkeleton();
    const auto Find=[&](const TCHAR* Name)->int32{
        const FName Key(Name);
        for(int32 I=0;I<Ref.GetNum();++I)if(UEXCombatPresentation::BindingName(Ref.GetBoneName(I))==Key)return I;
        return INDEX_NONE;
    };
    const auto Descendant=[&](int32 I,int32 Root){while(I!=INDEX_NONE&&I!=Root)I=Ref.GetParentIndex(I);return I==Root;};
    const auto& Blade=State.weapon;
    const FVector Axis=TPVec(Blade.tip-Blade.hilt).GetSafeNormal();
    const FVector Edge=TPVec(Blade.edge).GetSafeNormal();
    const FTransform Canonical(FRotationMatrix::MakeFromZX(Axis,Edge).ToQuat(),TPVec(Blade.hilt),
        FVector(1,1,(Blade.tip-Blade.hilt).length()/103.5));
    const TArray<FTransform> NativePose=Pose;
    TargetWeapon=NativeWeapon;
    // Aim is visible through connected chest/head articulation, not a hip fold.
    // Move the nondamaging weapon with the same chest pivots as its native hands.
    const auto RotateAim=[&](const TCHAR* Name,double Fraction,bool MoveWeapon){
        const int32 Root=Find(Name);if(Root==INDEX_NONE)return;
        const FVector Pivot=Pose[Root].GetLocation();
        const FQuat WorldRotation=FRotator(State.exSampleView.pitch*Fraction,State.exSampleView.yaw,0).Quaternion()*
            FRotator(0,State.exSampleView.yaw,0).Quaternion().Inverse();
        const FQuat Rotation=BodyWorld.GetRotation().Inverse()*WorldRotation*BodyWorld.GetRotation();
        for(int32 I=0;I<Pose.Num();++I)if(Descendant(I,Root)){
            Pose[I].SetLocation(Pivot+Rotation.RotateVector(Pose[I].GetLocation()-Pivot));
            Pose[I].SetRotation((Rotation*Pose[I].GetRotation()).GetNormalized());
        }
        if(MoveWeapon){
            TargetWeapon.SetLocation(Pivot+Rotation.RotateVector(TargetWeapon.GetLocation()-Pivot));
            TargetWeapon.SetRotation((Rotation*TargetWeapon.GetRotation()).GetNormalized());
        }
    };
    RotateAim(TEXT("spine05"),.08,true);
    RotateAim(TEXT("spine01"),.57,true);
    RotateAim(TEXT("head"),.35,false);
    const auto Sample=SourceBinding.sample(State.state,State.exSourceTime,State.exTransitionAge);
    const double AimWeight=mcl::TPPresentationPolicy::cameraAim(State.state,SourceTime,Sample.authored||Sample.tail);
    const FTransform YawCamera(FRotator(0,State.exSampleView.yaw,0),TPVec(State.uprightEye()));
    const FTransform AimCamera(FRotator(State.exSampleView.pitch,State.exSampleView.yaw,0),TPVec(State.exSampleEye));
    const FTransform AimedNative=((NativeWeapon*BodyWorld).GetRelativeTransform(YawCamera)*AimCamera).GetRelativeTransform(BodyWorld);
    FTransform AimedWeapon;AimedWeapon.Blend(TargetWeapon,AimedNative,AimWeight);TargetWeapon=AimedWeapon;
    if(mcl::TPPresentationPolicy::contact(State.state,SourceTime,Sample.authored))
        TargetWeapon=Canonical.GetRelativeTransform(BodyWorld);
    // Source release endpoints match canonical. Native carry continues immediately
    // afterward; FP's nondamaging recovery hold never overwrites this performance.
    FitContactArms(Pose,NativePose,NativeWeapon,TargetWeapon);
}

void UTPCombatPresentation::FitContactArms(TArray<FTransform>& Pose,const TArray<FTransform>& NativePose,
    const FTransform& NativeWeapon,const FTransform& TargetWeapon)
{
    const auto& Ref=Sampler->GetSkeletalMeshAsset()->GetRefSkeleton();
    const auto Find=[&](const TCHAR* Name)->int32{
        for(int32 I=0;I<Ref.GetNum();++I)if(UEXCombatPresentation::BindingName(Ref.GetBoneName(I))==FName(Name))return I;
        return INDEX_NONE;
    };
    const auto Descendant=[&](int32 I,int32 Root){while(I!=INDEX_NONE&&I!=Root)I=Ref.GetParentIndex(I);return I==Root;};
    const auto M=[](FVector P){return mcl::Vec{P.X,P.Y,P.Z};};
    for(const TCHAR* Side:{TEXT("r"),TEXT("l")}){
        const int32 Upper=Find(*(FString(TEXT("upperarm01_"))+Side));
        const int32 Lower=Find(*(FString(TEXT("lowerarm01_"))+Side));
        const int32 Wrist=Find(*(FString(TEXT("wrist_"))+Side));
        if(Upper==INDEX_NONE||Lower==INDEX_NONE||Wrist==INDEX_NONE)continue;
        const FTransform Goal=NativePose[Wrist].GetRelativeTransform(NativeWeapon)*TargetWeapon;
        const FVector Shoulder=Pose[Upper].GetLocation(),Elbow=Pose[Lower].GetLocation(),Hand=Pose[Wrist].GetLocation();
        const auto Fit=mcl::presentation::solveArm(M(Shoulder),M(Goal.GetLocation()),M(Elbow-Shoulder),
            FVector::Distance(Shoulder,Elbow),FVector::Distance(Elbow,Hand));
        ArmReachScale=FMath::Max(ArmReachScale,Fit.reachScale);
        const auto MoveChain=[&](int32 Root,FVector EndBefore,FVector EndAfter){
            const FVector Pivot=Pose[Root].GetLocation(),Before=EndBefore-Pivot,After=EndAfter-Pivot;
            const FQuat Rotation=FQuat::FindBetweenVectors(Before,After);
            const double Scale=After.Size()/FMath::Max(Before.Size(),1.e-6);
            for(int32 I=0;I<Pose.Num();++I)if(Descendant(I,Root)){
                Pose[I].SetLocation(Pivot+Rotation.RotateVector(Pose[I].GetLocation()-Pivot)*Scale);
                Pose[I].SetRotation((Rotation*Pose[I].GetRotation()).GetNormalized());
            }
        };
        MoveChain(Upper,Elbow,TPVec(Fit.elbow));
        MoveChain(Lower,Pose[Wrist].GetLocation(),Goal.GetLocation());
        for(int32 I=0;I<Pose.Num();++I)if(Descendant(I,Wrist))Pose[I]=NativePose[I].GetRelativeTransform(NativeWeapon)*TargetWeapon;
        GripErrorCm=FMath::Max(GripErrorCm,FVector::Distance(Pose[Wrist].GetLocation(),Goal.GetLocation()));
    }
}
