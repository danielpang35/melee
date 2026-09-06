#include "Combat/CombatSimulation.h"
#include "Combat/Attacks/AttackDirectionResolver.h"
#include "Movement/MomentumModel.h"
#include "Movement/LungeModel.h"
#include "Training/TrainingPattern.h"
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace mcl;
int checks=0;
void expect(bool ok,const char* message){++checks;if(!ok)throw std::runtime_error(message);}
void near(double a,double b,double tolerance,const char* message){expect(std::abs(a-b)<=tolerance,message);}
void stateTests()
{
    Tuning t;AttackStateMachine s;
    expect(s.start({},t),"Idle accepts attack");expect(s.phase==Phase::Windup,"Starts windup");
    s.advance(t.StrikeWindup,t);expect(s.phase==Phase::Release,"Windup -> release");
    s.advance(t.StrikeRelease,t);expect(s.phase==Phase::Recovery,"Release -> recovery");
    s.advance(.675,t);expect(s.phase==Phase::Idle,"Recovery -> idle");
    s.start({},t);s.advance(.3,t);expect(s.feint(t),"Late windup feint");expect(s.phase==Phase::Idle,"Feint neutral");
    expect(s.parry(t),"Immediate parry after ordinary feint");s.advance(t.ParryDuration,t);
    expect(s.phase==Phase::ParryRecovery,"Missed parry recovery");expect(!s.start({},t),"Missed parry punish window");
    s.advance(t.ParryRecovery,t);s.parry(t);s.parrySuccess(t);expect(s.start({AttackKind::Strike,60,60},t),"Riposte accepts direction");
    near(s.definition.windup,t.RiposteWindup,1e-8,"Riposte timing");
    s=AttackStateMachine{};s.start({},t);s.advance(.2,t);expect(s.start({AttackKind::Stab,0,0},t),"Strike -> stab morph");
    expect(!s.start({},t),"Cannot endlessly morph");expect(s.morphed,"Morph recorded");
    s.advance(s.definition.windup,t);s.advance(t.StabRelease*.6,t);expect(s.start({AttackKind::Strike,180,180},t),"Combo buffer");
    s.advance(t.StabRelease*.4,t);expect(s.phase==Phase::Windup&&s.attack.angle==180,"Combo -> selected windup");
    near(s.definition.windup,t.ComboWindup,1e-8,"Combo windup duration");
    s=AttackStateMachine{};s.start({},t);s.advance(t.StrikeWindup-t.FeintLockout+.001,t);expect(!s.feint(t),"Feint lockout");
    s.flinch();expect(s.phase==Phase::Flinch,"Windup hit enters flinch");expect(!s.start({},t)&&!s.parry(t),"Flinch locks offense and defense");s.advance(t.FlinchDuration,t);expect(s.phase==Phase::Idle,"Flinch recovery");
    s.start({},t);s.advance(2.,t);expect(s.phase==Phase::Idle,"Coarse phase overshoot preserved");
}
void comboTests()
{
    Tuning t;
    near(t.StrikeRelease*(t.DamageEnd-t.DamageStart),.45,1e-9,"450 ms active strike");
    for(int source=0;source<6;++source)for(int next=0;next<6;++next)for(int kind=0;kind<2;++kind){
        AttackStateMachine s;s.start({AttackKind::Strike,source*60.,source*60.},t);
        s.advance(t.StrikeWindup+t.StrikeRelease*.6,t);
        s.start({kind?AttackKind::Stab:AttackKind::Strike,next*60.,next*60.},t);
        s.advance(t.StrikeRelease*.4,t);
        expect(std::cos(s.attack.angle*Rad)*std::cos(source*60.*Rad)<0,"Every combo alternates body side");
        expect(!s.chamberActive(t)&&!ChamberSystem::matches(s,s.attack,t),"Combo strike or stab cannot chamber");
        AttackIntent morph=s.attack;morph.kind=kind?AttackKind::Strike:AttackKind::Stab;
        expect(s.start(morph,t)&&!s.chamberActive(t),"Morph cannot give a combo a chamber window");
        expect(s.feint(t),"Combo-derived attempt can feint");s.advance(t.FeintRecovery,t);expect(s.start({},t)&&s.chamberActive(t),"Fresh neutral attack regains chamber eligibility after feint recovery");
    }
    auto right=AttackTrajectory::release({AttackKind::Stab,0,0},.5);
    auto left=AttackTrajectory::release({AttackKind::Stab,180,180},.5);
    expect(right.hilt.y>0&&left.hilt.y<0,"Stab origins visibly alternate");
    for(int sector=0;sector<6;++sector){
        auto incoming=ChamberSystem::inDefenderView({AttackKind::Strike,sector*60.,sector*60.},{0,0},{180,0});
        near(wrap(incoming.angle-(180.-sector*60.)),0,1e-6,"Chamber origin mirrors into defender view");
    }
}
void chamberTests()
{
    Tuning t;
    for(int incoming=0;incoming<6;++incoming)for(int defense=0;defense<6;++defense){
        AttackStateMachine s;s.start({AttackKind::Strike,defense*60.,defense*60.},t);
        expect(ChamberSystem::matches(s,{AttackKind::Strike,incoming*60.,incoming*60.},t)==(incoming==defense),"All 36 chamber pairings");
    }
    AttackStateMachine s;s.start({},t);expect(ChamberSystem::matches(s,{AttackKind::Strike,31,31},t),"Continuous angle inside tolerance");
    expect(!ChamberSystem::matches(s,{AttackKind::Strike,33,33},t),"Angle outside tolerance");
    s.advance(t.ChamberDuration+.001,t);expect(!ChamberSystem::matches(s,{},t),"Microdrag after chamber time fails");
    expect(s.feint(t),"Expired chamber attempt can feint");expect(s.parry(t),"Feinted chamber can immediately parry");
    s=AttackStateMachine{};s.start({AttackKind::Stab,0,0},t);expect(ChamberSystem::matches(s,{AttackKind::Stab,0,0},t),"Stab chambers stab");
    expect(!ChamberSystem::matches(s,{},t),"Strike cannot chamber stab");
}
void geometryTests()
{
    Tuning t;auto neutral=ParryGeometry::make({}, {},t);
    expect(neutral.box({{100,0,0},{0,0,0}},4),"Front box sweep");
    expect(!neutral.catches({{-150,0,0},{-35,0,0}},4),"Rear attack bypasses guard");
    expect(neutral.cone({{145,60,20},{150,70,20}},4),"Forward extended cone catches beyond box");
    expect(!neutral.box({{145,60,20},{150,70,20}},4),"Extended cone test is outside main box");
    auto up=ParryGeometry::make({}, {0,45},t),down=ParryGeometry::make({}, {0,-45},t);
    Segment feet{{45,0,-84},{60,0,-84}};
    expect(up.box(feet,4),"Looking up protects feet through transformed box");
    expect(!down.box(feet,4),"Looking down exposes feet through transformed box");
    expect(up.catches(feet,4),"Complete parry protects feet when looking up");
    expect(!down.catches(feet,4),"Extended cone must not erase downward foot exposure");
    auto guard=approach({}, {90,60},t.ParryYawRate,t.ParryPitchRate,.1);
    near(guard.yaw,18,.001,"Guard yaw cap");near(guard.pitch,14,.001,"Guard pitch cap");
    expect(segmentCone({{100,-200,0},{100,200,0}}, {},{},200,30,4),"Swept segment crosses cone with both endpoints outside");
    expect(!segmentCone({{100,-200,300},{100,200,300}}, {},{},200,30,4),"Swept segment misses cone");
    near(segmentDistance({{0,0,0},{10,0,0}},{{5,-5,0},{5,5,0}}),0,1e-7,"Crossing segment distance");
    Tuning curved=t;curved.BladeLength=100;
    auto sweeps=WeaponTraceSystem::adaptiveSweeps(.1,{{0,0,0},{100,0,0}},{{0,0,0},{-100,0,0}},curved);
    bool arcContact=false;for(auto sweep:sweeps)if(pointSegmentDistance({0,-100,0},sweep)<=curved.BladeRadius)arcContact=true;
    expect(arcContact,"Adaptive curved sweep covers an arc missed by endpoint chords");
}
double contactTime(int fps,double turnRate)
{
    CombatSimulation sim;Combatant a,b;a.id=1;b.id=2;
    a.reset({0,0,88},{},sim.tuning);b.reset({135,0,88},{180,0},sim.tuning);
    sim.actors={&a,&b};a.start({},sim.tuning);
    double result=-1;
    for(int frame=0;frame<fps*2;++frame){if(a.state.phase==Phase::Release)a.look(turnRate/fps,0,1./fps,sim.tuning);
        sim.advance(1./fps);for(auto e:sim.events)if(e.result==Resolution::Hit&&result<0)result=e.time;}
    expect(b.health>=65,"One damage per target per swing");
    return result;
}
void spatialTests()
{
    double neutral=contactTime(240,0),accel=contactTime(240,-80),drag=contactTime(240,80);
    std::cout<<"Contact seconds: accel="<<accel<<" neutral="<<neutral<<" drag="<<drag<<'\n';
    expect(accel>0&&accel<neutral-.015,"Spatial accel advances contact");
    expect(drag>neutral+.02,"Spatial drag delays contact");
    for(int fps:{30,60,120,144,240}){
        near(contactTime(fps,0),neutral,.009,"Frame-rate collision equivalence");
        near(contactTime(fps,-80),accel,.018,"Frame-rate accel equivalence");
        near(contactTime(fps,80),drag,.018,"Frame-rate drag equivalence");
    }
    Tuning t;Combatant a;a.reset({0,0,88},{},t);a.start({},t);a.state.advance(t.StrikeWindup,t);
    for(int i=0;i<100;++i)a.look(100,0,.01,t);
    expect(a.state.releaseRotation>t.AntiSpinThreshold,"Cumulative rotation anti-spin");
    double previous=a.view.yaw;a.state.phase=Phase::Idle;a.look(0,0,.1,t);near(a.view.yaw,previous,1e-8,"Turncap discarded input never snaps");
    for(int sector=0;sector<6;++sector){auto p=AttackTrajectory::release({AttackKind::Strike,sector*60.,sector*60.},0);
        Vec origin{0,std::cos(sector*60.*Rad),std::sin(sector*60.*Rad)};expect(p.direction.dot(origin)>.9,"Six attacks originate on correct side");}
}
void doubleParryTimingTests()
{
    Tuning t;
    double contact=contactTime(240,0);
    const double secondParryReady=t.ParryDuration+t.ParryRecovery;
    const double secondThreat=t.FeintRecovery+contact;
    std::cout<<"Double-parry timing: ready="<<secondParryReady
             <<" secondThreat="<<secondThreat
             <<" margin="<<(secondThreat-secondParryReady)<<'\n';
    expect(secondThreat<secondParryReady,
    "Stationary double-parry must be numerically impossible");
    expect(secondParryReady-secondThreat<=.05,
        "Static double-parry gap must remain narrow enough for footwork to create extra reaction time");
    
    }
        void defenseIntegration()

{
    auto run=[](bool parry,bool chamber,double defenseAt,bool wrong=false){
        CombatSimulation sim;Combatant a,b;a.id=1;b.id=2;a.reset({0,0,88},{},sim.tuning);b.reset({135,0,88},{180,0},sim.tuning);
        sim.actors={&a,&b};a.start({},sim.tuning);bool started=false;Resolution outcome=Resolution::None;
        for(int i=0;i<260;++i){if(!started&&sim.time>=defenseAt){if(parry)b.parry(sim.tuning);if(chamber)b.start({AttackKind::Strike,wrong?60.:180.,wrong?60.:180.},sim.tuning);started=true;}
            sim.advance(1./240.);for(auto e:sim.events)if(e.attacker==a.id)outcome=e.result;}
        return outcome;
    };
    expect(run(true,false,.5)==Resolution::Parry,"Integrated active parry blocks");
    expect(run(true,false,0)==Resolution::Hit,"Expired parry fails");
    expect(run(false,true,.60)==Resolution::Chamber,"Integrated matching chamber");
    expect(run(false,true,.60,true)==Resolution::Hit,"Integrated wrong chamber fails");
}
void robustnessTests()
{
    // Sweep bodies and defenses together: insufficient defense stamina must fall through to damage.
    CombatSimulation sim;Combatant a,b;a.id=1;b.id=2;
    a.reset({0,0,88},{},sim.tuning);b.reset({135,0,88},{180,0},sim.tuning);sim.actors={&a,&b};a.start({},sim.tuning);
    b.state.infiniteStamina=false;b.state.stamina=0;sim.tuning.StaminaRegen=0;
    bool attempted=false;
    for(int i=0;i<240;++i){if(sim.time>.6&&!attempted){b.start({AttackKind::Strike,180,180},sim.tuning);attempted=true;}sim.advance(1./240.);}
    near(b.health,65,1e-8,"Exhausted chamber falls through to damage");
    auto againstDrag=[](bool parry,double start){
        CombatSimulation world;Combatant attacker,defender;attacker.id=1;defender.id=2;
        attacker.reset({0,0,88},{},world.tuning);defender.reset({135,0,88},{180,0},world.tuning);
        attacker.externalView=false;world.actors={&attacker,&defender};attacker.start({},world.tuning);bool defending=false;
        world.beforeStep=[&](double dt){if(attacker.state.phase==Phase::Release)attacker.look(45*dt,0,dt,world.tuning);};
        Resolution outcome=Resolution::None;
        for(int i=0;i<240;++i){if(world.time>=start&&!defending){if(parry)defender.parry(world.tuning);else defender.start({AttackKind::Strike,180,180},world.tuning);defending=true;}
            world.advance(1./240.);for(auto e:world.events)if(e.attacker==1)outcome=e.result;}
        return outcome;
    };
    expect(againstDrag(false,.51)==Resolution::Hit,"Legal microdrag arrives after short chamber window");
    expect(againstDrag(true,.51)==Resolution::Parry,"Same microdrag is caught by normal parry");
    // Reversing actor registration must not change defense priority.
    auto order=[](bool reverse){CombatSimulation world;Combatant attacker,defender;attacker.id=1;defender.id=2;
        attacker.reset({0,0,88},{},world.tuning);defender.reset({135,0,88},{180,0},world.tuning);
        world.actors=reverse?std::vector<Combatant*>{&defender,&attacker}:std::vector<Combatant*>{&attacker,&defender};attacker.start({},world.tuning);
        bool defending=false;int count=0;for(int i=0;i<240;++i){if(world.time>=.6&&!defending){defender.start({AttackKind::Strike,180,180},world.tuning);defending=true;}
            world.advance(1./240.);for(auto e:world.events)if(e.result==Resolution::Chamber)++count;}return count;};
    expect(order(false)==1&&order(true)==1,"Defense independent of registration order");
}
void flinchAndRiposteTests()
{
    Tuning t;
    for(auto phase:{Phase::Idle,Phase::Windup,Phase::Release,Phase::Recovery,Phase::Parry,Phase::ParryRecovery}){
        AttackStateMachine s;s.start({},t);s.phase=phase;s.comboQueued=true;s.riposteRemaining=.2;
        s.flinch();
        expect(s.phase==Phase::Flinch&&!s.comboQueued&&s.riposteRemaining==0,"Ordinary hit enters flinch and clears buffers");
        expect(!s.start({},t)&&!s.parry(t),"Flinch prevents immediate action");
        s.advance(t.FlinchDuration,t);
        expect(s.phase==Phase::Idle&&s.start({},t),"Fresh input accepted after flinch duration");
    }

    AttackStateMachine s;s.parrySuccess(t);s.start({},t);
    expect(s.isRiposte,"Riposte tracked independently of last event");
    s.flinch();expect(s.phase==Phase::Windup,"Riposte windup immune");
    s.advance(t.RiposteWindup,t);s.last=Resolution::Hit;s.flinch();
    expect(s.phase==Phase::Release,"Riposte release immune even after another event");
    near(s.yawCap(t),t.ReleaseEarlyCap*t.RiposteTurnScale,1e-8,"Riposte yaw is looser");

    auto ordinary=AttackTrajectory::release({},.5),counter=AttackTrajectory::riposteRelease({},.5,true);
    expect(counter.hilt.z>ordinary.hilt.z+10,"Riposte has a distinct authoritative raised swing");

    s.advance(t.StrikeRelease,t);s.flinch();
    expect(s.phase==Phase::Flinch,"Riposte recovery is vulnerable");
    s.advance(t.FlinchDuration,t);

    s.parrySuccess(t);s.start({},t);s.advance(t.RiposteWindup+t.StrikeRelease*.6,t);
    s.start({},t);s.advance(t.StrikeRelease*.4,t);
    expect(s.isCombo&&!s.isRiposte,"Combo cannot inherit riposte immunity");
    s.flinch();expect(s.phase==Phase::Flinch,"Combo is interrupted");
    s.advance(t.FlinchDuration,t);

    s.parrySuccess(t);s.start({},t);s.start({AttackKind::Stab,0,0},t);
    expect(!s.isRiposte,"Morph becomes an ordinary attack");

    for(bool riposte:{false,true}){
        CombatSimulation world;Combatant a,b;a.id=1;b.id=2;
        a.reset({0,0,88},{},t);b.reset({135,0,88},{180,0},t);world.actors={&a,&b};a.start({},t);
        bool began=false;
        for(int i=0;i<240;++i){
            if(world.time>=.65&&!began){
                if(riposte)b.state.parrySuccess(t);
                b.start({},t);b.state.advance(b.state.definition.windup,t);
                b.state.definition.damageStart=.9;b.state.comboQueued=true;began=true;
            }
            world.advance(1./240.);
        }
        near(b.health,65,1e-8,"Release hit still causes damage");
        expect(b.state.phase==(riposte?Phase::Release:Phase::Flinch),
            "Integrated hit flinches normal release but preserves riposte");
        if(!riposte){
            expect(!b.state.comboQueued&&b.returnAge<t.FlinchDuration,
                "Interrupted swing clears combo and begins flinch presentation");
        }
    }

    CombatSimulation world;Combatant a,b;a.id=1;b.id=2;b.infiniteHealth=true;
    b.reset({135,0,88},{180,0},t);world.actors={&a,&b};
    for(int hit=0;hit<20;++hit){
        a.reset({0,0,88},{},t);a.start({},t);
        for(int i=0;i<480;++i)world.advance(1./240.);
    }
    expect(b.health==100&&b.hitsTaken==20&&b.damageTaken==700,
        "Infinite target survives repeated hits and records damage");
}
void newStateTimingTests()
{
    Tuning t;

    // Pure feint: immediate parry is legal, immediate re-attack is not.
    AttackStateMachine s;s.start({},t);s.advance(.20,t);
    expect(s.feint(t),"Feint accepted");
    expect(!s.start({},t),"Feint recovery blocks immediate re-attack");
    expect(s.parry(t),"Parry remains legal during feint recovery");

    // Atomic windup -> feint -> parry.
    s=AttackStateMachine{};s.start({},t);s.advance(.20,t);
    expect(s.parry(t)&&s.phase==Phase::Parry,"RMB during windup performs atomic feint-to-parry");
    s=AttackStateMachine{};s.start({},t);
    s.advance(t.StrikeWindup-t.FeintLockout+.001,t);
    expect(!s.parry(t)&&s.phase==Phase::Windup,"Committed late windup cannot FTP");

    // Explicit offensive lockout length.
    s=AttackStateMachine{};s.start({},t);s.advance(.20,t);s.feint(t);
    s.advance(t.FeintRecovery-.001,t);expect(!s.start({},t),"Feint recovery still active");
    s.advance(.002,t);expect(s.start({},t),"Attack accepted when feint recovery expires");
    near(s.definition.windup,.60,1e-8,"Normal strike windup baseline is 600 ms");

    // Chambered attacker becomes gameplay-neutral immediately.
    s=AttackStateMachine{};s.start({},t);s.advance(t.StrikeWindup,t);
    s.chambered();
    expect(s.phase==Phase::Idle&&!s.comboQueued&&!s.isRiposte,"Chamber hard-resets attacker to idle");
    expect(s.start({},t),"Chambered attacker may act immediately after neutral reset");

    near(t.ComboWindup,.65,1e-8,"Combo windup baseline is 650 ms");
}void movementTests()
{
    Tuning t;MomentumModel m;for(int i=0;i<240;++i)m.update({500,0,0},{1,0,0},1./240.,t);
    expect(m.value>.65,"Consistent movement builds momentum");double before=m.value;
    for(int i=0;i<24;++i)m.update({500,0,0},{-1,0,0},1./240.,t);
    expect(m.value<before-.1,"Reversal loses momentum");
    m=MomentumModel{};m.value=1;for(int i=0;i<240;++i)m.update({500,0,0},{1,0,0},1./240.,t);
    near(m.value,1,1e-8,"Camera-only changes have no momentum input");
    LungeModel l;l.begin({1,0,0},1,1,t);double distance=0;for(int i=0;i<120;++i)distance+=l.step(1./240.,t).length()/240.;
    expect(distance>25&&distance<=t.LungeMaxDisplacement+.001,"Lunge controlled displacement");
    l.begin({1,0,0},-1,1,t);near(l.step(.01,t).length(),0,1e-8,"Backpedal does not lunge");
    AttackDirectionResolver resolver;resolver.sample(0,10,0);auto intent=resolver.resolve(.01,t);near(intent.angle,0,1e-8,"Right selection");
    resolver.sample(.1,-10,17);intent=resolver.resolve(.1,t);near(intent.angle,120,1e-8,"Upper-left selection");
    near(resolver.resolve(1,t).angle,120,1e-8,"Deadzone stable fallback");
}
int main()
{
    try{stateTests();comboTests();chamberTests();geometryTests();spatialTests();defenseIntegration();robustnessTests();flinchAndRiposteTests();newStateTimingTests();doubleParryTimingTests();movementTests();
        std::cout<<"PASS: "<<checks<<" checks\n";return 0;}
    catch(const std::exception& e){std::cerr<<"FAIL after "<<checks<<" checks: "<<e.what()<<'\n';return 1;}
}

