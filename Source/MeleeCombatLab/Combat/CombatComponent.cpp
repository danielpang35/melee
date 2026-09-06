#include "CombatComponent.h"
#include "Training/CombatLabGameMode.h"
#include "GameFramework/Actor.h"
#include "Engine/World.h"

UCombatComponent::UCombatComponent(){PrimaryComponentTick.bCanEverTick=false;}
void UCombatComponent::BeginPlay()
{
    Super::BeginPlay();
    if(auto* Lab=GetWorld()->GetAuthGameMode<ACombatLabGameMode>())Lab->Register(this);
}
void UCombatComponent::EndPlay(const EEndPlayReason::Type Reason)
{
    if(auto* Lab=GetWorld()->GetAuthGameMode<ACombatLabGameMode>())Lab->Unregister(this);
    Super::EndPlay(Reason);
}
const mcl::Tuning& UCombatComponent::Tuning() const
{
    if(auto* Lab=GetWorld()->GetAuthGameMode<ACombatLabGameMode>())return Lab->Combat.tuning;
    static const mcl::Tuning Defaults;return Defaults;
}
void UCombatComponent::Strike(double Angle,double RawAngle){Simulation.start({mcl::AttackKind::Strike,RawAngle,Angle},Tuning());}
void UCombatComponent::Stab(){Simulation.start({mcl::AttackKind::Stab,0,0},Tuning());}
void UCombatComponent::Feint(){Simulation.feint(Tuning());}
void UCombatComponent::Parry(){Simulation.parry(Tuning());}
