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
    static ParryGeometry make(Vec body, Orientation guard, const Tuning& t)
    {
        Orientation yaw{guard.yaw, 0};

        const Vec boxCenter =
            body
            + yaw.forward() *
                (t.ParryForward + t.BoxForwardInfluence * guard.pitch)
            + Vec{
                0,
                0,
                t.ParryVertical + t.BoxZInfluence * guard.pitch
            };

        const Orientation outward{
            guard.yaw,
            guard.pitch * t.ConePitchInfluence
        };

        // This is the CENTER OF THE WIDE END, close to the defender.
        const Vec coneBase =
            body
            + yaw.forward() * t.ConeForward
            + Vec{0, 0, t.ConeVertical};

        // Put the APEX farther out from the defender.
        const Vec coneApex =
            coneBase + outward.forward() * t.ConeLength;

        // segmentCone() grows away from coneOrigin.
        // Therefore start at the distant apex and point BACK toward the defender.
        const Orientation inward{
            wrap(outward.yaw + 180.0),
            -outward.pitch
        };

        return {
            boxCenter,
            {
                t.ParryDepth * .5,
                t.ParryWidth * .5,
                t.ParryHeight * .5
            },
            coneApex,
            {
                guard.yaw,
                guard.pitch * t.BoxPitchInfluence
            },
            inward,
            t.ConeLength,
            t.ConeHalfAngle
        };
    }
    bool box(Segment sweep,double radius) const{return segmentBox(sweep,center,boxRotation,half,radius);}
    bool cone(Segment sweep,double radius) const{return segmentCone(sweep,coneOrigin,coneRotation,coneLength,coneAngle,radius);}
    bool catches(Segment sweep,double radius) const{return box(sweep,radius)||cone(sweep,radius);}
};
}
