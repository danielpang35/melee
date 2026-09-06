#include "CombatPlaytest.h"
#include "Training/CombatLabGameMode.h"
#include "Training/TrainingDummy.h"
#include "Character/MeleeCharacter.h"
#include "Character/MeleeCharacterMovementComponent.h"
#include "Combat/CombatComponent.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "UnrealClient.h"
#include "InputKeyEventArgs.h"
#include "Components/CapsuleComponent.h"

namespace
{
const TCHAR* Names[]={TEXT("right"),TEXT("upper_right"),TEXT("upper_left"),TEXT("left"),TEXT("lower_left"),TEXT("lower_right"),TEXT("stab"),
    TEXT("accel"),TEXT("drag"),TEXT("parry"),TEXT("chamber"),TEXT("wrong_chamber"),TEXT("microdrag_chamber"),TEXT("microdrag_parry"),
    TEXT("feint_to_parry"),TEXT("morph"),TEXT("combo"),TEXT("riposte"),TEXT("parry_look_up"),TEXT("parry_look_down"),TEXT("momentum_and_lunge"),TEXT("tuning_save_load"),
    TEXT("feint_baits_parry"),TEXT("chamber_punishes_feint"),TEXT("chamber_feint_parry"),TEXT("enhanced_strike_key"),TEXT("enhanced_mouse_direction"),
    TEXT("enhanced_move_sprint_jump"),TEXT("enhanced_crouch"),TEXT("enhanced_feint_parry"),TEXT("tuning_panel"),TEXT("lab_presentation"),TEXT("release_flinch"),TEXT("riposte_armor"),TEXT("infinite_damage_target"),TEXT("movement_baseline"),TEXT("movement_response"),TEXT("courtyard_readability")};
void Key(AMeleeCharacter* P,FKey K,EInputEvent Event,float Amount=1)
{
    if(auto* PC=Cast<APlayerController>(P->Controller))PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,Event,Amount));
}
}
UCombatPlaytest::UCombatPlaytest(){PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.TickGroup=TG_PostUpdateWork;}
void UCombatPlaytest::BeginScenario(ACombatLabGameMode* Lab,AMeleeCharacter* P,ATrainingDummy* D)
{
    if(Scenario<0){UserTuning=Lab->Combat.tuning;bHadTuningFile=FFileHelper::LoadFileToString(UserTuningFile,*(FPaths::ProjectSavedDir()/TEXT("Config/CombatTuning.json")));bSavedFixture=true;Lab->Combat.tuning=mcl::Tuning{};}
    ++Scenario;Age=0;ScenarioStartTime=Lab->Combat.time;bAction=bSnapshot=bObserved=false;FirstContact=-1;
    Lab->ResetLab();Lab->bDebug=true;if(Lab->bInspection)Lab->ToggleInspection();D->Pattern.mode=mcl::TrainingMode::Passive;
    P->ResetAt(FVector(0,0,90),FRotator::ZeroRotator);D->ResetAt(FVector(135,0,90),FRotator(0,180,0));
    StartPosition=P->GetActorLocation();
    if(Scenario<=5)P->Combat->Strike(Scenario*60.,Scenario*60.);
    else if(Scenario==6)P->Combat->Stab();
    else if(Scenario==7||Scenario==8||Scenario==14||Scenario==15||Scenario==16)P->Combat->Strike(0,0);
    else if(Scenario<=13||Scenario==17)D->Combat->Strike(0,0);
    if(Scenario==9||Scenario==10)Lab->bDebug=false;
    if(Scenario==18||Scenario==19){P->Combat->Simulation.view.pitch=Scenario==18?45:-45;P->Combat->Simulation.desired=P->Combat->Simulation.view;P->Combat->Parry();Lab->ToggleInspection();}
    if(Scenario==20){D->ResetAt(FVector(900,600,90),FRotator(0,180,0));auto* M=CastChecked<UMeleeCharacterMovementComponent>(P->GetCharacterMovement());M->bSprint=true;}
    if(Scenario==21){const double Original=Lab->Combat.tuning.StrikeRelease;Lab->Combat.tuning.StrikeRelease=.51;
        bool Saved=Lab->SaveTuning();Lab->Combat.tuning.StrikeRelease=.4;bool Loaded=Lab->LoadTuning();
        bObserved=Saved&&Loaded&&FMath::Abs(Lab->Combat.tuning.StrikeRelease-.51)<1e-6;
        Lab->Combat.tuning.StrikeRelease=Original;Lab->SaveTuning();}
    if(Scenario==22||Scenario==23||Scenario==24)D->Combat->Strike(0,0);
    if(Scenario==22)P->Combat->Parry();
    if(Scenario==23||Scenario==24)P->Combat->Strike(0,0);
    if(Scenario==25||Scenario==29)Key(P,EKeys::One,IE_Pressed);
    if(Scenario==26){Key(P,EKeys::MouseX,IE_Axis,30);Key(P,EKeys::MouseY,IE_Axis,52);}
    if(Scenario==27){Key(P,EKeys::W,IE_Pressed);Key(P,EKeys::LeftShift,IE_Pressed);D->ResetAt(FVector(900,600,90),FRotator(0,180,0));}
    if(Scenario==28)Key(P,EKeys::LeftControl,IE_Pressed);
    if(Scenario==30)Key(P,EKeys::F4,IE_Pressed);
    if(Scenario==31){Lab->bDebug=false;P->ResetAt(FVector(0,-110,90),FRotator(0,15,0));D->ResetAt(FVector(350,0,90),FRotator(0,180,0));bObserved=true;}
    if(Scenario==32||Scenario==33){Lab->bDebug=false;D->Combat->Strike(0,0);}
    if(Scenario==34){Lab->bDebug=false;D->ResetAt(FVector(900,600,90),FRotator(0,180,0));Lab->PassiveDummy->ResetAt(FVector(135,0,90),FRotator(0,180,0));P->Combat->Strike(0,0);}
    if(Scenario==35||Scenario==36){
        Lab->bDebug=false;SpeedAt=-1;StopDistance=0;D->ResetAt(FVector(900,600,90),FRotator(0,180,0));
        if(Scenario==35){MovementTuning=Lab->Combat.tuning;Lab->Combat.tuning.ForwardSpeed=420;Lab->Combat.tuning.LateralSpeed=355;Lab->Combat.tuning.Acceleration=2400;Lab->Combat.tuning.Deceleration=2200;Lab->Combat.tuning.GroundFriction=6;}
        Key(P,EKeys::W,IE_Pressed);
    }
    if(Scenario==37){
        Lab->bDebug=false;P->ResetAt(FVector(-450,180,90),FRotator(0,46,0));
        mcl::Vec Point;bool Basin=Lab->Combat.worldSweep(-1,{{-300,650,40},{300,650,40}},4,Point);
        bool Lane=Lab->Combat.worldSweep(-1,{{-650,0,90},{650,0,90}},32,Point);bObserved=Basin&&!Lane;
    }
    UE_LOG(LogTemp,Display,TEXT("COMBAT PLAYTEST BEGIN %s"),Names[Scenario]);
}
void UCombatPlaytest::FinishScenario(ACombatLabGameMode* Lab,AMeleeCharacter* P,ATrainingDummy* D)
{
    bool Passed=bObserved;
    if(Scenario<=8)Passed=FirstContact>0&&D->Combat->Simulation.health==65;
    if(Scenario==0)NeutralContact=FirstContact;
    if(Scenario==7){AccelContact=FirstContact;Passed=Passed&&AccelContact<NeutralContact-.015;}
    if(Scenario==8){DragContact=FirstContact;Passed=Passed&&DragContact>NeutralContact+.015;}
    if(Scenario==11||Scenario==12)Passed=P->Combat->Simulation.health==65;
    if(Scenario==22)Passed=P->Combat->Simulation.health==65;
    if(Scenario==23)Passed=D->Combat->Simulation.health==65&&P->Combat->Simulation.health==100;
    if(Scenario==25)Passed=bObserved&&D->Combat->Simulation.health==65;
    if(Scenario==27)Passed=bObserved&&(P->GetActorLocation()-StartPosition).Size2D()>150;
    if(Scenario==28)Passed=bObserved&&!P->bIsCrouched;
    if(Scenario==18||Scenario==19){auto G=mcl::ParryGeometry::make({0,0,90},{0,Scenario==18?45.:-45.},Lab->Combat.tuning);
        Passed=G.catches({{45,0,6},{60,0,6}},4)==(Scenario==18);}
    if(Scenario==34){const auto& Target=Lab->PassiveDummy->Combat->Simulation;Passed=Target.infiniteHealth&&Target.health==100&&Target.hitsTaken==1&&Target.damageTaken==35;}
    if(Scenario==35||Scenario==36){
        Passed=SpeedAt>0&&P->GetVelocity().Size2D()<1;
        if(Scenario==35){BaselineSpeedAt=SpeedAt;BaselineStop=StopDistance;Lab->Combat.tuning=MovementTuning;}
        else Passed=Passed&&SpeedAt<BaselineSpeedAt&&StopDistance<BaselineStop&&StopDistance<25;
        UE_LOG(LogTemp,Display,TEXT("MOVEMENT RESPONSE %d: 90 percent speed %.4f seconds, stopping %.2f cm"),Scenario,SpeedAt,StopDistance);
    }
    Results.Add(FString::Printf(TEXT("{\"scenario\":\"%s\",\"passed\":%s,\"first_contact_seconds\":%.6f}"),Names[Scenario],Passed?TEXT("true"):TEXT("false"),FirstContact));
    UE_LOG(LogTemp,Display,TEXT("COMBAT PLAYTEST %s: %s (contact %.4f)"),Names[Scenario],Passed?TEXT("PASS"):TEXT("FAIL"),FirstContact);
    if(auto* PC=Cast<APlayerController>(P->Controller))PC->FlushPressedKeys();
}
void UCombatPlaytest::TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* TickFunction)
{
    Super::TickComponent(Dt,TickType,TickFunction);if(bFinished)return;
    auto* Lab=Cast<ACombatLabGameMode>(GetOwner());auto* P=Cast<AMeleeCharacter>(UGameplayStatics::GetPlayerPawn(this,0));
    if(!Lab||!P||!Lab->AttackingDummy)return;auto* D=Lab->AttackingDummy.Get();
    if(Scenario<0){Age+=Dt;if(Age<1)return;BeginScenario(Lab,P,D);return;}
    if(Scenario==30)Age+=Dt;else Age=Lab->Combat.time-ScenarioStartTime;
    auto& PS=P->Combat->Simulation;auto& DS=D->Combat->Simulation;
    for(auto E:Lab->Combat.events){
        if(E.result==mcl::Resolution::Hit&&E.attacker==PS.id&&FirstContact<0)FirstContact=E.time-ScenarioStartTime;
        if((Scenario==9||Scenario==13||Scenario==17||Scenario==24)&&E.result==mcl::Resolution::Parry&&E.defender==PS.id)bObserved=true;
        if((Scenario==32||Scenario==33)&&E.result==mcl::Resolution::Hit&&E.defender==PS.id)
            bObserved=PS.state.phase==(Scenario==33?mcl::Phase::Release:mcl::Phase::Idle)&&PS.state.isRiposte==(Scenario==33);
        if(Scenario==10&&E.result==mcl::Resolution::Chamber&&E.defender==PS.id)bObserved=true;
    }
    if(PS.state.phase==mcl::Phase::Release&&(Scenario==7||Scenario==8))PS.look((Scenario==7?-80:80)*Dt,0,Dt,Lab->Combat.tuning);
    if(DS.state.phase==mcl::Phase::Release&&(Scenario==12||Scenario==13))DS.look(45*Dt,0,Dt,Lab->Combat.tuning);
    if(!bAction){
        if((Scenario==9||Scenario==13||Scenario==17)&&Age>.51){P->Combat->Parry();bAction=true;}
        if((Scenario==10||Scenario==11||Scenario==12)&&Age>(Scenario==12?.51:.6)){if(Scenario==10)Key(P,EKeys::Four,IE_Pressed);else P->Combat->Strike(Scenario==11?60:180,Scenario==11?60:180);bAction=true;}
        if(Scenario==14&&Age>.2){P->Combat->Feint();P->Combat->Parry();bObserved=PS.state.phase==mcl::Phase::Parry;bAction=true;}
        if(Scenario==15&&Age>.2){P->Combat->Stab();bObserved=PS.state.morphed&&PS.state.attack.kind==mcl::AttackKind::Stab;bAction=true;}
        if(Scenario==16&&PS.state.canCombo(Lab->Combat.tuning)){P->Combat->Strike(0,0);bAction=true;}
    }
    if((Scenario==32||Scenario==33)&&!bAction&&Age>(Scenario==33?.38:.18)){
        if(Scenario==33)PS.state.parrySuccess(Lab->Combat.tuning);P->Combat->Strike(0,0);bAction=true;
    }
    if(Scenario==16&&PS.state.last==mcl::Resolution::Combo)bObserved=PS.state.attack.angle==180;
    if(Scenario==17&&bObserved&&PS.state.riposteRemaining>0){P->Combat->Strike(60,60);bObserved=PS.state.last==mcl::Resolution::Riposte;}
    if(Scenario==20){auto* M=CastChecked<UMeleeCharacterMovementComponent>(P->GetCharacterMovement());
        P->AddMovementInput(FVector::ForwardVector,Age<1.7?1.f:-1.f);M->ForwardInput=Age<1.7?1:-1;
        if(Age>1.1&&!bAction){P->Combat->Strike(0,0);bAction=true;}
        if(M->Lunge.displacement>10&&M->Momentum.value>.4)bObserved=true;
    }
    if(Scenario==22&&Age>.2&&!bAction){D->Combat->Feint();D->Combat->Stab();bAction=true;}
    if(Scenario==23&&Age>.2&&!bAction){D->Combat->Feint();bAction=true;}
    if(Scenario==24&&Age>.2&&!bAction){P->Combat->Feint();bAction=true;}
    if(Scenario==24&&Age>.51&&Age<.53)P->Combat->Parry();
    if(Scenario==25){if(Age>.04)Key(P,EKeys::One,IE_Released,0);if(PS.state.serial>0&&PS.state.attack.angle==0)bObserved=true;}
    if(Scenario==26){if(Age>.03&&!bAction){Key(P,EKeys::LeftMouseButton,IE_Pressed);bAction=true;}if(Age>.07)Key(P,EKeys::LeftMouseButton,IE_Released,0);
        if(PS.state.serial>0&&PS.state.attack.angle==60)bObserved=true;}
    if(Scenario==27){if(Age>.5&&!bAction){Key(P,EKeys::SpaceBar,IE_Pressed);bAction=true;}if(Age>.6)Key(P,EKeys::SpaceBar,IE_Released,0);
        if(P->GetCharacterMovement()->IsFalling()&&P->GetVelocity().Z>10)bObserved=true;
        if(Age>1.5){Key(P,EKeys::W,IE_Released,0);Key(P,EKeys::LeftShift,IE_Released,0);}}
    if(Scenario==28){if(P->bIsCrouched&&P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()<60)bObserved=true;if(Age>1.2)Key(P,EKeys::LeftControl,IE_Released,0);}
    if(Scenario==29){if(Age>.03)Key(P,EKeys::One,IE_Released,0);if(Age>.2&&!bAction){Key(P,EKeys::Q,IE_Pressed);bAction=true;}
        if(Age>.24){Key(P,EKeys::Q,IE_Released,0);Key(P,EKeys::RightMouseButton,IE_Pressed);}if(PS.state.phase==mcl::Phase::Parry)bObserved=true;}
    if(Scenario==30){if(Lab->bTuningOpen)bObserved=true;if(Age>1.2&&Lab->bTuningOpen)Lab->ToggleTuning();Key(P,EKeys::F4,IE_Released,0);}
    if(Scenario==35||Scenario==36){
        if(SpeedAt<0&&P->GetVelocity().Size2D()>=Lab->Combat.tuning.ForwardSpeed*.9)SpeedAt=Age;
        if(Age>.6&&!bAction){StopPosition=P->GetActorLocation();Key(P,EKeys::W,IE_Released,0);bAction=true;}
        if(bAction)StopDistance=(P->GetActorLocation()-StopPosition).Size2D();
    }
    if(P->Controller)P->Controller->SetControlRotation(FRotator(PS.view.pitch,PS.view.yaw,0));
    const double SnapshotAt=Scenario==33?.8:(Scenario==18||Scenario==19)?.18:Scenario==10?.82:Scenario==9?.62:.72;
    if(!bSnapshot&&Age>SnapshotAt){
        FString Folder=FPaths::ProjectSavedDir()/TEXT("Playtests");IFileManager::Get().MakeDirectory(*Folder,true);
        FScreenshotRequest::RequestScreenshot(Folder/FString::Printf(TEXT("%02d_%s.png"),Scenario,Names[Scenario]),true,false,false);
        bSnapshot=true;
    }
    if(Age>2.2){FinishScenario(Lab,P,D);if(Scenario+1<UE_ARRAY_COUNT(Names))BeginScenario(Lab,P,D);
        else{bFinished=true;const FString Json=TEXT("{\"kind\":\"scripted_in_engine\",\"results\":[\n")+FString::Join(Results,TEXT(",\n"))+TEXT("\n]}");
            FFileHelper::SaveStringToFile(Json,*(FPaths::ProjectSavedDir()/TEXT("Playtests/results.json")));
            UE_LOG(LogTemp,Display,TEXT("COMBAT PLAYTEST COMPLETE"));Lab->ResetLab();D->Pattern.mode=mcl::TrainingMode::Right;
            if(FParse::Param(FCommandLine::Get(),TEXT("CombatPlaytestQuit")))FPlatformMisc::RequestExit(false);
        }
    }
}

void UCombatPlaytest::EndPlay(const EEndPlayReason::Type Reason)
{
    if(bSavedFixture){
        if(auto* Lab=Cast<ACombatLabGameMode>(GetOwner()))Lab->Combat.tuning=UserTuning;
        const FString Path=FPaths::ProjectSavedDir()/TEXT("Config/CombatTuning.json");
        if(bHadTuningFile)FFileHelper::SaveStringToFile(UserTuningFile,*Path);
        else IFileManager::Get().Delete(*Path);
    }
    Super::EndPlay(Reason);
}
