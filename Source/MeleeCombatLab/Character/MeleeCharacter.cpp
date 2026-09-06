#include "MeleeCharacter.h"
#include "Visual/TournamentGraphics.h"
#include "Visual/KnightPresentation.h"
#include "MeleeCharacterMovementComponent.h"
#include "Combat/CombatComponent.h"
#include "Camera/CameraComponent.h"
#include "Camera/WeaponPresentationComponent.h"
#include "Training/CombatLabGameMode.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/PlayerController.h"
#include "Engine/LocalPlayer.h"
#include "Engine/World.h"

AMeleeCharacter::AMeleeCharacter(const FObjectInitializer& O):Super(O.SetDefaultSubobjectClass<UMeleeCharacterMovementComponent>(ACharacter::CharacterMovementComponentName))
{
    PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickGroup=TG_PostUpdateWork;
    GetCapsuleComponent()->InitCapsuleSize(32,88);bUseControllerRotationYaw=true;
    Knight=CreateDefaultSubobject<UKnightPresentation>(TEXT("KnightArmor"));Knight->SetupAttachment(GetCapsuleComponent());
    Combat=CreateDefaultSubobject<UCombatComponent>(TEXT("Combat"));
    Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("CombatCamera"));Camera->SetupAttachment(GetCapsuleComponent());
    Camera->SetRelativeLocation(FVector(0,0,64));Camera->bUsePawnControlRotation=true;
    Presentation=CreateDefaultSubobject<UWeaponPresentationComponent>(TEXT("WeaponPresentation"));Presentation->SetupAttachment(GetCapsuleComponent());
}
void AMeleeCharacter::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    auto* Enhanced=CastChecked<UEnhancedInputComponent>(Input);
    Context=NewObject<UInputMappingContext>(this);
    auto Make=[&](const TCHAR* Name,EInputActionValueType Type){auto* A=NewObject<UInputAction>(this,FName(Name));A->ValueType=Type;Actions.Add(A);return A;};
    auto Axis=[&](const TCHAR* Name,FKey Positive,FKey Negative,void(AMeleeCharacter::*Fn)(const FInputActionValue&)){
        auto* A=Make(Name,EInputActionValueType::Axis1D);Context->MapKey(A,Positive);
        if(Negative.IsValid()){auto& Mapping=Context->MapKey(A,Negative);Mapping.Modifiers.Add(NewObject<UInputModifierNegate>(Context));}
        Enhanced->BindAction(A,ETriggerEvent::Triggered,this,Fn);Enhanced->BindAction(A,ETriggerEvent::Completed,this,Fn);
    };
    Axis(TEXT("MoveForward"),EKeys::W,EKeys::S,&AMeleeCharacter::Forward);
    Axis(TEXT("MoveRight"),EKeys::D,EKeys::A,&AMeleeCharacter::Right);
    Axis(TEXT("LookX"),EKeys::MouseX,FKey(),&AMeleeCharacter::LookX);
    Axis(TEXT("LookY"),EKeys::MouseY,FKey(),&AMeleeCharacter::LookY);
    auto Button=[&](const TCHAR* Name,FKey Key,void(AMeleeCharacter::*Fn)()){
        auto* A=Make(Name,EInputActionValueType::Boolean);Context->MapKey(A,Key);Enhanced->BindAction(A,ETriggerEvent::Started,this,Fn);return A;
    };
    Button(TEXT("GraphicsProfile"),EKeys::F7,&AMeleeCharacter::CycleGraphics);
    Button(TEXT("Strike"),EKeys::LeftMouseButton,&AMeleeCharacter::Strike);
    auto* StabAction=Button(TEXT("Stab"),EKeys::MouseScrollUp,&AMeleeCharacter::Stab);Context->MapKey(StabAction,EKeys::E);
    Button(TEXT("Parry"),EKeys::RightMouseButton,&AMeleeCharacter::Parry);Button(TEXT("Feint"),EKeys::Q,&AMeleeCharacter::Feint);
    auto* SprintAction=Button(TEXT("Sprint"),EKeys::LeftShift,&AMeleeCharacter::SprintStart);Enhanced->BindAction(SprintAction,ETriggerEvent::Completed,this,&AMeleeCharacter::SprintEnd);
    auto* CrouchAction=Button(TEXT("Crouch"),EKeys::LeftControl,&AMeleeCharacter::CrouchStart);Enhanced->BindAction(CrouchAction,ETriggerEvent::Completed,this,&AMeleeCharacter::CrouchEnd);
    auto* JumpAction=Make(TEXT("Jump"),EInputActionValueType::Boolean);Context->MapKey(JumpAction,EKeys::SpaceBar);
    Enhanced->BindAction(JumpAction,ETriggerEvent::Started,this,&ACharacter::Jump);Enhanced->BindAction(JumpAction,ETriggerEvent::Completed,this,&ACharacter::StopJumping);
    Button(TEXT("Debug"),EKeys::F3,&AMeleeCharacter::ToggleDebug);Button(TEXT("Tuning"),EKeys::F4,&AMeleeCharacter::ToggleTuning);
    Button(TEXT("Inspection"),EKeys::F5,&AMeleeCharacter::ToggleInspection);
    Button(TEXT("Reset"),EKeys::R,&AMeleeCharacter::ResetLab);Button(TEXT("Pattern"),EKeys::F2,&AMeleeCharacter::NextPattern);
    Button(TEXT("InfiniteStamina"),EKeys::F6,&AMeleeCharacter::ToggleStamina);
    Button(TEXT("RightHorizontal"),EKeys::One,&AMeleeCharacter::Direction0);Button(TEXT("UpperRight"),EKeys::Two,&AMeleeCharacter::Direction1);
    Button(TEXT("UpperLeft"),EKeys::Three,&AMeleeCharacter::Direction2);Button(TEXT("LeftHorizontal"),EKeys::Four,&AMeleeCharacter::Direction3);
    Button(TEXT("LowerLeft"),EKeys::Five,&AMeleeCharacter::Direction4);Button(TEXT("LowerRight"),EKeys::Six,&AMeleeCharacter::Direction5);
    if(auto* PC=Cast<APlayerController>(GetController()))if(auto* LP=PC->GetLocalPlayer())
        LP->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>()->AddMappingContext(Context,0);
}
void AMeleeCharacter::Forward(const FInputActionValue& V)
{
    if(Combat->Simulation.health<=0)return;
    const float Amount=V.Get<float>();CastChecked<UMeleeCharacterMovementComponent>(GetCharacterMovement())->ForwardInput=Amount;
    AddMovementInput(FRotator(0,GetControlRotation().Yaw,0).Vector(),Amount);
}
void AMeleeCharacter::Right(const FInputActionValue& V){AddMovementInput(FRotationMatrix(FRotator(0,GetControlRotation().Yaw,0)).GetUnitAxis(EAxis::Y),V.Get<float>());}
void AMeleeCharacter::LookX(const FInputActionValue& V)
{
    if(auto* Lab=GetWorld()->GetAuthGameMode<ACombatLabGameMode>();Lab&&Lab->bTuningOpen)return;
    const double Delta=V.Get<float>();Direction.sample(GetWorld()->GetTimeSeconds(),Delta,0);
    Combat->Simulation.look(Delta*Combat->Tuning().MouseSensitivity,0,GetWorld()->GetDeltaSeconds(),Combat->Tuning());
    if(Controller)Controller->SetControlRotation(FRotator(Combat->Simulation.view.pitch,Combat->Simulation.view.yaw,0));
}
void AMeleeCharacter::LookY(const FInputActionValue& V)
{
    if(auto* Lab=GetWorld()->GetAuthGameMode<ACombatLabGameMode>();Lab&&Lab->bTuningOpen)return;
    const double Delta=V.Get<float>();Direction.sample(GetWorld()->GetTimeSeconds(),0,Delta);
    Combat->Simulation.look(0,Delta*Combat->Tuning().MouseSensitivity,GetWorld()->GetDeltaSeconds(),Combat->Tuning());
    if(Controller)Controller->SetControlRotation(FRotator(Combat->Simulation.view.pitch,Combat->Simulation.view.yaw,0));
}
void AMeleeCharacter::SprintStart(){CastChecked<UMeleeCharacterMovementComponent>(GetCharacterMovement())->bSprint=true;}
void AMeleeCharacter::SprintEnd(){CastChecked<UMeleeCharacterMovementComponent>(GetCharacterMovement())->bSprint=false;}
void AMeleeCharacter::CrouchStart(){Crouch();}void AMeleeCharacter::CrouchEnd(){UnCrouch();}
void AMeleeCharacter::Strike(){auto A=Direction.resolve(GetWorld()->GetTimeSeconds(),Combat->Tuning());Combat->Strike(A.angle,A.rawAngle);}
void AMeleeCharacter::Stab(){Combat->Stab();}void AMeleeCharacter::Parry(){Combat->Parry();}void AMeleeCharacter::Feint(){Combat->Feint();}
void AMeleeCharacter::ToggleDebug(){if(auto* Lab=GetWorld()->GetAuthGameMode<ACombatLabGameMode>())Lab->bDebug=!Lab->bDebug;}
void AMeleeCharacter::ToggleTuning(){if(auto* Lab=GetWorld()->GetAuthGameMode<ACombatLabGameMode>())Lab->ToggleTuning();}
void AMeleeCharacter::ToggleInspection(){if(auto* Lab=GetWorld()->GetAuthGameMode<ACombatLabGameMode>())Lab->ToggleInspection();}
void AMeleeCharacter::ResetLab(){if(auto* Lab=GetWorld()->GetAuthGameMode<ACombatLabGameMode>())Lab->ResetLab();}
void AMeleeCharacter::NextPattern(){if(auto* Lab=GetWorld()->GetAuthGameMode<ACombatLabGameMode>())Lab->NextPattern();}
void AMeleeCharacter::ToggleStamina(){Combat->Simulation.state.infiniteStamina=!Combat->Simulation.state.infiniteStamina;}
void AMeleeCharacter::Direction0(){Combat->Strike(0,0);}void AMeleeCharacter::Direction1(){Combat->Strike(60,60);}
void AMeleeCharacter::Direction2(){Combat->Strike(120,120);}void AMeleeCharacter::Direction3(){Combat->Strike(180,180);}
void AMeleeCharacter::Direction4(){Combat->Strike(-120,-120);}void AMeleeCharacter::Direction5(){Combat->Strike(-60,-60);}
void AMeleeCharacter::Tick(float Dt)
{
    Super::Tick(Dt);Presentation->Present(Combat->Simulation,Combat->Tuning(),Dt);
    const auto* PC=GetWorld()->GetFirstPlayerController();
    const bool bShowBody=!IsLocallyControlled()||(PC&&PC->GetViewTarget()!=this);
    Knight->SetFirstPerson(!bShowBody);
    BodyReaction=FMath::FInterpTo(BodyReaction,0,Dt,8);
    Knight->Present(Combat->Simulation,Combat->Tuning(),bBlueArmor,BodyReaction,Dt);
    Camera->SetFieldOfView(static_cast<float>(Combat->Tuning().FOV));
    CameraKick=FMath::FInterpTo(CameraKick,0,Dt,22);
    Camera->ClearAdditiveOffset();Camera->AddAdditiveOffset(FTransform(FRotator(CameraKick,0,CameraKick*.2)),0);
}
void AMeleeCharacter::Feedback(mcl::Resolution R)
{
    BodyReaction=1.f;
    const auto& T=Combat->Tuning();CameraKick=static_cast<float>(R==mcl::Resolution::Parry?T.ParryRecoil:R==mcl::Resolution::Chamber?T.ChamberRecoil:T.CameraHitImpulse);
}
void AMeleeCharacter::ResetAt(FVector Position,FRotator Facing)
{
    SetActorLocationAndRotation(Position,Facing,false,nullptr,ETeleportType::TeleportPhysics);GetCharacterMovement()->StopMovementImmediately();
    auto* Movement=CastChecked<UMeleeCharacterMovementComponent>(GetCharacterMovement());Movement->ResetCombatMovement();
    Combat->Simulation.reset({Position.X,Position.Y,Position.Z},{Facing.Yaw,Facing.Pitch},Combat->Tuning());
    if(Controller)Controller->SetControlRotation(Facing);
}

void AMeleeCharacter::CycleGraphics(){TournamentGraphics::Cycle();}
