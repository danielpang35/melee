#include "Movement/LocomotionModel.h"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <vector>

using namespace mcl;

namespace
{
int Checks=0;
void expect(bool Ok,const char* Message){++Checks;if(!Ok)throw std::runtime_error(Message);}
void near(double A,double B,double Tolerance,const char* Message){expect(std::abs(A-B)<=Tolerance,Message);}

struct RunResult
{
    LocomotionOutput output;
    Vec position;
    double firstZero=-1;
    double firstNinety=-1;
};

RunResult run(double Seconds,double FrameDt,LocomotionInput Input,const Tuning& T,Vec OppositeTarget={})
{
    RunResult Result;
    double Age=0;
    while(Age+1e-10<Seconds){
        double Frame=std::min(FrameDt,Seconds-Age);
        double Remaining=Frame;
        while(Remaining>1e-10){
            const double Dt=std::min(Remaining,LocomotionModel::MaxSimulationStep);
            Input.dt=Dt;
            Result.output=LocomotionModel::step(Input,T);
            Result.position+=Result.output.velocity*Dt;
            Input.velocity=Result.output.velocity;
            Age+=Dt;Remaining-=Dt;

            if(Result.firstZero<0&&OppositeTarget.length()>1&&
                Result.output.velocity.dot(OppositeTarget.normal())>0)Result.firstZero=Age;
            if(Result.firstNinety<0&&OppositeTarget.length()>1&&
                Result.output.velocity.dot(OppositeTarget.normal())>=OppositeTarget.length()*.9)Result.firstNinety=Age;
        }
    }
    return Result;
}
}

int main()
{
    try{
        Tuning T;

        // Start from rest: immediate intent, bounded body acceleration.
        for(double Fps:{30.,60.,120.,144.,240.}){
            LocomotionInput In;In.intent={1,0,0};
            auto R=run(.10,1./Fps,In,T);
            expect(R.output.velocity.x>320&&R.output.velocity.x<=T.ForwardSpeed+.01,
                "Forward start reaches useful speed without instant target-velocity teleport");
        }

        // Constant directional caps and no diagonal sqrt(2) exploit.
        LocomotionInput Forward;Forward.intent={1,0,0};
        near(run(1,1./240.,Forward,T).output.velocity.x,T.ForwardSpeed,.01,"Forward cap");
        LocomotionInput Back;Back.intent={-1,0,0};
        near(run(1,1./240.,Back,T).output.velocity.x,-T.BackwardSpeed,.01,"Backward cap");
        LocomotionInput Side;Side.intent={0,1,0};
        near(run(1,1./240.,Side,T).output.velocity.y,T.LateralSpeed,.01,"Lateral cap");
        LocomotionInput Diagonal;Diagonal.intent={1,1,0};
        expect(run(1,1./240.,Diagonal,T).output.velocity.length()<T.ForwardSpeed,
            "Diagonal movement obeys directional ellipse");

        // Sprint: gait is a target-velocity state, not a momentum scalar.
        LocomotionInput Sprint;Sprint.intent={1,0,0};Sprint.sprintRequested=true;
        auto SprintRun=run(1,1./240.,Sprint,T);
        near(SprintRun.output.velocity.x,T.SprintSpeed,.01,"Sprint cap");
        expect(SprintRun.output.gait==Gait::Sprint,"Sprint gait signal");

        // Sprint stop distance should be substantial but not slippery and nearly frame independent.
        std::vector<double> Stops;
        for(double Fps:{30.,60.,120.,144.,240.}){
            LocomotionInput Stop;Stop.velocity={T.SprintSpeed,0,0};
            auto R=run(.25,1./Fps,Stop,T);
            Stops.push_back(R.position.x);
            expect(R.output.velocity.length()<.01,"Sprint stops within 250 ms");
            expect(R.position.x>28&&R.position.x<40,"Sprint stop distance remains grounded and bounded");
        }
        const auto [MinStop,MaxStop]=std::minmax_element(Stops.begin(),Stops.end());
        expect(*MaxStop-*MinStop<2.0,"Sprint stopping distance is frame-rate stable");

        // Hard A/D or W/S reversal gets extra authority without snapping velocity.
        for(double Fps:{30.,60.,120.,144.,240.}){
            LocomotionInput Reverse;Reverse.velocity={T.LateralSpeed,0,0};Reverse.intent={-1,0,0};
            Reverse.dt=std::min(1./Fps,LocomotionModel::MaxSimulationStep);
            auto First=LocomotionModel::step(Reverse,T);
            expect(First.reversalSeverity>.9,"Hard reversal severity is exposed");
            auto R=run(.16,1./Fps,Reverse,T,{-T.BackwardSpeed,0,0});
            expect(R.firstZero>0&&R.firstZero<=.075,"Reversal crosses zero quickly");
            expect(R.firstNinety>0&&R.firstNinety<=.15,"Reversal reaches useful opposite speed");
        }

        // Tiny corrections receive precision authority.
        LocomotionInput Precision;Precision.intent={.25,0,0};
        auto P=run(.035,1./240.,Precision,T);
        expect(P.output.velocity.x>70,"Small correction becomes perceptible immediately");
        expect(P.output.velocity.x<=T.ForwardSpeed*.25+.01,"Analog correction remains proportional");

        // Entering combat drops sprint but never zeros ordinary locomotion.
        Sprint.phase=Phase::Windup;Sprint.velocity={T.SprintSpeed,0,0};Sprint.dt=1./120.;
        auto Windup=LocomotionModel::step(Sprint,T);
        expect(Windup.gait==Gait::Walk,"Attack disengages sprint gait");
        expect(Windup.targetSpeed>300&&Windup.targetSpeed<T.ForwardSpeed,
            "Windup keeps agency while lowering target speed");

        // Release drive is input-authored and bounded: no automatic capsule lunge.
        LocomotionInput Release;Release.velocity={T.ForwardSpeed*T.ReleaseMoveScale,0,0};
        Release.intent={1,0,0};Release.phase=Phase::Release;Release.attackProgress=.41;Release.dt=1./120.;
        auto Driven=LocomotionModel::step(Release,T);
        expect(Driven.targetSpeed>T.ForwardSpeed*T.ReleaseMoveScale,"Forward release bias exists");
        Release.intent={};
        auto StationaryAttack=LocomotionModel::step(Release,T);
        near(StationaryAttack.targetSpeed,0,.001,"Release never creates free motion without movement intent");

        // Compare release displacement against the same combat movement with bias disabled.
        auto DefaultT=T,NoBias=T;NoBias.ReleaseForwardBias=0;
        LocomotionInput Attack;Attack.velocity={T.ForwardSpeed*T.WindupMoveScale,0,0};
        Attack.intent={1,0,0};Attack.phase=Phase::Release;
        Vec WithBias,WithoutBias;
        auto A=Attack,B=Attack;
        for(int I=0;I<60;++I){
            A.attackProgress=(I+.5)/60.;A.dt=1./120.;auto OA=LocomotionModel::step(A,DefaultT);A.velocity=OA.velocity;WithBias+=OA.velocity*A.dt;
            B.attackProgress=(I+.5)/60.;B.dt=1./120.;auto OB=LocomotionModel::step(B,NoBias);B.velocity=OB.velocity;WithoutBias+=OB.velocity*B.dt;
        }
        const double Extra=(WithBias-WithoutBias).length();
        expect(Extra>5&&Extra<12,"Default release drive adds only a small footwork-scale displacement");

        // Crouch and dead states are explicit.
        LocomotionInput Crouch;Crouch.intent={1,0,0};Crouch.crouched=true;
        near(run(1,1./240.,Crouch,T).output.velocity.x,T.ForwardSpeed*T.CrouchMoveScale,.01,"Crouch scale");
        LocomotionInput Dead;Dead.velocity={200,0,0};Dead.intent={1,0,0};Dead.phase=Phase::Dead;
        auto D=run(.1,1./240.,Dead,T);
        expect(D.output.gait==Gait::Disabled&&D.output.velocity.length()<1,"Dead movement brakes to zero");

        std::cout<<"PASS: "<<Checks<<" movement checks\n";
        return 0;
    }catch(const std::exception& E){
        std::cerr<<"FAIL after "<<Checks<<" movement checks: "<<E.what()<<'\n';
        return 1;
    }
}
