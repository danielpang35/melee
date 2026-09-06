#pragma once
#include "Combat/CombatMath.h"
#include "Combat/CombatTuning.h"
namespace mcl
{
struct MomentumModel
{
    double value=0,turnRate=0,loss=0;
    Vec previousDesired;
    void update(Vec velocity,Vec desired,double dt,const Tuning& t)
    {
        if(dt<=0)return;
        velocity.z=desired.z=0;
        bool moving=desired.length()>.05;
        turnRate=moving&&previousDesired.length()>.05?angle(previousDesired,desired)/dt:0;
        double redirect=clamp((turnRate-t.SoftTurnThreshold)/(t.HardTurnThreshold-t.SoftTurnThreshold),0.,1.);
        double reversal=velocity.length()>30&&moving?clamp((angle(velocity,desired)-100.)/80.,0.,1.):0;
        loss=(redirect*t.MomentumLoss+reversal*t.ReversePenalty+(!moving?t.MomentumLoss:0))*dt;
        value=clamp(value+(moving?t.MomentumBuild*dt:0)-loss,0.,1.);
        previousDesired=desired;
    }
};
}
