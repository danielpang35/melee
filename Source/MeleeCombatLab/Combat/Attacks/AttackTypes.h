#pragma once
#include "Combat/CombatMath.h"
namespace mcl
{
enum class AttackKind { Strike,Stab };
enum class Phase { Idle,Windup,Release,Recovery,Parry,ParryRecovery,Flinch,Dead };
enum class Resolution { None,Hit,Parry,Chamber,Miss,Wall,Feint,Morph,Combo,Riposte };
// Angle is in the attacker's view plane: 0=right; +60=upper right; +120=upper left.
struct AttackIntent { AttackKind kind=AttackKind::Strike; double rawAngle=0,angle=0; };
inline const char* phaseName(Phase p)
{
    constexpr const char* names[]={"IDLE","WINDUP","RELEASE","RECOVERY","PARRY","PARRY RECOVERY","FLINCH","DEAD"};
    return names[static_cast<int>(p)];
}
inline const char* resultName(Resolution r)
{
    constexpr const char* names[]={"--","HIT","PARRY","CHAMBER","MISS","WALL","FEINT","MORPH","COMBO","RIPOSTE"};
    return names[static_cast<int>(r)];
}
}
