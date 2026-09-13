#pragma once
#include "AttackStateMachine.h"
#include "EXWeaponMotion.h"

namespace mcl {
// One phase map shared by native presentation and collision substeps.
// Timing is selected at attack start; player manipulation never changes this rate.
struct EXSourceClock {
    static double age(const AttackStateMachine& state,double attackAge) {
        const double windup=state.definition.windup;
        const double release=state.definition.release;
        const double sourceRelease=EXWeaponMotion::Exit-EXWeaponMotion::Release;
        if(attackAge<=windup)return std::max(0.,attackAge);
        if(attackAge<=windup+release)
            return windup+(attackAge-windup)*sourceRelease/release;
        return attackAge-release+sourceRelease;
    }
    static double age(const AttackStateMachine& state){return age(state,state.attackAge);}
    static double time(const AttackStateMachine& state,double attackAge){
        return clamp(EXWeaponMotion::Start+age(state,attackAge),EXWeaponMotion::Start,EXWeaponMotion::End);
    }
};
}
