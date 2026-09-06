#pragma once
#include "AttackTypes.h"
#include "Combat/CombatTuning.h"
namespace mcl
{
struct AttackDefinition
{
    double windup,release,recovery,damageStart,damageEnd;
    static AttackDefinition make(AttackKind kind,const Tuning& t)
    {
        return kind==AttackKind::Strike?AttackDefinition{t.StrikeWindup,t.StrikeRelease,t.StrikeRecovery,t.DamageStart,t.DamageEnd}:
            AttackDefinition{t.StabWindup,t.StabRelease,t.StabRecovery,t.DamageStart,t.DamageEnd};
    }
};
}
