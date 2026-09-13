#pragma once
#include "CoreMinimal.h"
#include "Combat/CombatTuning.h"

class FJsonObject;

// Paths are injectable so automation never reads or writes the user's tuning.
struct FCombatTuningSource
{
    FString Path, Status=TEXT("not-attempted"), Detail, ContentIdentity;
    int32 AppliedFields=0, ClampedFields=0;
};

struct FCombatTuningPersistence
{
    FString ProjectPath, SavedPath, PromotionPath;
    bool bDefaultsOnly=false, bExplicitProjectPath=false;
    bool bLoadSucceeded=false;
    FCombatTuningSource ActiveProject, ActiveSaved, AttemptProject, AttemptSaved;
    FString EffectiveIdentity, StartupIdentity, EffectiveOrigin=TEXT("built-in"), Event;
    int32 Sequence=0;

    bool Load(mcl::Tuning& Values);
    void Reset(mcl::Tuning& Values);
    bool SetValue(mcl::Tuning& Values, const FString& Name, double Value);
    bool Save(mcl::Tuning& Values, bool bPromote, FString& Message);
    FString Describe() const;
    TSharedRef<FJsonObject> Receipt(mcl::Tuning Values) const;
    bool WriteReceipt(mcl::Tuning Values, const FString& Path) const;
    static FString Identity(mcl::Tuning Values);
private:
    void Changed(mcl::Tuning& Values, const TCHAR* NewEvent);
};
