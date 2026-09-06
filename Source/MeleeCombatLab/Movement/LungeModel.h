#pragma once
#include "Combat/CombatMath.h"
#include "Combat/CombatTuning.h"
namespace mcl
{
struct LungeModel
{
    double elapsed=100,displacement=0,velocity=0,commitment=0;
    Vec direction;
    void begin(Vec forward,double forwardInput,double momentum,const Tuning& t)
    {
        elapsed=0;displacement=velocity=0;direction=Vec{forward.x,forward.y,0}.normal();
        commitment=forwardInput>t.LungeForwardRequirement?forwardInput*mix(1-t.LungeMomentumScaling,1.,momentum):0;
    }
    Vec step(double dt,const Tuning& t)
    {
        if(elapsed>=t.LungeDuration||commitment<=0){velocity=0;return {};}
        double step=std::min(dt,t.LungeDuration-elapsed);
        double p=(elapsed+step*.5)/t.LungeDuration;
        velocity=t.LungeStrength*commitment*std::sin(Pi*p);
        double distance=std::min(velocity*step,std::max(0.,t.LungeMaxDisplacement-displacement));
        displacement+=distance;elapsed+=dt;return direction*(distance/dt);
    }
};
}
