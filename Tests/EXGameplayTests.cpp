#include "Combat/CombatSimulation.h"
#include <fstream>
#include <iostream>
#include <cstdlib>
using namespace mcl;
static void require(bool ok,const char* message){if(!ok){std::cerr<<"FAIL: "<<message<<'\n';std::exit(1);}}
struct Fixture {
    CombatSimulation sim;Combatant a,b;
    Fixture(std::shared_ptr<const EXWeaponMotion> motion,Vec target={150,0,88}){
        a.exMotion=motion;a.id=1;b.id=2;a.state.infiniteStamina=false;
        a.reset({0,0,86},{},sim.tuning);b.reset(target,{180,0},sim.tuning);b.infiniteHealth=true;
        sim.actors={&a,&b};
    }
    void start(){require(a.start({},sim.tuning),"normal input starts");}
    void tick(double dt){sim.advance(dt);}
};
int main(int argc,char** argv){
    require(argc==2,"selected export path");auto motion=std::make_shared<EXWeaponMotion>();std::ifstream in(argv[1]);
    require(motion->read(in),"selected export loads");
    Fixture exact(motion,{400,0,88});exact.a.look(13.,7.,1./60.,exact.sim.tuning);exact.start();
    require(!exact.a.exEntryBridge,"aim before ordinary input does not change source entry");
    for(int i=0;i<20;++i){exact.tick(1./240.);auto expected=exact.a.exWorld(motion->sample(.30+exact.a.state.attackAge));
        require((expected.tip-exact.a.weapon.tip).length()<1e-8,"ordinary entry preserves approved source samples");}
    for(int fps:{30,60,144}){
        Fixture aim(motion,{400,0,88});aim.start();
        for(int i=0;i<fps;++i){aim.a.look(.4,.12,1./fps,aim.sim.tuning);aim.a.frameTarget=aim.a.position+Vec{.2,.1,0};aim.tick(1./fps);
            if(aim.a.state.phase==Phase::Release){const auto local=motion->sample(aim.a.exSourceTime);
                const auto expected=aim.a.exSampleEye+aim.a.exSampleView.world(local.tip-Vec{11.5,0,168});
                require((expected-aim.a.weapon.tip).length()<1e-8,"sampled camera and contact agree at fractional render cadence");}
        }
    }
    double first=-1;
    for(int fps:{30,60,144}){
        Fixture f(motion);f.start();double hit=-1;int hits=0;
        for(int i=0;i<fps*3;++i){f.tick(1./fps);for(auto e:f.sim.events)if(e.result==Resolution::Hit){hit=e.time;++hits;}}
        std::cout<<"production body fps="<<fps<<" hits="<<hits<<" contact="<<hit<<'\n';
        require(hits==1,"once-per-target body hit");
        if(first<0)first=hit;else require(std::abs(hit-first)<1e-9,"contact independent of render cadence");
        require(f.a.state.phase==Phase::Idle,"continuous ready after recovery");
        f.start();for(int i=0;i<fps*3;++i)f.tick(1./fps);
        require(f.b.hitsTaken==2,"repeat without reset hits again");
    }
    Fixture boundary(motion,{400,0,88});boundary.start();double earliest=100,latest=0;
    boundary.sim.worldSweep=[&](int,Segment,double,Vec&,Vec&){earliest=std::min(earliest,boundary.sim.time);latest=std::max(latest,boundary.sim.time);return false;};
    for(int i=0;i<12;++i)boundary.tick(.25);
    require(std::abs(earliest-(EXWeaponMotion::Release-.30+1./240.))<1e-8,"windup geometry excluded");
    require(std::abs(latest-(EXWeaponMotion::Exit-.30))<1e-8,"final release span retained");
    require(boundary.b.hitsTaken==0,"range miss");
    Fixture wall(motion,{400,0,88});wall.start();
    wall.sim.worldSweep=[&](int,Segment s,double,Vec& p,Vec& n){p=s.b;n={-1,0,0};return wall.sim.time>=EXWeaponMotion::Exit-.30-1e-9;};
    for(int i=0;i<250;++i)wall.tick(1./240.);
    require(wall.a.state.last==Resolution::Wall&&wall.a.state.stamina==100,"final-span wall precedes miss cost");
    for(int i=0;i<600;++i)wall.tick(1./240.);
    require(wall.a.state.phase==Phase::Idle&&wall.a.start({},wall.sim.tuning),"wall returns and permits repeat");
    Fixture defense(motion);defense.start();for(int i=0;i<180;++i)defense.tick(1./240.);
    require(defense.b.parry(defense.sim.tuning),"defender parry legal");
    bool parried=false;for(int i=0;i<70&&!parried;++i){defense.tick(1./240.);for(auto e:defense.sim.events)parried|=e.result==Resolution::Parry;}
    require(parried&&defense.b.hitsTaken==0,"parry blocks body");
    require(defense.b.start({},defense.sim.tuning)&&defense.b.state.isRiposte,"riposte remains legal");
    Fixture branch(motion);branch.start();branch.tick(.1);
    require(branch.a.parry(branch.sim.tuning)&&branch.a.state.phase==Phase::Parry,"atomic feint-to-parry");
    Fixture feint(motion);feint.start();feint.tick(.1);require(feint.a.feint(feint.sim.tuning),"feint legal");
    require(feint.a.parry(feint.sim.tuning),"defense before cosmetic return ends");
    Fixture morph(motion);morph.start();morph.tick(.1);
    require(morph.a.start({AttackKind::Stab,0,0},morph.sim.tuning)&&!morph.a.state.exActive,"morph switches explicit binding");
    require(std::abs(morph.a.state.definition.release-morph.sim.tuning.StabRelease)<1e-10,"stab keeps own timing");
    Fixture combo(motion,{400,0,88});combo.start();for(int i=0;i<217;++i)combo.tick(1./240.);
    require(combo.a.start({},combo.sim.tuning)&&combo.a.state.comboQueued,"combo queues");
    for(int i=0;i<35;++i)combo.tick(1./240.);
    require(combo.a.state.isCombo&&!combo.a.state.exActive&&resolvedStance(combo.a.state.attack)==Stance::Left,"combo alternates and selects fallback");
    require(std::abs(combo.a.state.definition.windup-.8)<1e-10,"EX-initiated combo uses requested 800 ms windup");
    const double remaining=.8-combo.a.state.elapsed;
    for(int i=0;i<static_cast<int>(std::round(remaining*240))-1;++i)combo.tick(1./240.);
    require(combo.a.state.phase==Phase::Windup,"EX combo still winds up before 800 ms");
    combo.tick(1./240.);require(combo.a.state.phase==Phase::Release,"EX combo releases at 800 ms");
    const auto& qa=motion->frames[112].rotation;const auto& qb=motion->frames[113].rotation;
    const auto raw=qa*.25+qb*(qa.dot(qb)<0?-.75:.75);const auto normalized=raw*(1/std::sqrt(raw.dot(raw)));
    const auto rapid=motion->sample(112.75/60.);
    require(((rapid.tip-rapid.hilt).normal()-EXWeaponMotion::basis(normalized.rotate({0,0,1}))).length()<1e-9,"rapid-roll subframe retains normalized FastLerp");
    Fixture movement(motion,{400,0,88});movement.start();
    for(int i=0;i<248;++i){movement.a.frameTarget=movement.a.position+Vec{.15,.1,0};movement.a.look(.1,.04,1./240.,movement.sim.tuning);movement.tick(1./240.);
        if(movement.a.state.phase==Phase::Release){
            auto expected=movement.a.exWorld(motion->sample(movement.a.exSourceTime));
            require((expected.tip-movement.a.weapon.tip).length()<1e-7,"movement and full aim preserve shared blade");
            require(std::abs((movement.a.weapon.tip-movement.a.weapon.hilt).length()-103.5)<.001,"actual blade length");
        }
    }
    // Legacy partial damage windows: collisions must not sweep across either edge.
    Fixture window(motion,{400,0,88});window.a.exMotion.reset();window.a.state.exEnabled=false;window.start();
    double firstDamage=-1,lastDamage=-1;
    window.sim.sampleStep=[&](const Combatant& a,double time){if(a.id==1&&a.intervalDamage){if(firstDamage<0)firstDamage=time;lastDamage=time;}};
    for(int i=0;i<8;++i)window.tick(.25);
    require(firstDamage>window.sim.tuning.StrikeWindup+window.sim.tuning.StrikeRelease*window.sim.tuning.DamageStart,"partial damage starts after boundary");
    require(std::abs(lastDamage-window.sim.tuning.StrikeWindup-window.sim.tuning.StrikeRelease*window.sim.tuning.DamageEnd)<1e-8,"partial damage final span preserved");
    // The requested feel candidate preserves source geometry and uses one fixed
    // 500 ms release clock for native rendering and every collision substep.
    double tunedContact=-1;
    for(int fps:{30,60,144,240}){
        Fixture tuned(motion);tuned.sim.tuning.EXReleaseDuration=.50;
        tuned.sim.tuning.ReleaseEarlyCap=205;tuned.sim.tuning.ReleaseMidCap=195;
        tuned.sim.tuning.ReleaseLateCap=175;tuned.sim.tuning.PitchCap=145;
        tuned.start();
        require(std::abs(tuned.a.state.definition.release-.50)<1e-10,"EX uses requested 500 ms release");
        double firstSweep=-1,lastSweep=-1,hit=-1;int hits=0;
        tuned.sim.worldSweep=[&](int,Segment,double,Vec&,Vec&){if(firstSweep<0)firstSweep=tuned.sim.time;lastSweep=tuned.sim.time;return false;};
        tuned.sim.sampleStep=[&](const Combatant& actor,double){
            if(actor.id!=1||!actor.intervalRelease)return;
            const double source=EXWeaponMotion::Release+(actor.state.attackAge-actor.state.definition.windup)*.30/.50;
            require(std::abs(actor.exSourceTime-source)<1e-9,"release geometry uses fixed phase map at every simulation substep");
            const auto expected=actor.exWorld(motion->sample(source));
            require((expected.tip-actor.weapon.tip).length()<1e-8,"retimed native source and collision pose agree");
        };
        for(int i=0;i<fps*3;++i){tuned.tick(1./fps);for(const auto& e:tuned.sim.events)if(e.result==Resolution::Hit){hit=e.time;++hits;}}
        require(hits==1&&tuned.a.state.phase==Phase::Idle,"500 ms exchange hits once and returns to ready");
        require(std::abs(firstSweep-(EXWeaponMotion::Release-.30+1./240.))<1e-8,"slower release excludes windup");
        require(std::abs(lastSweep-(EXWeaponMotion::Release-.30+.50))<1e-8,"slower release retains final damaging substep");
        if(tunedContact<0)tunedContact=hit;else require(std::abs(hit-tunedContact)<1e-9,"500 ms contact is frame-rate independent");
        Fixture steer(motion,{400,0,88});steer.sim.tuning=tuned.sim.tuning;steer.start();
        for(int i=0;i<fps*2;++i){
            if(steer.a.state.phase==Phase::Release){
                const auto before=steer.a.view;const double cap=steer.a.state.yawCap(steer.sim.tuning);
                steer.a.look(100,-100,1./fps,steer.sim.tuning);
                require(std::abs(wrap(steer.a.view.yaw-before.yaw)-cap/fps)<1e-9,"release yaw saturates at selected cap");
                require(std::abs(steer.a.view.pitch-before.pitch)<=145./fps+1e-9,"release pitch respects selected cap");
            }
            steer.tick(1./fps);
        }
        require(steer.b.hitsTaken==0,"steered out-of-range swing remains a miss");
        Fixture comboTuned(motion,{400,0,88});comboTuned.sim.tuning=tuned.sim.tuning;comboTuned.start();
        for(int i=0;i<250;++i)comboTuned.tick(1./240.);
        require(comboTuned.a.start({},comboTuned.sim.tuning)&&comboTuned.a.state.comboQueued,"combo buffers during longer release");
        for(int i=0;i<48;++i)comboTuned.tick(1./240.);
        require(comboTuned.a.state.isCombo&&std::abs(comboTuned.a.state.definition.windup-.8)<1e-9,"longer release preserves 800 ms combo windup");
    }
    std::cout<<"PASS feel candidate: 500 ms, yaw 205/195/175, pitch145; contact="<<tunedContact<<'\n';
    std::cout<<"PASS production: 30/60/144 Hz, repeat, moving aim, miss, phase/damage boundaries, wall, parry/riposte, FTP, morph, combo\n";
}
