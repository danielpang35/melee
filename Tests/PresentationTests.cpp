#include "Visual/MeleePresentationPose.h"
#include <iostream>
#include <stdexcept>
using namespace mcl;
int checks=0;
void require(bool value,const char* message){++checks;if(!value)throw std::runtime_error(message);}
bool close(Vec a,Vec b){return (a-b).length()<1e-7;}
struct RigArmInput
{
    Vec shoulder,clavicle,grip,shaft,rail,restGrip,restLower,palmOffset;
};
constexpr double RigClavicleLength=17.013405;
RigArmInput rigArmInput(Vec shoulder,Vec clavicle,Vec grip,Vec shaft,Vec rail,int side)
{
    const double sign=side==0?1.:-1.;
    // Measured imported rig vectors, including the corrected glove chirality.
    const Vec finger=Vec{.03,sign*.22,-.24}.normal();
    const Vec palm=(Vec{-1,0,0}+finger*finger.x).normal();
    return {shoulder,clavicle,grip,shaft.normal(),rail,
        (finger.cross(palm)*(-sign)+finger*.8).normal(),
        Vec{0,sign*.215,-.135}.normal(),finger*4.5+palm*2.};
}
presentation::GripArmPose solveRigArm(const RigArmInput& in)
{
    return presentation::solveGripArm(in.shoulder,in.clavicle,RigClavicleLength,
        in.grip,in.shaft,in.rail,in.restGrip,in.restLower,in.palmOffset);
}
void verifyRigArm(const RigArmInput& in,const presentation::GripArmPose& out)
{
    const Vec sourceRadial=(in.restLower-in.restGrip*in.restLower.dot(in.restGrip)).normal();
    const Vec sourceSide=in.restGrip.cross(sourceRadial);
    const Vec mappedOffset=out.handRadial*in.palmOffset.dot(sourceRadial)+
        in.shaft.cross(out.handRadial)*in.palmOffset.dot(sourceSide)+
        in.shaft*in.palmOffset.dot(in.restGrip);
    const auto& arm=out.arm;
    require(close(arm.hand+mappedOffset,in.grip),"Actual rig wrist plus rigid palm offset must contact the grip exactly");
    require(std::abs(mappedOffset.length()-in.palmOffset.length())<1e-7,
        "Actual glove mapping preserves palm geometry");
    require(std::abs(out.handRadial.length()-1.)<1e-7&&std::abs(out.handRadial.dot(in.shaft))<1e-7,
        "Actual glove frame is finite and orthonormal");
    require(std::isfinite(out.wristBend)&&std::isfinite(arm.elbow.x)&&std::isfinite(arm.elbow.y)&&std::isfinite(arm.elbow.z),
        "Actual rig solve remains finite");
    require(std::abs((arm.shoulder-in.clavicle).length()-RigClavicleLength)<1e-7,
        "Actual shoulder remains attached to its fixed length clavicle");
    require(std::abs((arm.elbow-arm.shoulder).length()-presentation::UpperArmLength*arm.reachScale)<1e-7,
        "Actual upper arm length matches the imported rig");
    require(std::abs((arm.hand-arm.elbow).length()-presentation::ForearmLength*arm.reachScale)<1e-7,
        "Actual forearm length matches the imported rig");
    require(arm.reachScale<1.000001,"Validated overhead trajectories do not stretch the actual rig");
}
double transportedHandStep(Vec previousShaft,Vec previousRadial,Vec shaft,Vec radial)
{
    const Vec turn=previousShaft.cross(shaft);
    const double cosine=previousShaft.dot(shaft);
    require(cosine>-.9999,"Adjacent diagnostic shafts have a unique shortest arc");
    const Vec transported=previousRadial+turn.cross(previousRadial)+turn.cross(turn.cross(previousRadial))/(1.+cosine);
    return angle(transported,radial);
}
void actualGripSolverContracts()
{
    Tuning t;
    double maxStep=0,maxBoundaryStep=0,maxWrist=0,maxElbowStep=0;
    double worstOrigin=0,worstPitch=0,worstProgress=0;
    int worstSide=0,worstPhase=0;
    for(double origin:{0.,60.,90.,120.,180.})for(double pitch:{-85.,0.,85.})
        for(bool crouched:{false,true})for(bool firstPerson:{false,true}){
            CombatSimulation sim;Combatant s;s.reset({130,-47,crouched?60.:88.},{37,pitch},t);
            s.bodyHalfHeight=crouched?60.:88.;s.eyeHeight=s.bodyHalfHeight-6.;
            sim.actors={&s};s.start({AttackKind::Strike,origin,origin},t);
            std::array<std::vector<RigArmInput>,2> inputs;
            std::array<std::vector<presentation::GripArmPose>,2> outputs;
            Phase previousPhase=s.state.phase;
            for(int frame=0;frame<720;++frame){
                sim.advance(1./240.);
                const auto pose=presentation::evaluate(s,t);
                const Orientation chest{s.view.yaw+pose.body.chestYaw,pose.body.chestPitch};
                for(int side=0;side<2;++side){
                    const double sign=side==0?1.:-1.;
                    // Native core cannot reproduce UE's skinned torso transform.
                    // This explicit inboard anchor tests the measured clavicle
                    // length while the shoulder follows the shared body motion.
                    const Vec clavicle=pose.arms[side].shoulder-s.bodyFrame().vector(
                        chest.world({0,sign*RigClavicleLength,0}));
                    const auto in=rigArmInput(pose.arms[side].shoulder,clavicle,pose.arms[side].hand,
                        pose.axis,presentation::elbowRail(s,pose.body,side,firstPerson),side);
                    const auto out=solveRigArm(in);verifyRigArm(in,out);
                    if(out.wristBend>maxWrist){
                        maxWrist=out.wristBend;worstOrigin=origin;worstPitch=pitch;
                        worstSide=side;worstPhase=static_cast<int>(s.state.phase);worstProgress=s.state.progress();
                    }
                    if(frame){
                        const auto& old=outputs[side].back();
                        const double step=transportedHandStep(inputs[side].back().shaft,old.handRadial,in.shaft,out.handRadial);
                        if(s.state.phase==previousPhase){
                            maxStep=std::max(maxStep,step);
                            maxElbowStep=std::max(maxElbowStep,(out.arm.elbow-old.arm.elbow).length());
                            if(step>=45.)std::cerr<<"Swivel diagnostic origin="<<origin<<" pitch="<<pitch<<" crouched="<<crouched<<" fp="<<firstPerson<<" side="<<side<<" frame="<<frame<<" phase="<<phaseName(s.state.phase)<<" step="<<step<<'\n';
                            require(step<45.,"Actual hand must not switch swivel branches within a continuous phase at 240 Hz");
                        }else maxBoundaryStep=std::max(maxBoundaryStep,step);
                    }
                    inputs[side].push_back(in);outputs[side].push_back(out);
                }
                previousPhase=s.state.phase;
            }
            // Revisit frames backwards and alternate arms. A hidden previous-
            // frame branch or a view-dependent cache would change these poses.
            for(int frame=719;frame>=0;--frame)for(int side:{1,0}){
                const auto again=solveRigArm(inputs[side][frame]);
                const auto& before=outputs[side][frame];
                require(close(again.handRadial,before.handRadial)&&close(again.arm.shoulder,before.arm.shoulder)&&
                    close(again.arm.elbow,before.arm.elbow)&&close(again.arm.hand,before.arm.hand)&&
                    again.wristBend==before.wristBend&&again.arm.reachScale==before.arm.reachScale,
                    "Actual grip solver is independent of frame order, previous arm and previous view");
            }
        }
    std::cout<<"Actual grip solver: max transported roll "<<maxStep<<" deg at 240 Hz, phase-boundary roll "
        <<maxBoundaryStep<<" deg, elbow step "<<maxElbowStep<<" cm; max wrist "<<maxWrist
        <<" deg (origin "<<worstOrigin<<", pitch "<<worstPitch<<", side "<<worstSide
        <<", phase "<<worstPhase<<", progress "<<worstProgress<<"). Clavicle anchors are native approximations.\n";

    // Retained Candidate 2, frames 33/34/35: the prior feedback solver rolled
    // the right glove 135 degrees in one 30 Hz step. Keep the saved contacts
    // and physical shoulder anchors, with the obsolete FP shoulder offset removed.
    struct CapturedGrip { Vec shoulder[2],contact[2]; };
    const CapturedGrip captured[]={
        {{{15.58240,20.56424,146.54060},{4.42699,-21.86270,148.02158}},
         {{35.05896,.5,142.07082},{24.88665,.5,146.17611}}},
        {{{17.36182,19.66187,145.87145},{2.78614,-21.61161,147.63481}},
         {{33.06707,.5,135.07723},{24.03221,.5,141.29821}}},
        {{{18.60407,18.65351,145.31754},{.97706,-21.29967,147.33264}},
         {{30.62400,.5,128.29358},{23.11414,.5,136.28929}}}
    };
    double capturedMaxStep=0,capturedMaxWrist=0;
    for(int side=0;side<2;++side){
        const double sign=side==0?1.:-1.;
        Vec previousShaft,previousRadial;
        for(int frame=0;frame<3;++frame){
            const auto& sample=captured[frame];
            const Vec shaft=(sample.contact[0]-sample.contact[1]).normal();
            const auto in=rigArmInput(sample.shoulder[side],sample.shoulder[side]-Vec{0,sign*RigClavicleLength,0},
                sample.contact[side],shaft,{side==0?.15:.35,sign*.4,-1.2},side);
            const auto out=solveRigArm(in);verifyRigArm(in,out);
            capturedMaxWrist=std::max(capturedMaxWrist,out.wristBend);
            if(frame){
                const double step=transportedHandStep(previousShaft,previousRadial,shaft,out.handRadial);
                capturedMaxStep=std::max(capturedMaxStep,step);
                require(step<60.,"Candidate 2 folded carry targets must not reproduce the glove branch jump");
            }
            previousShaft=shaft;previousRadial=out.handRadial;
        }
    }
    std::cout<<"Retained Candidate 2 contacts: max transported roll "<<capturedMaxStep
        <<" deg at 30 Hz, max wrist "<<capturedMaxWrist<<" deg (diagnostic, not a visual acceptance limit).\n";
}
presentation::GripArmPose presentedRigArm(const Combatant& s,const Tuning& t,int side,bool fp)
{
    const auto pose=presentation::evaluate(s,t);
    const double sign=side==0?1.:-1.;
    const Orientation chest{s.view.yaw+pose.body.chestYaw,pose.body.chestPitch};
    const Vec shoulder=pose.arms[side].shoulder;
    const Vec clavicle=shoulder-s.bodyFrame().vector(chest.world({0,sign*RigClavicleLength,0}));
    return solveRigArm(rigArmInput(shoulder,clavicle,pose.arms[side].hand,pose.axis,
        presentation::elbowRail(s,pose.body,side,fp),side));
}
void advancePresentationFor(Combatant& s,double seconds,const Tuning& t)
{
    while(seconds>1e-12){const double dt=std::min(seconds,1./240.);s.advance(dt,t);seconds-=dt;}
}
void presentationTransition(const Combatant& before,const Combatant& after,const Tuning& t)
{
    Combatant epsilon=after;epsilon.advance(1e-8,t);
    require((after.weapon.hilt-before.weapon.hilt).length()<.001&&
        (after.weapon.tip-before.weapon.tip).length()<.001,
        "Controlled transition preserves the contact-time weapon");
    for(int side=0;side<2;++side)for(bool fp:{false,true}){
        const auto a=presentedRigArm(before,t,side,fp);
        for(const auto* state:std::array<const Combatant*,2>{&after,&epsilon}){
            const auto b=presentedRigArm(*state,t,side,fp);
            require((b.arm.elbow-a.arm.elbow).length()<.001,
                "Stops, combos and changed-origin ripostes preserve the actual elbow at the boundary");
            require(angle(a.handRadial,b.handRadial)<.01,
                "Stops, combos and changed-origin ripostes preserve the actual glove at the boundary");
            require((b.arm.hand-a.arm.hand).length()<.001,
                "Transition cannot move the rigid wrist away from its captured grip contact");
        }
    }
}
void contactAndLoadedPoseContracts()
{
    Tuning t;int contacts=0;
    // Controlled collision traces isolate real resolver transitions from
    // target placement. Before/after samples have the same weapon contact.
    for(double origin:{0.,60.,90.,120.,180.,-60.,-120.})for(double pitch:{-85.,0.,85.})
        for(double p:{.1,.3,.6,.9})for(bool riposte:{false,true})
            for(Resolution result:{Resolution::Hit,Resolution::Parry,Resolution::Wall}){
                CombatSimulation sim;Combatant a,d;a.id=1;d.id=2;
                a.reset({0,0,88},{0,pitch},t);d.reset({135,0,88},{180,0},t);
                if(riposte)a.state.parrySuccess(t);
                require(a.start({AttackKind::Strike,origin,origin},t),"Controlled strike starts");
                advancePresentationFor(a,a.state.definition.windup+t.StrikeRelease*p,t);
                const Combatant before=a;
                if(result==Resolution::Parry){
                    require(d.parry(t),"Controlled defender enters parry");d.advance(.02,t);
                    a.traces={{d.defense.center-Vec{0,2,0},d.defense.center+Vec{0,2,0}}};
                }else a.traces={{d.position-Vec{0,2,0},d.position+Vec{0,2,0}}};
                if(result==Resolution::Wall){
                    sim.actors={&a};sim.worldSweep=[&](int,Segment,double,Vec& point,Vec& normal){point=a.weapon.tip;normal={-1,0,0};return true;};
                }else sim.actors={&a,&d};
                sim.resolve();
                require(sim.events.size()==1&&sim.events[0].result==result,"Controlled contact reaches the expected resolver branch");
                presentationTransition(before,a,t);++contacts;
                if(result==Resolution::Parry){
                    const Combatant defended=d;
                    require(d.start({AttackKind::Strike,origin,origin},t)&&d.state.isRiposte,"Real parry success permits immediate riposte");
                    presentationTransition(defended,d,t);
                }
            }
    for(double origin:{0.,60.,90.,120.,180.,-60.,-120.})for(double pitch:{-85.,0.,85.}){
        Combatant a;a.reset({0,0,88},{0,pitch},t);a.start({AttackKind::Strike,origin,origin},t);
        advancePresentationFor(a,t.StrikeWindup+t.StrikeRelease*.7,t);
        require(a.start({AttackKind::Strike,origin,origin},t)&&a.state.comboQueued,"Presentation combo fixture queues a real combo");
        advancePresentationFor(a,t.StrikeRelease*.3-1e-8,t);const Combatant before=a;
        a.advance(2e-8,t);require(a.state.isCombo,"Fixture straddles the queued combo boundary");
        presentationTransition(before,a,t);
    }
    // A loaded defender must carry the exact high guard through FTP and
    // parry success when the riposte selects a different origin. This detects
    // a hidden live-angle dependency that neutral-guard fixtures miss.
    for(double origin:{60.,90.,120.})for(double next:{0.,60.,90.,120.,180.})for(double pitch:{-85.,0.,85.}){
        Combatant d,a;d.id=2;a.id=1;d.reset({0,0,88},{0,pitch},t);a.reset({135,0,88},{180,0},t);
        d.start({AttackKind::Strike,origin,origin},t);advancePresentationFor(d,t.StrikeWindup*.65,t);
        const Combatant loaded=d;require(d.parry(t),"Loaded guard can feint to parry");presentationTransition(loaded,d,t);
        d.advance(1e-5,t);
        a.start({AttackKind::Strike,0,0},t);advancePresentationFor(a,t.StrikeWindup+t.StrikeRelease*.3,t);
        a.traces={{d.defense.center-Vec{0,2,0},d.defense.center+Vec{0,2,0}}};
        CombatSimulation sim;sim.actors={&a,&d};const Combatant defending=d;sim.resolve();
        require(sim.events.size()==1&&sim.events[0].result==Resolution::Parry,"Loaded defender resolves a real successful parry");
        presentationTransition(defending,d,t);const Combatant success=d;
        require(d.start({AttackKind::Strike,next,next},t)&&d.state.isRiposte,"Loaded defender starts a changed-origin riposte");
        presentationTransition(success,d,t);
    }
    double minDepth=1e30,maxLoadedWrist=0;
    for(double origin:{60.,90.,120.}){
        Combatant s;s.reset({0,0,88},{0,85},t);s.start({AttackKind::Strike,origin,origin},t);
        for(int frame=0;frame<138;++frame){
            s.advance(1./240.,t);if(s.state.phase!=Phase::Windup)continue;
            const auto p=presentation::evaluate(s,t);
            for(int side=0;side<2;++side){
                const double depth=s.view.local(p.arms[side].hand-s.eye()).x;minDepth=std::min(minDepth,depth);
                require(depth>12.,"High-aim loaded hands retain camera clearance instead of crowding the near plane");
                const auto arm=presentedRigArm(s,t,side,true);maxLoadedWrist=std::max(maxLoadedWrist,arm.wristBend);
                require(arm.arm.reachScale<1.000001,"The clear high guard fits the imported arm lengths");
            }
        }
    }
    std::cout<<"Actual rig transitions: "<<contacts<<" controlled contacts, changed-origin loaded ripostes and queued combos continuous; "
        <<"high-aim windup minimum contact depth "<<minDepth<<" cm, max wrist "<<maxLoadedWrist<<" deg (reported, not a visual limit).\n";
}
void wristPoleContracts()
{
    const Vec shoulder{},wrist{30,0,0},rail{0,0,-1};
    Vec previous;
    for(int i=0;i<=720;++i){
        const double a=i*Pi/360.;
        const Vec direction{std::cos(a),std::sin(a),0};
        const Vec pole=presentation::assistArmPlane(shoulder,wrist,direction,rail);
        require(std::abs(pole.length()-1.)<1e-7&&angle(pole,rail)<=20.0001,
            "A hand swivel cannot invert the authored humeral plane");
        if(i)require(previous.dot(pole)>.999,"Elbow assist remains continuous across opposite and parallel wrist directions");
        previous=pole;
    }
    for(double reach:{.001,1.,30.,54.}){
        const auto arm=presentation::solveArm({},Vec{reach,0,0},rail);
        require(std::isfinite(arm.elbow.z)&&arm.elbow.z<=0,"Near extension retains the authored elbow hemisphere");
    }
}
void motionContracts()
{
    Tuning t;
    for(double strength:{0.,.45,.85,1.}){
        t.StrikeReleaseAcceleration=strength;
        double previous=0;
        for(int i=1;i<=1000;++i){
            const double q=AttackTrajectory::releaseMap(i/1000.,t);
            require(q>previous&&q<=1.,"Release must remain monotonic without a plateau");previous=q;
        }
        require((1.-AttackTrajectory::releaseMap(.99999,t))/.00001>.8,"Release carries speed through final damaging frames");
        require(std::abs(AttackTrajectory::releaseMap(.37,t,true)-.37)<1e-9,"Riposte spatial progression is linear");
    }
    t=Tuning{};
    for(double p:{.3,.5,.7}){
        Combatant visible;visible.reset({0,0,88},{},t);visible.start({},t);
        visible.advance(t.StrikeWindup+t.StrikeRelease*p,t);
        for(const auto& arm:presentation::evaluate(visible,t).arms){
            const Vec camera=visible.view.local(arm.hand-visible.eye());
            const double screenY=.5-.5*camera.z/(camera.x*std::tan(t.FOV*Rad*.5)/(16./9.));
            // Composition is reviewed in rendered sequences. Requiring both
            // contacts above screenY .95 encouraged the rejected high folded
            // carriage instead of an outward, lower delivered cut.
            require(camera.x>0&&std::isfinite(screenY),"Horizontal delivery contacts remain forward and project finitely");
            std::cout<<"Horizontal delivery p="<<p<<" contact screenY="<<screenY<<"\n";
        }
    }
    require(AttackTrajectory::releaseMap(.5,t)<.5,"Regular release is modestly back-loaded");
    double peak=0,peakAt=0;
    for(int i=1;i<1000;++i){
        const double p=i/1000.;
        const double v=AttackTrajectory::releaseMap(p+.001,t)-AttackTrajectory::releaseMap(p-.001,t);
        if(v>peak){peak=v;peakAt=p;}
    }
    require(peakAt>.5&&peakAt<.7,"Peak speed occurs through the middle/later contact sector");
    for(bool riposte:{false,true})for(double origin:{0.,60.,120.,180.,-120.,-60.}){
        AttackIntent a{AttackKind::Strike,origin,origin};
        const double w=riposte?t.RiposteWindup:t.StrikeWindup,dt=.00001;
        const auto before=AttackTrajectory::windup(a,1.-dt/w,AttackTrajectory::rest(),t,false,riposte);
        const auto boundary=AttackTrajectory::riposteRelease(a,0,riposte,t);
        const auto after=AttackTrajectory::riposteRelease(a,dt/t.StrikeRelease,riposte,t);
        require(((boundary.hilt-before.hilt)/dt-(after.hilt-boundary.hilt)/dt).length()<.1,"Windup/release hilt velocity is continuous");
        require(((boundary.direction-before.direction)/dt-(after.direction-boundary.direction)/dt).length()<.01,"Windup/release angular tangent is continuous");
    }
    for(double origin:{0.,60.,120.,180.,-120.,-60.}){
        double previous=0;
        for(int i=0;i<=100;++i){
            auto pose=AttackTrajectory::release({AttackKind::Stab,origin,origin},i/100.,t);
            require(pose.hilt.x>=previous,"Damaging stab must not retract");previous=pose.hilt.x;
        }
    }
    double maxReach=0,maxStep=0;
    for(double origin:{0.,60.,120.,180.,-120.,-60.})for(double next:{0.,60.,120.,180.,-120.,-60.})
        for(double pitch:{-85.,-45.,0.,45.,85.})for(AttackKind kind:{AttackKind::Strike,AttackKind::Stab}){
            CombatSimulation sim;Combatant s;s.reset({0,0,88},{0,pitch},t);sim.actors={&s};s.start({kind,origin,origin},t);
            bool queued=false;
            for(int i=0;i<720;++i){
                if(!queued&&s.state.canCombo(t)){s.start({kind,next,next},t);queued=true;}
                const Vec before=s.weapon.hilt;sim.advance(1./240.);
                const auto pose=presentation::evaluate(s,t);
                if(pitch==0&&s.state.phase==Phase::Release)
                    require(std::min(s.weapon.hilt.z,s.weapon.tip.z)>t.BladeRadius,
                        "Standing neutral cuts must clear the floor throughout release");
                for(const auto& arm:pose.arms){maxReach=std::max(maxReach,arm.reachScale);require(arm.reachScale<1.001,"Shared reach envelope prevents stretched adapter arms");}
                const double step=(s.weapon.hilt-before).length();maxStep=std::max(maxStep,step);
                require(step<5.,"Combo and family transitions cannot teleport the hilt");
            }
        }
    std::cout<<"Motion envelope: max adapter reach "<<maxReach<<", max hilt step "<<maxStep<<" cm at 240 Hz\n";
    // Rate-limited guard and its rendered sword must face together after settling.
    Combatant guard;guard.reset({0,0,88},{},t);guard.parry(t);guard.look(70,40,.1,t);
    for(int i=0;i<20;++i)guard.advance(1./240.,t);
    const Vec intended=guard.guard.world(AttackTrajectory::evaluate(guard.state,guard.windupStart,t).direction);
    require(angle(guard.weapon.tip-guard.weapon.hilt,intended)<.001,"Defensive sword follows authoritative guard, not unrestricted view");
    // Body carries into cancellation rather than snapping to neutral.
    Combatant feint;feint.reset({0,0,88},{},t);feint.start({},t);feint.advance(.3,t);
    const double yaw=feint.bodyMotion.chestYaw;feint.feint(t);feint.advance(1./240.,t);
    require(std::abs(feint.bodyMotion.chestYaw-yaw)<.1,"Feint preserves loaded body pose");
}
void verify(const Combatant& s,const Tuning& t)
{
    const auto p=presentation::evaluate(s,t);
    require(close(p.blade.hilt,s.weapon.hilt)&&close(p.blade.tip,s.weapon.tip),"Blade must equal simulation in every phase");
    require(std::abs(p.axis.dot(p.edge))<1e-7&&std::abs(p.normal.length()-1.)<1e-7,"Sword frame must be orthonormal");
    for(int i=0;i<2;++i){
        const auto& arm=p.arms[i];
        const double depth=(s.weapon.hilt-arm.hand).dot(p.axis)/t.BladeLength;
        require(depth>(i==0?.10:.20)&&depth<(i==0?.12:.22),"Palm must lie on the calibrated leather grip behind the guard");
        require((s.weapon.hilt-arm.hand).cross(p.axis).length()<1e-7,"Palm contact must stay on the hilt axis");
        require(std::isfinite(arm.elbow.x)&&std::isfinite(arm.elbow.y)&&std::isfinite(arm.elbow.z),"Finite IK at extreme pitch");
        require(std::abs((arm.elbow-arm.shoulder).length()-presentation::UpperArmLength*arm.reachScale)<1e-6,"Upper arm length must match reported reach");
        require(std::abs((arm.elbow-arm.hand).length()-presentation::ForearmLength*arm.reachScale)<1e-6,"Forearm length must match reported reach");
    }
}
int main()
{
    try{
        wristPoleContracts();
        actualGripSolverContracts();
        contactAndLoadedPoseContracts();
        motionContracts();
        Tuning t;
        for(double origin:{0.,60.,120.,180.,-120.,-60.})for(AttackKind kind:{AttackKind::Strike,AttackKind::Stab}){
            const AttackIntent intent{kind,origin,origin};
            const auto loaded=AttackTrajectory::windup(intent,1.,AttackTrajectory::rest(),t,false,true);
            const auto start=AttackTrajectory::riposteRelease(intent,0.,true,t);
            const auto end=AttackTrajectory::riposteRelease(intent,1.,true,t);
            const auto settle=AttackTrajectory::recovery(intent,0.,t,Resolution::Miss,true);
            require(close(loaded.hilt,start.hilt)&&close(loaded.direction,start.direction),"Riposte windup must meet raised release without a hilt teleport");
            require(close(end.hilt,settle.hilt)&&close(end.direction,settle.direction),"Riposte recovery must start at the actual raised release end");
        }
        for(int fps:{30,60,144,240})for(double pitch:{-85.,0.,85.})
            for(double origin:{0.,60.,120.,180.,-120.,-60.})for(AttackKind kind:{AttackKind::Strike,AttackKind::Stab}){
                Combatant s;s.reset({130,-47,88},{37,pitch},t);s.start({kind,origin,origin},t);
                for(int frame=0;frame<fps*3;++frame){s.advance(1./fps,t);verify(s,t);}
            }
        for(Phase phase:{Phase::Idle,Phase::Parry,Phase::ParryRecovery,Phase::Flinch,Phase::Dead}){
            Combatant s;s.reset({0,0,88},{},t);s.state.phase=phase;verify(s,t);
        }
        // Eyes and shoulders share a rigid hip arc; lower-body roots stay fixed.
        Combatant a,b;a.reset({0,0,88},{20,-85},t);b.reset({0,0,88},{20,85},t);
        require(close(a.bodyFrame().hip,b.bodyFrame().hip),"Looking up/down keeps the hip pivot fixed");
        require(close(a.bodyFrame().untransform(presentation::evaluate(a,t).arms[0].shoulder),
            b.bodyFrame().untransform(presentation::evaluate(b,t).arms[0].shoulder)),"Shoulders follow the same rigid hip arc as the eye");
        require((a.eye()-b.eye()).length()>100.,"Extreme views produce a real torso dodge");
        // Long reach and a pole parallel to the arm must not collapse or NaN.
        auto far=presentation::solveArm({0,0,0},{150,0,0},{1,0,0});
        require(close(far.hand,{150,0,0})&&far.reachScale>1.&&std::isfinite(far.elbow.z),"Unreachable hand uses explicit cosmetic stretch");
        auto folded=presentation::solveArm({0,0,0},{0,0,0},{1,0,0});
        require(std::isfinite(folded.elbow.x),"Coincident targets remain finite");
        // Sword frame must remain continuous through vertical/lateral directions.
        Vec previous;
        for(int i=0;i<=720;++i){
            Combatant s;s.reset({0,0,88},{},t);
            const double theta=(-112.+212.*i/720.)*Rad;
            s.weapon.tip=s.weapon.hilt+Vec{std::cos(theta),std::sin(theta),0}*t.BladeLength;
            s.weapon.edge={}; // Manual shaft mutation intentionally exercises legacy frame fallback.
            auto frame=presentation::evaluate(s,t);
            if(i)require(previous.dot(frame.edge)>.99,"Edge must not flip during broad cuts");
            previous=frame.edge;
        }
        std::cout<<"PASS: "<<checks<<" presentation checks\n";return 0;
    }catch(const std::exception& e){std::cerr<<"FAIL: "<<e.what()<<'\n';return 1;}
}
