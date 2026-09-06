#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "CitadelAssetTools.generated.h"
class USkeletalMesh;
class USkeleton;
UCLASS()
class MELEECOMBATLAB_API UCitadelAssetTools : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // Explicit dependency creation for unattended asset builds. Never called by gameplay.
    UFUNCTION(BlueprintCallable,Category="Citadel|Asset Build")
    static USkeleton* EnsureSkeleton(USkeletalMesh* Mesh);
};
