#pragma once
#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
class ACombatLabGameMode;
class SCombatTuningPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SCombatTuningPanel){} SLATE_ARGUMENT(ACombatLabGameMode*,Lab) SLATE_END_ARGS()
    void Construct(const FArguments& Args);
private:
    TWeakObjectPtr<ACombatLabGameMode> Lab;
};
