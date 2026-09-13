#include "Misc/AutomationTest.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Animation/Skeleton.h"
#include "Materials/MaterialInterface.h"
#include "Materials/Material.h"
#include "Visual/EXCombatPresentation.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Rendering/SkeletalMeshLODRenderData.h"
#if WITH_DEV_AUTOMATION_TESTS
// The old 186 cm / Citadel glove-slot / shared-old-skeleton asset contract is
// retired with the old character. Preserve equivalent fresh-asset guarantees.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFreshAssets,"MeleeCombatLab.Fresh.AssetContract",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFreshAssets::RunTest(const FString&)
{
    auto* Body=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/CharacterReset/CF_v001/CF_GameplayBody.CF_GameplayBody"));
    auto* Arms=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/EXPreview/EX_v002/EX_v002.EX_v002"));
    auto* Sword=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/EXPreview/EX_v002/EXPreviewWeapon.EXPreviewWeapon"));
    auto* ArmsMaterial=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/EXPreview/EX_v002/Study_WarmClay.Study_WarmClay"));
    if(!TestNotNull(TEXT("Fresh weighted body"),Body)||!TestNotNull(TEXT("Approved FP arms"),Arms)||!TestNotNull(TEXT("Approved rigid weapon"),Sword))return false;
    if(!TestNotNull(TEXT("Fresh persisted skeleton"),Body->GetSkeleton()))return false;
    TestTrue(TEXT("Body uses its independent CF skeleton"),Body->GetSkeleton()!=Arms->GetSkeleton()&&Body->GetSkeleton()->GetPathName().StartsWith(TEXT("/Game/CharacterReset/CF_v001/")));
    for(auto* Mesh:{Body,Arms}){
        TestTrue(TEXT("Bound surface materials"),Mesh->GetMaterials().Num()>0);
        for(int32 I=0;I<Mesh->GetMaterials().Num();++I){
            // EX's approved first slot is assigned explicitly by the runtime loader.
            auto* Material=Mesh==Arms&&I==0?ArmsMaterial:Mesh->GetMaterials()[I].MaterialInterface.Get();
            TestNotNull(TEXT("Rendered material persists"),Material);
            if(Material)TestTrue(TEXT("Skeletal shader usage persists"),Material->GetUsageByFlag(MATUSAGE_SkeletalMesh));
        }
        const auto& Ref=Mesh->GetRefSkeleton();TArray<FTransform> Pose=Ref.GetRefBonePose();
        for(int32 I=0;I<Ref.GetNum();++I){const int32 Parent=Ref.GetParentIndex(I);if(Parent!=INDEX_NONE)Pose[I]=Pose[I]*Pose[Parent];TestFalse(TEXT("Finite reference transform"),Pose[I].ContainsNaN());}
    }
    const auto& Ref=Body->GetRefSkeleton();TMap<FName,int32> Bones;
    for(int32 I=0;I<Ref.GetNum();++I)Bones.Add(UEXCombatPresentation::BindingName(Ref.GetBoneName(I)),I);
    for(const TCHAR* Name:{TEXT("root"),TEXT("head"),TEXT("upperarm01_r"),TEXT("lowerarm01_r"),TEXT("wrist_r"),TEXT("wrist_l"),TEXT("foot_r"),TEXT("foot_l")})
        TestTrue(TEXT("Fresh named deformation binding"),Bones.Contains(FName(Name)));
    // FBX adds one armature root to each 102-bone source; CF also has two rigid eyes.
    AddInfo(FString::Printf(TEXT("Imported roots: EX=%s CF=%s"),*Arms->GetRefSkeleton().GetBoneName(0).ToString(),*Ref.GetBoneName(0).ToString()));
    TestEqual(TEXT("Approved FP deformation bones plus import root"),Arms->GetRefSkeleton().GetNum(),103);
    TestEqual(TEXT("Fresh body, import root and eye attachment hierarchy"),Ref.GetNum(),105);
    TestTrue(TEXT("Sword actual 103.5 cm tip"),FMath::Abs(Sword->GetBoundingBox().Max.Z-103.5)<.05);
    TestTrue(TEXT("Fresh 180 cm body scale"),FMath::Abs(Body->GetImportedBounds().BoxExtent.Z*2.-180.)<2.);
    if(const auto* Data=Body->GetResourceForRendering();Data&&!Data->LODRenderData.IsEmpty()){
        const auto& Vertices=Data->LODRenderData[0].StaticVertexBuffers.PositionVertexBuffer;
        FBox Rest(ForceInit);for(uint32 I=0;I<Vertices.GetNumVertices();++I)Rest+=FVector(Vertices.VertexPosition(I));
        AddInfo(FString::Printf(TEXT("Fresh unskinned vertex bounds %s; import root scale %s"),*Rest.ToString(),*Ref.GetRefBonePose()[0].GetScale3D().ToString()));
        TestTrue(TEXT("Finite nonempty fresh rest surface"),Rest.IsValid&&Rest.GetSize().Z>0.&&!Rest.GetSize().ContainsNaN());
    }else AddError(TEXT("Fresh body render data unavailable"));
    return true;
}
#endif
