#pragma once
#include "Combat/CombatMath.h"
#include "Combat/CombatTuning.h"
namespace mcl
{
struct ParryGeometry
{
    Vec center,half,coneOrigin;
    Orientation boxRotation,coneRotation;
    double coneLength=0,coneAngle=0;
    static ParryGeometry make(Vec body,Orientation guard,const Tuning& t)
    {
        Orientation yaw{guard.yaw,0};
        return {body+yaw.forward()*(t.ParryForward+t.BoxForwardInfluence*guard.pitch)+Vec{0,0,t.ParryVertical+t.BoxZInfluence*guard.pitch},
            {t.ParryDepth*.5,t.ParryWidth*.5,t.ParryHeight*.5},
            body+yaw.forward()*t.ConeForward+Vec{0,0,t.ConeVertical},
            {guard.yaw,guard.pitch*t.BoxPitchInfluence},{guard.yaw,guard.pitch*t.ConePitchInfluence},t.ConeLength,t.ConeHalfAngle};
    }
    bool box(Segment sweep,double radius) const{return segmentBox(sweep,center,boxRotation,half,radius);}
    bool cone(Segment sweep,double radius) const{return segmentCone(sweep,coneOrigin,coneRotation,coneLength,coneAngle,radius);}
    bool catches(Segment sweep,double radius) const{return box(sweep,radius)||cone(sweep,radius);}
};
}
