#pragma once
#include "CoreMinimal.h"
namespace TournamentGraphics
{
    extern FString Profile;
    extern int Tier;
    void Apply(const FString& Name);
    void Initialize();
    void Cycle();
}
