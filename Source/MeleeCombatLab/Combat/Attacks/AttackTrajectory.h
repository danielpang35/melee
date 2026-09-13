#pragma once
#include "Combat/CombatBodyPose.h"
#include "AttackStateMachine.h"
namespace mcl
{
struct LocalPose { Vec hilt,direction; };
inline LocalPose blend(LocalPose a,LocalPose b,double t){return {lerp(a.hilt,b.hilt,t),slerp(a.direction,b.direction,t)};}

struct BodyMotion
{
    double chestYaw=0;
    double chestPitch=0;
    double forwardLean=0;
    double gripRoll=0;
    double rightShoulderX=0;
    double leftShoulderX=0;
    double rightElbowOut=0;
    double leftElbowOut=0;
    double rightElbowLift=0;
    double leftElbowLift=0;
    double rightShoulderZ=0;
    double leftShoulderZ=0;
    // Arm organization belongs to the transported body pose. Recomputing it
    // from the new phase loses the contact pose on an interruption or combo.
    double elbowCarry=0;
    double rightForearmCarry=0;
    double leftForearmCarry=0;
    double rightHighGuardWeight=0;
    double leftHighGuardWeight=0;
    // Preweighted local targets also retain their authored origin when a
    // captured load transfers to a different attack or defensive action.
    Vec rightHighGuardRail,leftHighGuardRail;
    // Authored lower-chain channels, carried through contacts and transfers.
    // Chest yaw remains the total thorax heading; these are its independently
    // timed pelvis/waist contributions rather than fixed fractions of it.
    double pelvisYaw=0,waistYaw=0,pelvisDrop=0;
    double rightFootYaw=0,leftFootYaw=0;
};
inline BodyMotion blend(BodyMotion a,BodyMotion b,double t)
{
    return {mix(a.chestYaw,b.chestYaw,t),mix(a.chestPitch,b.chestPitch,t),
        mix(a.forwardLean,b.forwardLean,t),mix(a.gripRoll,b.gripRoll,t),
        mix(a.rightShoulderX,b.rightShoulderX,t),mix(a.leftShoulderX,b.leftShoulderX,t),
        mix(a.rightElbowOut,b.rightElbowOut,t),mix(a.leftElbowOut,b.leftElbowOut,t),
        mix(a.rightElbowLift,b.rightElbowLift,t),mix(a.leftElbowLift,b.leftElbowLift,t),
        mix(a.rightShoulderZ,b.rightShoulderZ,t),mix(a.leftShoulderZ,b.leftShoulderZ,t),
        mix(a.elbowCarry,b.elbowCarry,t),mix(a.rightForearmCarry,b.rightForearmCarry,t),
        mix(a.leftForearmCarry,b.leftForearmCarry,t),
        mix(a.rightHighGuardWeight,b.rightHighGuardWeight,t),mix(a.leftHighGuardWeight,b.leftHighGuardWeight,t),
        lerp(a.rightHighGuardRail,b.rightHighGuardRail,t),lerp(a.leftHighGuardRail,b.leftHighGuardRail,t),
        mix(a.pelvisYaw,b.pelvisYaw,t),mix(a.waistYaw,b.waistYaw,t),mix(a.pelvisDrop,b.pelvisDrop,t),
        mix(a.rightFootYaw,b.rightFootYaw,t),mix(a.leftFootYaw,b.leftFootYaw,t)};
}
inline BodyMotion bodyTransfer(BodyMotion a,BodyMotion b,BodyMotion tangentFrom,BodyMotion tangentTo,double tangentScale,double p,bool atEnd)
{
    BodyMotion out=blend(a,b,smooth(p));
    const double h=(atEnd?p*p*(p-1.):p*(1.-p)*(1.-p))*tangentScale;
#define TRANSFER(Field) out.Field+=(tangentTo.Field-tangentFrom.Field)*h;
    TRANSFER(chestYaw) TRANSFER(chestPitch) TRANSFER(forwardLean) TRANSFER(gripRoll)
    TRANSFER(rightShoulderX) TRANSFER(leftShoulderX) TRANSFER(rightElbowOut)
    TRANSFER(leftElbowOut) TRANSFER(rightElbowLift) TRANSFER(leftElbowLift)
    TRANSFER(rightShoulderZ) TRANSFER(leftShoulderZ)
    TRANSFER(elbowCarry) TRANSFER(rightForearmCarry) TRANSFER(leftForearmCarry)
    TRANSFER(rightHighGuardWeight) TRANSFER(leftHighGuardWeight) TRANSFER(rightHighGuardRail) TRANSFER(leftHighGuardRail)
    TRANSFER(pelvisYaw) TRANSFER(waistYaw) TRANSFER(pelvisDrop) TRANSFER(rightFootYaw) TRANSFER(leftFootYaw)
#undef TRANSFER
    return out;
}

struct AttackTrajectory
{
    // Fitted ready position: guard above the paired hands at upper abdomen.
    // Attack load and parry retain their own elevated keys; only the neutral
    // endpoint changes, and existing phase transfers carry into/out of it.
    static LocalPose rest(){return {{42,12,-20},Vec{.75,.10,.65}.normal()};}

    // Hand-authored grip poses at load, target passage and completed cut.
    // The middle tangent carries the hands through contact instead of easing
    // to a stop there. Right hand remains forward on the grip in both origins.
    static Vec gripArc(Vec load,Vec passage,Vec finish,double q,double finishVerticalSpeed=1.)
    {
        // The base track reaches X31 at passage with a zero X tangent.
        // A separate diagonal key can drive forward after target passage.
        Vec tangent{0,(finish.y-load.y)*.5,(finish.z-load.z)*.5};
        const double entryHeight=passage.z-load.z,exitHeight=finish.z-passage.z;
        if(entryHeight*exitHeight>=0){
            // Keep descending keys monotone, including a clearance-limited
            // plateau. This leaves the calibrated diagonal tangents intact.
            const double limit=2.*std::min(std::abs(entryHeight),std::abs(exitHeight));
            tangent.z=clamp(tangent.z,-limit,limit);
        }
        const bool second=q>.5;
        const double p=second?(q-.5)*2.:q*2.;
        const Vec a=second?passage:load,b=second?finish:passage;
        const Vec va=second?tangent:(passage-load)*.8;
        Vec vb=second?(finish-passage)*.75:tangent;
        if(second)vb.z*=finishVerticalSpeed;
        const double h=p*p*(3.-2.*p),h0=p*(1.-p)*(1.-p),h1=p*p*(p-1.);
        return lerp(a,b,h)+va*h0+vb*h1;
    }

    static Vec strikeGrip(const AttackIntent& a,double q,const Tuning& t)
    {
        const double lateral=std::cos(a.angle*Rad),vertical=std::sin(a.angle*Rad);
        const double stanceSide=resolvedStance(a)==Stance::Right?1.:-1.;
        const double right=clamp((stanceSide*smooth(std::abs(lateral))+1.)*.5,0.,1.);
        if(vertical>=0){
            const double overhead=clamp(vertical/.866025403784439,0.,1.);
            // Hold the high guard in front of the face in the shared pose.
            // A near-face load became a large glove occlusion when looking up.
            Vec loaded=lerp(lerp(Vec{32,-25,-8},Vec{32,26,-10},right),
                lerp(Vec{26,-12,23},Vec{26,13,22},right),overhead);
            // Right-horizontal pilot: draw toward the rear shoulder. Fade
            // out by 30 degrees so diagonal/overhead anchors stay unchanged.
            const double rightLoad=right*(1.-smooth(clamp(vertical/.5,0.,1.)));
            loaded+=Vec{-t.RightCutLoadBack,t.RightCutLoadSide,t.RightCutLoadLift}*rightLoad;
            Vec passage=lerp(lerp(Vec{48,-2,-16},Vec{48,2,-16},right),
                lerp(Vec{31,-2,-2},Vec{31,3,-1},right),overhead);
            Vec finish=lerp(lerp(Vec{38,29,-23},Vec{37,-29,-25},right),
                lerp(Vec{22,9,-36},Vec{23,-8,-37},right),overhead);
            const double verticalCore=smooth((vertical-.866025403784439)/(1.-.866025403784439));
            // A vertical cut keeps driving the grip forward through its
            // finish. Retraction here crowded the elbows behind a low grip.
            finish.x=mix(finish.x,passage.x,verticalCore);
            // Author a floor-safe endpoint before constructing the hand arc.
            // The former sample-wise floor clamp made a vertical cut dip low
            // and then raise the hands again in the last damaging frames.
            const double depth=t.BladeLength*.175/1.103061375617981;
            const double down=vertical*(t.StrikeArcEnd<=-90.?1.:std::max(0.,-std::sin(t.StrikeArcEnd*Rad)));
            const double carryAngle=t.StrikeArcEnd-24.*1.10;
            const double carryDown=vertical*(carryAngle<=-90.?1.:std::max(0.,-std::sin(carryAngle*Rad)));
            // Bound the low carry's q*(1-q)^6 momentum lobe up front.
            // Its maximum is at q=1/7. Solve for the finish height rather
            // than correcting the hands after they have already descended.
            const double carryPeak=std::pow(6./7.,6.)/7.;
            const double exitRate=1.-.15*clamp(t.StrikeReleaseAcceleration,0.,1.);
            // Recovery estimates its entry tangent from the last .0001 of
            // release; reserve .2% slope and .001 cm for that approximation.
            const double carrySlope=1.5*(1.-verticalCore)*exitRate*.22*
                t.StrikeRecovery/t.StrikeRelease*carryPeak*1.002;
            const double carryFloor=t.BladeRadius-152.+verticalCore+.001+
                carryDown*(t.BladeLength+depth);
            const double carryFinish=carryFloor<passage.z?
                (carryFloor+carrySlope*passage.z)/(1.+carrySlope):carryFloor;
            const double floorFinish=std::max(t.BladeRadius-151.+down*(t.BladeLength+depth),
                carryFinish);
            if(floorFinish>finish.z){
                finish.z=floorFinish;
                // Nonstandard long blades can require the earlier keys to
                // rise as well; never interpolate below the safe endpoint.
                passage.z=std::max(passage.z,finish.z);
                loaded.z=std::max(loaded.z,passage.z);
            }
            // Arrest the hands at the low vertical finish while the blade
            // completes its angular carry; diagonals retain their exit speed.
            Vec grip=gripArc(loaded,passage,finish,q,1.-verticalCore);
            const double postTargetDrive=overhead*smooth(clamp(2.*std::abs(lateral),0.,1.));
            if(q>.5&&postTargetDrive>0.){
                // Drive the hands after the blade has crossed the target,
                // creating forearm space without extending target passage.
                // Stop forward travel at the authored q=.7 key, then carry
                // to the finish with the original exit velocity for recovery.
                constexpr double driveKey=.7,driveDistance=10.;
                const double forwardKey=gripArc(loaded,passage,finish,driveKey,1.-verticalCore).x+driveDistance;
                double drivenX;
                if(q<=driveKey)drivenX=mix(passage.x,forwardKey,smooth((q-.5)/(driveKey-.5)));
                else{
                    const double duration=1.-driveKey,p=(q-driveKey)/duration;
                    const double exitVelocity=1.5*(finish.x-passage.x);
                    drivenX=mix(forwardKey,finish.x+driveDistance,smooth(p))+
                        exitVelocity*duration*p*p*(p-1.);
                }
                grip.x=mix(grip.x,drivenX,postTargetDrive);
            }
            return grip;
        }
        // Preserve the established underhand family while sharing the same
        // body/weapon authority and continuous transfer boundaries.
        const double handAngle=mix(66.,-66.,q)*Rad;
        const Vec origin{0,lateral,vertical};
        return Vec{17.+14.*std::cos(handAngle),0,2.}+origin*(19.*std::sin(handAngle));
    }

    static double releaseMap(double p,const Tuning& t,bool riposte=false)
    {
        p=clamp(p,0.,1.);
        // Integral of a positive velocity curve, peaking at p=.604.
        // Nonzero exit speed carries into recovery; zero strength is linear.
        const double curved=.35*p+1.45*p*p-.8*p*p*p;
        return riposte?p:mix(p,curved,clamp(t.StrikeReleaseAcceleration,0.,1.));
    }

    static LocalPose release(const AttackIntent& a,double p,const Tuning& t,bool riposte=false)
    {
        const double q=releaseMap(p,t,riposte);
        if(a.kind==AttackKind::Stab){
            const double side=resolvedStance(a)==Stance::Right?1.:-1.;
            return {{28.+24.*q,side*mix(13.,5.,q),mix(4.,10.,q)},
                Vec{1,side*mix(.08,.015,q),mix(.06,-.02,q)}.normal()};
        }
        const Vec origin{0,std::cos(a.angle*Rad),std::sin(a.angle*Rad)};
        const double theta=mix(t.StrikeArcStart,t.StrikeArcEnd,q)*Rad;
        const Vec direction=Vec{1,0,0}*std::cos(theta)+origin*std::sin(theta);
        // Author the grip-centre arc first. The guard is a rigid extension
        // of it, rather than a separately spinning blade on a compressed hilt.
        const Vec grip=strikeGrip(a,q,t);
        const double midpointDepth=t.BladeLength*.175/1.103061375617981;
        return {grip+direction*midpointDepth,direction};
    }

    static LocalPose hermite(LocalPose a,LocalPose b,LocalPose va,LocalPose vb,double p)
    {
        p=clamp(p,0.,1.);
        const double h=p*p*(3.-2.*p),h0=p*(1.-p)*(1.-p),h1=p*p*(p-1.);
        return {lerp(a.hilt,b.hilt,h)+va.hilt*h0+vb.hilt*h1,
            (lerp(a.direction,b.direction,h)+va.direction*h0+vb.direction*h1).normal()};
    }

    static LocalPose release(const AttackIntent& a,double p)
    {
        static const Tuning Defaults;
        return release(a,p,Defaults);
    }

    static LocalPose windup(const AttackIntent& a,double p,LocalPose start,const Tuning& t,bool combo=false,bool riposte=false,double duration=0,LocalPose velocity={{},{}})
    {
        const LocalPose loaded=riposteRelease(a,0,riposte,t);
        const LocalPose next=riposteRelease(a,.0001,riposte,t);
        const double seconds=duration>0?duration:(riposte?t.RiposteWindup:combo?t.ComboWindup:
            a.kind==AttackKind::Stab?t.StabWindup:t.StrikeWindup);
        const double releaseSeconds=a.kind==AttackKind::Stab?t.StabRelease:t.StrikeRelease;
        const double tangentScale=seconds/(releaseSeconds*.0001);
        const LocalPose tangent{(next.hilt-loaded.hilt)*tangentScale,(next.direction-loaded.direction)*tangentScale};
        // End tangent transfers torque into the release with no hold or snap.
        return hermite(start,loaded,{velocity.hilt*seconds,velocity.direction*seconds},tangent,p);
    }

    static LocalPose recovery(const AttackIntent& a,double p,const Tuning& t,Resolution result,bool riposte=false)
    {
        p=clamp(p,0.,1.);
        const LocalPose end=riposteRelease(a,1,riposte,t);
        const double side=resolvedStance(a)==Stance::Right?1.:-1.;
        const double carry=result==Resolution::Miss?1.10:result==Resolution::Hit?.88:1.;

        LocalPose settle=end;
        const double vertical=std::sin(a.angle*Rad);
        settle.hilt+=a.kind==AttackKind::Stab?Vec{-9.*carry,side*3.,-3.}:
            Vec{2.*carry,-side*3.*carry,(-7.+9.*std::max(0.,-vertical))*carry};
        const Vec origin{0,std::cos(a.angle*Rad),vertical};
        // Continue around the cutting plane before returning the guard.
        // The old settle immediately reversed the blade toward the target.
        const double exitAngle=(t.StrikeArcEnd-24.*carry)*Rad;
        settle.direction=a.kind==AttackKind::Stab?end.direction:
            (Vec{1,0,0}*std::cos(exitAngle)+origin*std::sin(exitAngle)).normal();
        if(a.kind==AttackKind::Strike&&vertical>0){
            const double depth=t.BladeLength*.175/1.103061375617981;
            const Vec endGrip=end.hilt-end.direction*depth;
            // Preserve the diagonal carries while blending their lateral
            // direction continuously through the true vertical origin.
            const double carrySide=mix(-1.,1.,smooth(side*smooth(std::abs(std::cos(a.angle*Rad)))+.5));
            const Vec carryGrip{std::min(31.,endGrip.x+1.*carry),endGrip.y-carrySide*2.*carry,endGrip.z};
            const auto fromGrip=[&](LocalPose grip){
                return LocalPose{grip.hilt+grip.direction*depth,grip.direction};
            };
            if(p<.22){
                const auto prev=riposteRelease(a,.9999,riposte,t);
                const double scale=.22*t.StrikeRecovery/(t.StrikeRelease*.0001);
                const Vec previousGrip=prev.hilt-prev.direction*depth;
                const double q=p/.22;
                LocalPose carried=hermite({endGrip,end.direction},{carryGrip,settle.direction},
                    {(endGrip-previousGrip)*scale,(end.direction-prev.direction)*scale},{{},{}},q);
                // The arms arrest their downward travel before the blade
                // finishes its carry. Preserve entry velocity but dissipate
                // grip momentum sooner to keep the completed cut off ground.
                carried.hilt=lerp(endGrip,carryGrip,smooth(q))+
                    (endGrip-previousGrip)*(scale*q*std::pow(1.-q,6.));
                return fromGrip(carried);
            }

            // Finish low, turn the blade, then bring the hands up. Blending
            // guard/hilt transforms together used to lift the hands while
            // the blade still pointed down, folding the wrists in recovery.
            const Vec turnGrip{std::min(31.,carryGrip.x+5.),carryGrip.y,carryGrip.z+3.};
            const Vec readyGrip=rest().hilt-rest().direction*depth;
            constexpr double turnEnd=.52,turnAngularVelocity=1.2,gripRiseVelocity=10.;
            if(p<turnEnd){
                const double duration=turnEnd-.22,q=(p-.22)/duration;
                const double h=q*q*(3.-2.*q),h1=q*q*(q-1.);
                const Vec grip=lerp(carryGrip,turnGrip,h)+Vec{0,0,gripRiseVelocity*duration}*h1;
                // Turn within the cutting plane, so a low diagonal finish
                // does not take a shortcut through a steeper, floor-hit pose.
                const double theta=exitAngle*(1.-h)+turnAngularVelocity*duration*h1;
                const Vec axis=Vec{1,0,0}*std::cos(theta)+origin*std::sin(theta);
                return fromGrip({grip,axis});
            }
            const double duration=1.-turnEnd,q=(p-turnEnd)/duration;
            const double h=q*q*(3.-2.*q),h0=q*(1.-q)*(1.-q);
            const Vec grip=lerp(turnGrip,readyGrip,h)+Vec{0,0,gripRiseVelocity*duration}*h0;
            const Vec axis=(lerp(Vec{1,0,0},rest().direction,h)+origin*(turnAngularVelocity*duration*h0)).normal();
            return fromGrip({grip,axis});
        }
        LocalPose ready={{30,side*10,6},Vec{.82,side*.12,.50}.normal()};

        if(p<.22){
            const auto prev=riposteRelease(a,.9999,riposte,t);
            const double scale=.22*(a.kind==AttackKind::Stab?t.StabRecovery:t.StrikeRecovery)/
                ((a.kind==AttackKind::Stab?t.StabRelease:t.StrikeRelease)*.0001);
            return hermite(end,settle,{(end.hilt-prev.hilt)*scale,(end.direction-prev.direction)*scale},{{},{}},p/.22);
        }
        const double q=smooth((p-.22)/.78);
        // A continuous curved return, without stopping at an intermediate pose.
        return blend(blend(settle,ready,q),blend(ready,rest(),q),q);
    }

    static LocalPose opposition(LocalPose contact,double p,Resolution result,Vec normal={})
    {
        // A stopped attack first compresses behind contact, then disengages.
        // Input may interrupt this presentation immediately when gameplay allows.
        p=clamp(p,0.,1.);
        LocalPose brace=contact;
        brace.hilt=contact.hilt-contact.direction*(result==Resolution::Chamber?7.:4.);
        brace.direction=slerp(contact.direction,Vec{.3,contact.direction.y,.65}.normal(),.12);
        if(normal.length()>.5){
            const double rebound=result==Resolution::Wall?7.:result==Resolution::Chamber?5.:3.;
            brace.hilt=contact.hilt+normal*rebound;
            const Vec reflected=contact.direction-normal*(2.*contact.direction.dot(normal));
            brace.direction=slerp(contact.direction,reflected,result==Resolution::Wall?.23:.12);
        }
        if(p<.22)return blend(contact,brace,smooth(p/.22));
        return blend(brace,rest(),smooth((p-.22)/.78));
    }

    static LocalPose riposteRelease(const AttackIntent& attack,double progress,bool riposte,const Tuning& t)
    {
        LocalPose pose=release(attack,progress,t,riposte);
        if(riposte){
            // Counter directly along the selected attack's hand arc. Its
            // load already supplies the appropriate height; an extra lift
            // pushed diagonal counters above the head and obscured the view.
            pose.hilt.x+=8.*std::sin(progress*Pi);
        }
        return pose;
    }

    static LocalPose riposteRelease(const AttackIntent& attack,double progress,bool riposte)
    {
        static const Tuning Defaults;
        return riposteRelease(attack,progress,riposte,Defaults);
    }

    static BodyMotion body(const AttackStateMachine& s,const Tuning& t)
    {
        BodyMotion b;
        if(s.phase==Phase::Idle||s.phase==Phase::Dead||s.phase==Phase::Parry||
           s.phase==Phase::ParryRecovery||s.phase==Phase::Flinch)return b;

        const double side=resolvedStance(s.attack)==Stance::Right?1.:-1.;
        const double lateral=side*smooth(std::abs(std::cos(s.attack.angle*Rad)));
        const double vertical=std::sin(s.attack.angle*Rad);
        const double over=std::max(0.,vertical),under=std::max(0.,-vertical);
        const double verticalWeight=std::abs(vertical);

        if(s.attack.kind==AttackKind::Stab){
            double load=0.,extension=0.;
            if(s.phase==Phase::Windup)load=smooth(s.progress());
            else if(s.phase==Phase::Release){load=1.;extension=releaseMap(s.progress(),t,s.isRiposte);}
            else if(s.phase==Phase::Recovery)load=extension=1.-smooth(s.progress());
            b.chestYaw=side*(-5.*load+12.*extension);b.chestPitch=-3.*load;
            b.forwardLean=4.*extension;b.gripRoll=side*4.*load;
            b.rightShoulderX=-2.*load+6.*extension;b.leftShoulderX=-load+4.*extension;
            b.rightElbowOut=b.leftElbowOut=3.*(load-extension);
            return b;
        }

        double load=0,through=0;
        if(s.phase==Phase::Windup){load=smooth(s.progress());b.forwardLean=-3.*load;}
        else if(s.phase==Phase::Release){
            const double q=releaseMap(s.progress(),t,s.isRiposte);
            // Body leads the exact blade fractionally: perceived inertia without
            // any collision/rendered-blade divergence.
            const double bodyQ=clamp(q+.07*std::sin(q*Pi),0.,1.);
            load=1.-bodyQ;through=bodyQ;
            b.forwardLean=6.*std::sin(q*Pi)-3.*(1.-q);
        }
        else if(s.phase==Phase::Recovery)through=1.-smooth(s.progress());

        // Preserve the authored ordinary swing rails while making their
        // weights available to contact capture and body-pose transitions.
        const double armOverhead=clamp(vertical/.866025403784439,0.,1.);
        if(s.phase==Phase::Release){
            b.elbowCarry=armOverhead*smooth((s.progress()-.40)/.50);
            const double support=armOverhead*smooth((s.progress()-.20)/.45);
            b.rightForearmCarry=support*(1.-smooth(2.*lateral));
            b.leftForearmCarry=support*(1.-smooth(-2.*lateral));
        }else if(s.phase==Phase::Recovery){
            b.elbowCarry=armOverhead*(1.-smooth((s.progress()-.40)/.40));
            const double support=armOverhead*(1.-smooth((s.progress()-.38)/.30));
            b.rightForearmCarry=support*(1.-smooth(2.*lateral));
            b.leftForearmCarry=support*(1.-smooth(-2.*lateral));
        }
        const double highGuardVertical=smooth((vertical-.866025403784439)/(1.-.866025403784439));
        b.rightHighGuardWeight=armOverhead*load*(1.-smooth(2.*lateral))*mix(1.,side>0?1.:.4,highGuardVertical);
        b.leftHighGuardWeight=armOverhead*load*(1.-smooth(-2.*lateral))*mix(1.,side>0?.4:1.,highGuardVertical);
        b.rightHighGuardRail=lerp(Vec{.48,.4,.7},Vec{1.,.4,.6},highGuardVertical)*b.rightHighGuardWeight;
        b.leftHighGuardRail=lerp(Vec{.48,-.4,.7},Vec{1.,-.4,.6},highGuardVertical)*b.leftHighGuardWeight;

        const double yawScale=1.-.12*verticalWeight;
        // A vertical cut is driven chiefly by thorax pitch. Using the sign
        // of its tiny lateral component gave it full horizontal torque and
        // reversed that torque abruptly when the origin crossed 90 degrees.
        const double rotationWeight=vertical>=0?mix(lateral,side*.18,highGuardVertical):side;
        b.chestYaw=rotationWeight*(22.*load-30.*through)*yawScale;
        b.chestPitch=-vertical*(7.*load+4.*through)-2.*over*through+1.5*under*load;

        const double originRight=vertical>=0?mix(clamp((lateral+1.)*.5,0.,1.),.5+side*.25,highGuardVertical):(side>0?1.:0.);
        const double originLeft=1.-originRight;
        b.rightShoulderX=(-6.*originRight+3.*originLeft)*load+(3.*originRight-5.*originLeft)*through;
        b.leftShoulderX=(3.*originRight-6.*originLeft)*load+(-5.*originRight+3.*originLeft)*through;

        b.rightElbowOut=mix(4.,10.,originRight)*load+mix(9.,4.,originRight)*through;
        b.leftElbowOut=mix(4.,10.,originLeft)*load+mix(9.,4.,originLeft)*through;
        b.rightElbowLift=mix(1.,5.,originRight)*load-vertical*2.*through+over*5.*load-under*3.*load;
        b.leftElbowLift=mix(1.,5.,originLeft)*load-vertical*2.*through+over*5.*load-under*3.*load;

        if(vertical>=0){
            const double overhead=clamp(over/.866025403784439,0.,1.);
            b.chestPitch+=overhead*(4.*load-5.*through);
            b.rightShoulderZ=mix(1.5*load-through,3.*load-3.5*through,overhead);
            b.leftShoulderZ=mix(.5*load-2.*through,4.*load-2.5*through,overhead);
            // Thorax pitch already brings the girdle forward in an overhead.
            // Reserve the added protraction for the lateral part of the cut;
            // otherwise the shoulder overtakes the hands at the low finish.
            const double protraction=overhead*lateral*lateral*through;
            b.rightShoulderX+=3.*protraction;
            b.leftShoulderX+=4.*protraction;
            b.chestYaw+=(1.-overhead)*mix(3.*load-2.*through,-2.*load-3.*through,originRight);
        }else if(verticalWeight<.05){
            // A right-handed grip makes the two horizontal cuts different:
            // the forward hand directs; the rear hand draws the pommel.
            b.chestYaw+=side>0?(-2.*load-3.*through):(3.*load-2.*through);
            b.rightShoulderZ=1.5*load-through;
            b.leftShoulderZ=.5*load-2.*through;
        }

        // Orient the cutting edge into the selected attack plane as the wrists
        // load; diagonal cuts must not retain a horizontal flat-blade frame.
        const double planeRoll=std::atan2(vertical,std::abs(lateral))*side/Rad;
        // The calibrated double-edge plane has a 180-degree frame branch at
        // vertical. Keep that existing handed grip convention; the smaller
        // loading/twist accent must still vary continuously with the origin.
        b.gripRoll=planeRoll*(load+through)+rotationWeight*(-7.*load+13.*through)+vertical*(5.*load-3.*through);
        // The support leg/pelvis starts redirecting before the thorax. The
        // waist follows between the hips and shoulder girdle, without adding
        // a root step or changing the sword's release clock/acceleration map.
        double hipLoad=load,hipThrough=through,waistLoad=load,waistThrough=through;
        if(s.phase==Phase::Release){
            const double q=releaseMap(s.progress(),t,s.isRiposte);
            hipThrough=clamp(q+.17*std::sin(q*Pi),0.,1.);hipLoad=1.-hipThrough;
            waistThrough=clamp(q+.11*std::sin(q*Pi),0.,1.);waistLoad=1.-waistThrough;
        }
        b.pelvisYaw=rotationWeight*(9.*hipLoad-14.*hipThrough);
        b.waistYaw=rotationWeight*(6.*waistLoad-8.*waistThrough);
        b.pelvisDrop=1.2*load+2.2*std::sin(Pi*through);
        b.rightFootYaw=rotationWeight*(2.*hipLoad-6.*hipThrough);
        b.leftFootYaw=rotationWeight*(4.*hipLoad-3.*hipThrough);
        return b;
    }

    static LocalPose evaluate(const AttackStateMachine& s,LocalPose windupStart,const Tuning& t,LocalPose velocity={{},{}})
    {
        if(s.phase==Phase::Windup)return windup(s.attack,s.progress(),windupStart,t,s.isCombo,s.isRiposte,s.definition.windup,velocity);
        if(s.phase==Phase::Release)return riposteRelease(s.attack,s.progress(),s.isRiposte,t);
        if(s.phase==Phase::Recovery)return recovery(s.attack,s.progress(),t,s.last,s.isRiposte);
        if(s.phase==Phase::Parry)return {{35,0,8},Vec{.12,.8,.58}.normal()};
        return rest();
    }

    static Vec shoulder(Vec eye,Orientation orientation,BodyMotion b,int side,double torsoPitch)
    {
        const Orientation torso{orientation.yaw+b.chestYaw,b.chestPitch};
        // Revised imported Citadel glenohumeral centers: Y +/-22 cm.
        // The shoulder lies inside its armor silhouette; keep this shared
        // target on that measured center while the thorax organizes the arm.
        return BodyFrame::make(eye,orientation,torsoPitch).transform(eye+Vec{0,0,-52.-b.pelvisDrop}+torso.world({
            (side==0?b.rightShoulderX:b.leftShoulderX)+b.forwardLean,
            side==0?22.:-22.,29.47+(side==0?b.rightShoulderZ:b.leftShoulderZ)}));
    }

    static Pose desiredWorld(LocalPose p,Vec eye,Orientation orientation,const Tuning& t,
                             Orientation bodyView,double leanFraction=1.,double gripRoll=0.)
    {
        const double pitch=clamp(bodyView.pitch,-85.,85.)*t.TorsoPitchScale*leanFraction;
        const auto frame=BodyFrame::make(eye,bodyView,pitch);
        const Vec h=frame.eye()-frame.torso.up()*18.+orientation.world(p.hilt);
        const Vec axis=orientation.world(p.direction).normal();
        return {h,h+axis*t.BladeLength,weaponEdge(axis,orientation,gripRoll)};
    }

    static Pose world(LocalPose p,Vec eye,Orientation orientation,const Tuning& t,BodyMotion bodyPose,Orientation bodyView,double leanFraction=1.)
    {
        const double pitch=clamp(bodyView.pitch,-85.,85.)*t.TorsoPitchScale*leanFraction;
        const Pose desired=desiredWorld(p,eye,orientation,t,bodyView,leanFraction,bodyPose.gripRoll);
        Vec h=desired.hilt;
        const Vec axis=(desired.tip-desired.hilt).normal();
        // Project the shared weapon into the two-hand reach envelope before
        // collision. Camera pitch can no longer demand arbitrarily long arms.
        // Grip spacing scales with the calibrated estoc, exactly as in the rig.
        for(int pass=0;pass<8;++pass)for(int side=0;side<2;++side){
            const double depth=t.BladeLength*(side==0?.12:.23)/1.103061375617981;
            const Vec center=shoulder(eye,bodyView,bodyPose,side,pitch)+axis*depth;
            const Vec delta=h-center;
            // Imported upper/lower links total 55.800818 cm. Reserve the
            // 4.92443 cm rigid palm offset and a half-centimetre elbow margin.
            // The historical 43 cm sphere prevented a delivered extension.
            constexpr double palmReach=55.800818-4.92443-.5;
            if(delta.length()>palmReach)h=center+delta.normal()*palmReach;
        }
        return {h,h+axis*t.BladeLength,desired.edge};
    }

    static Pose world(LocalPose p,Vec eye,Orientation orientation,const Tuning& t,BodyMotion bodyPose={})
    {return world(p,eye,orientation,t,bodyPose,orientation);}
};
}
