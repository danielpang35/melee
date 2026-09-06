#pragma once
#include "AttackTypes.h"
#include "Combat/CombatTuning.h"
#include <deque>
namespace mcl
{
class AttackDirectionResolver
{
    struct Sample { double time,x,y; };
    std::deque<Sample> history;
    double last=0;
public:
    void sample(double time,double x,double y) { history.push_back({time,x,y}); while(!history.empty()&&time-history.front().time>.25)history.pop_front(); }
    AttackIntent resolve(double time,const Tuning& t)
    {
        Vec v;
        for(const auto& s:history){double age=time-s.time;if(age>=0&&age<t.MouseWindow)v+=Vec{s.x,s.y,0}*(1-age/t.MouseWindow);}
        double raw=v.length()>=t.MouseDeadzone?std::atan2(v.y,v.x)/Rad:last;
        last=wrap(std::round(raw/60.)*60.);
        return {AttackKind::Strike,raw,last};
    }
};
}
