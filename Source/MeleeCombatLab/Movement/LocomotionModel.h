#pragma once
#include "Combat/CombatMath.h"
#include "Combat/CombatTuning.h"
#include "Combat/Attacks/AttackTypes.h"

namespace mcl
{
enum class Gait { Idle,Walk,Sprint,Crouch,Airborne,Disabled };
enum class CombatMovementState { Neutral,Windup,Release,Recovery,Parry,ParryRecovery,Flinch,Dead };

struct LocomotionInput
{
    Vec velocity;
    Vec intent;
    Vec forward{1,0,0};
    double dt=0;
    double attackProgress=0;
    bool sprintRequested=false;
    bool crouched=false;
    bool grounded=true;
    Phase phase=Phase::Idle;
};

struct LocomotionOutput
{
    Vec velocity;
    Vec acceleration;
    Vec localVelocity;
    Vec localAcceleration;
    double brakingIntensity=0;
    double speedNormalized=0;
    double reversalSeverity=0;
    double targetSpeed=0;
    Gait gait=Gait::Idle;
    CombatMovementState combatState=CombatMovementState::Neutral;
};

struct LocomotionModel
{
    static constexpr double MaxSimulationStep=1./120.;

    static CombatMovementState combatState(Phase phase)
    {
        switch(phase){
        case Phase::Windup:return CombatMovementState::Windup;
        case Phase::Release:return CombatMovementState::Release;
        case Phase::Recovery:return CombatMovementState::Recovery;
        case Phase::Parry:return CombatMovementState::Parry;
        case Phase::ParryRecovery:return CombatMovementState::ParryRecovery;
        case Phase::Flinch:return CombatMovementState::Flinch;
        case Phase::Dead:return CombatMovementState::Dead;
        default:return CombatMovementState::Neutral;
        }
    }

    static double phaseScale(Phase phase,const Tuning& t)
    {
        switch(phase){
        case Phase::Windup:return t.WindupMoveScale;
        case Phase::Release:return t.ReleaseMoveScale;
        case Phase::Recovery:return t.RecoveryMoveScale;
        case Phase::Parry:return t.ParryMoveScale;
        case Phase::ParryRecovery:return t.ParryRecoveryMoveScale;
        case Phase::Flinch:return t.FlinchMoveScale;
        case Phase::Dead:return 0;
        default:return 1;
        }
    }

    static Vec right(Vec forward)
    {
        forward.z=0;forward=forward.normal();
        return {-forward.y,forward.x,0};
    }

    static Vec local(Vec worldValue,Vec forward)
    {
        forward.z=0;forward=forward.normal();const Vec r=right(forward);
        return {worldValue.dot(forward),worldValue.dot(r),worldValue.z};
    }

    static double directionalSpeed(Vec localDirection,const Tuning& t)
    {
        const double forwardAxis=localDirection.x>=0?t.ForwardSpeed:t.BackwardSpeed;
        const double denominator=std::sqrt(
            (localDirection.x/forwardAxis)*(localDirection.x/forwardAxis)+
            (localDirection.y/t.LateralSpeed)*(localDirection.y/t.LateralSpeed));
        return denominator>1e-9?1./denominator:0;
    }

    static Vec moveTowards(Vec current,Vec target,double maxDelta)
    {
        Vec delta=target-current;delta.z=0;const double distance=delta.length();
        return distance<=maxDelta||distance<1e-9?target:current+delta*(maxDelta/distance);
    }

    static LocomotionOutput step(const LocomotionInput& input,const Tuning& t)
    {
        LocomotionOutput out;out.velocity=input.velocity;out.combatState=combatState(input.phase);
        if(input.dt<=0)return out;

        Vec forward=input.forward;forward.z=0;if(forward.length()<1e-6)forward={1,0,0};forward=forward.normal();
        Vec intent=input.intent;intent.z=0;const double rawMagnitude=intent.length();
        const double magnitude=clamp(rawMagnitude,0.,1.);
        const Vec direction=rawMagnitude>1e-6?intent/rawMagnitude:Vec{};
        const Vec localDirection=local(direction,forward);

        const bool disabled=input.phase==Phase::Dead;
        const bool hasIntent=magnitude>.01&&!disabled;
        double targetSpeed=hasIntent?directionalSpeed(localDirection,t)*magnitude*phaseScale(input.phase,t):0;

        bool sprinting=false;
        if(hasIntent&&input.grounded&&!input.crouched&&input.phase==Phase::Idle&&input.sprintRequested&&
            localDirection.x>=t.SprintForwardRequirement)
        {
            const double alpha=clamp((localDirection.x-t.SprintForwardRequirement)/
                std::max(1e-6,1.-t.SprintForwardRequirement),0.,1.);
            targetSpeed=mix(targetSpeed,t.SprintSpeed*magnitude,alpha);
            sprinting=alpha>.01;
        }
        if(input.crouched)targetSpeed*=t.CrouchMoveScale;

        Vec target=direction*targetSpeed;
        if(hasIntent&&input.phase==Phase::Release&&localDirection.x>0){
            const double p=clamp(input.attackProgress/.82,0.,1.);
            const double envelope=std::sin(Pi*p);
            target+=forward*(t.ReleaseForwardBias*localDirection.x*magnitude*envelope*envelope);
        }

        Vec planar=input.velocity;planar.z=0;
        const double currentSpeed=planar.length();
        const Vec velocityDirection=currentSpeed>1e-6?planar/currentSpeed:direction;
        const double alignment=hasIntent?clamp(velocityDirection.dot(direction),-1.,1.):1;
        out.reversalSeverity=hasIntent&&currentSpeed>30?clamp((-alignment-.05)/.95,0.,1.):0;

        double authority=t.Deceleration;
        if(hasIntent){
            const double redirect=clamp((1.-alignment)/1.2,0.,1.);
            authority=mix(t.Acceleration,t.RedirectAcceleration,redirect);
            authority=mix(authority,t.ReverseAcceleration,out.reversalSeverity);
            if(currentSpeed<t.PrecisionSpeedThreshold&&alignment>.25)
                authority=std::max(authority,t.PrecisionAcceleration);
            if(target.length()+1<currentSpeed&&alignment>.2)
                authority=std::max(authority,t.Deceleration);
        }else if(currentSpeed>t.ForwardSpeed*1.1){
            authority=t.SprintDeceleration;
        }

        const Vec next=moveTowards(planar,target,authority*input.dt);
        out.velocity={next.x,next.y,input.velocity.z};
        out.acceleration=(next-planar)/input.dt;
        out.targetSpeed=target.length();
        out.localVelocity=local(out.velocity,forward);
        out.localAcceleration=local(out.acceleration,forward);

        const double decelDot=currentSpeed>1e-6?-out.acceleration.dot(velocityDirection):0;
        out.brakingIntensity=clamp(decelDot/std::max(1.,t.SprintDeceleration),0.,1.);
        const double normalization=sprinting?t.SprintSpeed:
            std::max({t.ForwardSpeed,t.LateralSpeed,t.BackwardSpeed});
        out.speedNormalized=clamp(next.length()/std::max(1.,normalization),0.,1.);

        if(disabled)out.gait=Gait::Disabled;
        else if(!input.grounded)out.gait=Gait::Airborne;
        else if(input.crouched)out.gait=Gait::Crouch;
        else if(sprinting)out.gait=Gait::Sprint;
        else if(next.length()>5||hasIntent)out.gait=Gait::Walk;
        else out.gait=Gait::Idle;
        return out;
    }
};
}
