#pragma once
#include "Attacks/AttackTrajectory.h"
#include "Attacks/AuthoredRightCut.h"
#include "Attacks/EXWeaponMotion.h"
#include "Defense/ParryGeometry.h"
#include "Defense/ChamberSystem.h"
#include "Collision/WeaponTraceSystem.h"
#include <functional>
#include <array>
#include <unordered_set>
#include <vector>
namespace mcl
{
struct SwingDiagnostics
{
    double p=0,q=0,intrinsicAngularSpeed=0,yawRate=0,pitchRate=0,yawUtilization=0,pitchUtilization=0;
    Vec localTipVelocity,intrinsicTipVelocity,yawTipVelocity,pitchTipVelocity,translationVelocity;
    Vec hiltVelocity,tipVelocity;
};
struct Combatant
{
    std::shared_ptr<const EXWeaponMotion> exMotion;
    double exSourceTime=EXWeaponMotion::Start,exTransitionAge=1;
    Phase exPhase=Phase::Idle;
    std::uint64_t exSerial=0;
    Pose exFrom;
    Vec exSampleEye;Orientation exSampleView;
    bool intervalRelease=false,intervalDamage=false,exEntryBridge=false;
    void syncEXTransition();
    Pose exWorld(Pose p) const {const Vec pivot{11.5,0,168};return
        {eye()+view.world(p.hilt-pivot),eye()+view.world(p.tip-pivot),view.world(p.edge)};}
    Pose cameraPose(Pose p) const {return {view.local(p.hilt-eye()),view.local(p.tip-eye()),view.local(p.edge)};}
    void finishBoundary(const Tuning& t);
    void advanceEX(double dt,const Tuning& t);
    std::shared_ptr<const AuthoredRightCut> rightCut;
    LocalPose evaluateWeapon(const AttackStateMachine& s,const Tuning& t) const {
        return rightCut?rightCut->evaluate(s,windupStart,windupVelocity,t):
            AttackTrajectory::evaluate(s,windupStart,t,windupVelocity);
    }
    int id=0;
    AttackStateMachine state;
    Vec position,frameStart,frameTarget;
    Orientation view,desired,guard,simulatedView,frameViewStart,frameViewTarget;
    bool externalView=true,infiniteHealth=false;
    double damageTaken=0;int hitsTaken=0;
    LocalPose local=AttackTrajectory::rest(),windupStart=AttackTrajectory::rest(),returnStart=AttackTrajectory::rest();
    Vec desiredHilt;
    LocalPose localVelocity={{},{}},windupVelocity={{},{}};
    Pose weapon,previousWeapon;
    BodyMotion bodyMotion,bodyStart;
    Vec tipVelocity,tipAcceleration;
    SwingDiagnostics motion;
    Vec sampledPosition,lungeVelocity,inheritedVelocity;
    Orientation sampledView;
    double lungeDisplacement=0;
    Vec contactNormal;
    double contactAge=1,contactStrength=0;
    Resolution contactKind=Resolution::None;
    double reachCorrection=0;
    double health=100,bodyRadius=32,bodyHalfHeight=88,eyeHeight=82,returnAge=1;
    double torsoPitchScale=.75,leanFraction=1.;
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
    Vec uprightEye() const {return position+Vec{0,0,eyeHeight};}
    BodyFrame bodyFrame() const {return BodyFrame::make(uprightEye(),view,clamp(view.pitch,-85.,85.)*torsoPitchScale*leanFraction);}
    Vec eye() const {return bodyFrame().eye();}
    Vec weaponOrigin() const {const auto f=bodyFrame();return f.eye()-f.torso.up()*18.;}
    Vec guardAnchor() const {return position+eye()-uprightEye();}
    std::array<Segment,2> hurtAxes() const {
        const auto frame=bodyFrame();
        const Vec bottom=position+Vec{0,0,-bodyHalfHeight+bodyRadius};
        const Vec top=position+Vec{0,0,bodyHalfHeight-bodyRadius};
        // Clamp only for nonstandard short capsules; standing and crouched
        // Citadel dimensions keep a continuous lower / upper capsule union.
        const Vec joint{position.x,position.y,clamp(frame.hip.z,bottom.z,top.z)};
        return {{{bottom,joint},{joint,frame.transform(top)}}};
    }
    ContactRegion region(Resolution result,Vec point) const {
        return contactRegion(result,bodyFrame().untransform(point),position,bodyHalfHeight,bodyRadius);
    }
    Vec nearestHurtPoint(Vec point) const {
        Vec nearest;double distance=1e30;
        for(const auto axis:hurtAxes()){
            const Vec delta=axis.b-axis.a;
            const Vec candidate=axis.a+delta*clamp((point-axis.a).dot(delta)/std::max(1e-12,delta.dot(delta)),0.,1.);
            const double d=(point-candidate).length();
            if(d<distance){distance=d;nearest=candidate;}
        }
        return nearest;
    }
    void advance(double dt,const Tuning& t,bool deferTransitions=false);
};
// Feedback consumers receive the contact-time motion, not a later frame's pose.
// Direction is incoming tip travel; it is not a fabricated surface normal.
struct CombatEvent { Resolution result; int attacker,defender; Vec point; double time;
    Vec incomingVelocity; double energy=0; Vec normal; ContactRegion region=ContactRegion::None; };
class CombatSimulation
{
public:
    Tuning tuning;
    std::vector<Combatant*> actors;
    std::vector<CombatEvent> events;
    // World query excludes registered combatants; UE owns world collision, core owns combat resolution.
    std::function<bool(int,Segment,double,Vec&,Vec&)> worldSweep;
    std::function<void(double)> beforeStep;
    // World obstruction limits the shared lean, never just the rendered camera.
    std::function<double(const Combatant&)> constrainLean;
    std::function<void(const Combatant&,double)> sampleStep;
    double time=0,accumulator=0;
    int stepsLastFrame=0,queriesLastFrame=0;
    bool overload=false;
    void advance(double dt);
    void resolve(bool interval=false);
    void emit(Resolution r,Combatant& attacker,Combatant* defender,Vec point,Vec normal={});
};
}
