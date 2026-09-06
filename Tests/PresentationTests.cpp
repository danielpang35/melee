#include "Visual/MeleePresentationPose.h"
#include <iostream>
#include <stdexcept>
using namespace mcl;
int checks=0;
void require(bool value,const char* message){++checks;if(!value)throw std::runtime_error(message);}
bool close(Vec a,Vec b){return (a-b).length()<1e-7;}
void verify(const Combatant& s,const Tuning& t)
{
    const auto p=presentation::evaluate(s,t);
    require(close(p.blade.hilt,s.weapon.hilt)&&close(p.blade.tip,s.weapon.tip),"Blade must equal simulation in every phase");
    require(std::abs(p.axis.dot(p.edge))<1e-7&&std::abs(p.normal.length()-1.)<1e-7,"Sword frame must be orthonormal");
    for(int i=0;i<2;++i){
        const auto& arm=p.arms[i];
        const double depth=(s.weapon.hilt-arm.hand).dot(p.axis)/t.BladeLength;
        require(depth>(i==0?.10:.20)&&depth<(i==0?.12:.22),"Palm must lie on the calibrated leather grip behind the guard");
        require((s.weapon.hilt-arm.hand).cross(p.axis).length()<1e-7,"Palm contact must stay on the hilt axis");
        require(std::isfinite(arm.elbow.x)&&std::isfinite(arm.elbow.y)&&std::isfinite(arm.elbow.z),"Finite IK at extreme pitch");
        require(std::abs((arm.elbow-arm.shoulder).length()-36.*arm.reachScale)<1e-6,"Upper arm length must match reported reach");
        require(std::abs((arm.elbow-arm.hand).length()-34.*arm.reachScale)<1e-6,"Forearm length must match reported reach");
    }
}
int main()
{
    try{
        Tuning t;
        for(double origin:{0.,60.,120.,180.,-120.,-60.})for(AttackKind kind:{AttackKind::Strike,AttackKind::Stab}){
            const AttackIntent intent{kind,origin,origin};
            const auto loaded=AttackTrajectory::windup(intent,1.,AttackTrajectory::rest(),t,false,true);
            const auto start=AttackTrajectory::riposteRelease(intent,0.,true,t);
            const auto end=AttackTrajectory::riposteRelease(intent,1.,true,t);
            const auto settle=AttackTrajectory::recovery(intent,0.,t,Resolution::Miss,true);
            require(close(loaded.hilt,start.hilt)&&close(loaded.direction,start.direction),"Riposte windup must meet raised release without a hilt teleport");
            require(close(end.hilt,settle.hilt)&&close(end.direction,settle.direction),"Riposte recovery must start at the actual raised release end");
        }
        for(int fps:{30,60,144,240})for(double pitch:{-85.,0.,85.})
            for(double origin:{0.,60.,120.,180.,-120.,-60.})for(AttackKind kind:{AttackKind::Strike,AttackKind::Stab}){
                Combatant s;s.reset({130,-47,88},{37,pitch},t);s.start({kind,origin,origin},t);
                for(int frame=0;frame<fps*3;++frame){s.advance(1./fps,t);verify(s,t);}
            }
        for(Phase phase:{Phase::Idle,Phase::Parry,Phase::ParryRecovery,Phase::Flinch,Phase::Dead}){
            Combatant s;s.reset({0,0,88},{},t);s.state.phase=phase;verify(s,t);
        }
        // Shoulder anchor must not orbit the camera when looking up or down.
        Combatant a,b;a.reset({0,0,88},{20,-85},t);b.reset({0,0,88},{20,85},t);
        require(close(presentation::evaluate(a,t).arms[0].shoulder,presentation::evaluate(b,t).arms[0].shoulder),"Shoulder stays on torso at pitch extremes");
        // Long reach and a pole parallel to the arm must not collapse or NaN.
        auto far=presentation::solveArm({0,0,0},{150,0,0},{1,0,0});
        require(close(far.hand,{150,0,0})&&far.reachScale>1.&&std::isfinite(far.elbow.z),"Unreachable hand uses explicit cosmetic stretch");
        auto folded=presentation::solveArm({0,0,0},{0,0,0},{1,0,0});
        require(std::isfinite(folded.elbow.x),"Coincident targets remain finite");
        // Sword frame must remain continuous through vertical/lateral directions.
        Vec previous;
        for(int i=0;i<=720;++i){
            Combatant s;s.reset({0,0,88},{},t);
            const double theta=(-112.+212.*i/720.)*Rad;
            s.weapon.tip=s.weapon.hilt+Vec{std::cos(theta),std::sin(theta),0}*t.BladeLength;
            auto frame=presentation::evaluate(s,t);
            if(i)require(previous.dot(frame.edge)>.99,"Edge must not flip during broad cuts");
            previous=frame.edge;
        }
        std::cout<<"PASS: "<<checks<<" presentation checks\n";return 0;
    }catch(const std::exception& e){std::cerr<<"FAIL: "<<e.what()<<'\n';return 1;}
}
