#pragma once
#include "Combat/CombatMath.h"
#include <istream>
#include <sstream>
#include <string>
#include <vector>

namespace mcl {
// Candidate source sampler. No authority is inferred from visual markers.
// Quaternion channels stay in Blender space; points convert by C(x,y,z)=100(-y,-x,z).
struct EXWeaponMotion {
    struct Quaternion {
        double w=1,x=0,y=0,z=0;
        double dot(Quaternion b) const {return w*b.w+x*b.x+y*b.y+z*b.z;}
        Quaternion operator*(double t) const {return {w*t,x*t,y*t,z*t};}
        Quaternion operator+(Quaternion b) const {return {w+b.w,x+b.x,y+b.y,z+b.z};}
        Vec rotate(Vec v) const {const Vec q{x,y,z};return v+q.cross(v)*(2*w)+q.cross(q.cross(v))*2;}
        static Quaternion interpolate(Quaternion a,Quaternion b,double t) {
            // Match the accepted UE FTransform::Blend: shortest-path FastLerp,
            // then normalization. SLERP diverges on this source's rapid blade roll.
            if(a.dot(b)<0)b=b*-1;
            const Quaternion q=a*(1-t)+b*t;
            return q*(1/std::sqrt(q.dot(q)));
        }
    };
    struct Frame {Vec hilt;Quaternion rotation;double length=0;};
    std::vector<Frame> frames;
    static constexpr double Rate=60.,Start=.30,Release=62./60.,Exit=80./60.,End=153./60.;
    static Vec basis(Vec v) {return {-v.y,-v.x,v.z};}
    bool read(std::istream& input) {
        std::string line;if(!std::getline(input,line)||line!="EX_WEAPON_V1 60 154")return false;
        std::vector<Frame> next;
        while(std::getline(input,line)) {
            std::istringstream row(line);size_t index;Frame f;std::string extra;
            if(!(row>>index>>f.hilt.x>>f.hilt.y>>f.hilt.z>>f.rotation.w>>f.rotation.x>>f.rotation.y>>f.rotation.z>>f.length)||row>>extra||index!=next.size())return false;
            if(!std::isfinite(f.hilt.length())||f.hilt.length()>1000||!std::isfinite(f.rotation.dot(f.rotation))||
                std::abs(f.rotation.dot(f.rotation)-1)>.001||!std::isfinite(f.length)||std::abs(f.length-103.5)>.01)return false;
            f.rotation=f.rotation*(1/std::sqrt(f.rotation.dot(f.rotation)));next.push_back(f);
        }
        if(next.size()!=154)return false;
        frames=std::move(next);return true;
    }
    Pose sample(double seconds) const {
        if(frames.size()!=154||!std::isfinite(seconds))return {};
        const double frame=clamp(seconds*Rate,0.,153.);const size_t a=static_cast<size_t>(frame),b=std::min(a+1,frames.size()-1);
        const double t=frame-static_cast<double>(a);const auto q=Quaternion::interpolate(frames[a].rotation,frames[b].rotation,t);
        const Vec hilt=lerp(frames[a].hilt,frames[b].hilt,t);
        return {hilt,hilt+basis(q.rotate({0,0,1}))*mix(frames[a].length,frames[b].length,t),basis(q.rotate({1,0,0}))};
    }
    Pose world(double seconds,Vec origin,Orientation aim) const {
        const auto p=sample(seconds);const Vec pivot{11.5,0,168};
        return {origin+pivot+aim.world(p.hilt-pivot),origin+pivot+aim.world(p.tip-pivot),aim.world(p.edge)};
    }
};
}
