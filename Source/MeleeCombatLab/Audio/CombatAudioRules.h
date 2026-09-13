#pragma once
#include "Combat/Attacks/AttackTypes.h"
#include <cstdint>

namespace mcl
{
enum class AudioCue { Swing, Stab, Body, Parry, Chamber, Wall, Head, Armor, None };
inline constexpr int AudioVariantCount=3;
inline constexpr const char* AudioCueNames[]={"Swing","Stab","Body","Parry","Chamber","Wall","Head","Armor"};
inline constexpr int AudioCueCount=static_cast<int>(AudioCue::None);
inline constexpr float AudioBaseGain=.68f;

inline AudioCue contactAudio(Resolution result,ContactRegion region=ContactRegion::None)
{
    switch(result){
    case Resolution::Hit:return region==ContactRegion::Head?AudioCue::Head:AudioCue::Body;
    case Resolution::Parry:return AudioCue::Parry;
    case Resolution::Chamber:return AudioCue::Chamber;
    case Resolution::Wall:return AudioCue::Wall;
    default:return AudioCue::None;
    }
}

// Consume fixed simulation samples, before contact resolution can cancel release.
// Every entry into release emits once, including a new combo serial. Windup,
// feint and morph never manufacture an impact or a committed swing sound.
struct ReleaseAudioGate
{
    std::uint64_t serial=0;
    bool releasing=false;
    AudioCue sample(Phase phase,std::uint64_t attackSerial,AttackKind kind)
    {
        const bool next=phase==Phase::Release;
        const bool entered=next&&(!releasing||serial!=attackSerial);
        releasing=next;serial=attackSerial;
        return entered?(kind==AttackKind::Stab?AudioCue::Stab:AudioCue::Swing):AudioCue::None;
    }
};

// Physical equipment movement, independent of committed blade air. Distance
// and view travel keep the cadence stable across rendering frame rates.
struct ArmorAudioGate
{
    bool initialized=false;
    Vec previousPosition;
    Orientation previousView;
    Phase previousPhase=Phase::Idle;
    std::uint64_t previousSerial=0;
    double lastSound=-1,distance=0,turn=0;
    float sample(double time,Vec position,Orientation view,Phase phase,std::uint64_t serial)
    {
        const Vec delta=position-previousPosition;
        if(!initialized||time<lastSound||delta.length()>120){
            lastSound=initialized?time:time-.24;
            initialized=true;previousPosition=position;previousView=view;
            previousPhase=phase;previousSerial=serial;distance=turn=0;
            return 0;
        }
        distance+=delta.length();
        turn+=std::abs(std::remainder(view.yaw-previousView.yaw,360.))+
              .5*std::abs(view.pitch-previousView.pitch);
        const bool action=(phase==Phase::Windup&&(previousPhase!=phase||previousSerial!=serial))||
            ((phase==Phase::Parry||phase==Phase::Recovery)&&previousPhase!=phase);
        previousPosition=position;previousView=view;previousPhase=phase;previousSerial=serial;
        if(phase==Phase::Dead){distance=turn=0;return 0;}
        if(time-lastSound>=.24&&(action||distance>=95||turn>=38)){
            const float strength=action?1.f:.65f;
            lastSound=time;distance=turn=0;return strength;
        }
        return 0;
    }
};
}
