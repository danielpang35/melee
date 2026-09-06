#include "CitadelAssetTools.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/Skeleton.h"
#include "Materials/MaterialInterface.h"
#include "UObject/Package.h"
#if WITH_EDITOR
#include "AssetRegistry/AssetRegistryModule.h"
#endif
USkeleton* UCitadelAssetTools::EnsureSkeleton(USkeletalMesh* Mesh)
{
#if WITH_EDITOR
    if(!Mesh)return nullptr;
    const TCHAR* Path=TEXT("/Game/Visual/Citadel/Meshes/SKEL_Citadel");
    USkeleton* Skeleton=FindObject<USkeleton>(nullptr,TEXT("/Game/Visual/Citadel/Meshes/SKEL_Citadel.SKEL_Citadel"));
    if(!Skeleton){
        UPackage* Package=CreatePackage(Path);
        Skeleton=NewObject<USkeleton>(Package,TEXT("SKEL_Citadel"),RF_Public|RF_Standalone);
        FAssetRegistryModule::AssetCreated(Skeleton);
    }
    if(!Skeleton->MergeAllBonesToBoneTree(Mesh))return nullptr;
    Skeleton->UpdateReferencePoseFromMesh(Mesh);
    auto* Material=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Visual/Citadel/Materials/M_CitadelKnight.M_CitadelKnight"));
    if(!Material)return nullptr;
    TArray<FSkeletalMaterial> Surfaces=Mesh->GetMaterials();
    if(Surfaces.IsEmpty())Surfaces.Add(FSkeletalMaterial(Material));
    for(auto& Surface:Surfaces){Surface.MaterialInterface=Material;Surface.MaterialSlotName=TEXT("KnightPBR");}
    // SetMaterials updates the serialized material information cache; writing
    // the reflected transient Materials array from Python does not.
    Mesh->SetMaterials(Surfaces);
    Mesh->SetSkeleton(Skeleton);Mesh->MarkPackageDirty();Skeleton->MarkPackageDirty();
    return Skeleton;
#else
    return nullptr;
#endif
}
