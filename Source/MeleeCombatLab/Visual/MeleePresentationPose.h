#pragma once
#include "Combat/CombatSimulation.h"
#include <array>

// Read-only adapter. Rig/Control Rig consumers take these world-space targets;
// they never write a socket transform back into Combatant::weapon.
namespace mcl::presentation
{
constexpr double UpperArmLength=30.413813,ForearmLength=25.387005;
struct ArmPose { Vec shoulder,elbow,hand; double reachScale=1.; };
struct PoseFrame
{
    Pose blade;
    Vec axis,edge,normal;
    BodyMotion body;
    std::array<ArmPose,2> arms;
};

// The humeral plane is authored in the moving rib-cage frame. A glove frame
// supplies only a bounded wrist preference; it must never choose the elbow's
// hemisphere. This function is stateless, including at full reach.
inline Vec armPlane(Vec shoulder,Vec wrist,Vec rail)
{
    const Vec axis=(wrist-shoulder).normal();
    Vec plane=rail-axis*rail.dot(axis);
    if(plane.length()<1e-5){
        const Vec fallback=std::abs(axis.z)<.9?Vec{0,0,-1}:Vec{1,0,0};
        plane=fallback-axis*fallback.dot(axis);
    }
    return plane.normal();
}

inline Vec elbowRail(const Combatant& s,const BodyMotion& body,int side,bool firstPerson=false)
{
    const double sign=side==0?1.:-1.;
    const double out=side==0?body.rightElbowOut:body.leftElbowOut;
    const double lift=side==0?body.rightElbowLift:body.leftElbowLift;
    const Orientation chest{s.view.yaw+body.chestYaw,body.chestPitch};
    // Reach forward from a relaxed humerus; loading elevates the elbow in the
    // scapular plane, while carry lets it descend behind the moving hands.
    // These authored weights are part of the saved body pose. Contact stops
    // and new attacks inherit the actual humeral organization at the transition.
    const double carry=body.elbowCarry;
    const double forearmCarry=side==0?body.rightForearmCarry:body.leftForearmCarry;
    // As the hands descend, the humeri settle beside the ribs. A forward
    // carry plane put the elbows ahead of the wrists and folded the forearms
    // back toward the chest. The pommel arm retains more forward elevation.
    const Vec descending{mix(.48,side==0?.15:.35,carry),sign*((firstPerson?.34:.46)+out*.018),
        mix((firstPerson?-1.20:-1.05)+lift*.065,-1.20,carry)};
    // The trailing humerus rises with the high guard. Store the weighted
    // target in BodyMotion so a new attack origin cannot flip a captured arm.
    const double highGuardWeight=side==0?body.rightHighGuardWeight:body.leftHighGuardWeight;
    const Vec highGuardRail=side==0?body.rightHighGuardRail:body.leftHighGuardRail;
    const Vec loaded=descending*(1.-highGuardWeight)+highGuardRail;
    const Vec local=lerp(loaded,{1.15,sign*.4,.10},forearmCarry);
    return s.bodyFrame().vector(chest.world(local));
}

inline Vec assistArmPlane(Vec shoulder,Vec wrist,Vec forearmDirection,Vec rail)
{
    const Vec axis=(wrist-shoulder).normal();
    const Vec base=armPlane(shoulder,wrist,rail);
    const Vec wanted=axis*forearmDirection.dot(axis)-forearmDirection;
    // A vector blend has no +/-pi clamp seam and vanishes smoothly when the
    // forearm is parallel to the reach. Its maximum angular influence is 20deg.
    return (base+wanted.normal()*(std::min(wanted.length(),1.)*.342)).normal();
}

inline ArmPose solveArm(Vec shoulder,Vec hand,Vec pole,double upper=UpperArmLength,double lower=ForearmLength)
{
    Vec delta=hand-shoulder;
    const double distance=delta.length();
    const Vec axis=distance>1e-6?delta/distance:Vec{1,0,0};
    pole=pole-axis*pole.dot(axis);
    if(pole.length()<1e-5){
        const Vec fallback=std::abs(axis.z)<.9?Vec{0,0,-1}:Vec{0,1,0};
        pole=fallback-axis*fallback.dot(axis);
    }
    // Imported or unvalidated hand targets may exceed anatomical reach.
    // Stretch the cosmetic links only; keep both grip contacts exact. Expose
    // reachScale so a future rig can distribute this across clavicle and spine.
    const double scale=std::max(1.,distance/(upper+lower-.5));
    upper*=scale;lower*=scale;
    const double d=std::max(distance,1e-6);
    const double along=clamp((d*d+upper*upper-lower*lower)/(2*d),-upper,upper);
    const double bend=std::sqrt(std::max(0.,upper*upper-along*along));
    return {shoulder,shoulder+axis*along+pole.normal()*bend,hand,scale};
}

struct GripArmPose { ArmPose arm; Vec handRadial; double wristBend=0.; };

// Visual attachment: an authored elbow direction and wrist twist, followed by
// one two-bone fit. No iterative shoulder fitting, wrist feedback, or dynamics.
// Any reach adaptation belongs exclusively to the cosmetic mesh.
inline GripArmPose attachPerformanceArm(Vec shoulder,Vec grip,Vec shaft,Vec elbowDirection,
    double wristTwist,Vec restGrip,Vec restLower,Vec palmOffset,double upper,double lower)
{
    shaft=shaft.normal();restGrip=restGrip.normal();restLower=restLower.normal();
    const Vec sourceRadial=(restLower-restGrip*restLower.dot(restGrip)).normal();
    const Vec sourceSide=restGrip.cross(sourceRadial);
    const Vec authoredElbow=shoulder+elbowDirection.normal()*upper;
    Vec radial=armPlane({},shaft,grip-authoredElbow);
    const double twist=wristTwist*Rad;
    radial=radial*std::cos(twist)+shaft.cross(radial)*std::sin(twist);
    const Vec offset=radial*palmOffset.dot(sourceRadial)+shaft.cross(radial)*palmOffset.dot(sourceSide)+shaft*palmOffset.dot(restGrip);
    const Vec wrist=grip-offset;
    const auto arm=solveArm(shoulder,wrist,elbowDirection,upper,lower);
    const Vec mappedLower=radial*restLower.dot(sourceRadial)+shaft*restLower.dot(restGrip);
    return {arm,radial,angle(wrist-arm.elbow,mappedLower)};
}

// Choose pronation from a body-authored guide arm, before placing the wrist.
// The palm's radial offset must not feed back into that orientation: the old
// fixed-point loop could jump between two glove orientations in one frame.
inline GripArmPose solveGripArm(Vec bodyShoulder,Vec clavicleStart,double clavicleLength,
    Vec grip,Vec shaft,Vec rail,Vec restGrip,Vec restLower,Vec palmOffset,
    double upper=UpperArmLength,double lower=ForearmLength)
{
    shaft=shaft.normal();restGrip=restGrip.normal();restLower=restLower.normal();
    const Vec sourceRadial=(restLower-restGrip*restLower.dot(restGrip)).normal();
    const Vec sourceSide=restGrip.cross(sourceRadial);
    const auto fitShoulder=[&](Vec wrist){
        Vec anchor=bodyShoulder;
        for(int pass=0;pass<6;++pass){
            const Vec reach=wrist-anchor;
            if(reach.length()>upper+lower-1.)anchor=wrist-reach.normal()*(upper+lower-1.);
            if(clavicleLength>0.)anchor=clavicleStart+(anchor-clavicleStart).normal()*clavicleLength;
        }
        return anchor;
    };
    const Vec guide=grip-shaft*palmOffset.dot(restGrip);
    const auto guideArm=solveArm(fitShoulder(guide),guide,rail,upper,lower);
    const Vec guideForearm=(guide-guideArm.elbow).normal();
    Vec radial=guideForearm-shaft*guideForearm.dot(shaft);
    if(radial.length()<1e-5)radial=armPlane({},shaft,rail);
    radial=radial.normal();
    const Vec mappedOffset=radial*palmOffset.dot(sourceRadial)+
        shaft.cross(radial)*palmOffset.dot(sourceSide)+shaft*palmOffset.dot(restGrip);
    const Vec wrist=grip-mappedOffset;
    const Vec shoulder=fitShoulder(wrist);
    const Vec mappedLower=radial*restLower.dot(sourceRadial)+shaft*restLower.dot(restGrip);
    const auto arm=solveArm(shoulder,wrist,assistArmPlane(shoulder,wrist,mappedLower,rail),upper,lower);
    return {arm,radial,angle(wrist-arm.elbow,mappedLower)};
}


inline PoseFrame evaluate(const Combatant& s,const Tuning& t,bool solveLegacyArms=true)
{
    PoseFrame f;
    f.blade=s.weapon;f.body=s.bodyMotion;
    f.axis=(f.blade.tip-f.blade.hilt).normal();
    if(f.axis.length()<.5)f.axis=s.view.forward();
    // Runtime blades carry the authoritative frame, including authored roll.
    // Only legacy test/manual poses with no edge reconstruct their frame here.
    f.edge=f.blade.edge.length()>0.?f.blade.edge:weaponEdge(f.axis,s.view,f.body.gripRoll);
    f.normal=f.axis.cross(f.edge).normal();
    for(int i=0;i<2;++i){
        const Vec shoulder=AttackTrajectory::shoulder(s.uprightEye(),s.view,f.body,i,s.bodyFrame().torso.pitch);
        // Estoc calibration: source blade base Z=.19 m, tip Z=1.293061 m.
        // Palm contacts at Z=.07 / -.04 m sit on leather behind the guard.
        const double gripDepth=t.BladeLength*(i==0?.12:.23)/1.103061375617981;
        const Vec hand=f.blade.hilt-f.axis*gripDepth;
        f.arms[i]=solveLegacyArms?solveArm(shoulder,hand,elbowRail(s,f.body,i)):ArmPose{shoulder,{},hand,1.};
    }
    return f;
}
}
