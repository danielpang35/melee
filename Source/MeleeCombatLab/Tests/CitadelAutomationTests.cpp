#include "Misc/AutomationTest.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Animation/Skeleton.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCitadelAssets,"MeleeCombatLab.Citadel.AssetContract",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCitadelAssets::RunTest(const FString&)
{
    auto* Body=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Visual/Citadel/Meshes/SK_CitadelKnight.SK_CitadelKnight"));
    auto* Arms=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Visual/Citadel/Meshes/SK_CitadelArms.SK_CitadelArms"));
    auto* Sword=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Visual/Citadel/Meshes/SM_CitadelSword.SM_CitadelSword"));
    if(!TestNotNull(TEXT("Weighted body exists"),Body)||!TestNotNull(TEXT("First-person arms exist"),Arms)||!TestNotNull(TEXT("Textured sword exists"),Sword))return false;
    TestNotNull(TEXT("Persisted skeleton exists"),Body->GetSkeleton());
    TestTrue(TEXT("Body has a bound surface material"),Body->GetMaterials().Num()>0&&Body->GetMaterials()[0].MaterialInterface!=nullptr);
    TestTrue(TEXT("Arms have a bound surface material"),Arms->GetMaterials().Num()>0&&Arms->GetMaterials()[0].MaterialInterface!=nullptr);
    TestEqual(TEXT("Body and arms share skeleton"),Body->GetSkeleton(),Arms->GetSkeleton());
    const auto& Ref=Body->GetRefSkeleton();const auto& FP=Arms->GetRefSkeleton();
    TestEqual(TEXT("Identical bone count"),Ref.GetNum(),FP.GetNum());
    TArray<FTransform> Pose=Ref.GetRefBonePose();
    for(int32 I=0;I<Ref.GetNum();++I){
        const int32 Parent=Ref.GetParentIndex(I);if(Parent!=INDEX_NONE)Pose[I]=Pose[I]*Pose[Parent];
        if(I<FP.GetNum())TestEqual(TEXT("Identical pose index mapping"),Ref.GetBoneName(I),FP.GetBoneName(I));
        TestFalse(TEXT("Reference transform finite"),Pose[I].ContainsNaN());
    }
    for(FName Name:{FName("pelvis"),FName("head"),FName("upperarm_r"),FName("lowerarm_r"),FName("hand_r"),FName("hand_l")})
        TestTrue(TEXT("Required deform bone exists"),Ref.FindBoneIndex(Name)!=INDEX_NONE);
    const int32 Right=Ref.FindBoneIndex(TEXT("upperarm_r"));
    if(Right!=INDEX_NONE)TestTrue(TEXT("Right shoulder is right of body in Unreal space"),Pose[Right].GetLocation().Y>20.&&FMath::Abs(Pose[Right].GetLocation().X)<1.);
    TestTrue(TEXT("Sword tip calibrated to Z=100 cm"),FMath::Abs(Sword->GetBoundingBox().Max.Z-100.)<.05);
    TestTrue(TEXT("Hero has human scale"),FMath::Abs(Body->GetImportedBounds().BoxExtent.Z*2.-186.)<2.);
    return true;
}
#endif
