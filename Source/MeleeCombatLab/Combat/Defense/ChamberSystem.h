#pragma once
#include "Combat/Attacks/AttackStateMachine.h"
namespace mcl
{
struct ChamberSystem
{
    // Express the incoming origin in the defender's view before matching.
    static AttackIntent inDefenderView(AttackIntent incoming,Orientation attacker,Orientation defender)
    {
        Vec origin=defender.local(attacker.world({0,std::cos(incoming.angle*Rad),std::sin(incoming.angle*Rad)}));
        incoming.angle=std::atan2(origin.z,origin.y)/Rad;incoming.rawAngle=incoming.angle;return incoming;
    }
    static double difference(AttackIntent incoming,AttackIntent defensive)
    {
        Vec a{std::cos(incoming.angle*Rad),std::sin(incoming.angle*Rad),0};
        Vec b{std::cos(defensive.angle*Rad),std::sin(defensive.angle*Rad),0};
        return angle(a,b);
    }
    static bool matches(const AttackStateMachine& defender,AttackIntent incoming,const Tuning& t)
    {
        if(!defender.chamberActive(t)||defender.attack.kind!=incoming.kind)return false;
        return incoming.kind==AttackKind::Stab||difference(incoming,defender.attack)<=t.ChamberTolerance;
    }
};
}
