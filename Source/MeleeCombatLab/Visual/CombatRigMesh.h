#pragma once
#include "CoreMinimal.h"
#include "Components/PoseableMeshComponent.h"
#include "CombatRigMesh.generated.h"

// One bulk pose commit instead of rebuilding a hierarchy for every IK target.
UCLASS()
class MELEECOMBATLAB_API UCombatRigMesh : public UPoseableMeshComponent
{
    GENERATED_BODY()
public:
    void CommitComponentPose(const TArray<FTransform>& Pose);
};
