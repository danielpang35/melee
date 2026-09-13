#include "AttackStateMachine.h"
namespace mcl
{
void AttackStateMachine::selectMotion(const Tuning& t)
{
    exActive=exEnabled&&attack.kind==AttackKind::Strike&&std::abs(wrap(attack.angle))<.001&&
        resolvedStance(attack)==Stance::Right&&!isCombo&&!isRiposte&&!morphed;
    if(exActive)definition={62./60.-.30,t.EXReleaseDuration,73./60.,0.,1.};
}
double AttackStateMachine::boundary(const Tuning& t) const
{
    if(phase==Phase::Idle||phase==Phase::Dead)return 1e30;
    double end=duration();
    if(phase==Phase::Parry)end=t.ParryDuration;
    if(phase==Phase::ParryRecovery)end=t.ParryRecovery;
    if(phase==Phase::Flinch)end=t.FlinchDuration;
    if(phase==Phase::Release)for(double p:{definition.damageStart,definition.damageEnd})
        if(p*definition.release>elapsed+1e-10)end=std::min(end,p*definition.release);
    return std::max(0.,end-elapsed);
}
double AttackStateMachine::duration() const
{
    switch(phase){case Phase::Windup:return definition.windup;case Phase::Release:return definition.release;
    case Phase::Recovery:return definition.recovery;default:return 1.;}
}
bool AttackStateMachine::spend(double cost)
{
    if(!infiniteStamina&&stamina<cost)return false;
    if(!infiniteStamina)stamina-=cost;
    lastSpend=0;return true;
}
bool AttackStateMachine::canFeint(const Tuning& t) const{return phase==Phase::Windup&&elapsed<definition.windup-t.FeintLockout;}
bool AttackStateMachine::canMorph(const Tuning& t) const{return phase==Phase::Windup&&!morphed&&progress()<t.MorphWindow;}
bool AttackStateMachine::canCombo(const Tuning& t) const{return phase==Phase::Release&&progress()>=t.ComboStart&&progress()<=t.ComboEnd;}
bool AttackStateMachine::chamberActive(const Tuning& t) const{return phase==Phase::Windup&&!isCombo&&attackAge<t.ChamberDuration;}
bool AttackStateMachine::damaging() const{return phase==Phase::Release&&progress()>=definition.damageStart&&progress()<=definition.damageEnd;}

bool AttackStateMachine::start(AttackIntent intent,const Tuning& t)
{
    if(canCombo(t)){
        const Stance nextSide=oppositeStance(resolvedStance(attack));
        // Preserve legacy angle selection for Auto inputs in the six ordinary
        // directions. Explicit stance callers select angle independently.
        // Vertical reflection leaves the cut vertical; stance still alternates.
        if(intent.stance==Stance::Auto&&resolvedStance(intent)!=nextSide){
            intent.angle=wrap(180.-intent.angle);intent.rawAngle=wrap(180.-intent.rawAngle);
        }
        intent.stance=nextSide;
        queued=intent;comboQueued=true;return true;
    }
    if(canMorph(t)&&attack.kind!=intent.kind){
        if(!spend(t.MorphCost))return false;
        // A morph changes attack kind inside the committed body-side action.
        // Retain that stance even if the caller supplies a different side.
        intent.stance=resolvedStance(attack);
        attack=intent;isRiposte=false;
        definition=AttackDefinition::make(intent.kind,t);definition.windup+=t.MorphAdditionalWindup;
        elapsed=0;morphed=true;selectMotion(t);last=Resolution::Morph;return true;
    }
    if(phase!=Phase::Idle||feintRecoveryRemaining>1e-10)return false;

    intent.stance=resolvedStance(intent);
    attack=intent;definition=AttackDefinition::make(intent.kind,t);
    isRiposte=riposteRemaining>0;
    if(isRiposte){definition.windup=t.RiposteWindup;last=Resolution::Riposte;}
    else last=Resolution::None;

    phase=Phase::Windup;elapsed=attackAge=releaseRotation=0;
    comboQueued=isCombo=morphed=hitSomeone=false;
    riposteRemaining=0;selectMotion(t);comboBaseWindup=definition.windup;++serial;return true;
}
bool AttackStateMachine::feint(const Tuning& t)
{
    if(!canFeint(t)||!spend(t.FeintCost))return false;
    phase=Phase::Idle;elapsed=attackAge=releaseRotation=0;
    comboQueued=isCombo=isRiposte=morphed=hitSomeone=false;queued={};
    riposteRemaining=0;feintRecoveryRemaining=t.FeintRecovery;
    last=Resolution::Feint;return true;
}
bool AttackStateMachine::feintToParry(const Tuning& t)
{
    if(!canFeint(t)||!spend(t.FeintCost))return false;

    // Atomic authoritative FTP: one transition, not synthetic Q + RMB inputs.
    phase=Phase::Parry;elapsed=attackAge=releaseRotation=0;
    comboQueued=isCombo=isRiposte=morphed=hitSomeone=false;queued={};
    riposteRemaining=0;feintRecoveryRemaining=0;
    definition.recovery=t.ParryRecovery;last=Resolution::Feint;
    return true;
}
bool AttackStateMachine::parry(const Tuning& t)
{
    if(phase==Phase::Windup)return feintToParry(t);
    if(phase!=Phase::Idle)return false;

    // Defensive input is intentionally legal during offensive feint recovery.
    phase=Phase::Parry;elapsed=0;definition.recovery=t.ParryRecovery;return true;
}
void AttackStateMachine::parrySuccess(const Tuning& t)
{
    phase=Phase::Idle;elapsed=0;feintRecoveryRemaining=0;
    riposteRemaining=t.RiposteWindow;last=Resolution::Parry;
}
void AttackStateMachine::flinch()
{
    if(phase==Phase::Dead||(isRiposte&&(phase==Phase::Windup||phase==Phase::Release)))return;

    phase=Phase::Flinch;elapsed=attackAge=riposteRemaining=releaseRotation=0;
    feintRecoveryRemaining=0;
    comboQueued=isCombo=isRiposte=morphed=hitSomeone=false;queued={};
    last=Resolution::Hit;
}
void AttackStateMachine::chambered()
{
    if(phase==Phase::Dead)return;

    // Gameplay-neutral immediately. Presentation can still return the sword smoothly.
    phase=Phase::Idle;elapsed=attackAge=riposteRemaining=releaseRotation=0;
    feintRecoveryRemaining=0;
    comboQueued=isCombo=isRiposte=morphed=hitSomeone=false;queued={};
    last=Resolution::Chamber;
}
void AttackStateMachine::cancel(Resolution result)
{
    if(result==Resolution::Chamber){chambered();return;}
    phase=Phase::Recovery;elapsed=0;comboQueued=false;last=result;
}
void AttackStateMachine::advance(double dt,const Tuning& t,bool deferTransitions)
{
    lastSpend+=dt;
    if(lastSpend>t.StaminaDelay)stamina=std::min(100.,stamina+t.StaminaRegen*dt);
    riposteRemaining=std::max(0.,riposteRemaining-dt);
    feintRecoveryRemaining=std::max(0.,feintRecoveryRemaining-dt);

    if(phase==Phase::Idle||phase==Phase::Dead)return;

    elapsed+=dt;attackAge+=dt;
    if(deferTransitions)return;
    for(int transitions=0;transitions<8;++transitions){
        double limit=duration();
        if(phase==Phase::Parry)limit=t.ParryDuration;
        if(phase==Phase::ParryRecovery)limit=t.ParryRecovery;
        if(phase==Phase::Flinch)limit=t.FlinchDuration;
        if(elapsed+1e-10<limit)break;
        elapsed=std::max(0.,elapsed-limit);

        if(phase==Phase::Windup){phase=Phase::Release;releaseRotation=0;}
        else if(phase==Phase::Release){
            if(!hitSomeone){spend(t.MissCost);last=Resolution::Miss;}
            if(comboQueued){
                attack=queued;definition=AttackDefinition::make(attack.kind,t);
                // Combo timing is explicit, including after an authored EX opener.
                definition.windup=t.ComboWindup;
                phase=Phase::Windup;attackAge=elapsed;isCombo=true;isRiposte=false;
                comboQueued=morphed=hitSomeone=false;selectMotion(t);++serial;last=Resolution::Combo;
            }
            else phase=Phase::Recovery;
        }
        else if(phase==Phase::Parry)phase=Phase::ParryRecovery;
        else{
            phase=Phase::Idle;isRiposte=false;elapsed=0;break;
        }
    }
}
double AttackStateMachine::yawCap(const Tuning& t) const
{
    if(phase==Phase::Release){
        double p=progress();
        return (isRiposte?t.RiposteTurnScale:1.)*
            (p<.5?mix(t.ReleaseEarlyCap,t.ReleaseMidCap,p*2):
                mix(t.ReleaseMidCap,t.ReleaseLateCap,(p-.5)*2));
    }
    if(phase==Phase::Windup)return t.WindupYawCap*(isRiposte?t.RiposteTurnScale:1.);
    if(phase==Phase::Recovery)return mix(t.ReleaseLateCap,1200.,progress());
    return 100000.;
}
}
