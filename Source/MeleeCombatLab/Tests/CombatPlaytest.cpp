#include "CombatPlaytest.h"
#include "Training/CombatLabGameMode.h"
#include "Training/TrainingDummy.h"
#include "Character/MeleeCharacter.h"
#include "Character/MeleeCharacterMovementComponent.h"
#include "Combat/CombatComponent.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"
#include "Engine/GameViewportClient.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "UnrealClient.h"
#include "InputKeyEventArgs.h"
#include "Components/CapsuleComponent.h"
#include "Camera/WeaponPresentationComponent.h"
#include "Visual/KnightPresentation.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"

namespace
{
const TCHAR* Names[]={TEXT("right"),TEXT("upper_right"),TEXT("upper_left"),TEXT("left"),TEXT("lower_left"),TEXT("lower_right"),TEXT("stab"),
    TEXT("accel"),TEXT("drag"),TEXT("parry"),TEXT("chamber"),TEXT("wrong_chamber"),TEXT("microdrag_chamber"),TEXT("microdrag_parry"),
    TEXT("feint_to_parry"),TEXT("morph"),TEXT("combo"),TEXT("riposte"),TEXT("parry_look_up"),TEXT("parry_look_down"),TEXT("combat_footwork"),TEXT("tuning_save_load"),
    TEXT("feint_baits_parry"),TEXT("chamber_punishes_feint"),TEXT("chamber_feint_parry"),TEXT("enhanced_strike_key"),TEXT("enhanced_mouse_direction"),
    TEXT("enhanced_move_sprint_jump"),TEXT("enhanced_crouch"),TEXT("enhanced_feint_parry"),TEXT("tuning_panel"),TEXT("lab_presentation"),TEXT("release_flinch"),TEXT("riposte_armor"),TEXT("infinite_damage_target"),TEXT("movement_baseline"),TEXT("movement_response"),TEXT("courtyard_readability"),
    TEXT("air_fp_right"),TEXT("air_fp_upper_right"),TEXT("air_fp_upper_left"),TEXT("air_fp_left"),TEXT("air_fp_lower_left"),TEXT("air_fp_lower_right"),TEXT("air_fp_stab"),
    TEXT("air_external_right"),TEXT("air_external_upper_right"),TEXT("air_external_upper_left"),TEXT("air_external_left"),TEXT("air_external_lower_left"),TEXT("air_external_lower_right"),TEXT("air_external_stab"),
    TEXT("air_fp_up"),TEXT("air_fp_down"),TEXT("air_external_up"),TEXT("air_external_down")};
void Key(AMeleeCharacter* P,FKey K,EInputEvent Event,float Amount=1)
{
    if(auto* PC=Cast<APlayerController>(P->Controller))PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,Event,Amount));
}
}
UCombatPlaytest::UCombatPlaytest(){PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.TickGroup=TG_PostUpdateWork;}
void UCombatPlaytest::DestroyReviewWall()
{
    if(auto* Wall=ReviewWall.Get()){
        Wall->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Wall->Destroy();
    }
    ReviewWall.Reset();
}
void UCombatPlaytest::StartReviewAttack(AMeleeCharacter* P)
{
    bReviewAttackPending=false;
    if(FParse::Param(FCommandLine::Get(),TEXT("NeutralPoseReview")))return;
    if(ReviewSequence==TEXT("parry")){P->Combat->Parry();bReviewSequenceObserved=P->Combat->Simulation.state.phase==mcl::Phase::Parry;return;}
    if(ReviewSequence==TEXT("riposte")){
        if(auto* Lab=Cast<ACombatLabGameMode>(GetOwner()))Lab->AttackingDummy->Combat->Strike(0,0);
        return;
    }
    const int Direction=(Scenario-38)%7;
    if(Direction==6&&Scenario<52&&!bReviewAngle)P->Combat->Stab();
    else {const double Angle=bReviewAngle?ReviewAngle:Scenario>=52?60.:Direction*60.;P->Combat->Strike(Angle,Angle);}
}
void UCombatPlaytest::UpdateReviewCamera(AMeleeCharacter* P)
{
    if(ReviewCamera.IsEmpty()||ReviewCamera==TEXT("firstperson"))return;
    auto* PC=Cast<APlayerController>(P->Controller);
    auto* Camera=PC?Cast<ACameraActor>(PC->GetViewTarget()):nullptr;
    if(!Camera)return;
    FVector Offset(340,0,35),FocusOffset(15,0,20);
    if(ReviewCamera==TEXT("side"))Offset=FVector(15,350,30);
    else if(ReviewCamera==TEXT("rear3q"))Offset=FVector(-260,260,55);
    else if(ReviewCamera==TEXT("defender")){Offset=FVector(240,0,65);FocusOffset=FVector(0,0,35);}
    const FVector Focus=P->GetActorLocation();
    const FRotator Facing(0,P->Combat->Simulation.view.yaw,0);
    const FVector At=Focus+Facing.RotateVector(Offset);
    Camera->SetActorLocationAndRotation(At,(Focus+Facing.RotateVector(FocusOffset)-At).Rotation());
    Camera->GetCameraComponent()->SetFieldOfView(ReviewCamera==TEXT("defender")?85.f:65.f);
    // This component runs after actor presentation. Refresh the cached view so
    // the screenshot and pose telemetry refer to this frame's chosen camera.
    if(PC->PlayerCameraManager)PC->PlayerCameraManager->UpdateCamera(0.f);
}
void UCombatPlaytest::BeginScenario(ACombatLabGameMode* Lab,AMeleeCharacter* P,ATrainingDummy* D)
{
    if(Scenario<0){UserTuning=Lab->Combat.tuning;bHadTuningFile=FFileHelper::LoadFileToString(UserTuningFile,*(FPaths::ProjectSavedDir()/TEXT("Config/CombatTuning.json")));bSavedFixture=true;Lab->Combat.tuning=mcl::Tuning{};}
    if(Scenario<0){
        // Pose audit/trace reads must follow presentation, not merely simulation.
        AddTickPrerequisiteActor(P);AddTickPrerequisiteActor(D);
        OutputFolder=FPaths::ProjectSavedDir()/TEXT("Playtests");
        MotionFrameFolder=FPaths::ProjectSavedDir()/TEXT("MotionReviewFrames");
        FString Tag;
        if(FParse::Value(FCommandLine::Get(),TEXT("ArmReviewTag="),Tag)){
            Tag=FPaths::MakeValidFileName(Tag);
            if(!Tag.IsEmpty()){
                OutputFolder=FPaths::ProjectSavedDir()/TEXT("ArmRepair")/Tag;
                MotionFrameFolder=OutputFolder/TEXT("Frames");
            }
        }
        IFileManager::Get().MakeDirectory(*OutputFolder,true);
        // Hardware input enters through the viewport; simulated PC key events
        // below bypass it and continue to exercise Enhanced Input normally.
        if(auto* Viewport=GetWorld()->GetGameViewport()){
            bPriorIgnoreInput=Viewport->IgnoreInput();Viewport->SetIgnoreInput(true);
        }
        OriginalBeforeStep=Lab->Combat.beforeStep;
        Lab->Combat.beforeStep=[this,Lab,P,D](double Step){
            if(OriginalBeforeStep)OriginalBeforeStep(Step);
            auto& Player=P->Combat->Simulation;
            if(Scenario>=38){
                if(bReviewAttackPending&&Lab->Combat.time-ScenarioStartTime+1e-10>=ReviewLeadIn)StartReviewAttack(P);
                if(ReviewSequence==TEXT("combo")&&!bReviewSequenceIssued&&Player.state.canCombo(Lab->Combat.tuning)){
                    P->Combat->Strike(Player.state.attack.angle,Player.state.attack.angle);
                    bReviewSequenceIssued=Player.state.comboQueued;
                }
                if(ReviewSequence==TEXT("combo")&&Player.state.isCombo)bReviewSequenceObserved=true;
                if(ReviewSequence==TEXT("riposte")){
                    const auto& Incoming=D->Combat->Simulation.state;
                    if(!bReviewParryIssued&&Incoming.phase==mcl::Phase::Windup&&Incoming.elapsed>=Incoming.duration()-.08){
                        P->Combat->Parry();bReviewParryIssued=true;
                    }
                    if(!bReviewSequenceIssued&&Player.state.riposteRemaining>0){
                        const double Angle=bReviewAngle?ReviewAngle:60.;P->Combat->Strike(Angle,Angle);
                        bReviewSequenceIssued=Player.state.isRiposte;bReviewSequenceObserved=bReviewSequenceIssued;
                    }
                }
                if(Player.state.phase==mcl::Phase::Windup||Player.state.phase==mcl::Phase::Release)
                    ReviewAttackStartTime=Lab->Combat.time-Player.state.attackAge;
            }
            if((Scenario==7||Scenario==8)&&Player.state.phase==mcl::Phase::Release)
                Player.look((Scenario==7?-80.:80.)*Step,0,Step,Lab->Combat.tuning);
            if(Scenario>=38&&bReviewOutcome&&ReviewOutcome==TEXT("parry")&&!bReviewParryIssued&&
                Player.state.phase==mcl::Phase::Windup&&Player.state.elapsed>=Player.state.duration()-.08){
                bReviewParryIssued=true;D->Combat->Parry();
                UE_LOG(LogTemp,Display,TEXT("MOTION OUTCOME defender parry at attack %.6f"),Player.state.attackAge);
            }
        };
    }
    if(Scenario<0&&FParse::Param(FCommandLine::Get(),TEXT("MotionReview"))){
        FParse::Value(FCommandLine::Get(),TEXT("MotionReviewScenario="),ReviewOnlyScenario);
        if(ReviewOnlyScenario<38||ReviewOnlyScenario>=UE_ARRAY_COUNT(Names))ReviewOnlyScenario=-1;
        FString ReviewSet;FParse::Value(FCommandLine::Get(),TEXT("MotionReviewSet="),ReviewSet);
        bReviewCoreSet=ReviewSet.Equals(TEXT("core"),ESearchCase::IgnoreCase);
        if(bReviewCoreSet)ReviewOnlyScenario=-1;
        FParse::Value(FCommandLine::Get(),TEXT("MotionReviewCamera="),ReviewCamera);ReviewCamera.ToLowerInline();
        if(ReviewCamera!=TEXT("front")&&ReviewCamera!=TEXT("side")&&ReviewCamera!=TEXT("rear3q")&&ReviewCamera!=TEXT("defender")&&ReviewCamera!=TEXT("firstperson"))ReviewCamera.Empty();
        FParse::Value(FCommandLine::Get(),TEXT("MotionReviewPose="),ReviewPose);ReviewPose.ToLowerInline();
        FParse::Value(FCommandLine::Get(),TEXT("MotionReviewSequence="),ReviewSequence);ReviewSequence.ToLowerInline();
        if(ReviewSequence!=TEXT("combo")&&ReviewSequence!=TEXT("riposte")&&ReviewSequence!=TEXT("parry"))ReviewSequence.Empty();
        bReviewOutcome=FParse::Value(FCommandLine::Get(),TEXT("MotionReviewOutcome="),ReviewOutcome);ReviewOutcome.ToLowerInline();
        if(bReviewOutcome&&ReviewOutcome!=TEXT("miss")&&ReviewOutcome!=TEXT("body")&&ReviewOutcome!=TEXT("parry")&&ReviewOutcome!=TEXT("wall")){
            UE_LOG(LogTemp,Warning,TEXT("Unknown MotionReviewOutcome '%s'; using existing air review"),*ReviewOutcome);
            bReviewOutcome=false;ReviewOutcome.Empty();
        }
        FParse::Value(FCommandLine::Get(),TEXT("MotionReviewLeadIn="),ReviewLeadIn);ReviewLeadIn=FMath::Clamp(ReviewLeadIn,0.,2.);
        bReviewPitch=FParse::Value(FCommandLine::Get(),TEXT("MotionReviewPitch="),ReviewPitch);ReviewPitch=FMath::Clamp(ReviewPitch,-85.,85.);
        bReviewAngle=FParse::Value(FCommandLine::Get(),TEXT("MotionReviewAngle="),ReviewAngle);
        if(bReviewCoreSet)bReviewAngle=false; // The core set is the four authored 0/60/120/180-degree cuts.
        bReviewKeys=FParse::Param(FCommandLine::Get(),TEXT("MotionReviewKeys"));
        ReviewFrameRows.Add(TEXT("frame,scenario,scenario_seconds,attack_seconds,phase,phase_progress,angle,pitch,pose,camera,actor_x,actor_y,actor_z,nominal_attack_seconds,phase_elapsed,phase_duration,attack_serial,is_combo,is_riposte,sequence,state_resolution"));
        if(bReviewOutcome){
            ReviewFrameRows[0]+=TEXT(",requested_outcome,resolution,target_health,target_hits,player_health");
        }
        ReviewContactRows.Add(TEXT("scenario,requested_outcome,resolution,attacker,defender,scenario_seconds,attack_seconds,point_x,point_y,point_z,nominal_attack_seconds"));
        Scenario=bReviewCoreSet?44:ReviewOnlyScenario>=38?ReviewOnlyScenario-1:37;
    }
    DestroyReviewWall();
    ++Scenario;Age=0;ScenarioStartTime=Lab->Combat.time;bAction=bSnapshot=bObserved=false;FirstContact=-1;
    bReviewParryIssued=false;bReviewFixtureReady=true;ReviewExpectedContacts=ReviewUnexpectedContacts=0;
    bReviewSequenceIssued=bReviewSequenceObserved=false;ReviewAttackStartTime=-1;ReviewKeySerial=0;ReviewKeyPhase=mcl::Phase::Dead;
    bReviewFinishPending=false;
    ReviewContactTime=-1;ReviewContactResolution=mcl::Resolution::None;
    MotionSnapshot=0;ReviewKey=0;MaxBladeError=0;MaxProjectionError=0;MaxReleaseProjectionError=0;MaxArmStretch=1.;MaxArmSurfaceStretch=1.;
    ReviewScenarioFrameRows.Reset();
    if(ReviewFrameRows.Num()>0)ReviewScenarioFrameRows.Add(ReviewFrameRows[0]);
    Lab->ResetLab();Lab->bDebug=true;if(Lab->bInspection)Lab->ToggleInspection();D->Pattern.mode=mcl::TrainingMode::Passive;
    P->ResetAt(FVector(0,0,90),FRotator::ZeroRotator);D->ResetAt(FVector(135,0,90),FRotator(0,180,0));
    P->Combat->Simulation.externalView=Scenario!=7&&Scenario!=8;
    StartPosition=P->GetActorLocation();
    if(Scenario<=5)P->Combat->Strike(Scenario*60.,Scenario*60.);
    else if(Scenario==6)P->Combat->Stab();
    else if(Scenario==7||Scenario==8||Scenario==14||Scenario==15||Scenario==16)P->Combat->Strike(0,0);
    else if(Scenario<=13||Scenario==17)D->Combat->Strike(0,0);
    if(Scenario==9||Scenario==10)Lab->bDebug=false;
    if(Scenario==18||Scenario==19){P->Combat->Simulation.view.pitch=Scenario==18?45:-45;P->Combat->Simulation.desired=P->Combat->Simulation.view;P->Combat->Parry();Lab->ToggleInspection();}
    if(Scenario==20){D->ResetAt(FVector(900,600,90),FRotator(0,180,0));auto* M=CastChecked<UMeleeCharacterMovementComponent>(P->GetCharacterMovement());M->bSprintRequested=true;}
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
        if(Scenario==35){MovementTuning=Lab->Combat.tuning;Lab->Combat.tuning.ForwardSpeed=320;Lab->Combat.tuning.LateralSpeed=280;Lab->Combat.tuning.Acceleration=1800;Lab->Combat.tuning.PrecisionAcceleration=2200;Lab->Combat.tuning.RedirectAcceleration=2600;Lab->Combat.tuning.ReverseAcceleration=3200;Lab->Combat.tuning.Deceleration=2200;Lab->Combat.tuning.SprintDeceleration=2600;}
        Key(P,EKeys::W,IE_Pressed);
    }
    if(Scenario==37){
        Lab->bDebug=false;P->ResetAt(FVector(-450,180,90),FRotator(0,46,0));
        mcl::Vec Point,Normal;bool Basin=Lab->Combat.worldSweep(-1,{{-300,650,40},{300,650,40}},4,Point,Normal);
        bool Lane=Lab->Combat.worldSweep(-1,{{-650,0,90},{650,0,90}},32,Point,Normal);bObserved=Basin&&!Lane;
    }
    if(Scenario>=38){
        D->ResetAt(FVector(900,600,90),FRotator(0,180,0));Lab->bDebug=false;
        if(ReviewSequence==TEXT("riposte"))D->ResetAt(FVector(135,0,90),FRotator(0,180,0));
        if(bReviewOutcome&&(ReviewOutcome==TEXT("body")||ReviewOutcome==TEXT("parry")))
            D->ResetAt(FVector(135,0,90),FRotator(0,180,0));
        if(bReviewOutcome&&ReviewOutcome==TEXT("wall")){
            // A real Visibility-blocking surface in the standard contact lane.
            // It belongs only to this review and never modifies arena assets.
            auto* Wall=GetWorld()->SpawnActor<AStaticMeshActor>(FVector(115,0,150),FRotator::ZeroRotator);
            ReviewWall=Wall;bReviewFixtureReady=Wall!=nullptr;
            if(Wall){
                auto* Mesh=Wall->GetStaticMeshComponent();Mesh->SetMobility(EComponentMobility::Movable);
                auto* Cube=LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube"));
                bReviewFixtureReady=Cube!=nullptr;Mesh->SetStaticMesh(Cube);
                Wall->SetActorScale3D(FVector(.1,4.,3.));Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
                Mesh->SetCollisionResponseToAllChannels(ECR_Block);
            }
        }
        const bool External=ReviewCamera.IsEmpty()?((Scenario>=45&&Scenario<=51)||Scenario>=54):ReviewCamera!=TEXT("firstperson");
        if(External){Lab->ToggleInspection();Lab->bDebug=false;}
        if(Scenario>=52){
            const double Pitch=Scenario%2==0?85.:-85.;
            P->Combat->Simulation.view.pitch=Pitch;P->Combat->Simulation.desired=P->Combat->Simulation.view;
        }
        if(bReviewPitch){P->Combat->Simulation.view.pitch=ReviewPitch;P->Combat->Simulation.desired=P->Combat->Simulation.view;}
        if(ReviewPose==TEXT("crouch"))Key(P,EKeys::LeftControl,IE_Pressed);
        if(ReviewPose==TEXT("moving"))Key(P,EKeys::D,IE_Pressed);
        bReviewAttackPending=ReviewLeadIn>0;
        if(!bReviewAttackPending)StartReviewAttack(P);
        UpdateReviewCamera(P);
        bObserved=true;
        if(Scenario==38&&FParse::Param(FCommandLine::Get(),TEXT("LeanClearanceAudit"))){
            mcl::Combatant Probe;Probe.reset({100,0,90},{0,85},Lab->Combat.tuning);
            const double Free=Lab->Combat.constrainLean(Probe);
            auto* Wall=GetWorld()->SpawnActor<AStaticMeshActor>(FVector(30,0,160),FRotator::ZeroRotator);
            auto* Mesh=Wall->GetStaticMeshComponent();Mesh->SetMobility(EComponentMobility::Movable);
            Mesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));
            Wall->SetActorScale3D(FVector(.1,2.,3.));Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
            Mesh->SetCollisionResponseToAllChannels(ECR_Block);
            const double Blocked=Lab->Combat.constrainLean(Probe);
            Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);Wall->Destroy();
            Probe.bodyHalfHeight=60;Probe.eyeHeight=54;Probe.position.z=62;Probe.view.pitch=-45;
            const double Crouched=Lab->Combat.constrainLean(Probe);
            bObserved=Free>.99&&Blocked>0.&&Blocked<.9&&Crouched>.25;
            UE_LOG(LogTemp,Display,TEXT("LEAN CLEARANCE free=%.5f wall=%.5f crouch=%.5f passed=%d"),Free,Blocked,Crouched,bObserved);
        }
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
    FString OutcomeFields;
    if(Scenario>=38&&!ReviewSequence.IsEmpty()){
        const auto& Player=P->Combat->Simulation;const auto& Target=D->Combat->Simulation;
        const bool Riposte=ReviewSequence==TEXT("riposte"),Combo=ReviewSequence==TEXT("combo");
        bool DamageOK=Player.health==100&&Player.hitsTaken==0&&Player.damageTaken==0&&
            Target.hitsTaken==(Riposte?1:0)&&Target.damageTaken==(Riposte?Lab->Combat.tuning.Damage:0.);
        for(const auto* Actor:Lab->Combat.actors)if(Actor!=&Target&&Actor!=&Player)
            DamageOK=DamageOK&&Actor->hitsTaken==0&&Actor->damageTaken==0;
        Passed=Passed&&bReviewSequenceObserved&&DamageOK&&Player.state.phase==mcl::Phase::Idle&&
            Player.state.serial==(Combo?2:Riposte?1:0)&&ReviewUnexpectedContacts==0&&ReviewExpectedContacts==(Riposte?2:0);
        OutcomeFields=FString::Printf(TEXT(",\"sequence\":\"%s\",\"sequence_observed\":%s"),*ReviewSequence,bReviewSequenceObserved?TEXT("true"):TEXT("false"));
    }
    if(Scenario>=38&&bReviewOutcome){
        const auto& Player=P->Combat->Simulation;const auto& Target=D->Combat->Simulation;
        const bool Body=ReviewOutcome==TEXT("body"),Miss=ReviewOutcome==TEXT("miss");
        const auto Expected=Body?mcl::Resolution::Hit:ReviewOutcome==TEXT("parry")?mcl::Resolution::Parry:
            ReviewOutcome==TEXT("wall")?mcl::Resolution::Wall:mcl::Resolution::Miss;
        const auto Observed=ReviewContactResolution==mcl::Resolution::None?Player.state.last:ReviewContactResolution;
        bool DamageOK=Player.health==100&&Player.hitsTaken==0&&Player.damageTaken==0&&
            Target.hitsTaken==(Body?1:0)&&FMath::Abs(Target.damageTaken-(Body?Lab->Combat.tuning.Damage:0.))<1e-6&&
            FMath::Abs(Target.health-(Body?100.-Lab->Combat.tuning.Damage:100.))<1e-6;
        for(const auto* Actor:Lab->Combat.actors)if(Actor!=&Target&&Actor!=&Player)
            DamageOK=DamageOK&&Actor->hitsTaken==0&&Actor->damageTaken==0;
        Passed=Passed&&bReviewFixtureReady&&Observed==Expected&&ReviewExpectedContacts==(Miss?0:1)&&
            ReviewUnexpectedContacts==0&&DamageOK;
        OutcomeFields=FString::Printf(TEXT(",\"requested_outcome\":\"%s\",\"expected_resolution\":\"%s\",\"observed_resolution\":\"%s\",\"outcome_contact_seconds\":%.6f,\"expected_contacts\":%d,\"unexpected_contacts\":%d,\"damage_ok\":%s,\"target_health\":%.6f,\"target_hits\":%d"),
            *ReviewOutcome,UTF8_TO_TCHAR(mcl::resultName(Expected)),UTF8_TO_TCHAR(mcl::resultName(Observed)),ReviewContactTime,
            ReviewExpectedContacts,ReviewUnexpectedContacts,DamageOK?TEXT("true"):TEXT("false"),Target.health,Target.hitsTaken);
        UE_LOG(LogTemp,Display,TEXT("MOTION OUTCOME %s requested=%s observed=%s expected_contacts=%d unexpected_contacts=%d damage_ok=%d passed=%d"),
            Names[Scenario],*ReviewOutcome,UTF8_TO_TCHAR(mcl::resultName(Observed)),ReviewExpectedContacts,ReviewUnexpectedContacts,DamageOK,Passed);
    }
    OutcomeFields+=FString::Printf(TEXT(",\"max_projection_offset_cm\":%.6f,\"max_release_projection_error_cm\":%.6f"),MaxProjectionError,MaxReleaseProjectionError);
    Results.Add(FString::Printf(TEXT("{\"scenario\":\"%s\",\"passed\":%s,\"first_contact_seconds\":%.6f,\"max_blade_error_cm\":%.6f,\"max_arm_stretch\":%.6f,\"max_arm_surface_edge_ratio\":%.6f%s}"),Names[Scenario],Passed?TEXT("true"):TEXT("false"),FirstContact,MaxBladeError,MaxArmStretch,MaxArmSurfaceStretch,*OutcomeFields));
    UE_LOG(LogTemp,Display,TEXT("COMBAT PLAYTEST %s: %s (contact %.4f)"),Names[Scenario],Passed?TEXT("PASS"):TEXT("FAIL"),FirstContact);
    if(ReviewScenarioFrameRows.Num()>1){
        const FString Folder=OutputFolder/TEXT("Scenarios")/FString::Printf(TEXT("%02d_%s"),Scenario,Names[Scenario]);
        IFileManager::Get().MakeDirectory(*Folder,true);
        FFileHelper::SaveStringToFile(FString::Join(ReviewScenarioFrameRows,TEXT("\n"))+TEXT("\n"),*(Folder/TEXT("frames.csv")));
    }
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
    MaxBladeError=FMath::Max(MaxBladeError,P->Presentation->BladeError);
    MaxProjectionError=FMath::Max(MaxProjectionError,P->Presentation->ProjectionError);
    MaxReleaseProjectionError=FMath::Max(MaxReleaseProjectionError,P->Presentation->ActiveBladeError);
    MaxArmStretch=FMath::Max(MaxArmStretch,P->Knight->MaxArmStretch);
    if(Scenario>=38&&!bReviewFinishPending){
        UpdateReviewCamera(P);
        bObserved=bObserved&&MaxBladeError<.01&&MaxReleaseProjectionError<.01&&MaxProjectionError<35.&&MaxArmStretch<1.015&&
            ((bReviewOutcome&&ReviewOutcome==TEXT("body"))||ReviewSequence==TEXT("riposte")||FirstContact<0);
        if(Scenario<52&&!(bReviewOutcome&&ReviewOutcome==TEXT("wall")))bObserved=bObserved&&PS.state.last!=mcl::Resolution::Wall;
        const double CaptureAt[]={.50,.80,1.12,1.45};
        const bool Review=FParse::Param(FCommandLine::Get(),TEXT("MotionReview"));
        const bool Capturing=Review&&(FParse::Param(FCommandLine::Get(),TEXT("AllMotionFrames"))||Scenario==38||Scenario==45||Scenario==46||Scenario==49||Scenario==51);
        if(Capturing){
            const FString Folder=MotionFrameFolder;IFileManager::Get().MakeDirectory(*Folder,true);
            const FString Filename=FString::Printf(TEXT("frame_%05d.png"),ReviewFrame++);
            FScreenshotRequest::RequestScreenshot(Folder/Filename,true,false,false);
            P->Knight->SaveMotionTrace(OutputFolder/TEXT("arm-traces.csv"),PS.state.attackAge);
            const FVector At=P->GetActorLocation();
            double PhaseDuration=PS.state.duration();
            if(PS.state.phase==mcl::Phase::Parry)PhaseDuration=Lab->Combat.tuning.ParryDuration;
            if(PS.state.phase==mcl::Phase::ParryRecovery)PhaseDuration=Lab->Combat.tuning.ParryRecovery;
            if(PS.state.phase==mcl::Phase::Flinch)PhaseDuration=Lab->Combat.tuning.FlinchDuration;
            ReviewFrameRows.Add(FString::Printf(TEXT("%s,%s,%.6f,%.6f,%s,%.6f,%.3f,%.3f,%s,%s,%.4f,%.4f,%.4f"),
                *Filename,Names[Scenario],Age,PS.state.attackAge,UTF8_TO_TCHAR(mcl::phaseName(PS.state.phase)),FMath::Clamp(PS.state.elapsed/PhaseDuration,0.,1.),PS.state.attack.angle,PS.view.pitch,
                ReviewPose.IsEmpty()?TEXT("standing"):*ReviewPose,ReviewCamera.IsEmpty()?TEXT("default"):*ReviewCamera,At.X,At.Y,At.Z));
            ReviewFrameRows.Last()+=FString::Printf(TEXT(",%.6f,%.6f,%.6f,%llu,%d,%d,%s,%s"),Age-ReviewLeadIn,
                PS.state.elapsed,PhaseDuration,static_cast<unsigned long long>(PS.state.serial),PS.state.isCombo,PS.state.isRiposte,
                *ReviewSequence,UTF8_TO_TCHAR(mcl::resultName(PS.state.last)));
            if(bReviewOutcome)ReviewFrameRows.Last()+=FString::Printf(TEXT(",%s,%s,%.6f,%d,%.6f"),*ReviewOutcome,
                UTF8_TO_TCHAR(mcl::resultName(PS.state.last)),DS.health,DS.hitsTaken,PS.health);
            ReviewScenarioFrameRows.Add(ReviewFrameRows.Last());
        }
        if(bReviewKeys){
            // Phase-driven samples survive interrupted cuts, stab clocks and
            // serial changes. The names describe observed state, not contact.
            const int Bucket=PS.state.phase==mcl::Phase::Idle?0:FMath::Min(4,int(PS.state.progress()*5.));
            if(ReviewKeyPhase!=PS.state.phase||ReviewKeySerial!=PS.state.serial||ReviewKey!=Bucket){
                const FString KeyPath=OutputFolder/FString::Printf(TEXT("%02d_%s_serial_%llu_%s_bin_%d_at_%.3f"),Scenario,Names[Scenario],
                    static_cast<unsigned long long>(PS.state.serial),UTF8_TO_TCHAR(mcl::phaseName(PS.state.phase)),Bucket,Age);
                P->Knight->SaveArmPoseAudit(KeyPath+TEXT(".csv"));
                if(!Capturing)FScreenshotRequest::RequestScreenshot(KeyPath+TEXT(".png"),true,false,false);
                ReviewKeyPhase=PS.state.phase;ReviewKeySerial=PS.state.serial;ReviewKey=Bucket;
            }
        }
        if(MotionSnapshot<4&&Age>CaptureAt[MotionSnapshot]){
            if(Review||FParse::Param(FCommandLine::Get(),TEXT("ArmSkinAudit"))){
                const double Surface=P->Knight->MeasureArmSurfaceStretch();
                MaxArmSurfaceStretch=FMath::Max(MaxArmSurfaceStretch,Surface);
                bObserved=bObserved&&Surface>=.99&&Surface<=1.02;
                UE_LOG(LogTemp,Display,TEXT("ARM SURFACE %s sample=%d max_edge_ratio=%.5f"),Names[Scenario],MotionSnapshot,Surface);
            }
            const FString Folder=OutputFolder;IFileManager::Get().MakeDirectory(*Folder,true);
            if(!Capturing)
                FScreenshotRequest::RequestScreenshot(Folder/FString::Printf(TEXT("%02d_%s_pose_%d.png"),Scenario,Names[Scenario],MotionSnapshot),true,false,false);
            if(FParse::Param(FCommandLine::Get(),TEXT("ArmPoseAudit")))
                P->Knight->SaveArmPoseAudit(Folder/FString::Printf(TEXT("%02d_%s_pose_%d.csv"),Scenario,Names[Scenario],MotionSnapshot));
            ++MotionSnapshot;
        }
    }
    for(auto E:Lab->Combat.events){
        if(Scenario>=38){
            const bool Expected=E.attacker==PS.id&&
                ((ReviewOutcome==TEXT("body")&&E.result==mcl::Resolution::Hit&&E.defender==DS.id)||
                 (ReviewOutcome==TEXT("parry")&&E.result==mcl::Resolution::Parry&&E.defender==DS.id)||
                 (ReviewOutcome==TEXT("wall")&&E.result==mcl::Resolution::Wall&&E.defender==-1))||
                (ReviewSequence==TEXT("riposte")&&
                 ((E.attacker==DS.id&&E.defender==PS.id&&E.result==mcl::Resolution::Parry)||
                  (E.attacker==PS.id&&E.defender==DS.id&&E.result==mcl::Resolution::Hit)));
            if(Expected)++ReviewExpectedContacts;else ++ReviewUnexpectedContacts;
            const double ContactAge=E.attacker==PS.id&&ReviewAttackStartTime>=0?E.time-ReviewAttackStartTime:-1.;
            if(E.attacker==PS.id){ReviewContactResolution=E.result;if(ReviewContactTime<0)ReviewContactTime=ContactAge;}
            ReviewContactRows.Add(FString::Printf(TEXT("%s,%s,%s,%d,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f"),Names[Scenario],*ReviewOutcome,
                UTF8_TO_TCHAR(mcl::resultName(E.result)),E.attacker,E.defender,E.time-ScenarioStartTime,ContactAge,E.point.x,E.point.y,E.point.z,E.time-ScenarioStartTime-ReviewLeadIn));
        }
        if(E.result==mcl::Resolution::Hit&&E.attacker==PS.id&&FirstContact<0)FirstContact=E.time-ScenarioStartTime;
        if((Scenario==9||Scenario==13||Scenario==17||Scenario==24)&&E.result==mcl::Resolution::Parry&&E.defender==PS.id)bObserved=true;
        if((Scenario==32||Scenario==33)&&E.result==mcl::Resolution::Hit&&E.defender==PS.id)
            bObserved=PS.state.phase==(Scenario==33?mcl::Phase::Release:mcl::Phase::Flinch)&&PS.state.isRiposte==(Scenario==33);
        if(Scenario==10&&E.result==mcl::Resolution::Chamber&&E.defender==PS.id)bObserved=true;
    }
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
        P->AddMovementInput(FVector::ForwardVector,Age<1.7?1.f:-1.f);
        if(Age>1.1&&!bAction){P->Combat->Strike(0,0);bAction=true;}
        if(Age>1.7&&M->MovementSignals.ReversalSeverity>.75f&&M->MovementSignals.Gait!=EMeleeGait::Sprint)bObserved=true;
    }
    if(Scenario==22&&Age>.2&&!bAction){D->Combat->Feint();bAction=true;}
    if(Scenario==22&&bAction&&DS.state.phase==mcl::Phase::Idle&&DS.state.last==mcl::Resolution::Feint&&DS.state.feintRecoveryRemaining<=0)D->Combat->Stab();
    if(Scenario==23&&Age>.2&&!bAction){D->Combat->Feint();bAction=true;}
    if(Scenario==24&&Age>.2&&!bAction){P->Combat->Feint();bAction=true;}
    // Trigger on crossing the deadline: a 30 Hz frame can skip a 20 ms window.
    if(Scenario==24&&Age>.51&&Age-Dt<=.51)P->Combat->Parry();
    if(Scenario==25){if(Age>.04)Key(P,EKeys::One,IE_Released,0);if(PS.state.serial>0&&PS.state.attack.angle==0)bObserved=true;}
    if(Scenario==26){if(Age>.03&&!bAction){Key(P,EKeys::LeftMouseButton,IE_Pressed);bAction=true;}if(Age>.07)Key(P,EKeys::LeftMouseButton,IE_Released,0);
        if(PS.state.serial>0&&PS.state.attack.angle==60)bObserved=true;}
    if(Scenario==27){if(Age>.5&&!bAction){Key(P,EKeys::SpaceBar,IE_Pressed);bAction=true;}if(Age>.6)Key(P,EKeys::SpaceBar,IE_Released,0);
        if(P->GetCharacterMovement()->IsFalling()&&P->GetVelocity().Z>10)bObserved=true;
        if(Age>1.5){Key(P,EKeys::W,IE_Released,0);Key(P,EKeys::LeftShift,IE_Released,0);}}
    if(Scenario==28){
        const double Expected=P->GetCharacterMovement()->GetCrouchedHalfHeight();
        if(P->bIsCrouched&&FMath::Abs(P->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()-Expected)<.1&&
            PS.bodyFrame().hip.z>P->GetActorLocation().Z-PS.bodyHalfHeight)bObserved=true;
        if(Age>1.2)Key(P,EKeys::LeftControl,IE_Released,0);
    }
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
    if(Scenario<38&&!bSnapshot&&Age>SnapshotAt){
        FString Folder=OutputFolder;IFileManager::Get().MakeDirectory(*Folder,true);
        FScreenshotRequest::RequestScreenshot(Folder/FString::Printf(TEXT("%02d_%s.png"),Scenario,Names[Scenario]),true,false,false);
        bSnapshot=true;
    }
    if(Age>(ReviewSequence==TEXT("combo")?3.6:ReviewSequence==TEXT("riposte")?3.:2.2)+(Scenario>=38?ReviewLeadIn:0.)){
        // Let the requested terminal screenshot render before changing actors,
        // inspection camera or exiting. The following tick requests no frame.
        if(Scenario>=38&&!bReviewFinishPending){bReviewFinishPending=true;return;}
        FinishScenario(Lab,P,D);if(ReviewOnlyScenario<0&&Scenario+1<UE_ARRAY_COUNT(Names)&&(!bReviewCoreSet||Scenario<48))BeginScenario(Lab,P,D);
        else{bFinished=true;const FString Json=TEXT("{\"kind\":\"scripted_in_engine\",\"results\":[\n")+FString::Join(Results,TEXT(",\n"))+TEXT("\n]}");
            FFileHelper::SaveStringToFile(Json,*(OutputFolder/TEXT("results.json")));
            if(ReviewFrameRows.Num()>1)FFileHelper::SaveStringToFile(FString::Join(ReviewFrameRows,TEXT("\n"))+TEXT("\n"),*(OutputFolder/TEXT("frames.csv")));
            if(ReviewContactRows.Num()>0)FFileHelper::SaveStringToFile(FString::Join(ReviewContactRows,TEXT("\n"))+TEXT("\n"),*(OutputFolder/TEXT("contact-events.csv")));
            DestroyReviewWall();
            UE_LOG(LogTemp,Display,TEXT("COMBAT PLAYTEST COMPLETE"));Lab->ResetLab();D->Pattern.mode=mcl::TrainingMode::Right;
            if(FParse::Param(FCommandLine::Get(),TEXT("CombatPlaytestQuit")))FPlatformMisc::RequestExit(false);
        }
    }
}

void UCombatPlaytest::EndPlay(const EEndPlayReason::Type Reason)
{
    DestroyReviewWall();
    if(bSavedFixture){
        if(auto* Viewport=GetWorld()->GetGameViewport())Viewport->SetIgnoreInput(bPriorIgnoreInput);
        if(auto* Lab=Cast<ACombatLabGameMode>(GetOwner())){Lab->Combat.tuning=UserTuning;Lab->Combat.beforeStep=OriginalBeforeStep;}
        const FString Path=FPaths::ProjectSavedDir()/TEXT("Config/CombatTuning.json");
        if(bHadTuningFile)FFileHelper::SaveStringToFile(UserTuningFile,*Path);
        else IFileManager::Get().Delete(*Path);
    }
    Super::EndPlay(Reason);
}
