#include "CombatSimulation.h"
#include "Attacks/EXSourceClock.h"
namespace mcl
{
bool Combatant::start(AttackIntent intent,const Tuning& t)
{
    auto phase=state.phase;auto serial=state.serial;
    bool ok=state.start(intent,t);
    if(ok&&(serial!=state.serial||(phase==Phase::Windup&&state.last==Resolution::Morph))){windupStart=local;windupVelocity=localVelocity;bodyStart=bodyMotion;}
    syncEXTransition();return ok;
}
void Combatant::flinch()
{
    state.flinch();
    if(state.phase==Phase::Flinch){returnStart=local;returnAge=0;bodyStart=bodyMotion;}
    syncEXTransition();
}
bool Combatant::feint(const Tuning& t)
{
    if(!state.feint(t))return false;
    returnStart=local;returnAge=0;bodyStart=bodyMotion;syncEXTransition();return true;
}
bool Combatant::parry(const Tuning& t)
{
    if(!state.parry(t))return false;
    guard=view;returnStart=local;returnAge=0;bodyStart=bodyMotion;syncEXTransition();return true;
}
void Combatant::look(double yawDelta,double pitchDelta,double dt,const Tuning& t)
{
    double yaw=clamp(yawDelta,-state.yawCap(t)*dt,state.yawCap(t)*dt);
    double pitchCap=state.phase==Phase::Release?t.PitchCap*(state.isRiposte?t.RiposteTurnScale:1.):100000.;
    double pitch=clamp(pitchDelta,-pitchCap*dt,pitchCap*dt);
    if(state.phase==Phase::Release)state.releaseRotation+=std::hypot(yaw,pitch);
    view={wrap(view.yaw+yaw),clamp(view.pitch+pitch,-85.,85.)};desired=view;
}
void Combatant::reset(Vec at,Orientation facing,const Tuning& t)
{
    bool infinite=state.infiniteStamina;state=AttackStateMachine{};state.infiniteStamina=infinite;
    state.exEnabled=bool(exMotion);
    position=frameStart=frameTarget=at;view=desired=guard=simulatedView=frameViewStart=frameViewTarget=facing;
    health=100;damageTaken=0;hitsTaken=0;hitActors.clear();trackedSerial=0;
    local=windupStart=returnStart=AttackTrajectory::rest();returnAge=1;
    localVelocity=windupVelocity={{},{}};
    bodyMotion=bodyStart={};tipVelocity=tipAcceleration={};reachCorrection=0;
    sampledPosition=position;sampledView=view;motion={};lungeVelocity=inheritedVelocity={};lungeDisplacement=0;
    contactAge=1;contactStrength=0;contactNormal={};contactKind=Resolution::None;
    torsoPitchScale=t.TorsoPitchScale;leanFraction=1.;
    desiredHilt=AttackTrajectory::desiredWorld(local,uprightEye(),view,t,view,leanFraction).hilt;
    weapon=previousWeapon=AttackTrajectory::world(local,uprightEye(),view,t,bodyMotion,view,leanFraction);
    defense=ParryGeometry::make(guardAnchor(),guard,t);
    if(exMotion){exSourceTime=EXWeaponMotion::Start;exPhase=Phase::Idle;exSerial=0;exTransitionAge=1;
        weapon=previousWeapon=exWorld(exMotion->sample(exSourceTime));exFrom=cameraPose(weapon);exSampleEye=eye();exSampleView=view;}
}
void Combatant::syncEXTransition()
{
    if(!exMotion||(exPhase==state.phase&&exSerial==state.serial))return;
    exFrom={exSampleView.local(weapon.hilt-exSampleEye),exSampleView.local(weapon.tip-exSampleEye),exSampleView.local(weapon.edge)};
    exTransitionAge=0;exPhase=state.phase;exSerial=state.serial;
    auto ready=exMotion->sample(EXWeaponMotion::Start);ready.hilt=ready.hilt-Vec{11.5,0,168};ready.tip=ready.tip-Vec{11.5,0,168};
    exEntryBridge=(ready.hilt-exFrom.hilt).length()>.001||(ready.tip-exFrom.tip).length()>.001||
        (ready.edge-exFrom.edge).length()>.001;
}
void Combatant::finishBoundary(const Tuning& t)
{
    const auto phase=state.phase;const auto serial=state.serial;
    state.advance(0,t);
    if(state.serial!=serial){windupStart=local;windupVelocity=localVelocity;bodyStart=bodyMotion;}
    if(state.phase!=phase&&(state.phase==Phase::Idle||state.phase==Phase::ParryRecovery)){
        returnStart=local;returnAge=0;bodyStart=bodyMotion;
    }
    syncEXTransition();
}
void Combatant::advanceEX(double dt,const Tuning& t)
{
    const bool action=state.exActive&&(state.phase==Phase::Windup||state.phase==Phase::Release||
        (state.phase==Phase::Recovery&&state.last!=Resolution::Wall&&state.last!=Resolution::Parry));
    exSourceTime=action?EXSourceClock::time(state,state.attackAge):EXWeaponMotion::Start;
    Pose target=cameraPose(exWorld(exMotion->sample(exSourceTime)));
    // Release uses the chosen fixed phase duration; entry/return offsets are cosmetic.
    const double blendAge=action?state.elapsed:exTransitionAge;
    const double w=action?(state.phase==Phase::Windup&&exEntryBridge?smooth(blendAge/.10):1.):smooth(blendAge/.18);
    if(w<1.){
        const double length=mix((exFrom.tip-exFrom.hilt).length(),(target.tip-target.hilt).length(),w);
        const Vec axis=slerp(exFrom.tip-exFrom.hilt,target.tip-target.hilt,w);
        target.hilt=lerp(exFrom.hilt,target.hilt,w);
        target.tip=target.hilt+axis*length;
        target.edge=lerp(exFrom.edge,target.edge,w).normal();
        target.edge=(target.edge-axis*target.edge.dot(axis)).normal();
    }
    weapon={eye()+view.world(target.hilt),eye()+view.world(target.tip),view.world(target.edge)};
    local={view.local(weapon.hilt-weaponOrigin()),view.local(weapon.tip-weapon.hilt).normal()};
    desiredHilt=weapon.hilt;reachCorrection=0;bodyMotion={};
    const Vec velocity=(weapon.tip-previousWeapon.tip)/dt;
    tipAcceleration=(velocity-tipVelocity)/dt;tipVelocity=velocity;speed=velocity.length();
    angularSpeed=angle(weapon.tip-weapon.hilt,previousWeapon.tip-previousWeapon.hilt)/dt;
    motion.p=state.progress();motion.q=motion.p;motion.tipVelocity=velocity;
    motion.hiltVelocity=(weapon.hilt-previousWeapon.hilt)/dt;
    sampledPosition=position;sampledView=view;
    if(action&&state.phase==Phase::Release){
        // Subdivide on the same native quaternion curve used by presentation,
        // not a second SLERP arc between sampled blade directions.
        traces.clear();Pose from=previousWeapon;
        const int count=WeaponTraceSystem::subdivisions(dt,previousWeapon,weapon);
        for(int i=1;i<=count;++i){
            const double alpha=double(i)/count;
            const Orientation aim{wrap(exSampleView.yaw+wrap(view.yaw-exSampleView.yaw)*alpha),mix(exSampleView.pitch,view.pitch,alpha)};
            const Vec pivot=lerp(exSampleEye,eye(),alpha);
            const auto localSample=exMotion->sample(EXSourceClock::time(state,state.attackAge-dt+dt*alpha));
            Pose to{pivot+aim.world(localSample.hilt-Vec{11.5,0,168}),pivot+aim.world(localSample.tip-Vec{11.5,0,168}),aim.world(localSample.edge)};
            if(i==count)to=weapon;
            const auto spans=WeaponTraceSystem::sweeps(from,to,t);traces.insert(traces.end(),spans.begin(),spans.end());from=to;
        }
    }else traces=WeaponTraceSystem::adaptiveSweeps(dt,previousWeapon,weapon,t);
    if(exMotion){exSampleEye=eye();exSampleView=view;}
}
void Combatant::advance(double dt,const Tuning& t,bool deferTransitions)
{
    if(dt<=0)return;
    torsoPitchScale=t.TorsoPitchScale;
    contactAge+=dt;
    auto oldPhase=state.phase;auto oldSerial=state.serial;LocalPose before=local;
    previousWeapon=weapon;state.advance(dt,t,deferTransitions);
    syncEXTransition();exTransitionAge+=dt;
    if(state.serial!=oldSerial){windupStart=before;windupVelocity=localVelocity;bodyStart=bodyMotion;}
    if(state.serial!=trackedSerial){trackedSerial=state.serial;hitActors.clear();}
    if(state.phase==Phase::Parry)guard=approach(guard,desired,t.ParryYawRate,t.ParryPitchRate,dt);else guard=view;
    // Preserve the rate-limited guard orientation and its existing shape;
    // translate its anchor by the shared eye's hip-arc displacement.
    defense=ParryGeometry::make(guardAnchor(),guard,t);

    if(state.phase==Phase::Idle&&oldPhase!=Phase::Idle){returnStart=before;returnAge=0;bodyStart=bodyMotion;}
    if(state.phase==Phase::ParryRecovery&&oldPhase==Phase::Parry){returnStart=before;returnAge=0;bodyStart=bodyMotion;}
    returnAge+=dt;

    if(exMotion&&(state.exActive||state.phase==Phase::Idle||state.phase==Phase::Flinch||state.phase==Phase::ParryRecovery||state.phase==Phase::Dead)
        &&state.phase!=Phase::Parry){advanceEX(dt,t);return;}

    if(state.phase==Phase::Idle){
        const double duration=state.last==Resolution::Feint?t.FeintReturnDuration:
            state.last==Resolution::Chamber?.18:.12;
        if(state.last==Resolution::Chamber)local=AttackTrajectory::opposition(returnStart,returnAge/duration,state.last);
        else if(state.last==Resolution::Parry)
            local=blend(returnStart,AttackTrajectory::rest(),smooth((returnAge-.06)/.16));
        else local=blend(returnStart,AttackTrajectory::rest(),smooth(returnAge/duration));
    }
    else if(state.phase==Phase::Flinch){
        local=blend(returnStart,AttackTrajectory::rest(),smooth(state.elapsed/std::max(.001,t.FlinchDuration)));
    }
    else if(state.phase==Phase::Parry){
        local=blend(returnStart,evaluateWeapon(state,t),smooth(state.elapsed/.055));
    }
    else if(state.phase==Phase::ParryRecovery){
        local=blend(returnStart,AttackTrajectory::rest(),smooth(state.elapsed/std::max(.001,t.ParryRecovery)));
    }
    else if(state.phase==Phase::Recovery){
        const bool interrupted=state.last==Resolution::Parry||state.last==Resolution::Wall;
        if(interrupted){
            if(oldPhase==Phase::Release){returnStart=before;local=before;}
            else local=AttackTrajectory::opposition(returnStart,state.progress(),state.last,view.local(contactNormal));
        }
        else local=evaluateWeapon(state,t);
    }
    else if(state.phase==Phase::Release&&contactKind==Resolution::Hit&&contactAge<.065){
        auto response=state;
        // A short spatial deceleration pulse. The attack clock, damage window,
        // input rotation and renderer remain authoritative and undelayed.
        const double pulse=std::sin(Pi*contactAge/.065);
        response.elapsed=std::max(0.,state.elapsed-state.definition.release*.012*pulse*pulse);
        local=evaluateWeapon(response,t);
    }
    else local=evaluateWeapon(state,t);

    const BodyMotion authoredBody=AttackTrajectory::body(state,t);
    BodyMotion target=authoredBody;
    if(state.phase==Phase::Windup){
        auto loaded=state;loaded.phase=Phase::Release;loaded.elapsed=0;
        const auto end=AttackTrajectory::body(loaded,t);
        loaded.elapsed=.0001;
        target=bodyTransfer(bodyStart,end,end,AttackTrajectory::body(loaded,t),
            state.definition.windup/.0001,state.progress(),true);
    }else if(state.phase==Phase::Idle||state.phase==Phase::Flinch||state.phase==Phase::ParryRecovery){
        const double duration=state.phase==Phase::Flinch?t.FlinchDuration:
            state.phase==Phase::ParryRecovery?t.ParryRecovery:t.FeintReturnDuration;
        target=blend(bodyStart,BodyMotion{},smooth(returnAge/std::max(.001,duration)));
    }else if(state.phase==Phase::Parry){
        BodyMotion brace;brace.chestPitch=-7.;brace.chestYaw=-6.;brace.forwardLean=-2.5;
        brace.rightElbowLift=4.;brace.leftElbowLift=6.;
        target=blend(bodyStart,brace,smooth(state.elapsed/.055));
    }else if(state.phase==Phase::Recovery&&(state.last==Resolution::Parry||state.last==Resolution::Wall)){
        target=blend(bodyStart,BodyMotion{},smooth(state.progress()));
    }else if(state.phase==Phase::Recovery){
        auto exit=state;exit.phase=Phase::Release;exit.elapsed=exit.definition.release;
        const auto end=AttackTrajectory::body(exit,t);exit.elapsed-=.0001;
        target=bodyTransfer(end,{},AttackTrajectory::body(exit,t),end,
            state.definition.recovery/.0001,state.progress(),false);
        // A completed cut retains its low carry before the guard return.
        // Interrupted recoveries use bodyStart above instead, so they never
        // acquire a completed-cut arm pose merely by resetting the phase.
        target.elbowCarry=authoredBody.elbowCarry;
        target.rightForearmCarry=authoredBody.rightForearmCarry;
        target.leftForearmCarry=authoredBody.leftForearmCarry;
        target.rightHighGuardWeight=authoredBody.rightHighGuardWeight;
        target.leftHighGuardWeight=authoredBody.leftHighGuardWeight;
        target.rightHighGuardRail=authoredBody.rightHighGuardRail;
        target.leftHighGuardRail=authoredBody.leftHighGuardRail;
    }
    if(contactAge<.18){
        const double pulse=std::sin(Pi*contactAge/.18)*std::exp(-contactAge*9.)*contactStrength;
        const Vec recoil=view.local(contactNormal);
        target.chestYaw+=recoil.y*7.*pulse;target.chestPitch-=recoil.x*5.*pulse;
        target.forwardLean+=recoil.x*2.*pulse;
        target.rightShoulderX+=recoil.x*2.*pulse;target.leftShoulderX+=recoil.x*2.*pulse;
        target.rightElbowLift+=pulse*3.;target.leftElbowLift+=pulse*3.;
    }
    bodyMotion=target;
    const Orientation weaponView=state.phase==Phase::Parry?guard:view;
    desiredHilt=AttackTrajectory::desiredWorld(local,uprightEye(),weaponView,t,view,leanFraction).hilt;
    weapon=AttackTrajectory::world(local,uprightEye(),weaponView,t,bodyMotion,view,leanFraction);
    reachCorrection=(weapon.hilt-(weaponOrigin()+weaponView.world(local.hilt))).length();
    // Keep transition capture in current camera coordinates, including any
    // authoritative reach correction and rate-limited defensive orientation.
    local={view.local(weapon.hilt-weaponOrigin()),view.local(weapon.tip-weapon.hilt).normal()};
    localVelocity={(local.hilt-before.hilt)/dt,(local.direction-before.direction)/dt};
    const Vec velocity=(weapon.tip-previousWeapon.tip)/dt;
    // Exact ordered finite-difference decomposition, including reach correction:
    // intrinsic/body, then yaw, pitch and translation. Contributions sum to tip velocity.
    const Vec oldEye=sampledPosition+Vec{0,0,eyeHeight};
    const auto intrinsic=AttackTrajectory::world(local,oldEye,sampledView,t,bodyMotion,sampledView,leanFraction);
    const Orientation yawOnly{weaponView.yaw,sampledView.pitch};
    const auto yawPose=AttackTrajectory::world(local,oldEye,yawOnly,t,bodyMotion,yawOnly,leanFraction);
    const auto pitchPose=AttackTrajectory::world(local,oldEye,weaponView,t,bodyMotion,view,leanFraction);
    motion.p=state.progress();motion.q=state.phase==Phase::Release?AttackTrajectory::releaseMap(motion.p,t,state.isRiposte):0;
    motion.intrinsicAngularSpeed=angle(before.direction,local.direction)/dt;
    motion.localTipVelocity=(local.hilt+local.direction*t.BladeLength-before.hilt-before.direction*t.BladeLength)/dt;
    motion.intrinsicTipVelocity=(intrinsic.tip-previousWeapon.tip)/dt;
    motion.yawTipVelocity=(yawPose.tip-intrinsic.tip)/dt;
    motion.pitchTipVelocity=(pitchPose.tip-yawPose.tip)/dt;
    motion.translationVelocity=(weapon.tip-pitchPose.tip)/dt;
    motion.yawRate=wrap(view.yaw-sampledView.yaw)/dt;motion.pitchRate=(view.pitch-sampledView.pitch)/dt;
    motion.yawUtilization=std::abs(motion.yawRate)/std::max(1.,state.yawCap(t));
    motion.pitchUtilization=std::abs(motion.pitchRate)/std::max(1.,t.PitchCap*(state.isRiposte?t.RiposteTurnScale:1.));
    motion.hiltVelocity=(weapon.hilt-previousWeapon.hilt)/dt;motion.tipVelocity=velocity;
    sampledPosition=position;sampledView=view;
    tipAcceleration=(velocity-tipVelocity)/dt;tipVelocity=velocity;
    speed=(weapon.tip-previousWeapon.tip).length()/dt;
    angularSpeed=angle(weapon.tip-weapon.hilt,previousWeapon.tip-previousWeapon.hilt)/dt;
    traces=WeaponTraceSystem::adaptiveSweeps(dt,previousWeapon,weapon,t);
    if(exMotion){exSampleEye=eye();exSampleView=view;}
}
void CombatSimulation::emit(Resolution r,Combatant& attacker,Combatant* defender,Vec point,Vec normal)
{
    const double strength=r==Resolution::Chamber?1.3:r==Resolution::Parry?1.1:r==Resolution::Wall?1.:.55;
    attacker.contactNormal=normal;attacker.contactAge=0;attacker.contactStrength=strength;attacker.contactKind=r;
    if(defender){defender->contactNormal=normal*-1.;defender->contactAge=0;defender->contactStrength=strength;defender->contactKind=r;}
    attacker.state.last=r;events.push_back({r,attacker.id,defender?defender->id:-1,point,time,
        attacker.tipVelocity,clamp(attacker.speed/1800.,0.,1.),normal,
        defender?defender->region(r,point):ContactRegion::None});
}
void CombatSimulation::resolve(bool interval)
{
    struct Contact{int priority;Combatant* a;Combatant* d;Vec point;double distance;Vec normal;};
    std::vector<Contact> contacts;

    for(auto* a:actors){
        if(a->state.phase!=Phase::Release||(interval&&!a->intervalRelease))continue;
        for(auto* d:actors){
            if(a==d||d->health<=0||a->hitActors.count(d->id))continue;
            bool body=false,parry=false;Vec point=d->position;
            for(auto sweep:a->traces){++queriesLastFrame;
                for(const auto axis:d->hurtAxes())if(segmentDistance(sweep,axis)<=d->bodyRadius+tuning.BladeRadius){
                    body=true;point=capsuleContactPoint(sweep,axis,d->bodyRadius+tuning.BladeRadius);}
                if(d->state.phase==Phase::Parry&&d->defense.catches(sweep,tuning.BladeRadius)){parry=true;point=sweep.b;}
            }
            auto incoming=ChamberSystem::inDefenderView(a->state.attack,a->view,d->view);
            d->incomingAngle=incoming.angle;d->chamberDifference=ChamberSystem::difference(incoming,d->state.attack);
            bool front=angle(d->view.forward(),a->position-d->position)<tuning.ChamberFacingAngle;
            bool chamber=body&&(interval?a->intervalDamage:a->state.damaging())&&front&&ChamberSystem::matches(d->state,incoming,tuning);

            const Vec axisPoint=d->nearestHurtPoint(point);
            const Vec normal=(point-axisPoint).normal();
            if(chamber)contacts.push_back({0,a,d,point,(point-a->weapon.hilt).length(),d->view.forward()});
            if(parry)contacts.push_back({1,a,d,point,(point-a->weapon.hilt).length(),d->guard.forward()});
            if(body&&(interval?a->intervalDamage:a->state.damaging())&&
                a->state.releaseRotation<=tuning.AntiSpinThreshold*(a->state.isRiposte?tuning.RiposteTurnScale:1.))
                contacts.push_back({3,a,d,point,(point-a->weapon.hilt).length(),normal});
        }
        if(worldSweep){
            for(auto sweep:a->traces){
                Vec point,normal;++queriesLastFrame;
                if(worldSweep(a->id,sweep,tuning.BladeRadius,point,normal)){
                    contacts.push_back({2,a,nullptr,point,(point-a->weapon.hilt).length(),normal});break;
                }
            }
        }
    }

    std::sort(contacts.begin(),contacts.end(),[](const Contact& a,const Contact& b){
        if(a.priority!=b.priority)return a.priority<b.priority;
        if(a.distance!=b.distance)return a.distance<b.distance;
        if(a.a->id!=b.a->id)return a.a->id<b.a->id;
        return (a.d?a.d->id:-1)<(b.d?b.d->id:-1);
    });

    for(auto c:contacts){
        auto& a=*c.a;auto* d=c.d;
        if(a.state.phase!=Phase::Release||(d&&a.hitActors.count(d->id)))continue;

        if(c.priority==0){
            if(!ChamberSystem::matches(d->state,ChamberSystem::inDefenderView(a.state.attack,a.view,d->view),tuning)||
               !d->state.spend(tuning.ChamberCost))continue;

            a.state.chambered();
            a.returnStart=a.local;a.returnAge=0;a.bodyStart=a.bodyMotion;
            d->state.last=Resolution::Chamber;
            emit(Resolution::Chamber,a,d,c.point,c.normal);
        }
        else if(c.priority==1){
            if(d->state.phase!=Phase::Parry||!d->state.spend(tuning.ParryCost))continue;
            d->state.parrySuccess(tuning);
            d->returnStart=d->local;d->returnAge=0;d->bodyStart=d->bodyMotion;
            a.state.cancel(Resolution::Parry);a.returnStart=a.local;a.bodyStart=a.bodyMotion;
            emit(Resolution::Parry,a,d,c.point,c.normal);
        }
        else if(c.priority==2){
            a.state.cancel(Resolution::Wall);a.returnStart=a.local;a.bodyStart=a.bodyMotion;
            emit(Resolution::Wall,a,nullptr,c.point,c.normal);
        }
        else if(d&&d->health>0){
            a.hitActors.insert(d->id);a.state.hitSomeone=true;
            d->damageTaken+=tuning.Damage;++d->hitsTaken;
            if(!d->infiniteHealth)d->health=std::max(0.,d->health-tuning.Damage);
            d->state.lastSpend=0;d->flinch();
            if(d->health==0)d->state.phase=Phase::Dead;
            emit(Resolution::Hit,a,d,c.point,c.normal);
        }
    }
}
void CombatSimulation::advance(double dt)
{
    events.clear();queriesLastFrame=stepsLastFrame=0;
    if(dt<=0)return;

    constexpr double step=1./240.;
    accumulator+=dt;overload=accumulator>.25;
    for(auto* a:actors){
        a->frameStart=a->position;a->frameViewStart=a->simulatedView;a->frameViewTarget=a->view;
    }

    double processed=0;
    while(accumulator+1e-10>=step&&stepsLastFrame<64){
        if(beforeStep)beforeStep(step);
        double remaining=step;
        while(remaining>1e-10){
            double span=remaining;
            for(auto* a:actors){a->finishBoundary(tuning);span=std::min(span,a->state.boundary(tuning));}
            // Every endpoint is committed below; zero limits indicate invalid tuning.
            if(span<1e-10)break;
            const double alpha=clamp((processed+step-remaining+span)/dt,0.,1.);
            for(auto* a:actors){
                a->position=lerp(a->frameStart,a->frameTarget,alpha);
                if(a->externalView){
                    a->view={wrap(a->frameViewStart.yaw+wrap(a->frameViewTarget.yaw-a->frameViewStart.yaw)*alpha),
                        mix(a->frameViewStart.pitch,a->frameViewTarget.pitch,alpha)};
                    a->desired=a->view;
                }
                a->torsoPitchScale=tuning.TorsoPitchScale;
                a->leanFraction=constrainLean?clamp(constrainLean(*a),0.,1.):1.;
                a->intervalRelease=a->state.phase==Phase::Release;
                const double mid=(a->state.elapsed+span*.5)/a->state.duration();
                a->intervalDamage=a->intervalRelease&&mid>=a->state.definition.damageStart&&mid<=a->state.definition.damageEnd;
                a->advance(span,tuning,true);a->simulatedView=a->view;
                if(a->exMotion){a->exSampleEye=a->eye();a->exSampleView=a->view;}
            }
            time+=span;
            resolve(true);
            if(sampleStep)for(auto* a:actors)sampleStep(*a,time);
            for(auto* a:actors)a->finishBoundary(tuning);
            remaining-=span;
        }
        accumulator-=step;processed+=step;++stepsLastFrame;
    }
    for(auto* a:actors)if(a->externalView)a->view=a->desired=a->frameViewTarget;
}
}
