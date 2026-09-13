#include "CombatDrawTracers.h"
#include "Training/CombatLabGameMode.h"
#include "Character/MeleeCharacter.h"
#include "Combat/CombatComponent.h"
#include "Visual/KnightPresentation.h"
#include "Visual/EXCombatPresentation.h"
#include "Camera/WeaponPresentationComponent.h"
#include "Components/LineBatchComponent.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "HAL/IConsoleManager.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

namespace {
TAutoConsoleVariable<int32> DrawTracers(TEXT("mcl.DrawTracers"),0,TEXT("F8: collision sweeps (orange), rendered blade (cyan), endpoint gaps (magenta)."));
TAutoConsoleVariable<float> StayTime(TEXT("mcl.DrawTracersStayTime"),2.f,TEXT("Tracer history in simulation seconds, clamped to 0.05..10; F9 clears."));
FVector V(mcl::Vec P){return {P.x,P.y,P.z};}
const FColor Contact(255,145,25),Presentation(30,225,255),Gap(255,45,210);
}
UCombatDrawTracers::UCombatDrawTracers()
{
    PrimaryComponentTick.bCanEverTick=true;
    PrimaryComponentTick.TickGroup=TG_PostUpdateWork;
}
bool UCombatDrawTracers::Enabled() const {return DrawTracers.GetValueOnGameThread()!=0;}
void UCombatDrawTracers::BeginPlay()
{
    Super::BeginPlay();
    // GameMode inherits hidden AInfo; geometry needs its own visible owner.
    FActorSpawnParameters Spawn;Spawn.ObjectFlags|=RF_Transient;
    auto* LineActor=GetWorld()->SpawnActor<AActor>(Spawn);
    Lines=NewObject<ULineBatchComponent>(LineActor);LineActor->AddInstanceComponent(Lines);
    Lines->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Lines->SetComponentTickEnabled(false); // History owns lifetime, including immediate clear/off.
    Lines->RegisterComponent();
    AddTickPrerequisiteActor(GetOwner());
    if(FParse::Param(FCommandLine::Get(),TEXT("DrawTracers")))DrawTracers->Set(1,ECVF_SetByCode);
}
void UCombatDrawTracers::Clear()
{
    History.clear();MaxGapCm=0;VisibleActors=0;
    if(Lines)Lines->Flush();
}
void UCombatDrawTracers::Toggle()
{
    DrawTracers->Set(Enabled()?0:1,ECVF_SetByConsole);Clear();
    UE_LOG(LogTemp,Display,TEXT("DRAW_TRACERS %s"),Enabled()?TEXT("on"):TEXT("off"));
}
void UCombatDrawTracers::Add(FVector A,FVector B,FColor Color,double Time,float Width)
{
    constexpr size_t MaxLines=24000;
    if(History.size()==MaxLines)History.pop_front();
    History.push_back({A,B,Color,Time,Width});
}
void UCombatDrawTracers::Sample(const mcl::Combatant& S,double Time)
{
    if(!Enabled())return;
    // These are the actual capsule sweep centerlines used by resolve(), including
    // substeps ending in hit/flinch. Line thickness is NOT collision radius.
    if(S.intervalDamage)for(const auto& Sweep:S.traces)Add(V(Sweep.a),V(Sweep.b),Contact,Time,.45f);
}
void UCombatDrawTracers::TickComponent(float Dt,ELevelTick Type,FActorComponentTickFunction* Tick)
{
    Super::TickComponent(Dt,Type,Tick);
    auto* Lab=Cast<ACombatLabGameMode>(GetOwner());if(!Lab||!Lines)return;
    const bool On=Enabled();
    if(!On){if(WasEnabled||!History.empty())Clear();WasEnabled=false;return;}
    WasEnabled=true;
    auto* PC=GetWorld()->GetFirstPlayerController();AActor* View=PC?PC->GetViewTarget():nullptr;
    if(ViewTarget.Get()!=View){Clear();ViewTarget=View;}
    MaxGapCm=0;VisibleActors=0;
    for(const auto& C:Lab->Combatants){
        if(!IsValid(C))continue;
        auto* Pawn=Cast<AMeleeCharacter>(C->GetOwner());if(!Pawn)continue;
        const auto& S=C->Simulation;
        if(S.state.phase!=mcl::Phase::Release)continue;
        FVector Base,Tip;bool Visible=false;
        if(View!=Pawn&&Pawn->Knight&&Pawn->Knight->TPActive){
            Base=Pawn->Knight->TPBladeBase;Tip=Pawn->Knight->TPBladeTip;Visible=true;
        }else if(Pawn->EXPresentation)Visible=Pawn->EXPresentation->GetVisibleBlade(Base,Tip);
        if(!Visible&&Pawn->Presentation&&Pawn->Presentation->IsVisible()){
            const auto Blade=Pawn->Presentation->RenderedBlade();Base=V(Blade.hilt);Tip=V(Blade.tip);Visible=true;
        }
        if(!Visible)continue;
        ++VisibleActors;
        const double BaseGap=FVector::Distance(Base,V(S.weapon.hilt)),TipGap=FVector::Distance(Tip,V(S.weapon.tip));
        MaxGapCm=FMath::Max(MaxGapCm,FMath::Max(BaseGap,TipGap));
        Add(Base,Tip,Presentation,Lab->Combat.time,1.2f);
        // Same-frame endpoint disagreement, not a claim of exact event-time contact.
        if(BaseGap>.5)Add(Base,V(S.weapon.hilt),Gap,Lab->Combat.time,.7f);
        if(TipGap>.5)Add(Tip,V(S.weapon.tip),Gap,Lab->Combat.time,.7f);
    }
    const double Cutoff=Lab->Combat.time-FMath::Clamp(StayTime.GetValueOnGameThread(),.05f,10.f);
    while(!History.empty()&&History.front().Time<Cutoff)History.pop_front();
    TArray<FBatchedLine> Batch;Batch.Reserve(static_cast<int32>(History.size()));
    for(const auto& L:History)Batch.Emplace(L.A,L.B,FLinearColor(L.Color),0.f,L.Width,0);
    Lines->Flush();Lines->DrawLines(Batch);
}


void UCombatDrawTracers::EndPlay(const EEndPlayReason::Type Reason)
{
    if(Lines&&Lines->GetOwner())Lines->GetOwner()->Destroy();
    Super::EndPlay(Reason);
}
