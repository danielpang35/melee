#pragma once
#include "AttackTrajectory.h"
#include <vector>
#include <memory>
#include <istream>
#include <sstream>
#include <string>

namespace mcl {
// In-place weapon choreography. The simulation still owns time, aim, reach,
// sweeps and damage. A combatant retains its revision throughout an exchange.
struct AuthoredRightCut {
    std::vector<LocalPose> frames;
    std::vector<Vec> viewOffsets;
    std::string bodyPath,firstPersonPath;
    static constexpr double Fps=120.;
    static bool supports(const AttackIntent& a) {
        return a.kind==AttackKind::Strike&&std::abs(wrap(a.angle))<.001;
    }
    static double sourceTime(const AttackStateMachine& s) {
        if(s.phase==Phase::Windup)return .25+.575*s.progress();
        if(s.phase==Phase::Release)return .825+.5*s.progress();
        if(s.phase==Phase::Recovery)return 1.325+.675*s.progress();
        return 0.;
    }
    bool read(std::istream& in) {
        std::string line;if(!std::getline(in,line)||line!="RIGHT_CUT_WEAPON_V1,120,271")return false;
        std::vector<LocalPose> next;
        while(std::getline(in,line)) {
            for(char& c:line)if(c==',')c=' ';
            std::istringstream row(line);int index;LocalPose p;std::string extra;
            if(!(row>>index>>p.hilt.x>>p.hilt.y>>p.hilt.z>>p.direction.x>>p.direction.y>>p.direction.z)||
                (row>>extra)||index!=static_cast<int>(next.size()))return false;
            for(double v:{p.hilt.x,p.hilt.y,p.hilt.z,p.direction.x,p.direction.y,p.direction.z})
                if(!std::isfinite(v)||std::abs(v)>200.)return false;
            if(std::abs(p.direction.length()-1.)>.001)return false;
            p.direction=p.direction.normal();next.push_back(p);
        }
        if(next.size()!=271)return false;
        const auto rest=AttackTrajectory::rest();
        for(int f:{0,30,240,270})if((next[f].hilt-rest.hilt).length()>.1||angle(next[f].direction,rest.direction)>.1)return false;
        frames=std::move(next);return true;
    }
    LocalPose sample(double seconds) const {
        const double f=clamp(seconds*Fps,0.,static_cast<double>(frames.size()-1));
        const auto a=static_cast<size_t>(f),b=std::min(a+1,frames.size()-1);
        return blend(frames[a],frames[b],f-static_cast<double>(a));
    }
    bool readView(std::istream& in) {
        std::string line;if(!std::getline(in,line)||line!="RIGHT_CUT_VIEW_V1,120,271")return false;
        std::vector<Vec> next;
        while(std::getline(in,line)){
            for(char& c:line)if(c==',')c=' ';
            std::istringstream row(line);int index;Vec v;std::string extra;
            if(!(row>>index>>v.x>>v.y>>v.z)||(row>>extra)||index!=static_cast<int>(next.size()))return false;
            if(!std::isfinite(v.length())||v.length()>35.)return false;
            // Includes both release boundaries. Cosmetic offsets may never
            // displace an active threat, even before a likely target passage.
            if(index>=99&&index<=159&&v.length()>1.e-8)return false;
            next.push_back(v);
        }
        if(next.size()!=271||(next[240]-next[0]).length()>1e-6||(next[270]-next[0]).length()>1e-6)return false;
        viewOffsets=std::move(next);return true;
    }
    Vec viewOffset(const AttackStateMachine& s) const {
        if(viewOffsets.empty()||s.phase==Phase::Release)return {};
        if(s.phase!=Phase::Idle&&(!supports(s.attack)||
            (s.phase!=Phase::Windup&&s.phase!=Phase::Recovery)||
            (s.phase==Phase::Recovery&&(s.last==Resolution::Parry||s.last==Resolution::Wall))))return {};
        const double f=clamp(sourceTime(s)*Fps,0.,270.);
        const auto a=static_cast<size_t>(f),b=std::min(a+1,viewOffsets.size()-1);
        Vec offset=lerp(viewOffsets[a],viewOffsets[b],f-static_cast<double>(a));
        if(s.phase==Phase::Windup&&(s.isRiposte||s.isCombo))offset=offset*smooth(s.progress()/.3);
        return offset;
    }
    LocalPose evaluate(const AttackStateMachine& s,LocalPose start,LocalPose velocity,const Tuning& t) const {
        if(!supports(s.attack)||frames.empty()||
            (s.phase!=Phase::Windup&&s.phase!=Phase::Release&&s.phase!=Phase::Recovery))
            return AttackTrajectory::evaluate(s,start,t,velocity);
        auto pose=sample(sourceTime(s));
        if(s.phase==Phase::Windup) {
            // Preserve the actual parry/combo/feint entry, including velocity;
            // join the authored load before the damaging phase starts.
            const double p=s.progress(),fade=1.-smooth(p);
            const auto ready=sample(.25);
            pose.hilt+=(start.hilt-ready.hilt)*fade+velocity.hilt*(s.definition.windup*p*(1.-p)*(1.-p));
            pose.direction=slerp(pose.direction,start.direction,fade);
        }
        return pose;
    }
};
}
