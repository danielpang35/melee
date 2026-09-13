#include "Visual/TPSourceBinding.h"
#include "Visual/TPPresentationPolicy.h"
#include <cstdlib>
#include <iostream>
#include <limits>

using namespace mcl;
static void require(bool ok,const char* message){if(!ok){std::cerr<<"FAIL: "<<message<<'\n';std::exit(1);}}
static bool near(double a,double b){return std::abs(a-b)<1.e-9;}
int main(){
    AttackStateMachine policyState;policyState.definition.windup=22./30.;
    policyState.phase=Phase::Recovery;
    require(TPPresentationPolicy::contact(policyState,.9,true),"early-hit recovery retains canonical release");
    require(!TPPresentationPolicy::contact(policyState,1.2,true),"nondamaging carry keeps native path");
    require(!TPPresentationPolicy::contact(policyState,.9,false),"fallback never inherits native binding");
    require(near(TPPresentationPolicy::cameraAim(policyState,22./30.,true),1.),"release entry retains full camera aim");
    require(near(TPPresentationPolicy::cameraAim(policyState,31./30.,true),1.),"release exit retains full camera aim");
    require(near(TPPresentationPolicy::cameraAim(policyState,1.3,true),0.),"recovery returns to chest aim");
    require(near(TPPresentationPolicy::cameraAim(policyState,0.,false),0.),"idle uses chest aim");
    TPSourceBinding legacy;
    require(legacy.valid()&&legacy.frames()==154,"legacy 154@60 metadata remains unchanged");
    AttackStateMachine state;state.exActive=true;state.phase=Phase::Windup;state.attackAge=.2;
    require(near(legacy.sample(state,.5,0).time,.5),"legacy uses accepted EX source time");
    state.phase=Phase::Idle;
    require(near(legacy.sample(state,.5,0).time,.30),"legacy idle remains .30");

    TPSourceBinding pilot;pilot.attackAge=true;pilot.duration=73./30.;pilot.idle=0;
    require(pilot.valid()&&pilot.frames()==147,"D source span resampled at60Hz is147 frames");
    auto invalid=pilot;invalid.duration+=.001;require(!invalid.valid(),"fractional endpoint rejected");
    invalid=pilot;invalid.rate=std::numeric_limits<double>::quiet_NaN();require(!invalid.valid(),"nonfinite rate rejected");
    invalid=pilot;invalid.duration=std::numeric_limits<double>::infinity();require(!invalid.valid(),"nonfinite duration rejected");
    invalid=pilot;invalid.idle=3.;require(!invalid.valid(),"idle outside source rejected");

    state.definition={62./60.-.30,18./60.,73./60.,0.,1.};
    for(auto phase:{Phase::Windup,Phase::Release,Phase::Recovery}){
        state.phase=phase;state.last=Resolution::Hit;state.attackAge=.9;state.elapsed=.01;
        auto sample=pilot.sample(state,1.2,.01);
        require(sample.authored&&!sample.tail&&near(sample.time,.9),"phase changes and early-hit recovery do not restart or retime source");
    }
    state.phase=Phase::Release;
    state.attackAge=state.definition.windup;
    require(near(pilot.sample(state,62./60.,0).time,22./30.),"EX release start exposes D source frame23");
    state.attackAge+=state.definition.release;
    require(near(pilot.sample(state,80./60.,0).time,31./30.),"EX release end exposes D source frame32");

    state.phase=Phase::Idle;state.attackAge=2.25;state.last=Resolution::Miss;
    for(double age:{0.,.05,.1,11./60.}){
        const auto sample=pilot.sample(state,.30,age);
        require(sample.tail&&!sample.authored&&near(sample.time,2.25+age),"natural idle tail uses existing transition clock at1x");
    }
    require(!pilot.sample(state,.30,.2).tail&&near(pilot.sample(state,.30,.2).time,0.),"finished source returns to ready");
    state.last=Resolution::Hit;require(pilot.sample(state,.30,.05).tail,"successful hit gets complete recovery");
    for(auto result:{Resolution::Wall,Resolution::Parry,Resolution::Chamber,Resolution::Feint,Resolution::None}){
        state.last=result;require(!pilot.sample(state,.30,.05).tail,"interrupted/initial idle never inherits tail");
    }
    state.last=Resolution::Hit;state.attackAge=0;
    require(!pilot.sample(state,.30,.05).tail,"reset attack age cannot inherit completed source");
    state.attackAge=2.25;state.phase=Phase::Flinch;
    require(!pilot.sample(state,.30,.05).tail&&!pilot.sample(state,.30,.05).authored,"flinch immediately cancels authored sampling");
    state.phase=Phase::Windup;state.attackAge=.01;++state.serial;
    require(near(pilot.sample(state,.31,0).time,.01),"new attack immediately starts its own source clock");
    state.exActive=false;
    require(!pilot.sample(state,.30,0).authored&&!pilot.sample(state,.30,0).tail,"unbound attack never inherits pilot motion");
    state.exActive=true;state.phase=Phase::Release;state.definition={22./30.,.50,73./60.,0.,1.};
    state.attackAge=state.definition.windup+.25;
    require(near(pilot.sample(state,0,0).time,22./30.+.15),"TP uses same 500 ms release map as FP/contact");
    state.attackAge=state.definition.windup+.50;
    require(near(pilot.sample(state,0,0).time,31./30.),"TP reaches original release endpoint after 500 ms");
    state.phase=Phase::Recovery;state.attackAge+=.1;
    require(near(pilot.sample(state,0,0).time,31./30.+.1),"recovery continues at native speed without source jump");
    state.phase=Phase::Idle;state.last=Resolution::Hit;state.attackAge=2.45;
    require(near(pilot.sample(state,.30,.1).time,2.35),"500 ms release preserves full TP idle tail");
    std::cout<<"TP source binding contracts passed\n";
}
