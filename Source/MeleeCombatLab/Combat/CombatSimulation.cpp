#include "CombatSimulation.h"
namespace mcl
{
bool Combatant::start(AttackIntent intent,const Tuning& t)
{
    auto phase=state.phase;auto serial=state.serial;
    bool ok=state.start(intent,t);
    if(ok&&(serial!=state.serial||(phase==Phase::Windup&&state.last==Resolution::Morph)))windupStart=local;
    return ok;
}
void Combatant::flinch()
{
    state.flinch();
    if(state.phase==Phase::Flinch){returnStart=local;returnAge=0;}
}
bool Combatant::feint(const Tuning& t)
{
    if(!state.feint(t))return false;
    returnStart=local;returnAge=0;return true;
}
bool Combatant::parry(const Tuning& t)
{
    if(!state.parry(t))return false;
    guard=view;returnStart=local;returnAge=0;return true;
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
    position=frameStart=frameTarget=at;view=desired=guard=simulatedView=frameViewStart=frameViewTarget=facing;
    health=100;damageTaken=0;hitsTaken=0;hitActors.clear();trackedSerial=0;
    local=windupStart=returnStart=AttackTrajectory::rest();returnAge=1;
    weapon=previousWeapon=AttackTrajectory::world(local,position+Vec{0,0,eyeHeight},view,t);
    defense=ParryGeometry::make(position,guard,t);
}
void Combatant::advance(double dt,const Tuning& t)
{
    auto oldPhase=state.phase;auto oldSerial=state.serial;LocalPose before=local;
    previousWeapon=weapon;state.advance(dt,t);
    if(state.serial!=oldSerial)windupStart=before;
    if(state.serial!=trackedSerial){trackedSerial=state.serial;hitActors.clear();}
    if(state.phase==Phase::Parry)guard=approach(guard,desired,t.ParryYawRate,t.ParryPitchRate,dt);else guard=view;
    defense=ParryGeometry::make(position,guard,t);

    if(state.phase==Phase::Idle&&oldPhase!=Phase::Idle){returnStart=before;returnAge=0;}
    if(state.phase==Phase::ParryRecovery&&oldPhase==Phase::Parry){returnStart=before;returnAge=0;}
    returnAge+=dt;

    if(state.phase==Phase::Idle){
        const double duration=state.last==Resolution::Feint?t.FeintReturnDuration:
            state.last==Resolution::Chamber?.10:.12;
        local=blend(returnStart,AttackTrajectory::rest(),smooth(returnAge/duration));
    }
    else if(state.phase==Phase::Flinch){
        local=blend(returnStart,AttackTrajectory::rest(),smooth(state.elapsed/std::max(.001,t.FlinchDuration)));
    }
    else if(state.phase==Phase::Parry){
        local=blend(returnStart,AttackTrajectory::evaluate(state,windupStart,t),smooth(state.elapsed/.055));
    }
    else if(state.phase==Phase::ParryRecovery){
        local=blend(returnStart,AttackTrajectory::rest(),smooth(state.elapsed/std::max(.001,t.ParryRecovery)));
    }
    else if(state.phase==Phase::Recovery){
        const bool interrupted=state.last==Resolution::Parry||state.last==Resolution::Wall;
        if(interrupted){
            if(oldPhase==Phase::Release){returnStart=before;local=before;}
            else local=blend(returnStart,AttackTrajectory::rest(),smooth(state.progress()));
        }
        else local=AttackTrajectory::evaluate(state,windupStart,t);
    }
    else local=AttackTrajectory::evaluate(state,windupStart,t);

    weapon=AttackTrajectory::world(local,position+Vec{0,0,eyeHeight},view,t);
    speed=(weapon.tip-previousWeapon.tip).length()/dt;
    angularSpeed=angle(weapon.tip-weapon.hilt,previousWeapon.tip-previousWeapon.hilt)/dt;
    traces=WeaponTraceSystem::adaptiveSweeps(dt,previousWeapon,weapon,t);
}
void CombatSimulation::emit(Resolution r,Combatant& attacker,Combatant* defender,Vec point)
{
    attacker.state.last=r;events.push_back({r,attacker.id,defender?defender->id:-1,point,time});
}
void CombatSimulation::resolve()
{
    struct Contact{int priority;Combatant* a;Combatant* d;Vec point;double distance;};
    std::vector<Contact> contacts;

    for(auto* a:actors){
        if(a->state.phase!=Phase::Release)continue;
        for(auto* d:actors){
            if(a==d||d->health<=0||a->hitActors.count(d->id))continue;
            bool body=false,parry=false;Vec point=d->position;
            for(auto sweep:a->traces){++queriesLastFrame;
                if(segmentDistance(sweep,d->hurtAxis())<=d->bodyRadius+tuning.BladeRadius){body=true;point=sweep.b;}
                if(d->state.phase==Phase::Parry&&d->defense.catches(sweep,tuning.BladeRadius)){parry=true;point=sweep.b;}
            }
            auto incoming=ChamberSystem::inDefenderView(a->state.attack,a->view,d->view);
            d->incomingAngle=incoming.angle;d->chamberDifference=ChamberSystem::difference(incoming,d->state.attack);
            bool front=angle(d->view.forward(),a->position-d->position)<tuning.ChamberFacingAngle;
            bool chamber=body&&a->state.damaging()&&front&&ChamberSystem::matches(d->state,incoming,tuning);

            if(chamber)contacts.push_back({0,a,d,point,(point-a->weapon.hilt).length()});
            if(parry)contacts.push_back({1,a,d,point,(point-a->weapon.hilt).length()});
            if(body&&a->state.damaging()&&
                a->state.releaseRotation<=tuning.AntiSpinThreshold*(a->state.isRiposte?tuning.RiposteTurnScale:1.))
                contacts.push_back({3,a,d,point,(point-a->weapon.hilt).length()});
        }
        if(worldSweep){
            for(auto sweep:a->traces){
                Vec point;++queriesLastFrame;
                if(worldSweep(a->id,sweep,tuning.BladeRadius,point)){
                    contacts.push_back({2,a,nullptr,point,(point-a->weapon.hilt).length()});break;
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
            a.returnStart=a.local;a.returnAge=0;
            d->state.last=Resolution::Chamber;
            emit(Resolution::Chamber,a,d,c.point);
        }
        else if(c.priority==1){
            if(d->state.phase!=Phase::Parry||!d->state.spend(tuning.ParryCost))continue;
            d->state.parrySuccess(tuning);
            a.state.cancel(Resolution::Parry);a.returnStart=a.local;
            emit(Resolution::Parry,a,d,c.point);
        }
        else if(c.priority==2){
            a.state.cancel(Resolution::Wall);a.returnStart=a.local;
            emit(Resolution::Wall,a,nullptr,c.point);
        }
        else if(d&&d->health>0){
            a.hitActors.insert(d->id);a.state.hitSomeone=true;
            d->damageTaken+=tuning.Damage;++d->hitsTaken;
            if(!d->infiniteHealth)d->health=std::max(0.,d->health-tuning.Damage);
            d->state.lastSpend=0;d->flinch();
            if(d->health==0)d->state.phase=Phase::Dead;
            emit(Resolution::Hit,a,d,c.point);
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
        const double alpha=clamp((processed+step)/dt,0.,1.);
        for(auto* a:actors){
            a->position=lerp(a->frameStart,a->frameTarget,alpha);
            if(a->externalView){
                a->view={wrap(a->frameViewStart.yaw+wrap(a->frameViewTarget.yaw-a->frameViewStart.yaw)*alpha),
                    mix(a->frameViewStart.pitch,a->frameViewTarget.pitch,alpha)};
                a->desired=a->view;
            }
        }
        if(beforeStep)beforeStep(step);
        for(auto* a:actors){a->advance(step,tuning);a->simulatedView=a->view;}
        time+=step;resolve();accumulator-=step;processed+=step;++stepsLastFrame;
    }
    for(auto* a:actors)if(a->externalView)a->view=a->desired=a->frameViewTarget;
}
}
