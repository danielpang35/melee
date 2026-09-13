#include "Debug/SwingTelemetry.h"
#include "Movement/LocomotionModel.h"
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace mcl;
int checks=0;
void require(bool b,const char* message){++checks;if(!b)throw std::runtime_error(message);}
struct Contact {double time=-1,speed=0,release=0;};
Contact measure(double family,double yawRate,double pitchRate,double yaw,double windup,double movement=0,AttackKind kind=AttackKind::Strike)
{
    CombatSimulation sim;sim.tuning.StrikeWindup=windup;
    Combatant a,b;a.id=1;b.id=2;a.reset({0,0,88},{yaw,0},sim.tuning);b.reset({135,0,88},{180,0},sim.tuning);
    a.externalView=false;sim.actors={&a,&b};a.start({kind,family,family},sim.tuning);
    sim.beforeStep=[&](double dt){if(a.state.phase==Phase::Release){a.look(yawRate*dt,pitchRate*dt,dt,sim.tuning);}};
    for(int i=0;i<360;++i){
        a.frameTarget=a.position+Vec{movement/240.,0,0};sim.advance(1./240.);
        for(const auto& e:sim.events)if(e.result==Resolution::Hit&&e.attacker==1)return {e.time,e.incomingVelocity.length(),a.state.definition.release};
    }
    return {};
}
void authoredLateContactCases()
{
    // These outcomes changed deliberately with the shared post-target hand
    // drive. Preserve representative edge contacts and a cleared late drag,
    // instead of assuming that a scalar reach ceiling fixes every collision.
    struct Fixture {double origin,x,y,yaw,manipulation,firstHit;};
    const Fixture fixtures[]={
        {60,175,0,30,1,215./240.},
        {120,135,60,0,-1,243./240.},
        {30,115,-30,30,-1,-1.}
    };
    for(const auto& fixture:fixtures){
        Vec referencePoint;double referenceTime=-1.;
        for(int frameRate:{30,60,120,240}){
            CombatSimulation sim;Combatant a,b;a.id=1;b.id=2;
            a.reset({0,0,88},{fixture.yaw,0},sim.tuning);
            b.reset({fixture.x,fixture.y,88},{180,0},sim.tuning);
            a.externalView=false;sim.actors={&a,&b};
            a.start({AttackKind::Strike,fixture.origin,fixture.origin},sim.tuning);
            sim.beforeStep=[&](double dt){if(a.state.phase==Phase::Release){
                a.look(-std::cos(fixture.origin*Rad)*80.*fixture.manipulation*dt,
                    -std::sin(fixture.origin*Rad)*70.*fixture.manipulation*dt,dt,sim.tuning);
            }};
            double firstHit=-1.;Vec contactPoint;
            for(int frame=0;frame<frameRate*2&&firstHit<0.;++frame){
                sim.advance(1./frameRate);
                for(const auto& event:sim.events)if(event.result==Resolution::Hit&&event.attacker==1){
                    firstHit=event.time;contactPoint=event.point;break;
                }
            }
            if(std::abs(firstHit-fixture.firstHit)>=1e-10)std::cerr<<"Late-contact diagnostic origin="<<fixture.origin<<" target="<<fixture.x<<","<<fixture.y<<" fps="<<frameRate<<" actual="<<firstHit<<" expected="<<fixture.firstHit<<'\n';
            require(std::abs(firstHit-fixture.firstHit)<1e-10,
                "Authored late-arc hit and miss fixtures retain their intended authoritative outcomes");
            if(firstHit>0.){
                const double damageProgress=(firstHit-sim.tuning.StrikeWindup)/sim.tuning.StrikeRelease;
                require(damageProgress>=sim.tuning.DamageStart&&damageProgress<=sim.tuning.DamageEnd,
                    "Newly supported late contacts still occur inside the existing damage window");
            }
            if(frameRate==30){referenceTime=firstHit;referencePoint=contactPoint;}
            else require(std::abs(firstHit-referenceTime)<1e-10&&(contactPoint-referencePoint).length()<1e-8,
                "The same late-arc contact result, timestamp and location are independent of render frame rate");
        }
    }
}
void authoredHandTravel()
{
    Tuning t;
    const double midpointDepth=t.BladeLength*.175/1.103061375617981;
    for(double family:{60.,120.}){
        Combatant s;s.reset({0,0,88},{},t);s.start({AttackKind::Strike,family,family},t);
        Vec loaded,finish;double path=0.;bool sampled=false;Vec previous;
        for(int i=0;i<260;++i){
            s.advance(1./240.,t);
            if(s.state.phase!=Phase::Release)continue;
            const Vec axis=(s.weapon.tip-s.weapon.hilt).normal();
            const Vec grip=s.weapon.hilt-axis*midpointDepth;
            if(sampled)path+=(grip-previous).length();else loaded=grip;
            previous=finish=grip;sampled=true;
        }
        require(loaded.z-finish.z>42.,"Overhead hands travel down through the target before recovery");
        require(finish.z>108.&&finish.z<126.,"Standing overhead completes at upper abdomen with the grip");
        require(path>55.,"Overhead blade rotation is supported by substantial hand translation");
    }
    const auto right=AttackTrajectory::release({AttackKind::Strike,0,0},.25,t);
    const auto left=AttackTrajectory::release({AttackKind::Strike,180,180},.25,t);
    const Vec rightGrip=right.hilt-right.direction*midpointDepth;
    const Vec leftGrip=left.hilt-left.direction*midpointDepth;
    // Keep distinct lead/trailing-hand choreography. The old 3 cm lower
    // bound described one candidate; it was not a calibrated anatomy limit.
    require((rightGrip-Vec{leftGrip.x,-leftGrip.y,leftGrip.z}).length()>.1,
        "Opposite horizontal origins retain distinct hand poses for a right-handed grip");
    const double existingForwardExtent=31.+midpointDepth+t.BladeLength;
    double maxExtent=0.;
    for(int family=-180;family<=180;family+=5){
        const AttackIntent intent{AttackKind::Strike,double(family),double(family)};
        AttackStateMachine state;state.start(intent,t);state.phase=Phase::Release;
        for(int sample=0;sample<=1000;++sample){
            state.elapsed=t.StrikeRelease*sample/1000.;
            const auto local=AttackTrajectory::release(intent,sample/1000.,t);
            const auto blade=AttackTrajectory::world(local,{0,0,170},{},t,AttackTrajectory::body(state,t));
            maxExtent=std::max(maxExtent,blade.tip.x);
            require(blade.tip.x<=existingForwardExtent+.001,
                "Authored hand travel does not increase the established global forward reach");
        }
    }
    require(maxExtent<=existingForwardExtent+1e-8,
        "The forward high guard and post-target extension preserve the established geometric reach ceiling");
    std::cout<<"Maximum standing strike forward extent: "<<maxExtent<<" cm\n";
}
void highGuardCameraDepth()
{
    Tuning t;
    double minimumHighGuardDepth=1e6;
    for(double family:{0.,60.,90.,120.,180.})for(double pitch:{-85.,0.,85.}){
        const bool overhead=family>0.&&family<180.;
        if(overhead)require(std::abs(AttackTrajectory::strikeGrip({AttackKind::Strike,family,family},0.,t).x-26.)<1e-10,
            "Overhead loading holds the shared grip in front of the face");
        Combatant s;s.reset({0,0,88},{0,pitch},t);s.start({AttackKind::Strike,family,family},t);
        for(int sample=0;sample<=138;++sample){
            if(sample)s.advance(t.StrikeWindup/138.,t);
            const Vec axis=(s.weapon.tip-s.weapon.hilt).normal();
            for(int side=0;side<2;++side){
                const double depth=t.BladeLength*(side==0?.12:.23)/1.103061375617981;
                const Vec contact=s.weapon.hilt-axis*depth;
                const double cameraDepth=s.view.local(contact-s.eye()).x;
                require(cameraDepth>0.,"The projected windup hand contacts remain in front of the actual eye");
                if(overhead){
                    minimumHighGuardDepth=std::min(minimumHighGuardDepth,cameraDepth);
                    require(cameraDepth>13.5,
                        "Physical overhead guard depth survives reach projection at extreme view pitches");
                }
            }
        }
    }
    std::cout<<"Minimum projected overhead windup contact depth: "<<minimumHighGuardDepth<<" cm\n";
}
void postTargetHandDrive()
{
    Tuning t;
    constexpr double step=.000001;
    for(double family:{60.,120.}){
        const AttackIntent intent{AttackKind::Strike,family,family};
        const auto drive=AttackTrajectory::strikeGrip(intent,.7,t);
        require(std::abs(drive.x-(family==60.?38.69:38.55))<1e-10,
            "The post-target diagonal grip key creates ten centimeters of forward forearm space");
    }
    for(double family:{0.,30.,60.,75.,89.9999,90.,90.0001,105.,120.,150.,180.,-60.,-120.}){
        const AttackIntent intent{AttackKind::Strike,family,family};
        for(double q:{.5,.7}){
            const auto left=AttackTrajectory::strikeGrip(intent,q-step,t);
            const auto middle=AttackTrajectory::strikeGrip(intent,q,t);
            const auto right=AttackTrajectory::strikeGrip(intent,q+step,t);
            require((right-left).length()<.002,
                "The post-target grip key cannot introduce a positional jump");
            require(((middle-left)-(right-middle)).length()/step<.01,
                "The target passage and post-target grip key preserve continuous hand velocity");
        }
        for(bool riposte:{false,true})for(Resolution result:{Resolution::Hit,Resolution::Miss}){
            const auto before=AttackTrajectory::riposteRelease(intent,1.-step,riposte,t);
            const auto end=AttackTrajectory::riposteRelease(intent,1.,riposte,t);
            const auto start=AttackTrajectory::recovery(intent,0.,t,result,riposte);
            const auto after=AttackTrajectory::recovery(intent,step,t,result,riposte);
            require((end.hilt-start.hilt).length()<1e-8&&(end.direction-start.direction).length()<1e-8,
                "Recovery begins at the completed forward-drive pose");
            const Vec incoming=(end.hilt-before.hilt)/(step*t.StrikeRelease);
            const Vec outgoing=(after.hilt-start.hilt)/(step*t.StrikeRecovery);
            require((outgoing-incoming).length()<.5,
                "The forward-driven finish transfers hand and guard velocity continuously into recovery");
        }
    }
    double minimumFloor=1e6;
    for(double family:{60.,90.,120.}){
        AttackStateMachine state;state.start({AttackKind::Strike,family,family},t);state.phase=Phase::Release;
        double previousHeight=1e6;
        for(int sample=0;sample<=1000;++sample){
            const double p=sample/1000.;state.elapsed=t.StrikeRelease*p;
            const auto local=AttackTrajectory::release(state.attack,p,t);
            const auto blade=AttackTrajectory::world(local,{0,0,170},{},t,AttackTrajectory::body(state,t));
            const double handHeight=blade.hilt.z-local.direction.z*t.BladeLength*.175/1.103061375617981;
            require(handHeight<=previousHeight+1e-7,
                "Authoritative overhead hands keep descending during the post-target forward drive");
            previousHeight=handHeight;
            minimumFloor=std::min(minimumFloor,blade.tip.z-t.BladeRadius);
            require(blade.tip.z>=t.BladeRadius-1e-7,
                "The projected post-target cut retains standing blade clearance");
        }
    }
    std::cout<<"Minimum authoritative overhead release floor margin: "<<minimumFloor<<" cm\n";
}
void overheadBodyContinuity()
{
    Tuning t;
    for(Stance stance:{Stance::Right,Stance::Left})for(double time:{.20,.50,.575,.80,1.075,1.22,1.50}){
        Combatant left,right,vertical;
        left.reset({0,0,88},{},t);right.reset({0,0,88},{},t);vertical.reset({0,0,88},{},t);
        // Compare compatible samples of one latched stance. Crossing angle
        // no longer selects or blends an opposite body-side performance.
        left.start({AttackKind::Strike,89.9999,89.9999,stance},t);
        right.start({AttackKind::Strike,90.0001,90.0001,stance},t);
        vertical.start({AttackKind::Strike,90.,90.,stance},t);
        left.advance(time,t);right.advance(time,t);vertical.advance(time,t);
        const auto a=left.bodyMotion,b=right.bodyMotion;
        require(std::abs(a.chestYaw-b.chestYaw)<.001,
            "Neighboring vertical origins cannot reverse full horizontal body torque");
        require(std::abs(a.rightElbowOut-b.rightElbowOut)<.001&&
            std::abs(a.leftElbowOut-b.leftElbowOut)<.001&&
            std::abs(a.rightElbowLift-b.rightElbowLift)<.001&&
            std::abs(a.leftElbowLift-b.leftElbowLift)<.001,
            "Lead and trailing elbow preferences blend continuously through a vertical origin");
        for(int side=0;side<2;++side){
            const auto first=AttackTrajectory::shoulder(left.uprightEye(),left.view,a,side,0);
            const auto second=AttackTrajectory::shoulder(right.uprightEye(),right.view,b,side,0);
            require((first-second).length()<.002,
                "Glenohumeral centers cannot jump when an overhead origin crosses vertical");
        }
        if(left.state.phase==Phase::Release){
            require(std::abs(wrap(a.gripRoll-b.gripRoll))<.001&&angle(left.weapon.edge,right.weapon.edge)<.001,
                "Compatible neighboring overheads retain the complete signed weapon frame");
            require(std::abs((vertical.weapon.tip-vertical.weapon.hilt).y)<1e-7,
                "A vertical cut keeps its blade in the vertical plane while the stance supports it");
        }
    }
    Combatant vertical;vertical.reset({0,0,88},{},t);vertical.start({AttackKind::Strike,90,90},t);
    vertical.advance(t.StrikeWindup+t.StrikeRelease*.999,t);
    const Vec axis=(vertical.weapon.tip-vertical.weapon.hilt).normal();
    const Vec hand=vertical.weapon.hilt-axis*(t.BladeLength*.12/1.103061375617981);
    const Vec shoulder=AttackTrajectory::shoulder(vertical.uprightEye(),vertical.view,vertical.bodyMotion,0,0);
    require(hand.x-shoulder.x>15.,
        "The vertical finish leaves forward hand space instead of moving the shoulder into the grip");
    for(double family:{0.,180.})for(double p:{0.,1.}){
        AttackStateMachine state;state.attack={AttackKind::Strike,family,family};
        state.phase=Phase::Release;state.definition.release=t.StrikeRelease;state.elapsed=t.StrikeRelease*p;
        const double expected=family==0?(p==0?20.:-33.):(p==0?-19.:28.);
        require(std::abs(AttackTrajectory::body(state,t).chestYaw-expected)<.000001,
            "Established right and left horizontal body endpoints remain unchanged");
    }
}
void overheadRecoveryContinuity()
{
    Tuning t;
    const double depth=t.BladeLength*.175/1.103061375617981;
    constexpr double angleStep=.0001,phaseStep=.000001;
    for(bool riposte:{false,true})for(Resolution result:{Resolution::Miss,Resolution::Hit}){
        const auto pose=[&](double angle,double p){
            return AttackTrajectory::recovery({AttackKind::Strike,angle,angle},p,t,result,riposte);
        };
        for(double p:{0.,.10,.22-phaseStep,.22,.22+phaseStep,.40,.52-phaseStep,.52,.52+phaseStep,.75,1.}){
            const auto left=pose(90.-angleStep,p),middle=pose(90.,p),right=pose(90.+angleStep,p);
            require((right.hilt-left.hilt).length()<.002,
                "Neighboring vertical recovery origins cannot jump between lateral hand carries");
            require((right.direction-left.direction).length()<.0001,
                "Neighboring vertical recovery origins preserve blade direction continuity");
            require(((middle.hilt-left.hilt)-(right.hilt-middle.hilt)).length()/angleStep<.001,
                "Recovery hand position has a continuous angle derivative through the vertical origin");
            require(((middle.direction-left.direction)-(right.direction-middle.direction)).length()/angleStep<.0001,
                "Recovery blade direction has a continuous angle derivative through the vertical origin");
        }
        for(double family:{60.,90.-angleStep,90.,90.+angleStep,120.})for(double p:{.22,.52}){
            const auto left=pose(family,p-phaseStep),middle=pose(family,p),right=pose(family,p+phaseStep);
            require((right.hilt-left.hilt).length()<.002,
                "The carry and return sections meet without a weapon position jump");
            require(((middle.hilt-left.hilt)-(right.hilt-middle.hilt)).length()/(phaseStep*t.StrikeRecovery)<.02,
                "The carry and return sections preserve continuous hand and guard velocity");
            require(((middle.direction-left.direction)-(right.direction-middle.direction)).length()/(phaseStep*t.StrikeRecovery)<.001,
                "The carry and return sections preserve continuous blade angular velocity");
        }
        const double carry=result==Resolution::Miss?1.10:.88;
        for(double family:{60.,90.,120.}){
            const auto end=AttackTrajectory::riposteRelease({AttackKind::Strike,family,family},1.,riposte,t);
            const auto carried=pose(family,.22);
            const double endY=end.hilt.y-end.direction.y*depth;
            const double carryY=carried.hilt.y-carried.direction.y*depth;
            const double expected=family==60.?-2.*carry:family==120.?2.*carry:0.;
            require(std::abs(carryY-endY-expected)<1e-10,
                "The vertical carry retains its grip asymmetry while diagonal carry endpoints stay unchanged");
        }
    }
}
void overheadEndpointClearance()
{
    Tuning t;
    const double depth=t.BladeLength*.175/1.103061375617981;
    const AttackIntent vertical{AttackKind::Strike,90,90};
    double previous=1e6,previousForward=-1e6;
    for(int sample=0;sample<=1000;++sample){
        const auto pose=AttackTrajectory::release(vertical,sample/1000.,t);
        const double handHeight=pose.hilt.z-pose.direction.z*depth;
        require(handHeight<=previous+1e-8,
            "A vertical cut completes its downward hand travel without a late floor-clamp rise");
        const double handForward=pose.hilt.x-pose.direction.x*depth;
        require(handForward>=previousForward-1e-8&&handForward<=31.+1e-8,
            "The vertical cut keeps driving the hands forward without exceeding the passage reach");
        previous=handHeight;
        previousForward=handForward;
    }
    // Current high-guard fixtures preserve target passage and the complete
    // lateral/height tracks while X now drives after the target.
    const double families[2]={60.,120.};
    const Vec reference[2][5]={
        {{26,6.75,22.25},{29,4.40625,11.8375},{31,1.75,-1.25},
            {27.6484375,-1.140625,-19.359375},{22.75,-3.75,-36.75}},
        {{26,-5.75,22.75},{29,-3.40625,11.7375},{31,-.75,-1.75},
            {27.4453125,2.140625,-19.453125},{22.25,4.75,-36.25}}
    };
    for(int family=0;family<2;++family)for(int sample=0;sample<5;++sample){
        const auto grip=AttackTrajectory::strikeGrip(
            {AttackKind::Strike,families[family],families[family]},sample*.25,t);
        const auto before=reference[family][sample];
        require(std::abs(grip.y-before.y)<1e-10&&std::abs(grip.z-before.z)<1e-10,
            "Post-target hand drive preserves the diagonal lateral and floor-safe height tracks");
        if(sample<=2)require(std::abs(grip.x-before.x)<1e-10,
            "The authored high guard joins the unchanged target passage");
        if(sample==4)require(std::abs(grip.x-before.x-10.)<1e-10,
            "The completed diagonal cut retains its authored ten-centimeter forward drive");
    }
    double minimumClearance=1e6;
    for(double length:{50.,110.,160.})for(double radius:{2.,4.,10.})
        for(double start:{55.,78.,100.})for(double end:{-110.,-90.,-82.,-55.})
            for(double family:{0.,30.,55.,60.,75.,85.,90.,95.,105.,120.,125.,150.,180.}){
                t.BladeLength=length;t.BladeRadius=radius;t.StrikeArcStart=start;t.StrikeArcEnd=end;
                for(int sample=0;sample<=256;++sample){
                    const auto pose=AttackTrajectory::release({AttackKind::Strike,family,family},sample/256.,t);
                    const double clearance=152.+pose.hilt.z+pose.direction.z*t.BladeLength-t.BladeRadius;
                    minimumClearance=std::min(minimumClearance,clearance);
                    require(clearance>=1.-1e-7,
                        "Authored overheads clear standing floor across configured blade lengths, radii and arc limits");
                }
            }
    std::cout<<"Minimum configured overhead floor margin: "<<minimumClearance<<" cm\n";
    double minimumRecoveryClearance=1e6;
    for(double length:{50.,110.,160.})for(double radius:{2.,4.,10.})
        for(double end:{-110.,-90.,-82.,-55.})
            for(double family:{30.,55.,60.,61.,63.,75.,90.,105.,117.,119.,120.,125.,150.})
                for(bool riposte:{false,true})for(Resolution result:{Resolution::Miss,Resolution::Hit}){
                    t.BladeLength=length;t.BladeRadius=radius;t.StrikeArcEnd=end;
                    for(int sample=0;sample<=256;++sample){
                        const auto pose=AttackTrajectory::recovery(
                            {AttackKind::Strike,family,family},sample/256.,t,result,riposte);
                        const double clearance=152.+pose.hilt.z+pose.direction.z*t.BladeLength-t.BladeRadius;
                        minimumRecoveryClearance=std::min(minimumRecoveryClearance,clearance);
                        require(clearance>=-1e-7,
                            "The authored low carry clears the floor before the blade turns back to guard");
                    }
                }
    std::cout<<"Minimum configured recovery floor margin: "<<minimumRecoveryClearance<<" cm\n";
}
int main(){try{
    authoredLateContactCases();
    authoredHandTravel();
    highGuardCameraDepth();
    postTargetHandDrive();
    overheadBodyContinuity();
    overheadRecoveryContinuity();
    overheadEndpointClearance();
    Tuning t;std::ofstream timing("swing-timing.csv");
    timing<<"windup,family,neutral,accel,drag,accel_delta,drag_delta,earliest_sampled,latest_sampled,neutral_tip_speed,release_duration\n";
    for(double windup:{.65,.62,.61,.575})for(double family:{0.,60.,120.,180.,-120.,-60.}){
        const double horizontal=std::cos(family*Rad),vertical=std::sin(family*Rad);
        auto neutral=measure(family,0,0,0,windup);
        auto accel=measure(family,-horizontal*80,-vertical*70,0,windup);
        auto drag=measure(family,horizontal*80,vertical*70,0,windup);
        double earliest=10,latest=-1;
        // A documented finite envelope, not an assertion of mathematical extrema.
        for(double yaw:{-30.,0.,30.})for(double manipulation:{-1.,-.5,0.,.5,1.}){
            const auto hit=measure(family,horizontal*255*manipulation,vertical*185*manipulation,yaw,windup);
            if(hit.time>0){earliest=std::min(earliest,hit.time);latest=std::max(latest,hit.time);}
        }
        require(neutral.time>0,"All six neutral families must hit the stationary dummy");
        require(accel.time>0&&accel.time<neutral.time-.015,"Each family's accel meaningfully advances contact");
        require(drag.time>neutral.time+.02,"Each family's drag meaningfully delays contact");
        timing<<windup<<','<<family<<','<<neutral.time<<','<<accel.time<<','<<drag.time<<','<<accel.time-neutral.time<<','<<drag.time-neutral.time
            <<','<<earliest<<','<<latest<<','<<neutral.speed<<','<<neutral.release<<'\n';
    }
    auto still=measure(0,0,0,0,t.StrikeWindup),moving=measure(0,0,0,0,t.StrikeWindup,45);
    const auto stab=measure(0,0,0,0,t.StrikeWindup,0,AttackKind::Stab);
    std::cout<<"Neutral stab contact: "<<stab.time<<'\n';
    require(stab.time>0,"Raised stab must contact the neutral dummy");
    require(moving.time>0&&moving.time<still.time-.01,"Player translation advances authoritative contact");
    CombatSimulation sim;Combatant a;a.reset({0,0,88},{},t);a.externalView=false;sim.actors={&a};a.start({},t);
    std::ofstream samples("swing-steps.csv");swingHeader(samples);
    sim.sampleStep=[&](const Combatant& s,double time){swingSample(samples,s,time);};
    sim.beforeStep=[&](double dt){if(a.state.phase==Phase::Release)a.look(-90*dt,25*dt,dt,t);};
    for(int i=0;i<350;++i){a.frameTarget=a.position+Vec{.12,.04,0};sim.advance(1./240.);
        const auto& m=a.motion;
        require((m.intrinsicTipVelocity+m.yawTipVelocity+m.pitchTipVelocity+m.translationVelocity-m.tipVelocity).length()<1e-6,
            "Per-step motion contributions sum to authoritative tip velocity");
        if(a.state.phase==Phase::Release)require(m.yawUtilization<=1.001&&m.pitchUtilization<=1.001,"Manipulation respects separate turn caps");
    }
    for(double family:{0.,60.,120.,180.,-120.,-60.}){
        Combatant c;c.reset({0,0,88},{},t);c.start({AttackKind::Strike,family,family},t);
        c.advance(t.StrikeWindup-.00001,t);const BodyMotion before=c.bodyMotion;
        c.advance(.00001,t);const BodyMotion at=c.bodyMotion;c.advance(.00001,t);const BodyMotion after=c.bodyMotion;
        require(std::abs((at.chestYaw-before.chestYaw)-(after.chestYaw-at.chestYaw))/.00001<.2,"Chest yaw transfers continuously through release");
    }
    CombatSimulation hitWorld,airWorld;Combatant striker,victim,air;
    striker.id=air.id=1;victim.id=2;
    striker.reset({0,0,88},{},t);air.reset({0,0,88},{},t);victim.reset({135,0,88},{180,0},t);
    hitWorld.actors={&striker,&victim};airWorld.actors={&air};striker.start({},t);air.start({},t);
    int hits=0;bool slowed=false;
    for(int i=0;i<260;++i){
        hitWorld.advance(1./240.);airWorld.advance(1./240.);
        for(const auto& event:hitWorld.events)if(event.result==Resolution::Hit){++hits;
            require(event.normal.length()>.9,"Body contact supplies a usable spatial normal");}
        require(striker.state.phase==air.state.phase&&std::abs(striker.state.elapsed-air.state.elapsed)<1e-9,
            "Contact deceleration must never change the attack clock");
        if(striker.contactAge<.035&&striker.state.phase==Phase::Release&&striker.speed<air.speed*.98)slowed=true;
        require((striker.weapon.hilt-striker.previousWeapon.hilt).length()<5.,"Contact response cannot teleport the grip");
    }
    require(hits==1&&slowed,"A body hit decelerates briefly without duplicate damage");
    const Vec n{-1,0,0};const auto contact=AttackTrajectory::release({},.45,t);
    require((AttackTrajectory::opposition(contact,.22,Resolution::Wall,n).hilt-
        AttackTrajectory::opposition(contact,.22,Resolution::Parry,n).hilt).length()>3.,"Wall and parry have distinct directional rebounds");
    std::cout<<"PASS: "<<checks<<" swing mechanics checks; swing-timing.csv and swing-steps.csv written\n";return 0;
}catch(const std::exception& e){std::cerr<<"FAIL: "<<e.what()<<'\n';return 1;}}
