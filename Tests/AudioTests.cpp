#include "Audio/CombatAudioRules.h"
#include "Combat/CombatSimulation.h"
#include <iostream>
#include <stdexcept>
using namespace mcl;
int checks=0;
void expect(bool value,const char* message){++checks;if(!value)throw std::runtime_error(message);}

struct Run { int swings=0,hits=0;double hitTime=-1,health=0; };
Run exchange(int fps,double angle,bool observe)
{
    CombatSimulation sim;Combatant a,b;a.id=1;b.id=2;
    a.reset({0,0,88},{},sim.tuning);b.reset({135,0,88},{180,0},sim.tuning);
    sim.actors={&a,&b};ReleaseAudioGate gate;Run run;
    if(observe)sim.sampleStep=[&](const Combatant& fighter,double){
        if(fighter.id==1&&gate.sample(fighter.state.phase,fighter.state.serial,fighter.state.attack.kind)!=AudioCue::None)++run.swings;
    };
    a.start({AttackKind::Strike,angle,angle},sim.tuning);
    for(int frame=0;frame<fps*2;++frame){
        sim.advance(1./fps);
        for(const auto& event:sim.events)if(event.result==Resolution::Hit){++run.hits;run.hitTime=event.time;}
    }
    run.health=b.health;return run;
}
int main()
{
    try{
        for(auto result:{Resolution::None,Resolution::Miss,Resolution::Feint,Resolution::Morph,Resolution::Combo,Resolution::Riposte})
            expect(contactAudio(result)==AudioCue::None,"Non-contact must not produce a hit sound");
        expect(contactAudio(Resolution::Hit)==AudioCue::Body,"Body sound");
        expect(contactAudio(Resolution::Hit,ContactRegion::Head)==AudioCue::Head,"Head replaces ordinary impact");
        expect(contactAudio(Resolution::Parry,ContactRegion::Head)==AudioCue::Parry,"Defensive contact never becomes a head hit");
        expect(contactRegion(Resolution::Hit,{0,0,150},{0,0,88},88,32)==ContactRegion::Head,"Head band includes boundary");
        expect(contactRegion(Resolution::Hit,{0,0,149.99},{0,0,88},88,32)==ContactRegion::Body,"Below head band stays body");
        expect(contactRegion(Resolution::Hit,{0,0,105},{0,0,64},64,32)==ContactRegion::Head,"Head follows crouched capsule");
        expect(contactRegion(Resolution::Hit,{0,0,80},{0,0,64},64,32)==ContactRegion::Body,"Crouched torso stays body");
        expect(contactRegion(Resolution::Wall,{0,0,200},{0,0,88},88,32)==ContactRegion::None,"Non-hit has no anatomical tag");
        {
            CombatSimulation sim;Combatant attacker,target;attacker.id=1;target.id=2;
            target.reset({0,0,88},{},sim.tuning);
            sim.emit(Resolution::Hit,attacker,&target,{0,0,165});
            target.position.z+=200;
            expect(sim.events.back().region==ContactRegion::Head,"Region captured at contact survives later target movement");
            expect(target.health==100,"Cosmetic head tag does not apply extra damage");
            sim.emit(Resolution::Wall,attacker,nullptr,{0,0,165});
            expect(sim.events.back().region==ContactRegion::None,"World contact has no region");
        }
        {
            double bodyHealth=0;
            for(double height:{100.,165.}){
                CombatSimulation sim;Combatant attacker,target;attacker.id=1;target.id=2;
                attacker.reset({0,0,88},{},sim.tuning);target.reset({135,0,88},{180,0},sim.tuning);
                attacker.state.phase=Phase::Release;
                attacker.state.elapsed=attacker.state.duration()*.5;
                attacker.traces={{{0,0,height},{200,0,height}}};sim.actors={&attacker,&target};
                sim.resolve();
                expect(sim.events.size()==1&&sim.events.front().result==Resolution::Hit,"Contact fixture resolves one real hit");
                expect(sim.events.front().region==(height>150?ContactRegion::Head:ContactRegion::Body),"Resolved contact carries correct region");
                if(height==100)bodyHealth=target.health;
                else expect(target.health==bodyHealth,"Head feedback preserves existing body damage");
            }
        }
        expect(contactAudio(Resolution::Parry)==AudioCue::Parry,"Parry sound");
        expect(contactAudio(Resolution::Chamber)==AudioCue::Chamber,"Chamber differs from parry");
        expect(contactAudio(Resolution::Wall)==AudioCue::Wall,"Wall differs from body");
        {
            ArmorAudioGate armor;
            expect(armor.sample(0,{0,0,88},{},Phase::Idle,0)==0,"Spawning does not rustle");
            expect(armor.sample(.05,{0,0,88},{},Phase::Windup,1)==1,"Committed body preparation rustles immediately");
            expect(armor.sample(.1,{0,0,88},{},Phase::Windup,1)==0,"No repeated rustle while holding windup");
            expect(armor.sample(.15,{0,0,88},{},Phase::Parry,1)==0,"Fast phase changes do not stack equipment voices");
            expect(armor.sample(.6,{0,0,88},{},Phase::Recovery,1)==1,"Recovery has a quiet equipment settle");
            expect(armor.sample(1,{0,0,88},{},Phase::Idle,1)==0,"Stationary idle remains quiet");
            expect(armor.sample(1.5,{1000,0,88},{},Phase::Idle,1)==0,"Teleport does not manufacture a step");
            expect(armor.sample(2,{1100,0,88},{},Phase::Dead,1)==0,"Dead actor does not emit movement foley");
            ArmorAudioGate moving;int rustles=0;
            moving.sample(0,{0,0,88},{},Phase::Idle,0);
            for(int i=1;i<=240;++i)if(moving.sample(i/240.,{i*200./240.,0,88},{},Phase::Idle,0)>0)++rustles;
            expect(rustles==2,"Two equipment shifts per 200 cm of continuous movement");
            ArmorAudioGate turning;
            turning.sample(0,{0,0,88},{179,0},Phase::Idle,0);
            expect(turning.sample(1,{0,0,88},{-179,0},Phase::Idle,0)==0,"Yaw wrap does not manufacture a huge turn");
            expect(turning.sample(2,{0,0,88},{-130,0},Phase::Idle,0)>0,"Substantial body turn rustles");
        }
        ReleaseAudioGate gate;
        expect(gate.sample(Phase::Windup,1,AttackKind::Strike)==AudioCue::None,"Windup has no committed air cue");
        expect(gate.sample(Phase::Idle,1,AttackKind::Strike)==AudioCue::None,"Feinted windup stays quiet");
        expect(gate.sample(Phase::Release,2,AttackKind::Strike)==AudioCue::Swing,"Release onset");
        for(int i=0;i<240;++i)expect(gate.sample(Phase::Release,2,AttackKind::Strike)==AudioCue::None,"No repeated cue within release");
        expect(gate.sample(Phase::Release,3,AttackKind::Stab)==AudioCue::Stab,"New combo serial and stab routing");
        gate.sample(Phase::Idle,0,AttackKind::Strike);
        expect(gate.sample(Phase::Release,1,AttackKind::Strike)==AudioCue::Swing,"Reset permits reused serial");
        gate.sample(Phase::Windup,4,AttackKind::Strike);
        gate.sample(Phase::Windup,4,AttackKind::Stab);
        expect(gate.sample(Phase::Release,4,AttackKind::Stab)==AudioCue::Stab,"Morph uses committed attack family");
        for(double angle:{0.,180.}){
            const auto reference=exchange(240,angle,true);
            for(int fps:{30,60,120,144,240}){
                const auto with=exchange(fps,angle,true),without=exchange(fps,angle,false);
                expect(with.swings==1,"Exactly one swing cue at each frame rate");
                expect(with.hits==1,"Fixture makes a real body contact");
                expect(with.hits==without.hits&&with.health==without.health&&with.hitTime==without.hitTime,
                    "Audio observation preserves authoritative damage and contact time");
                expect(std::abs(with.hitTime-reference.hitTime)<1e-9,"Contact time remains fixed across frame rates");
            }
        }
        std::cout<<"PASS "<<checks<<" audio checks\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
