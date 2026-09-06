#pragma once
#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "CombatDebugHUD.generated.h"
UCLASS()
class MELEECOMBATLAB_API ACombatDebugHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
};
