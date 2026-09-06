#pragma once
#include "AttackDefinition.h"
#include <cstdint>
namespace mcl
{
struct AttackStateMachine
{
    Phase phase=Phase::Idle;
    AttackIntent attack,queued;
    AttackDefinition definition=AttackDefinition::make(AttackKind::Strike,Tuning{});
    double elapsed=0,attackAge=0,releaseRotation=0,riposteRemaining=0;
    double stamina=100,lastSpend=100;
    bool infiniteStamina=true,comboQueued=false,isCombo=false,isRiposte=false,morphed=false,hitSomeone=false;
    std::uint64_t serial=0;
    Resolution last=Resolution::None;
    double duration() const;
    double progress() const { return clamp(elapsed/duration(),0.,1.); }
    bool canFeint(const Tuning& t) const;
    bool canMorph(const Tuning& t) const;
    bool canCombo(const Tuning& t) const;
    bool chamberActive(const Tuning& t) const;
    bool damaging() const;
    bool spend(double cost);
    bool start(AttackIntent intent,const Tuning& t);
    bool feint(const Tuning& t);
    bool parry(const Tuning& t);
    void parrySuccess(const Tuning& t);
    void flinch();
    void cancel(Resolution result);
    void advance(double dt,const Tuning& t);
    double yawCap(const Tuning& t) const;
};
}
