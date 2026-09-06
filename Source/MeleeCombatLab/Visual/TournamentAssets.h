#pragma once
#include "CoreMinimal.h"
class UStaticMesh;class UMaterialInstanceDynamic;
namespace TournamentAssets
{
    // Cached original geometry. Render-only meshes have no collision body or gameplay authority.
    UStaticMesh* Mesh(const FName& Shape);
    UMaterialInstanceDynamic* Material(UObject* Owner,const FString& Surface,FLinearColor Tint);
}
