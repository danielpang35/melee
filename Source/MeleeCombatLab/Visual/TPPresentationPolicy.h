#pragma once
#include "TPSourceBinding.h"

namespace mcl {
// Cosmetic aim blending only. Early-hit recovery still traverses the release arc.
struct TPPresentationPolicy {
    static bool contact(const AttackStateMachine& state,double source,bool authored) {
        const double start=state.definition.windup;
        const double end=start+EXWeaponMotion::Exit-EXWeaponMotion::Release;
        return authored&&source>=start-1.e-8&&source<=end+1.e-8;
    }
    static double cameraAim(const AttackStateMachine& state,double source,bool playing) {
        if(!playing)return 0.;
        const double start=state.definition.windup;
        const double end=start+EXWeaponMotion::Exit-EXWeaponMotion::Release;
        return smooth((source-(start-.18))/.18)*(1.-smooth((source-end)/.18));
    }
};
}
