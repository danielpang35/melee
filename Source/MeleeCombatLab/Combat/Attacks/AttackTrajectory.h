#pragma once
#include "AttackStateMachine.h"
namespace mcl
{
struct LocalPose { Vec hilt,direction; };
inline LocalPose blend(LocalPose a,LocalPose b,double t){return {lerp(a.hilt,b.hilt,t),slerp(a.direction,b.direction,t)};}
struct AttackTrajectory
{
    static LocalPose rest() { return {{25,23,-25},Vec{.65,.1,.75}.normal()}; }
    static LocalPose release(const AttackIntent& a,double p)
    {
        Vec origin{0,std::cos(a.angle*Rad),std::sin(a.angle*Rad)};
        if(a.kind==AttackKind::Stab){double thrust=std::sin(clamp(p,0.,1.)*Pi*.85);return {{20+thrust*38,std::cos(a.angle*Rad)>=0?12.:-12.,-12},{1,0,0}};}
        double theta=mix(102.,-102.,p)*Rad;
        Vec direction=Vec{1,0,0}*std::cos(theta)+origin*std::sin(theta);
        return {Vec{25,0,-16}+origin*(std::sin(theta)*27),direction};
    }
    static LocalPose riposteRelease(const AttackIntent& attack,double progress,bool riposte)
    {
        LocalPose pose=release(attack,progress);
        // A raised counter-cut: the rendered blade and damage sweep use the same path.
        if(riposte){pose.hilt.z+=12.+6.*std::sin(progress*Pi);pose.hilt.x+=8.*std::sin(progress*Pi);}
        return pose;
    }
    static LocalPose evaluate(const AttackStateMachine& s,LocalPose windupStart)
    {
        if(s.phase==Phase::Windup)return blend(windupStart,riposteRelease(s.attack,0,s.isRiposte),smooth(s.progress()));
        if(s.phase==Phase::Release)return riposteRelease(s.attack,s.progress(),s.isRiposte);
        if(s.phase==Phase::Recovery)return blend(riposteRelease(s.attack,1,s.isRiposte),rest(),smooth(s.progress()));
        if(s.phase==Phase::Parry)return {{35,0,-10},Vec{.12,.8,.58}.normal()};
        return rest();
    }
    static Pose world(LocalPose p,Vec eye,Orientation orientation,const Tuning& t)
    {
        Vec h=eye+orientation.world(p.hilt);return {h,h+orientation.world(p.direction)*t.BladeLength};
    }
};
}
