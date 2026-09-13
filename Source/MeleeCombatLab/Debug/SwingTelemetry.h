#pragma once
#include "Combat/CombatSimulation.h"
#include <ostream>
namespace mcl {
inline void swingHeader(std::ostream& o)
{
    o<<"time,actor,serial,phase,p,q,intrinsic_deg_s,yaw_deg_s,pitch_deg_s,yaw_utilization,pitch_utilization,damaging,release_rotation,lunge_displacement";
    for(const char* name:{"local_tip","intrinsic_tip","yaw_tip","pitch_tip","translation","inherited","lunge","world_hilt","world_tip"})
        for(const char* axis:{"x","y","z"})o<<','<<name<<'_'<<axis;
    o<<",world_angular_deg_s,reach_correction_cm\n";
}
inline void swingSample(std::ostream& o,const Combatant& s,double time)
{
    const auto& m=s.motion;
    o<<time<<','<<s.id<<','<<s.state.serial<<','<<phaseName(s.state.phase)<<','<<m.p<<','<<m.q<<','<<m.intrinsicAngularSpeed
        <<','<<m.yawRate<<','<<m.pitchRate<<','<<m.yawUtilization<<','<<m.pitchUtilization<<','<<s.state.damaging()
        <<','<<s.state.releaseRotation<<','<<s.lungeDisplacement;
    for(Vec v:{m.localTipVelocity,m.intrinsicTipVelocity,m.yawTipVelocity,m.pitchTipVelocity,m.translationVelocity,
        s.inheritedVelocity,s.lungeVelocity,m.hiltVelocity,m.tipVelocity})o<<','<<v.x<<','<<v.y<<','<<v.z;
    o<<','<<s.angularSpeed<<','<<s.reachCorrection<<'\n';
}
}
