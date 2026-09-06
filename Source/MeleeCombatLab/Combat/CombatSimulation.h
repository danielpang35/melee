#pragma once
#include "Attacks/AttackTrajectory.h"
#include "Defense/ParryGeometry.h"
#include "Defense/ChamberSystem.h"
#include "Collision/WeaponTraceSystem.h"
#include <functional>
#include <unordered_set>
#include <vector>
namespace mcl
{
struct Combatant
{
    int id=0;
    AttackStateMachine state;
    Vec position,frameStart,frameTarget;
    Orientation view,desired,guard,simulatedView,frameViewStart,frameViewTarget;
    bool externalView=true,infiniteHealth=false;
    double damageTaken=0;int hitsTaken=0;
    LocalPose local=AttackTrajectory::rest(),windupStart=AttackTrajectory::rest(),returnStart=AttackTrajectory::rest();
    Pose weapon,previousWeapon;
    double health=100,bodyRadius=32,bodyHalfHeight=88,eyeHeight=64,returnAge=1;
    double speed=0,angularSpeed=0,incomingAngle=0,chamberDifference=0;
    std::uint64_t trackedSerial=0;
    std::unordered_set<int> hitActors;
    std::vector<Segment> traces;
    ParryGeometry defense;
    bool start(AttackIntent intent,const Tuning& t);
    void flinch();
    bool feint(const Tuning& t);
    bool parry(const Tuning& t);
    void look(double yawDelta,double pitchDelta,double dt,const Tuning& t);
    void reset(Vec at,Orientation facing,const Tuning& t);
    Segment hurtAxis() const {return {position+Vec{0,0,-bodyHalfHeight+bodyRadius},position+Vec{0,0,bodyHalfHeight-bodyRadius}};}
    void advance(double dt,const Tuning& t);
};
struct CombatEvent { Resolution result; int attacker,defender; Vec point; double time; };
class CombatSimulation
{
public:
    Tuning tuning;
    std::vector<Combatant*> actors;
    std::vector<CombatEvent> events;
    // World query excludes registered combatants; UE owns world collision, core owns combat resolution.
    std::function<bool(int,Segment,double,Vec&)> worldSweep;
    std::function<void(double)> beforeStep;
    double time=0,accumulator=0;
    int stepsLastFrame=0,queriesLastFrame=0;
    bool overload=false;
    void advance(double dt);
    void resolve();
    void emit(Resolution r,Combatant& attacker,Combatant* defender,Vec point);
};
}
