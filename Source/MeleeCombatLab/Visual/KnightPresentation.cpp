#include "KnightPresentation.h"
#include "CombatRigMesh.h"
#include "EXCombatPresentation.h"
#include "TPCombatPresentation.h"
#include "MeleePresentationPose.h"
#include "Character/MeleeCharacter.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/Skeleton.h"
#include "Materials/MaterialInterface.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Rendering/SkeletalMeshLODRenderData.h"
#include "SkeletalRenderPublic.h"
#include "Rendering/SkinWeightVertexBuffer.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
namespace {FVector KnightVec(mcl::Vec P){return {P.x,P.y,P.z};}}
bool UKnightPresentation::PersistSurface(USkeletalMesh* Mesh,UMaterialInterface* Surface)
{
#if WITH_EDITOR
    if(!Mesh||!Surface)return false;
    if(!Mesh->GetPathName().StartsWith(TEXT("/Game/CharacterReset/CF_v001/"))&&
       Mesh->GetPathName()!=TEXT("/Game/UserKnight/KN_v002/SK_KnightBody.SK_KnightBody")&&
       Mesh->GetPathName()!=TEXT("/Game/UserMaleBody/MB_v004_Project/SK_MB_Body.SK_MB_Body"))return false;
    auto Materials=Mesh->GetMaterials();if(Materials.IsEmpty())return false;
    // UE 5.8 no longer exposes the skeletal LOD-info array to Python.
    // This selected body has one section and one baked normal material per LOD.
    if(Mesh->GetPathName()==TEXT("/Game/UserMaleBody/MB_v004_Project/SK_MB_Body.SK_MB_Body")){
        if(Materials.Num()!=4||Mesh->GetLODNum()!=4)return false;
        constexpr float ScreenSizes[]={1.f,.45f,.22f,.09f};
        for(int32 I=0;I<4;++I){
            auto* Info=Mesh->GetLODInfo(I);if(!Info)return false;
            Info->LODMaterialMap={I};Info->ScreenSize.Default=ScreenSizes[I];
        }
    }
    Materials[0].MaterialInterface=Surface;
    Mesh->SetMaterials(Materials);Mesh->PostEditChange();Mesh->MarkPackageDirty();return true;
#else
    return false;
#endif
}
void UKnightPresentation::SaveMotionTrace(const FString& Path,double SampleTime) const
{
#if !UE_BUILD_SHIPPING
    if(!IFileManager::Get().FileExists(*Path))
        FFileHelper::SaveStringToFile(TEXT("time,binding,side,phase,progress,reach_scale\n"),*Path);
    TArray<FString> Rows;MotionTrace.ParseIntoArrayLines(Rows);
    FString Output;
    for(const auto& Row:Rows)Output+=FString::Printf(TEXT("%.6f,%s\n"),SampleTime,*Row);
    FFileHelper::SaveStringToFile(Output,*Path,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_Append);
#endif
}
double UKnightPresentation::MeasureArmSurfaceStretch() const
{
    const auto* Mesh=Body.Get();
    if(!Mesh||!Mesh->GetSkinnedAsset())return 0.;
    const auto* Data=Mesh->GetSkinnedAsset()->GetResourceForRendering();
    if(!Data||Data->LODRenderData.IsEmpty())return 0.;
    const auto& LOD=Data->LODRenderData[0];
    TArray<FFinalSkinVertex> Vertices;Mesh->GetCPUSkinnedVertices(Vertices,0);
    const auto& Rest=LOD.StaticVertexBuffers.PositionVertexBuffer;
    if(Vertices.Num()!=static_cast<int32>(Rest.GetNumVertices()))return 0.;
    const auto* Indices=LOD.MultiSizeIndexContainer.GetIndexBuffer();
    double Maximum=1.;
    for(int32 I=0;I+2<Indices->Num();I+=3)for(int32 E=0;E<3;++E){
        const uint32 A=Indices->Get(I+E),B=Indices->Get(I+(E+1)%3);
        const FVector3f RA=Rest.VertexPosition(A),RB=Rest.VertexPosition(B);
        if(FMath::Abs(RA.X)<20||FMath::Abs(RB.X)<20||RA.Z<85||RB.Z<85)continue;
        const double Length=(RA-RB).Size();
        if(Length>.05)Maximum=FMath::Max(Maximum,(Vertices[A].Position-Vertices[B].Position).Size()/Length);
    }
    return Maximum;
}
int32 UKnightPresentation::Bone(FName Name) const {const auto* Index=BoneIndices.Find(UEXCombatPresentation::BindingName(Name));return Index?*Index:INDEX_NONE;}
void UKnightPresentation::SaveArmPoseAudit(const FString& Path) const
{
#if !UE_BUILD_SHIPPING
    const auto* Mesh=Body.Get();
    if(!Mesh||!Mesh->GetSkinnedAsset())return;
    const auto* Data=Mesh->GetSkinnedAsset()->GetResourceForRendering();
    if(!Data||Data->LODRenderData.IsEmpty())return;
    const auto& LOD=Data->LODRenderData[0];
    TArray<FFinalSkinVertex> Vertices;Mesh->GetCPUSkinnedVertices(Vertices,0);
    const auto& Ref=Mesh->GetSkinnedAsset()->GetRefSkeleton();
    const auto& Weights=LOD.SkinWeightVertexBuffer;
    FString Text=TEXT("kind,index,bone,rest_x,rest_y,rest_z,pose_x,pose_y,pose_z,view_x,view_y,view_z\n");
    for(const auto& Section:LOD.RenderSections)for(uint32 J=0;J<Section.NumVertices;++J){
        const uint32 I=Section.BaseVertexIndex+J;
        if(I>=static_cast<uint32>(Vertices.Num()))continue;
        const auto R=LOD.StaticVertexBuffers.PositionVertexBuffer.VertexPosition(I);
        const auto P=Vertices[I].Position;
        const FVector W=Mesh->GetComponentTransform().TransformPosition(FVector(P));
        const auto V=AuditView.local(mcl::Vec{W.X,W.Y,W.Z}-AuditEye);
        const uint32 LocalBone=Weights.GetBoneIndex(I,0);
        const FString Name=Section.BoneMap.IsValidIndex(LocalBone)?Ref.GetBoneName(Section.BoneMap[LocalBone]).ToString():TEXT("unknown");
        Text+=FString::Printf(TEXT("v,%u,%s,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f\n"),I,*Name,R.X,R.Y,R.Z,P.X,P.Y,P.Z,V.x,V.y,V.z);
    }
    const auto* Indices=LOD.MultiSizeIndexContainer.GetIndexBuffer();
    for(int32 I=0;I+2<Indices->Num();I+=3)Text+=FString::Printf(TEXT("f,%u,%u,%u\n"),Indices->Get(I),Indices->Get(I+1),Indices->Get(I+2));
    FFileHelper::SaveStringToFile(Text,*Path);
#endif
}

void UKnightPresentation::BeginPlay()
{
    Super::BeginPlay();
    auto* Asset=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/CharacterReset/CF_v001/CF_GameplayBody.CF_GameplayBody"));
    if(!ensureAlwaysMsgf(Asset&&Asset->GetSkeleton(),TEXT("Fresh CF body missing: run Tools/ImportFreshGameplayBody.py")))return;
    Body=NewObject<UCombatRigMesh>(GetOwner(),TEXT("FreshFoundationBody"));
    Body->SetSkinnedAssetAndUpdate(Asset);Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Body->SetGenerateOverlapEvents(false);Body->SetBoundsScale(3.f);Body->RegisterComponent();
    const auto& Ref=Asset->GetRefSkeleton();Reference=Ref.GetRefBonePose();Parents.SetNum(Ref.GetNum());
    for(int32 I=0;I<Ref.GetNum();++I){Parents[I]=Ref.GetParentIndex(I);BoneIndices.Add(UEXCombatPresentation::BindingName(Ref.GetBoneName(I)),I);
        if(Parents[I]!=INDEX_NONE)Reference[I]=Reference[I]*Reference[Parents[I]];}
    UE_LOG(LogTemp,Display,TEXT("FRESHBODY mesh=%s skeleton=%s bones=%d; old character assets disabled"),*Asset->GetPathName(),*Asset->GetSkeleton()->GetPathName(),Ref.GetNum());
    TP=NewObject<UTPCombatPresentation>(GetOwner());TP->RegisterComponent();TP->Initialize(Asset);
    TPSelected=TP->Selected;TPRevision=TP->Revision;
    if(!FParse::Param(FCommandLine::Get(),TEXT("FoundationBody"))){
        const TCHAR* KnightPath=FParse::Param(FCommandLine::Get(),TEXT("KnightArmor"))
            ? TEXT("/Game/UserKnight/KN_v001/SK_UserKnight.SK_UserKnight")
            : TEXT("/Game/UserMaleBody/MB_v004_Project/SK_MB_Body.SK_MB_Body");
        if(auto* Skin=LoadObject<USkeletalMesh>(nullptr,KnightPath)){
            KnightSkin=NewObject<UCombatRigMesh>(GetOwner(),TEXT("UserKnightSkin"));
            KnightSkin->SetSkinnedAssetAndUpdate(Skin);
            KnightSkin->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            KnightSkin->SetGenerateOverlapEvents(false);KnightSkin->SetBoundsScale(3.f);
            KnightSkin->RegisterComponent();KnightSkin->SetVisibility(false);
            UE_LOG(LogTemp,Display,TEXT("WORKING_BODY rig=%s; independent rest pose; combat retargeting separate"),*Skin->GetPathName());
        }
    }
}
void UKnightPresentation::SetFirstPerson(bool Value){bFirstPerson=Value;if(Body)Body->SetVisibility(!Value&&!KnightSkin);if(KnightSkin)KnightSkin->SetVisibility(!Value);if(Value&&TP){TP->Hide();TPActive=false;}}
void UKnightPresentation::RotateSubtree(int32 Root,FQuat Rotation,FVector Shift)
{
    if(Root==INDEX_NONE)return;
    const FVector Pivot=ComponentPose[Root].GetLocation();
    for(int32 I=0;I<ComponentPose.Num();++I){int32 Parent=I;while(Parent!=INDEX_NONE&&Parent!=Root)Parent=Parents[Parent];if(Parent!=Root)continue;
        ComponentPose[I].SetLocation(Pivot+Rotation.RotateVector(ComponentPose[I].GetLocation()-Pivot)+Shift);
        ComponentPose[I].SetRotation((Rotation*ComponentPose[I].GetRotation()).GetNormalized());}
}
void UKnightPresentation::FitLimb(int32 Upper,int32 Lower,int32 End,FVector Target,FVector Pole)
{
    if(Upper==INDEX_NONE||Lower==INDEX_NONE||End==INDEX_NONE)return;
    const auto M=[](FVector P){return mcl::Vec{P.X,P.Y,P.Z};};
    const FVector Shoulder=ComponentPose[Upper].GetLocation();
    const double UpperLength=FVector::Distance(Reference[Upper].GetLocation(),Reference[Lower].GetLocation());
    const double LowerLength=FVector::Distance(Reference[Lower].GetLocation(),Reference[End].GetLocation());
    const auto Fit=mcl::presentation::solveArm(M(Shoulder),M(Target),M(Pole),UpperLength,LowerLength);
    MaxArmStretch=FMath::Max(MaxArmStretch,Fit.reachScale);
    const FVector Elbow=KnightVec(Fit.elbow);
    RotateSubtree(Upper,FQuat::FindBetweenVectors(ComponentPose[Lower].GetLocation()-Shoulder,Elbow-Shoulder));
    RotateSubtree(Lower,FQuat::Identity,Elbow-ComponentPose[Lower].GetLocation());
    RotateSubtree(Lower,FQuat::FindBetweenVectors(ComponentPose[End].GetLocation()-Elbow,Target-Elbow));
    RotateSubtree(End,FQuat::Identity,Target-ComponentPose[End].GetLocation());
}
void UKnightPresentation::Present(const mcl::Combatant& State,const mcl::Tuning&,bool,float,float Dt,mcl::Vec)
{
    if(!Body)return;
    const auto* Character=Cast<AMeleeCharacter>(GetOwner());
    auto* EX=Character?Character->EXPresentation.Get():nullptr;
    if(KnightSkin&&!(TP&&TP->Selected)){
        // Unselected Knight placeholder. A selected TP asset owns its own rig.
        KnightSkin->SetWorldTransform(FTransform(FRotator(0,State.view.yaw-90.,0),
            KnightVec(State.position)-FVector(0,0,State.bodyHalfHeight)));
        KnightSkin->SetVisibility(!bFirstPerson);Body->SetVisibility(false);
        if(TP)TP->Hide();TPActive=false;
        if(EX)EX->SetWeaponVisible(bFirstPerson);
        return;
    }
    if(KnightSkin)KnightSkin->SetVisibility(false);
    if(!EX||!EX->Ready()){Body->SetVisibility(false);return;}
    const auto& View=State.exSampleView;
    const FVector Position=KnightVec(State.position);
    const double Distance=Initialized?FVector::Dist2D(Position,LastPosition):0.;
    Initialized=true;LastPosition=Position;if(Distance<100.)Gait+=Distance*.045;
    const double Crouch=FMath::Max(0.,88.-State.bodyHalfHeight);
    const FTransform World(FRotator(0,View.yaw-90.,0),Position-FVector(0,0,State.bodyHalfHeight));
    ComponentPose=Reference;MaxArmStretch=1.;MotionTrace.Empty();AuditEye=State.exSampleEye;AuditView=View;
    for(auto& Transform:ComponentPose)Transform.AddToTranslation(FVector(0,0,-Crouch*2.));
    const auto& S=State.state;
    const double Coil=S.phase==mcl::Phase::Windup?-12.*mcl::smooth(S.progress()):
        S.phase==mcl::Phase::Release?mcl::mix(-12.,10.,S.progress()):S.phase==mcl::Phase::Recovery?10.*(1.-mcl::smooth(S.progress())):0.;
    const double Pitch=View.pitch*State.torsoPitchScale*State.leanFraction;
    RotateSubtree(Bone(TEXT("spine05")),FQuat(FVector::UpVector,FMath::DegreesToRadians(Coil))*FQuat(FVector::ForwardVector,FMath::DegreesToRadians(Pitch)));
    RotateSubtree(Bone(TEXT("head")),FQuat(FVector::UpVector,FMath::DegreesToRadians(-Coil)));
    for(const TCHAR* Side:{TEXT("R"),TEXT("L")}){
        const bool Right=Side[0]=='R';const double Sign=Right?-1.:1.;
        auto Find=[&](const TCHAR* Prefix){return Bone(FName(*(FString(Prefix)+Side)));};
        const int32 Foot=Find(TEXT("foot."));
        if(Foot!=INDEX_NONE){
            FVector Target=Reference[Foot].GetLocation();
            if(Distance>.01&&Distance<100.){const double Wave=std::sin(Gait+(Right?0.:mcl::Pi));Target.Y+=Wave*17.;Target.Z+=FMath::Max(0.,Wave)*6.;}
            FitLimb(Find(TEXT("upperleg01.")),Find(TEXT("lowerleg01.")),Foot,Target,FVector(0,1,0));
            RotateSubtree(Foot,Reference[Foot].GetRotation()*ComponentPose[Foot].GetRotation().Inverse());
        }
        const int32 Wrist=Find(TEXT("wrist."));if(Wrist==INDEX_NONE)continue;
        const auto* Grip=EX->HandBinding.Find(UEXCombatPresentation::BindingName(FName(*(FString(TEXT("wrist."))+Side))));if(!Grip)continue;
        const auto& Blade=State.weapon;const FVector Axis=KnightVec(Blade.tip-Blade.hilt).GetSafeNormal();
        const FVector Edge=Blade.edge.length()>.5?KnightVec(Blade.edge):KnightVec(mcl::weaponEdge(Blade.tip-Blade.hilt,State.exSampleView));
        const FTransform Weapon(FRotationMatrix::MakeFromZX(Axis,Edge).ToQuat(),KnightVec(Blade.hilt));
        const FTransform Desired=(*Grip*Weapon).GetRelativeTransform(World);
        const int32 Upper=Find(TEXT("upperarm01.")),Lower=Find(TEXT("lowerarm01."));
        FitLimb(Upper,Lower,Wrist,Desired.GetLocation(),FVector(Sign*.7,-.15,-.8));
        const auto& Ref=Body->GetSkinnedAsset()->GetRefSkeleton();
        for(int32 I=0;I<ComponentPose.Num();++I){int32 Parent=I;while(Parent!=INDEX_NONE&&Parent!=Wrist)Parent=Parents[Parent];if(Parent!=Wrist)continue;
            if(const auto* Hand=EX->HandBinding.Find(UEXCombatPresentation::BindingName(Ref.GetBoneName(I))))ComponentPose[I]=(*Hand*Weapon).GetRelativeTransform(World);}
        if(Upper!=INDEX_NONE&&Lower!=INDEX_NONE)MotionTrace+=FString::Printf(TEXT("fresh,%s,%s,%.6f,%.6f\n"),Side,UTF8_TO_TCHAR(mcl::phaseName(S.phase)),S.progress(),MaxArmStretch);
    }
    TPActive=!bFirstPerson&&TP&&TP->Present(State,Dt,ComponentPose,World);
    if(TP){TPSelected=TP->Selected;TPRevision=TP->Revision;TPAuthored=TP->Authored;TPSourceTime=TP->SourceTime;
        TPPoseErrorCm=TP->PoseErrorCm;TPWeaponErrorCm=TP->WeaponErrorCm;TPBladeBaseErrorCm=TP->BladeBaseErrorCm;TPBladeTipErrorCm=TP->BladeTipErrorCm;TPBlendWeight=TP->BlendWeight;
        TPGripErrorCm=TP->GripErrorCm;TPArmReachScale=TP->ArmReachScale;
        TPImportPoseErrorCm=TP->ImportPoseErrorCm;TPImportRotationErrorDegrees=TP->ImportRotationErrorDegrees;
        TPBladeBase=TP->VisibleBladeBase;TPBladeTip=TP->VisibleBladeTip;}
    EX->SetWeaponVisible(!TPActive);
    Body->SetWorldTransform(World);Body->CommitComponentPose(ComponentPose);Body->SetVisibility(!bFirstPerson&&!TPActive);
}
