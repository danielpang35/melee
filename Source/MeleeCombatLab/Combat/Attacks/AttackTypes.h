#pragma once
#include "Combat/CombatMath.h"
namespace mcl
{
enum class AttackKind { Strike,Stab };
enum class Phase { Idle,Windup,Release,Recovery,Parry,ParryRecovery,Flinch,Dead };
enum class Resolution { None,Hit,Parry,Chamber,Miss,Wall,Feint,Morph,Combo,Riposte };
// Cosmetic contact tag; it does not alter damage or collision priority.
enum class ContactRegion { None,Body,Head };
inline ContactRegion contactRegion(Resolution result,Vec point,Vec center,double halfHeight,double radius)
{
    if(result!=Resolution::Hit)return ContactRegion::None;
    // The current hurt volume is one capsule. Use its upper 26 cm for head
    // feedback until anatomical hit volumes are available. Follow crouch/scale.
    const double headDepth=std::min(26.,std::min(radius,halfHeight));
    return point.z>=center.z+halfHeight-headDepth?ContactRegion::Head:ContactRegion::Body;
}
// Angle is in the attacker's view plane: 0=right; +60=upper right; +120=upper left.
// Stance is the body-side origin, not the right/left identity of either grip hand.
enum class Stance { Auto,Right,Left };
struct AttackIntent { AttackKind kind=AttackKind::Strike; double rawAngle=0,angle=0; Stance stance=Stance::Auto; };
inline Stance resolvedStance(AttackIntent intent)
{
    if(intent.stance!=Stance::Auto)return intent.stance;
    // Exact vertical has a deterministic default, independent of floating cosine sign.
    return std::cos(intent.angle*Rad)<-1e-10?Stance::Left:Stance::Right;
}
inline Stance oppositeStance(Stance stance) { return stance==Stance::Left?Stance::Right:Stance::Left; }
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
