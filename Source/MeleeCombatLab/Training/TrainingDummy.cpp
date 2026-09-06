#include "TrainingDummy.h"
#include "Visual/KnightPresentation.h"
#include "Combat/CombatComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Components/CapsuleComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"
#include "Materials/MaterialInterface.h"

ATrainingDummy::ATrainingDummy(const FObjectInitializer& O):Super(O)
{
    bUseControllerRotationYaw=false;AutoPossessAI=EAutoPossessAI::Disabled;
    Knight=CreateDefaultSubobject<UKnightPresentation>(TEXT("KnightArmor"));Knight->SetupAttachment(GetCapsuleComponent());
    Label=CreateDefaultSubobject<UTextRenderComponent>(TEXT("Label"));Label->SetupAttachment(GetCapsuleComponent());
    Label->SetRelativeLocation(FVector(0,0,130));Label->SetHorizontalAlignment(EHTA_Center);Label->SetWorldSize(11);Label->SetTextRenderColor(FColor(215,200,165));
}
void ATrainingDummy::BeginPlay(){Super::BeginPlay();}
void ATrainingDummy::React(mcl::Resolution R){Reaction=1;Feedback(R);}
void ATrainingDummy::Tick(float Dt)
{
    Super::Tick(Dt);Reaction=FMath::FInterpTo(Reaction,0,Dt,8);
    const auto& S=Combat->Simulation;
    SetActorRotation(FRotator(0,S.view.yaw,0));
    Knight->Present(bPassive,Reaction,S.health<=0,Dt);
    FString Text=S.infiniteHealth?FString::Printf(TEXT("DAMAGE TARGET | INFINITE HP\n%d HITS | %.0f DAMAGE"),S.hitsTaken,S.damageTaken):
        FString::Printf(TEXT("%s | %.0f HP\n%s"),UTF8_TO_TCHAR(mcl::trainingName(Pattern.mode)),S.health,UTF8_TO_TCHAR(mcl::phaseName(S.state.phase)));
    if(Text!=LastLabel){LastLabel=Text;Label->SetText(FText::FromString(Text));}
    if(auto* PC=GetWorld()->GetFirstPlayerController())if(auto Pawn=PC->GetPawn())Label->SetWorldRotation((Pawn->GetActorLocation()-Label->GetComponentLocation()).Rotation());
}
