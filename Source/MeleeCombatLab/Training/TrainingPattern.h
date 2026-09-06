#pragma once
#include "Combat/CombatSimulation.h"
namespace mcl
{
enum class TrainingMode {Passive,Right,Left,Upper,Lower,Stab,Alternating,Accel,Drag,Microdrag,Feint,Morph,Mixed,Count};
inline const char* trainingName(TrainingMode mode)
{
    constexpr const char* names[]={"PASSIVE","RIGHT HORIZONTAL","LEFT HORIZONTAL","UPPER","LOWER","STAB","ALTERNATING","ACCEL","DRAG","MICRODRAG","FEINT","MORPH","MIXED"};
    return names[static_cast<int>(mode)];
}
struct TrainingPattern
{
    TrainingMode mode=TrainingMode::Right;
    double wait=1.;int sequence=0;bool branched=false;
    void update(Combatant& self,const Combatant& target,double dt,const Tuning& t)
    {
        if(mode==TrainingMode::Passive||self.health<=0)return;
        Vec to=target.position-self.position;
        if(self.state.phase==Phase::Idle){self.view.yaw=std::atan2(to.y,to.x)/Rad;self.desired=self.view;}
        wait-=dt;
        TrainingMode action=mode==TrainingMode::Mixed?static_cast<TrainingMode>(1+sequence%11):mode;
        if(self.state.phase==Phase::Idle&&wait<=0){
            double a=0;if(action==TrainingMode::Left)a=180;
            if(action==TrainingMode::Upper)a=sequence%2?60:120;
            if(action==TrainingMode::Lower)a=sequence%2?-60:-120;
            if(action==TrainingMode::Alternating)a=(sequence%6)*60.;
            self.start({action==TrainingMode::Stab?AttackKind::Stab:AttackKind::Strike,a,a},t);
            wait=t.DummyInterval;branched=false;++sequence;
        }
        if(self.state.phase==Phase::Windup&&!branched&&self.state.progress()>.5){
            if(action==TrainingMode::Feint){self.feint(t);wait=.55;branched=true;}
            if(action==TrainingMode::Morph){self.start({AttackKind::Stab,0,0},t);branched=true;}
        }
        if(self.state.phase==Phase::Release){
            double rate=0;if(action==TrainingMode::Accel)rate=-t.DummyDragRate;
            if(action==TrainingMode::Drag)rate=t.DummyDragRate;
            if(action==TrainingMode::Microdrag)rate=t.DummyMicrodragRate;
            self.look(rate*dt,0,dt,t);
        }
    }
};
}
