#include "MeleeCharacter.h"
#include "Debug/CombatDrawTracers.h"
#include "Visual/TournamentGraphics.h"
#include "Visual/KnightPresentation.h"
#include "Visual/EXCombatPresentation.h"
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
    Camera->SetRelativeLocation(FVector(0,0,82));Camera->bUsePawnControlRotation=true;
    Presentation=CreateDefaultSubobject<UWeaponPresentationComponent>(TEXT("WeaponPresentation"));Presentation->SetupAttachment(GetCapsuleComponent());
    EXPresentation=CreateDefaultSubobject<UEXCombatPresentation>(TEXT("EXGameplayPresentation"));
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
    Button(TEXT("DrawTracers"),EKeys::F8,&AMeleeCharacter::ToggleTracers);
    Button(TEXT("ClearTracers"),EKeys::F9,&AMeleeCharacter::ClearTracers);
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
    Super::Tick(Dt);
    const auto* PC=GetWorld()->GetFirstPlayerController();
    const bool bShowBody=!PC||PC->GetViewTarget()!=this;
    const bool bEX=EXPresentation->Present(Combat->Simulation,Dt,!bShowBody);
    if(!bEX)Presentation->Present(Combat->Simulation,Combat->Tuning(),Dt,!bShowBody);
    Presentation->SetVisibility(!bEX,true);
    Knight->SetFirstPerson(!bShowBody);
    BodyReaction=FMath::FInterpTo(BodyReaction,0,Dt,8);
    if(!bEX||bShowBody)Knight->Present(Combat->Simulation,Combat->Tuning(),bBlueArmor,BodyReaction,Dt,bEX?mcl::Vec{}:Presentation->ViewOffset);
    if(bEX&&!bShowBody)Knight->SetVisibility(false,true);
    const auto Eye=bEX?Combat->Simulation.exSampleEye:Combat->Simulation.eye();
    Camera->SetWorldLocation(FVector(Eye.x,Eye.y,Eye.z));
    Camera->SetFieldOfView(bEX?FMath::RadiansToDegrees(2.f*FMath::Atan(36.f/40.f)):static_cast<float>(Combat->Tuning().FOV));
    CameraKick=FMath::FInterpTo(CameraKick,0,Dt,22);
    CameraRoll=FMath::FInterpTo(CameraRoll,0,Dt,22);
    Camera->ClearAdditiveOffset();Camera->AddAdditiveOffset(FTransform(FRotator(CameraKick,0,CameraRoll)),0);
}
void AMeleeCharacter::CalcCamera(float Dt,FMinimalViewInfo& OutResult)
{
    Super::CalcCamera(Dt,OutResult);
    // Raised glove surfaces remain 5+ cm ahead of the shared eye, but the
    // engine's 10 cm default slices them. Use a first-person near plane inside
    // the existing 6 cm camera world-clearance sphere.
    OutResult.PerspectiveNearClipPlane=2.f;
    if(EXPresentation&&EXPresentation->Ready()){
        const auto& S=Combat->Simulation;
        OutResult.Location=FVector(S.exSampleEye.x,S.exSampleEye.y,S.exSampleEye.z);
        OutResult.Rotation=FRotator(S.exSampleView.pitch,S.exSampleView.yaw,0);
    }
}
void AMeleeCharacter::Feedback(mcl::Resolution R)
{
    BodyReaction=1.f;
    const auto& T=Combat->Tuning();CameraKick=static_cast<float>(R==mcl::Resolution::Parry?T.ParryRecoil:R==mcl::Resolution::Chamber?T.ChamberRecoil:T.CameraHitImpulse);
}
void AMeleeCharacter::Feedback(const mcl::CombatEvent& Event)
{
    const auto& T=Combat->Tuning();
    const bool Victim=Combat->Simulation.id==Event.defender;
    const mcl::Vec Local=Combat->Simulation.view.local(Event.normal*(Victim?-1.:1.));
    const double scale=(Event.result==mcl::Resolution::Chamber?T.ChamberRecoil:
        Event.result==mcl::Resolution::Parry?T.ParryRecoil:T.CameraHitImpulse)*
        (.35+.65*Event.energy)*(Victim?.6:.35);
    CameraKick=static_cast<float>(-Local.x*scale);CameraRoll=static_cast<float>(Local.y*scale);
    // Directional skeletal shock is driven by the contact-time simulation.
    BodyReaction=0;
}
void AMeleeCharacter::ResetAt(FVector Position,FRotator Facing)
{
    SetActorLocationAndRotation(Position,Facing,false,nullptr,ETeleportType::TeleportPhysics);GetCharacterMovement()->StopMovementImmediately();
    auto* Movement=CastChecked<UMeleeCharacterMovementComponent>(GetCharacterMovement());Movement->ResetCombatMovement();
    Combat->Simulation.reset({Position.X,Position.Y,Position.Z},{Facing.Yaw,Facing.Pitch},Combat->Tuning());
    if(Controller)Controller->SetControlRotation(Facing);
}

void AMeleeCharacter::CycleGraphics(){TournamentGraphics::Cycle();}

void AMeleeCharacter::ToggleTracers(){if(auto* Lab=GetWorld()->GetAuthGameMode<ACombatLabGameMode>())if(Lab->Tracers)Lab->Tracers->Toggle();}
void AMeleeCharacter::ClearTracers(){if(auto* Lab=GetWorld()->GetAuthGameMode<ACombatLabGameMode>())if(Lab->Tracers)Lab->Tracers->Clear();}
