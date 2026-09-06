#include "CombatRigMesh.h"
#include "Engine/SkeletalMesh.h"
void UCombatRigMesh::CommitComponentPose(const TArray<FTransform>& Pose)
{
    const auto* Mesh=GetSkinnedAsset();
    if(!Mesh||Pose.Num()!=Mesh->GetRefSkeleton().GetNum())return;
    const auto& Ref=Mesh->GetRefSkeleton();
    BoneSpaceTransforms.SetNum(Pose.Num());
    for(int32 I=0;I<Pose.Num();++I){
        const int32 Parent=Ref.GetParentIndex(I);
        BoneSpaceTransforms[I]=Parent==INDEX_NONE?Pose[I]:Pose[I].GetRelativeTransform(Pose[Parent]);
        BoneSpaceTransforms[I].NormalizeRotation();
    }
    MarkRefreshTransformDirty();
    RefreshBoneTransforms();
}
