#pragma once
#include "Combat/Attacks/AttackTypes.h"
#include <array>
#include <cstdint>

// Presentation owns these curves. Nothing in the combat evaluator includes this
// file. Eight circular direction anchors produce 240 (or continuous) selections.
namespace mcl::performance
{
struct Pose
{
    double chest=0,pelvis=0,waist=0,pitch=0,forward=0,drop=0;
    Vec rightElbow{.45,.65,-1},leftElbow{.65,-.55,-1};
    double rightWrist=0,leftWrist=0;
};
inline Pose mixPose(const Pose& a,const Pose& b,double t)
{
    return {mix(a.chest,b.chest,t),mix(a.pelvis,b.pelvis,t),mix(a.waist,b.waist,t),
        mix(a.pitch,b.pitch,t),mix(a.forward,b.forward,t),mix(a.drop,b.drop,t),
        lerp(a.rightElbow,b.rightElbow,t),lerp(a.leftElbow,b.leftElbow,t),
        mix(a.rightWrist,b.rightWrist,t),mix(a.leftWrist,b.leftWrist,t)};
}
constexpr int Directions=8,Keys=10;
constexpr std::array<double,Keys> Times={0.,.65,1.,1.22,1.52,1.80,2.,2.22,2.60,3.};
struct Library
{
    std::array<std::array<Pose,Keys>,Directions> cuts{};
    Pose sample(double angle,double phase) const
    {
        double a=(std::fmod(std::fmod(angle,360.)+360.,360.))/45.;
        const int lo=static_cast<int>(a),hi=(lo+1)%Directions;
        int key=0;while(key<Keys-2&&phase>Times[key+1])++key;
        const double span=Times[key+1]-Times[key];
        const double p=clamp((phase-Times[key])/span,0.,1.);
        const auto track=[&](int direction){
            const int before=std::max(0,key-1),after=std::min(Keys-1,key+2);
            const auto &a0=cuts[direction][before],&a1=cuts[direction][key],
                &a2=cuts[direction][key+1],&a3=cuts[direction][after];
            const double in=key==0?0.:span/(Times[key+1]-Times[before]);
            const double out=key==Keys-2?0.:span/(Times[after]-Times[key]);
            const auto curve=[&](auto v0,auto v1,auto v2,auto v3){
                return v1*(1.-smooth(p))+v2*smooth(p)+(v2-v0)*(in*p*(1.-p)*(1.-p))+(v3-v1)*(out*p*p*(p-1.));
            };
            // Shared tangents carry motion through interior keys. A separate
            // ease-in/ease-out at every key made the performance stop-start.
#define PERFORMANCE_CURVE(Field) curve(a0.Field,a1.Field,a2.Field,a3.Field)
            return Pose{PERFORMANCE_CURVE(chest),PERFORMANCE_CURVE(pelvis),PERFORMANCE_CURVE(waist),
                PERFORMANCE_CURVE(pitch),PERFORMANCE_CURVE(forward),PERFORMANCE_CURVE(drop),
                PERFORMANCE_CURVE(rightElbow),PERFORMANCE_CURVE(leftElbow),
                PERFORMANCE_CURVE(rightWrist),PERFORMANCE_CURVE(leftWrist)};
#undef PERFORMANCE_CURVE
        };
        // Smooth direction weights have matching zero derivatives at anchors.
        // Both hands retain their identity throughout the circular blend.
        return mixPose(track(lo),track(hi),smooth(a-lo));
    }
};

// Interruptions capture the actual displayed pose. Ordinary phase boundaries
// use the shared track; only a changed action introduces a short visual blend.
struct Player
{
    Pose displayed{},origin{};
    Phase previous=Phase::Idle;
    std::uint64_t serial=0;
    double transfer=1.;
    bool initialized=false,contactRecovery=false;
    Pose contactPose{};
    Pose update(const Library& library,Phase phase,std::uint64_t action,double angle,double progress,double dt,
        AttackKind kind=AttackKind::Strike,Resolution result=Resolution::None)
    {
        const bool arrested=result==Resolution::Wall||result==Resolution::Parry||result==Resolution::Chamber;
        const bool ordinary=(previous==Phase::Windup&&phase==Phase::Release)||
            (previous==Phase::Release&&phase==Phase::Recovery&&!arrested);
        if(phase!=Phase::Recovery)contactRecovery=false;
        if(phase==Phase::Recovery&&previous!=phase&&arrested){contactRecovery=true;contactPose=displayed;}
        if(initialized&&(serial!=action||(phase!=previous&&!ordinary))){origin=displayed;transfer=0.;}
        double clock=0.;
        if(phase==Phase::Windup)clock=progress;
        if(phase==Phase::Release)clock=1.+progress;
        if(phase==Phase::Recovery)clock=2.+progress;
        Pose target=library.sample(angle,clock);
        if(kind==AttackKind::Stab&&clock>0.){
            // Thrusts keep a narrow straight delivery instead of sampling a cut.
            const double load=clock<1.?smooth(clock):1.-smooth(clamp(clock-1.,0.,1.));
            const double drive=clock<1.?0.:(clock<2.?smooth(clock-1.):1.-smooth(clock-2.));
            target={};target.forward=-2.*load+6.*drive;target.pitch=-3.*drive;
            target.chest=8.*load-10.*drive;target.pelvis=-5.*drive;target.drop=2.*drive;
        }
        if(contactRecovery)target=mixPose(contactPose,library.sample(angle,0.),smooth(progress));
        if(phase==Phase::Parry||phase==Phase::ParryRecovery){
            target.pitch=-3.;target.forward=2.;
            target.rightElbow={.7,.8,-.3};target.leftElbow={.8,-.7,-.3};
        }
        transfer=std::min(1.,transfer+std::max(0.,dt)/.10);
        displayed=initialized?mixPose(origin,target,smooth(transfer)):target;
        previous=phase;serial=action;initialized=true;return displayed;
    }
};
}
