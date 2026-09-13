#pragma once
#include "CombatMath.h"

namespace mcl
{
// Citadel pelvis is 82.65 cm above the sole; standing eyes are at 170 cm.
// Input pitch bends only the upper body about this fixed hip joint.
struct BodyFrame
{
    static constexpr double HipToEye=87.35;
    Vec hip;
    Orientation yaw,torso;
    static BodyFrame make(Vec uprightEye,Orientation view,double pitch)
    {return {uprightEye-Vec{0,0,HipToEye},{view.yaw,0},{view.yaw,pitch}};}
    Vec transform(Vec uprightPoint) const {return hip+torso.world(yaw.local(uprightPoint-hip));}
    Vec untransform(Vec point) const {return hip+yaw.world(torso.local(point-hip));}
    Vec eye() const {return hip+torso.up()*HipToEye;}
    Vec vector(Vec uprightVector) const {return torso.world(yaw.local(uprightVector));}
};

// Find the first obstruction along the angular path, including a blocked
// intermediate pose whose final pose happens to be clear. Queries receive
// both ends so the world adapter can sweep rather than only test endpoints.
template<class Clear> double clearLeanFraction(Clear clear)
{
    double previous=0.;
    for(int i=1;i<=16;++i){
        const double next=i/16.;
        if(!clear(previous,next)){
            double low=previous,high=next;
            for(int j=0;j<9;++j){const double mid=(low+high)*.5;
                if(clear(previous,mid))low=mid;else high=mid;}
            return low;
        }
        previous=next;
    }
    return 1.;
}
}
