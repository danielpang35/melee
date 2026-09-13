#pragma once
#include "Combat/Attacks/EXSourceClock.h"

namespace mcl {
// Presentation-only sampling. No phase duration, input, or contact authority.
struct TPSourceBinding {
    bool attackAge=false;
    double rate=60.,duration=2.55,idle=.30;
    bool valid() const {
        const double intervals=rate*duration;
        return std::isfinite(rate)&&rate>=1.&&rate<=240.&&
            std::isfinite(duration)&&duration>0.&&duration<=30.&&
            std::isfinite(idle)&&idle>=0.&&idle<=duration&&
            intervals>=1.&&std::abs(intervals-std::round(intervals))<1.e-6;
    }
    int frames() const {return static_cast<int>(std::round(rate*duration))+1;}
    struct Sample {double time;bool authored,tail;};
    Sample sample(const AttackStateMachine& state,double exSource,double transitionAge) const {
        const bool authored=state.exActive&&(state.phase==Phase::Windup||state.phase==Phase::Release||
            (state.phase==Phase::Recovery&&state.last!=Resolution::Wall&&state.last!=Resolution::Parry));
        if(!attackAge)return {authored?exSource:idle,authored,false};
        if(authored)return {clamp(EXSourceClock::age(state),0.,duration),true,false};
        // Natural EX completion freezes attackAge; the existing simulation
        // transition clock supplies the remaining cosmetic source recovery.
        // Resets, feints, parries, chambers and new attacks cannot inherit it.
        const bool completed=state.phase==Phase::Idle&&state.exActive&&
            (state.last==Resolution::Hit||state.last==Resolution::Miss)&&
            state.attackAge+1.e-8>=state.definition.windup+state.definition.release+state.definition.recovery;
        const double tailTime=EXSourceClock::age(state)+transitionAge;
        const bool tail=completed&&tailTime<=duration;
        return {tail?clamp(tailTime,0.,duration):idle,false,tail};
    }
};
}
