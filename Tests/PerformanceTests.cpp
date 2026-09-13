#include "Visual/AttackPerformance.h"
#include "Visual/MeleePresentationPose.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <stdexcept>
using namespace mcl;
void check(bool value,const char* message){if(!value)throw std::runtime_error(message);}
int main()
{
    try{
        {
            std::ifstream weaponFile("../../Config/RightCutWeapon.csv");
            auto clip=std::make_shared<AuthoredRightCut>();
            check(clip->read(weaponFile),"Authored weapon file invalid");
            std::ifstream viewFile("../../Config/RightCutView.csv");
            check(clip->readView(viewFile),"View offset file invalid");
            std::istringstream bad("RIGHT_CUT_WEAPON_V1,120,271\n0,NaN,0,0,1,0,0\n");
            check(!clip->read(bad)&&clip->frames.size()==271,"Malformed reload replaced live weapon");
            Tuning t;Combatant authored,baseline;
            authored.reset({0,0,88},{},t);baseline.reset({0,0,88},{},t);authored.rightCut=clip;
            authored.start({AttackKind::Strike,0,0},t);baseline.start({AttackKind::Strike,0,0},t);
            double difference=0.;
            for(int i=0;i<600;++i){
                authored.advance(1./240.,t);baseline.advance(1./240.,t);
                check(authored.state.phase==baseline.state.phase,"Authored path changed attack clock");
                check(std::abs((authored.weapon.tip-authored.weapon.hilt).length()-t.BladeLength)<1e-6,"Authored blade changed length");
                difference=std::max(difference,(authored.weapon.tip-baseline.weapon.tip).length());
                check(std::isfinite(authored.weapon.tip.x),"Nonfinite authored pose");
                if(authored.state.phase==Phase::Release)check(clip->viewOffset(authored.state).length()==0.,"View displaced active blade");
            }
            check(difference>30.,"Authored track was not consumed");
            check((authored.local.hilt-AttackTrajectory::rest().hilt).length()<.15,"Authored recovery did not return");
            authored.reset({0,0,88},{},t);authored.start({AttackKind::Strike,0,0},t);
            for(int i=0;i<60;++i)authored.advance(1./240.,t);
            check(authored.feint(t),"Authored windup could not feint");
            auto stopped=authored.weapon;authored.advance(1./240.,t);
            check((authored.weapon.hilt-stopped.hilt).length()<1.,"Feint teleported authored grip");
            check(authored.parry(t),"Authored feint could not parry");
            authored.advance(1./240.,t);check(authored.state.phase==Phase::Parry,"Parry did not interrupt authoring");
            for(double a:{90.,180.,270.}){
                AttackStateMachine state;state.start({AttackKind::Strike,a,a},t);
                auto x=clip->evaluate(state,AttackTrajectory::rest(),{{},{}},t);
                auto y=AttackTrajectory::evaluate(state,AttackTrajectory::rest(),t);
                check((x.hilt-y.hilt).length()<1e-9,"Pilot affected another attack direction");
            }
            std::cout<<"PASS: authored weapon validation, phase clocks, rigid blade, direction scope, feint/parry and return\n";
        }
        performance::Library library;
        std::ifstream file("../../Config/AttackPerformance.csv");
        check(file.good(),"Motion library missing");
        std::string line;std::getline(file,line);int rows=0;
        while(std::getline(file,line)){
            std::replace(line.begin(),line.end(),',',' ');std::istringstream row(line);
            int d,k;row>>d>>k;check(d>=0&&d<8&&k>=0&&k<10,"Invalid key index");
            auto& p=library.cuts[d][k];
            row>>p.chest>>p.pelvis>>p.waist>>p.pitch>>p.forward>>p.drop
                >>p.rightElbow.x>>p.rightElbow.y>>p.rightElbow.z
                >>p.leftElbow.x>>p.leftElbow.y>>p.leftElbow.z>>p.rightWrist>>p.leftWrist;
            check(!row.fail(),"Malformed key");++rows;
        }
        check(rows==80,"Incomplete library");
        double maxWrist=0,maxStretch=1;
        for(int d=0;d<240;++d){
            const double angle=d*1.5;
            check(std::abs(library.sample(angle,0).chest-library.sample(angle,3).chest)<1e-9,"Idle endpoints differ");
            Combatant actor;Tuning tuning;actor.reset({0,0,88},{},tuning);
            actor.start({AttackKind::Strike,angle,angle},tuning);
            performance::Player player;
            for(int frame=0;frame<120;++frame){
                actor.advance(1./60.,tuning);
                const auto before=actor.weapon;
                auto pose=player.update(library,actor.state.phase,actor.state.serial,angle,actor.state.progress(),1./60.);
                const auto adjacent=library.sample(angle+1.5,1.5);
                const auto current=library.sample(angle,1.5);
                check(std::abs(adjacent.chest-current.chest)<3,"Directional body seam");
                const auto f=presentation::evaluate(actor,tuning);
                for(int side=0;side<2;++side){
                    const double sign=side==0?1.:-1.;
                    Vec finger=Vec{.03,sign*.22,-.24}.normal();
                    Vec palm=(Vec{-1,0,0}+finger*finger.x).normal();
                    Vec restGrip=(finger.cross(palm)*(-sign)+finger*.8).normal();
                    Vec restLower=Vec{0,sign*.215,-.135}.normal();
                    Vec offset=finger*4.5+palm*2.;
                    const Vec rail=side==0?pose.rightElbow:pose.leftElbow;
                    const auto fit=presentation::attachPerformanceArm(f.arms[side].shoulder,f.arms[side].hand,
                        f.axis,rail,0,restGrip,restLower,offset,presentation::UpperArmLength,presentation::ForearmLength);
                    const Vec sr=(restLower-restGrip*restLower.dot(restGrip)).normal();
                    Vec mapped=fit.handRadial*offset.dot(sr)+f.axis.cross(fit.handRadial)*offset.dot(restGrip.cross(sr))+f.axis*offset.dot(restGrip);
                    check((fit.arm.hand+mapped-f.arms[side].hand).length()<1e-7,"Grip detached");
                    check(std::isfinite(fit.arm.elbow.z),"Nonfinite attachment");
                    maxWrist=std::max(maxWrist,fit.wristBend);maxStretch=std::max(maxStretch,fit.arm.reachScale);
                }
                check((actor.weapon.hilt-before.hilt).length()==0&&(actor.weapon.tip-before.tip).length()==0,"Presentation changed gameplay weapon");
            }
        }
        const auto seamA=library.sample(-.00001,1.7),seamB=library.sample(.00001,1.7);
        check(std::abs(seamA.chest-seamB.chest)<1e-5,"Circular wrap seam");
        std::cout<<"PASS: 240-direction library, circular continuity, exact visual grips, read-only weapon. Approximate rig diagnostic max wrist="<<maxWrist<<" stretch="<<maxStretch<<" (not rendered acceptance)\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
