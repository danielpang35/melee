#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Combat/Attacks/AttackDirectionResolver.h"
#include "MeleeCharacter.generated.h"

class UKnightPresentation;class UCombatComponent;class UCameraComponent;class UWeaponPresentationComponent;class UInputAction;class UInputMappingContext;
struct FInputActionValue;
UCLASS()
class MELEECOMBATLAB_API AMeleeCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AMeleeCharacter(const FObjectInitializer& ObjectInitializer);
    UPROPERTY(VisibleAnywhere) TObjectPtr<UKnightPresentation> Knight;
    bool bBlueArmor=true;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UCombatComponent> Combat;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UCameraComponent> Camera;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UWeaponPresentationComponent> Presentation;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    virtual void Tick(float DeltaTime) override;
    void Feedback(mcl::Resolution Result);
    void ResetAt(FVector Position,FRotator Facing);
private:
    UPROPERTY() TObjectPtr<UInputMappingContext> Context;
    UPROPERTY() TArray<TObjectPtr<UInputAction>> Actions;
    mcl::AttackDirectionResolver Direction;
    float CameraKick=0;
    float BodyReaction=0;
    void Forward(const FInputActionValue& Value);
    void Right(const FInputActionValue& Value);
    void LookX(const FInputActionValue& Value);
    void LookY(const FInputActionValue& Value);
    void SprintStart();void SprintEnd();void CrouchStart();void CrouchEnd();
    void Strike();void Stab();void Parry();void Feint();
    void ToggleDebug();void ToggleTuning();void ResetLab();void NextPattern();void ToggleStamina();void ToggleInspection();
    void CycleGraphics();
    void Direction0();void Direction1();void Direction2();void Direction3();void Direction4();void Direction5();
};
