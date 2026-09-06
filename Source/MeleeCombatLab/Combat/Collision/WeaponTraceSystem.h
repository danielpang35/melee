#pragma once
#include "Combat/CombatMath.h"
#include "Combat/CombatTuning.h"
#include <vector>
namespace mcl
{
struct WeaponTraceSystem
{
    // Overlapping equal-radius samples cover the ENTIRE blade without gameplay zones.
    static std::vector<Segment> sweeps(Pose previous,Pose current,const Tuning& t)
    {
        int count=static_cast<int>(std::ceil(t.BladeLength/(t.BladeRadius*1.25)));
        std::vector<Segment> out;out.reserve(count+3);
        for(int i=0;i<=count;++i){double p=double(i)/count;out.push_back({lerp(previous.hilt,previous.tip,p),lerp(current.hilt,current.tip,p)});}
        out.push_back(previous.blade());out.push_back(current.blade());return out;
    }
    static int subdivisions(double dt,Pose previous,Pose current)
    {
        double translation=std::max((current.hilt-previous.hilt).length(),(current.tip-previous.tip).length());
        double rotation=angle(previous.tip-previous.hilt,current.tip-current.hilt);
        return std::clamp(static_cast<int>(std::ceil(std::max({dt*240.,translation/6.,rotation/3.}))),1,64);
    }
    static std::vector<Segment> adaptiveSweeps(double dt,Pose previous,Pose current,const Tuning& t)
    {
        const int count=subdivisions(dt,previous,current);
        if(count==1)return sweeps(previous,current,t);
        std::vector<Segment> out;Pose start=previous;
        for(int i=1;i<=count;++i){double alpha=double(i)/count;Vec hilt=lerp(previous.hilt,current.hilt,alpha);
            Vec direction=slerp(previous.tip-previous.hilt,current.tip-current.hilt,alpha);
            Pose end{hilt,hilt+direction*t.BladeLength};auto batch=sweeps(start,end,t);
            out.insert(out.end(),batch.begin(),batch.end());start=end;
        }
        return out;
    }
};
}
