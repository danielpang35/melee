#include "Misc/AutomationTest.h"
#include "Combat/CombatSimulation.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCombatStateFlow,"MeleeCombatLab.StateFlow",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCombatStateFlow::RunTest(const FString& Parameters)
{
    mcl::Tuning T;mcl::AttackStateMachine S;
    TestTrue(TEXT("Attack accepted"),S.start({},T));S.advance(.2,T);
    TestTrue(TEXT("Feint accepted"),S.feint(T));TestTrue(TEXT("Parry immediately after feint"),S.parry(T));
    S.parrySuccess(T);TestTrue(TEXT("Riposte accepted"),S.start({},T));
    TestEqual(TEXT("Riposte windup"),S.definition.windup,T.RiposteWindup);return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCombatFrameRate,"MeleeCombatLab.FrameRates",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCombatFrameRate::RunTest(const FString& Parameters)
{
    double Reference=-1;
    for(int FPS:{30,60,120,144,240}){
        mcl::CombatSimulation Sim;mcl::Combatant A,B;A.id=1;B.id=2;
        A.reset({0,0,88},{},Sim.tuning);B.reset({135,0,88},{180,0},Sim.tuning);Sim.actors={&A,&B};A.start({},Sim.tuning);
        double HitTime=-1;
        for(int Frame=0;Frame<FPS*2;++Frame){Sim.advance(1./FPS);for(auto E:Sim.events)if(E.result==mcl::Resolution::Hit&&HitTime<0)HitTime=E.time;}
        TestTrue(TEXT("Hit registered"),HitTime>0);if(Reference<0)Reference=HitTime;
        TestTrue(TEXT("Contact time equivalent"),FMath::Abs(HitTime-Reference)<.009);
        TestEqual(TEXT("Once per target"),B.health,65.);
    }
    return true;
}
#endif
