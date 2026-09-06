#pragma once
#include "Combat/CombatSimulation.h"
#include <array>

// Read-only adapter. Rig/Control Rig consumers take these world-space targets;
// they never write a socket transform back into Combatant::weapon.
namespace mcl::presentation
{
struct ArmPose { Vec shoulder,elbow,hand; double reachScale=1.; };
struct PoseFrame
{
    Pose blade;
    Vec axis,edge,normal;
    BodyMotion body;
    std::array<ArmPose,2> arms;
};

inline ArmPose solveArm(Vec shoulder,Vec hand,Vec pole,double upper=36.,double lower=34.)
{
    Vec delta=hand-shoulder;
    const double distance=delta.length();
    const Vec axis=distance>1e-6?delta/distance:Vec{1,0,0};
    pole=pole-axis*pole.dot(axis);
    if(pole.length()<1e-5){
        const Vec fallback=std::abs(axis.z)<.9?Vec{0,0,-1}:Vec{0,1,0};
        pole=fallback-axis*fallback.dot(axis);
    }
    // The frozen hand trajectory exceeds anatomical reach at extreme pitch.
    // Stretch the cosmetic links only; keep both grip contacts exact. Expose
    // reachScale so a future rig can distribute this across clavicle and spine.
    const double scale=std::max(1.,distance/(upper+lower-.5));
    upper*=scale;lower*=scale;
    const double d=std::max(distance,1e-6);
    const double along=clamp((d*d+upper*upper-lower*lower)/(2*d),-upper,upper);
    const double bend=std::sqrt(std::max(0.,upper*upper-along*along));
    return {shoulder,shoulder+axis*along+pole.normal()*bend,hand,scale};
}

inline PoseFrame evaluate(const Combatant& s,const Tuning& t)
{
    PoseFrame f;
    f.blade=s.weapon;f.body=AttackTrajectory::body(s.state,t);
    // Defensive body poses belong to presentation. Guard contact and the blade
    // remain exact while the breastplate braces beneath the two-hand lock.
    if(s.state.phase==Phase::Parry){
        const double brace=smooth(s.state.elapsed/.055);
        f.body.chestPitch=-7.*brace;f.body.chestYaw=-6.*brace;
        f.body.forwardLean=-2.5*brace;
        f.body.rightElbowLift=4.*brace;f.body.leftElbowLift=6.*brace;
    }else if(s.state.phase==Phase::ParryRecovery){
        const double brace=1.-smooth(s.state.progress());
        f.body.chestPitch=-7.*brace;f.body.chestYaw=-6.*brace;
        f.body.forwardLean=-2.5*brace;
    }
    f.axis=(f.blade.tip-f.blade.hilt).normal();
    if(f.axis.length()<.5)f.axis=s.view.forward();
    // Shortest-arc transport from camera forward avoids an edge flip at either
    // vertical or lateral cuts. The frozen trajectories never point straight
    // backward; retain a finite frame even for an imported degenerate target.
    const Vec forward=s.view.forward(),right=s.view.right();
    const Vec turn=forward.cross(f.axis);
    const double cosine=forward.dot(f.axis);
    Vec edge=cosine>-.9999?right+turn.cross(right)+turn.cross(turn.cross(right))/(1.+cosine):right;
    edge=(edge-f.axis*edge.dot(f.axis)).normal();
    const double roll=f.body.gripRoll*Rad;
    f.edge=edge*std::cos(roll)+f.axis.cross(edge)*std::sin(roll);
    f.normal=f.axis.cross(f.edge).normal();
    const Orientation torso{s.view.yaw+f.body.chestYaw,0};
    for(int i=0;i<2;++i){
        const double sign=i==0?1.:-1.;
        const double drive=i==0?f.body.rightShoulderX:f.body.leftShoulderX;
        const double out=i==0?f.body.rightElbowOut:f.body.leftElbowOut;
        const double lift=i==0?f.body.rightElbowLift:f.body.leftElbowLift;
        // Yaw-space shoulders belong to the torso, not the camera pitch.
        const Vec shoulder=s.position+torso.world({-3.+drive+f.body.forwardLean,sign*23.,s.eyeHeight-25.});
        // Estoc calibration: source blade base Z=.19 m, tip Z=1.293061 m.
        // Palm contacts at Z=.07 / -.04 m sit on leather behind the guard.
        const double gripDepth=t.BladeLength*(i==0?.12:.23)/1.103061375617981;
        const Vec hand=f.blade.hilt-f.axis*gripDepth;
        double counter=s.state.isRiposte?1.:0.;
        if(s.state.phase==Phase::Windup)counter*=smooth(s.state.elapsed/.06);
        if(s.state.phase==Phase::Recovery)counter*=1.-smooth(s.state.progress()/.3);
        const Vec pole=torso.right()*sign*(1.+out*.035)+Vec{0,0,-.85+counter*.35+lift*.035};
        f.arms[i]=solveArm(shoulder,hand,pole);
    }
    return f;
}
}
