#pragma once
#include "AttackStateMachine.h"
namespace mcl
{
struct LocalPose { Vec hilt,direction; };
inline LocalPose blend(LocalPose a,LocalPose b,double t){return {lerp(a.hilt,b.hilt,t),slerp(a.direction,b.direction,t)};}

struct BodyMotion
{
    double chestYaw=0;
    double chestPitch=0;
    double forwardLean=0;
    double gripRoll=0;
    double rightShoulderX=0;
    double leftShoulderX=0;
    double rightElbowOut=0;
    double leftElbowOut=0;
    double rightElbowLift=0;
    double leftElbowLift=0;
};

struct AttackTrajectory
{
    static LocalPose rest(){return {{30,18,-31},Vec{.86,.20,.47}.normal()};}

    static double releaseMap(double p,const Tuning& t)
    {
        p=clamp(p,0.,1.);
        const double f=clamp(t.StrikeReleaseFrontLoad,0.,1.25);
        return clamp(p*(1.+f*(1.-p)),0.,1.);
    }

    static LocalPose release(const AttackIntent& a,double p,const Tuning& t)
    {
        p=clamp(p,0.,1.);
        if(a.kind==AttackKind::Stab){
            double q=smooth(p),thrust=std::sin(q*Pi*.88);
            return {{22+thrust*42,std::cos(a.angle*Rad)>=0?13.:-13.,-15},
                Vec{1,.03*std::cos(a.angle*Rad),-.02}.normal()};
        }

        const double q=releaseMap(p,t);
        Vec origin{0,std::cos(a.angle*Rad),std::sin(a.angle*Rad)};
        double theta=mix(100.,-112.,q)*Rad;
        Vec direction=(Vec{1,0,0}*std::cos(theta)+origin*std::sin(theta)).normal();

        const double vertical=std::sin(a.angle*Rad);
        const double forwardDrive=23.*std::sin(q*Pi);
        const double across=mix(36.,-32.,q);
        Vec hilt{19.+forwardDrive,0,-18.-5.*q};
        hilt+=origin*across;

        // Family-specific hand path: overheads stay slightly higher through entry;
        // underhands scoop slightly lower. Horizontal path remains the reference.
        hilt.z+=vertical*(6.*(1.-q)-2.*q);

        Vec tangent{0,-origin.z,origin.y};
        hilt+=tangent*(5.*std::sin(q*Pi));
        return {hilt,direction};
    }

    static LocalPose release(const AttackIntent& a,double p)
    {
        static const Tuning Defaults;
        return release(a,p,Defaults);
    }

    static LocalPose windup(const AttackIntent& a,double p,LocalPose start,const Tuning& t,bool combo=false)
    {
        p=clamp(p,0.,1.);
        const LocalPose loaded=release(a,0,t);
        Vec origin{0,std::cos(a.angle*Rad),std::sin(a.angle*Rad)};

        const double anticipationScale=combo?.25:1.;
        const double anticipationEnd=combo?.08:.18;
        LocalPose anticipation=start;
        anticipation.hilt=anticipation.hilt-origin*(5.*anticipationScale)+Vec{3.*anticipationScale,0,1.*anticipationScale};

        if(p<anticipationEnd)return blend(start,anticipation,smooth(p/anticipationEnd));
        return blend(anticipation,loaded,smooth((p-anticipationEnd)/(1.-anticipationEnd)));
    }

    static LocalPose recovery(const AttackIntent& a,double p,const Tuning& t,Resolution result)
    {
        p=clamp(p,0.,1.);
        const LocalPose end=release(a,1,t);
        const double side=std::cos(a.angle*Rad)>=0?1.:-1.;
        const double carry=result==Resolution::Miss?1.10:result==Resolution::Hit?.88:1.;

        LocalPose settle=end;
        settle.hilt+=Vec{4.*carry,0,-10.*carry};
        settle.direction=slerp(end.direction,Vec{.72,-side*.30,.32}.normal(),clamp(.45*carry,0.,1.));
        LocalPose ready={{27,side*10,-33},Vec{.82,side*.12,.50}.normal()};

        if(p<.28)return blend(end,settle,smooth(p/.28));
        if(p<.72)return blend(settle,ready,smooth((p-.28)/.44));
        return blend(ready,rest(),smooth((p-.72)/.28));
    }

    static LocalPose riposteRelease(const AttackIntent& attack,double progress,bool riposte,const Tuning& t)
    {
        LocalPose pose=release(attack,progress,t);
        if(riposte){
            pose.hilt.z+=12.+6.*std::sin(progress*Pi);
            pose.hilt.x+=8.*std::sin(progress*Pi);
        }
        return pose;
    }

    static LocalPose riposteRelease(const AttackIntent& attack,double progress,bool riposte)
    {
        static const Tuning Defaults;
        return riposteRelease(attack,progress,riposte,Defaults);
    }

    static BodyMotion body(const AttackStateMachine& s,const Tuning& t)
    {
        BodyMotion b;
        if(s.phase==Phase::Idle||s.phase==Phase::Dead||s.phase==Phase::Parry||
           s.phase==Phase::ParryRecovery||s.phase==Phase::Flinch)return b;

        const double side=std::cos(s.attack.angle*Rad)>=0?1.:-1.;
        const double vertical=std::sin(s.attack.angle*Rad);
        const double over=std::max(0.,vertical),under=std::max(0.,-vertical);
        const double verticalWeight=std::abs(vertical);

        if(s.attack.kind==AttackKind::Stab){
            double amount=0.;
            if(s.phase==Phase::Windup)amount=smooth(s.progress());
            else if(s.phase==Phase::Release)amount=1.-.35*smooth(s.progress());
            else if(s.phase==Phase::Recovery)amount=(1.-smooth(s.progress()))*.65;

            b.chestYaw=side*5.*amount;b.chestPitch=-3.*amount;
            b.forwardLean=s.phase==Phase::Release?4.*std::sin(clamp(s.progress()/.70,0.,1.)*Pi):0.;
            b.gripRoll=side*4.*amount;
            b.rightShoulderX=-2.*amount;b.leftShoulderX=-1.*amount;
            b.rightElbowOut=b.leftElbowOut=3.*amount;
            return b;
        }

        double load=0,through=0;
        if(s.phase==Phase::Windup)load=smooth(s.progress());
        else if(s.phase==Phase::Release){
            const double q=releaseMap(s.progress(),t);
            // Body leads the exact blade fractionally: perceived inertia without
            // any collision/rendered-blade divergence.
            const double bodyQ=clamp(q+.07*(1.-q),0.,1.);
            load=1.-bodyQ;through=bodyQ;
            b.forwardLean=5.*std::sin(clamp(s.progress()/.70,0.,1.)*Pi);
        }
        else if(s.phase==Phase::Recovery)through=1.-smooth(s.progress());

        const double yawScale=1.-.12*verticalWeight;
        b.chestYaw=side*(13.*load-17.*through)*yawScale;
        b.chestPitch=-vertical*(7.*load+4.*through)-2.*over*through+1.5*under*load;

        const double originRight=side>0?1.:0.,originLeft=1.-originRight;
        b.rightShoulderX=(-6.*originRight+3.*originLeft)*load+(3.*originRight-5.*originLeft)*through;
        b.leftShoulderX=(3.*originRight-6.*originLeft)*load+(-5.*originRight+3.*originLeft)*through;

        b.rightElbowOut=(originRight?10.:4.)*load+(originRight?4.:9.)*through;
        b.leftElbowOut=(originLeft?10.:4.)*load+(originLeft?4.:9.)*through;
        b.rightElbowLift=(originRight?5.:1.)*load-vertical*2.*through+over*5.*load-under*3.*load;
        b.leftElbowLift=(originLeft?5.:1.)*load-vertical*2.*through+over*5.*load-under*3.*load;

        b.gripRoll=side*(-7.*load+13.*through)+vertical*(5.*load-3.*through);
        return b;
    }

    static LocalPose evaluate(const AttackStateMachine& s,LocalPose windupStart,const Tuning& t)
    {
        if(s.phase==Phase::Windup)return windup(s.attack,s.progress(),windupStart,t,s.isCombo);
        if(s.phase==Phase::Release)return riposteRelease(s.attack,s.progress(),s.isRiposte,t);
        if(s.phase==Phase::Recovery)return recovery(s.attack,s.progress(),t,s.last);
        if(s.phase==Phase::Parry)return {{35,0,-10},Vec{.12,.8,.58}.normal()};
        return rest();
    }

    static Pose world(LocalPose p,Vec eye,Orientation orientation,const Tuning& t)
    {
        Vec h=eye+orientation.world(p.hilt);
        return {h,h+orientation.world(p.direction)*t.BladeLength};
    }
};
}
