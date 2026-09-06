#include "AttackStateMachine.h"
namespace mcl
{
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
        if(std::cos(intent.angle*Rad)*std::cos(attack.angle*Rad)>=0){
            intent.angle=wrap(180.-intent.angle);intent.rawAngle=wrap(180.-intent.rawAngle);
        }
        queued=intent;comboQueued=true;return true;
    }
    if(canMorph(t)&&attack.kind!=intent.kind){
        if(!spend(t.MorphCost))return false;
        attack=intent;isRiposte=false;
        definition=AttackDefinition::make(intent.kind,t);definition.windup+=t.MorphAdditionalWindup;
        elapsed=0;morphed=true;last=Resolution::Morph;return true;
    }
    if(phase!=Phase::Idle||feintRecoveryRemaining>1e-10)return false;

    attack=intent;definition=AttackDefinition::make(intent.kind,t);
    isRiposte=riposteRemaining>0;
    if(isRiposte){definition.windup=t.RiposteWindup;last=Resolution::Riposte;}
    else last=Resolution::None;

    phase=Phase::Windup;elapsed=attackAge=releaseRotation=0;
    comboQueued=isCombo=morphed=hitSomeone=false;
    riposteRemaining=0;++serial;return true;
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
void AttackStateMachine::advance(double dt,const Tuning& t)
{
    lastSpend+=dt;
    if(lastSpend>t.StaminaDelay)stamina=std::min(100.,stamina+t.StaminaRegen*dt);
    riposteRemaining=std::max(0.,riposteRemaining-dt);
    feintRecoveryRemaining=std::max(0.,feintRecoveryRemaining-dt);

    if(phase==Phase::Idle||phase==Phase::Dead)return;

    elapsed+=dt;attackAge+=dt;
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
                attack=queued;definition=AttackDefinition::make(attack.kind,t);definition.windup=t.ComboWindup;
                phase=Phase::Windup;attackAge=elapsed;isCombo=true;isRiposte=false;
                comboQueued=morphed=hitSomeone=false;++serial;last=Resolution::Combo;
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
