#include "EXGameplayCapture.h"
#include "Debug/CombatDrawTracers.h"
#include "Training/CombatLabGameMode.h"
#include "Training/TrainingDummy.h"
#include "Character/MeleeCharacter.h"
#include "Combat/CombatComponent.h"
#include "Visual/EXCombatPresentation.h"
#include "Visual/KnightPresentation.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "GameFramework/PlayerController.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Engine/World.h"
#include "Engine/GameViewportClient.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "InputKeyEventArgs.h"
#include "UnrealClient.h"
UEXGameplayCapture::UEXGameplayCapture(){PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.TickGroup=TG_PostUpdateWork;}
void UEXGameplayCapture::TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* TickFunction)
{
    Super::TickComponent(Dt,TickType,TickFunction);
    auto* Lab=Cast<ACombatLabGameMode>(GetOwner());
    auto* P=Cast<AMeleeCharacter>(UGameplayStatics::GetPlayerPawn(this,0));
    if(!Lab||!P||!Lab->AttackingDummy)return;
    auto* D=Lab->AttackingDummy.Get();auto* PC=Cast<APlayerController>(P->GetController());if(!PC)return;
    auto Key=[&](FKey K,EInputEvent E,float Amount=1.f){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,E,Amount));};
    if(!Started){
        Started=true;AddTickPrerequisiteActor(P);AddTickPrerequisiteActor(D);
        FString Tag;FParse::Value(FCommandLine::Get(),TEXT("EXGameplayCapture="),Tag);
        if(Tag.IsEmpty()||Tag.Contains(TEXT("/"))||Tag.Contains(TEXT("\\"))||Tag.Contains(TEXT("..")))return;
        Directory=FPaths::ProjectSavedDir()/TEXT("MEL15")/Tag;
        IFileManager::Get().MakeDirectory(*(Directory/TEXT("frames")),true);
        FParse::Value(FCommandLine::Get(),TEXT("EXGameplayView="),View);
        TPProof=FParse::Param(FCommandLine::Get(),TEXT("TPProof"));
        TracerSmoke=FParse::Param(FCommandLine::Get(),TEXT("TracerSmoke"));
        TracerRows=TEXT("frame,enabled,lines,visible_releasing,max_gap_cm\n");
        Pilot=TPProof&&FParse::Param(FCommandLine::Get(),TEXT("RightHorizontalPilot"));
        ReadabilitySmoke=Pilot&&FParse::Param(FCommandLine::Get(),TEXT("ReadabilitySmoke"));
        TPPoseReview=Pilot&&FParse::Param(FCommandLine::Get(),TEXT("TPPoseReview"));
        TPCompose=TPProof&&FParse::Param(FCommandLine::Get(),TEXT("TPCompose"));
        if(!Pilot)Lab->Combat.tuning=mcl::Tuning{};
        Lab->bDebug=false;
        D->Pattern.mode=mcl::TrainingMode::Passive;D->Combat->Simulation.infiniteHealth=true;
        Lab->PassiveDummy->ResetAt(FVector(900,550,90),FRotator(0,180,0));
        P->ResetAt(FVector(100,0,90),FRotator::ZeroRotator);D->ResetAt(FVector(250,0,90),FRotator(0,180,0));
        P->Combat->Simulation.infiniteHealth=true;
        if(View==TEXT("external")||View==TEXT("side")){ReviewCamera=GetWorld()->SpawnActor<ACameraActor>();PC->SetViewTarget(ReviewCamera);}
        else if(View==TEXT("defender"))PC->SetViewTarget(D);
        Rows=TEXT("frame,time,serial,phase,elapsed,source,ex_active,hits,player_hits,x,y,yaw,pitch,blade_error,pose_error,branch_grip_error,branch_anchor_error,branch_reach_scale\n");
        if(TPProof){Rows.RemoveAt(Rows.Len()-1);Rows+=TEXT(",tp_selected,tp_active,tp_authored,tp_source,tp_blend,tp_pose_error,tp_weapon_error,tp_canonical_base_error,tp_canonical_tip_error,tp_grip_error,tp_arm_reach_scale\n");}
        Events=TEXT("frame,time,result,attacker,defender\n");
        ContactRows=TEXT("frame,attack_age,damaging,tp_active,canonical_gap_cm,visible_gap_cm,canonical_base_x,canonical_base_y,canonical_base_z,canonical_tip_x,canonical_tip_y,canonical_tip_z,visible_base_x,visible_base_y,visible_base_z,visible_tip_x,visible_tip_y,visible_tip_z\n");
    }
    if(Frame<0){++Frame;return;}
    if(Frame>=(TPPoseReview?540:(ReadabilitySmoke?960:(Pilot?720:(TPProof?480:840))))){
        FFileHelper::SaveStringToFile(Rows,*(Directory/TEXT("frames.csv")));
        FFileHelper::SaveStringToFile(Events,*(Directory/TEXT("events.csv")));
        if(Pilot)FFileHelper::SaveStringToFile(ContactRows,*(Directory/TEXT("contact.csv")));
        if(TracerSmoke)FFileHelper::SaveStringToFile(TracerRows,*(Directory/TEXT("tracers.csv")));
        UKismetSystemLibrary::QuitGame(this,PC,EQuitPreference::Quit,true);return;
    }
    if(TracerSmoke&&Lab->Tracers){
        if(Frame==90||Frame==130)Key(EKeys::F8,IE_Pressed);
        if(Frame==91||Frame==131)Key(EKeys::F8,IE_Released);
        if(Frame==215)Key(EKeys::F9,IE_Pressed);
        if(Frame==216)Key(EKeys::F9,IE_Released);
        if(Frame==260){ReviewCamera=nullptr;PC->SetViewTarget(P);}
        TracerRows+=FString::Printf(TEXT("%d,%d,%d,%d,%.6f\n"),Frame,Lab->Tracers->Enabled(),Lab->Tracers->LineCount(),Lab->Tracers->VisibleActors,Lab->Tracers->MaxGapCm);
    }
    auto& S=P->Combat->Simulation;
    if(TPPoseReview){
        if(Frame==12||Frame==322)Key(EKeys::One,IE_Pressed);
        if(Frame==13||Frame==323)Key(EKeys::One,IE_Released);
        // Controlled substantial aim input through the same legal look API.
        double PitchInput=0.;
        if(Frame>=170&&Frame<190)PitchInput=-3.;
        if(Frame>=220&&Frame<250)PitchInput=3.;
        if(Frame>=275&&Frame<300)PitchInput=-3.;
        if(Frame>=450&&Frame<465)PitchInput=3.;
        if(PitchInput!=0.){
            S.look(0,PitchInput,1./60.,Lab->Combat.tuning);
            PC->SetControlRotation(FRotator(S.view.pitch,S.view.yaw,0));
        }
        if(Frame==310)Key(EKeys::D,IE_Pressed);
        if(Frame==350)Key(EKeys::D,IE_Released);
    }else if(TPProof){
        if(Frame==12||Frame==162||Frame==312)Key(EKeys::One,IE_Pressed);
        if(Frame==13||Frame==163||Frame==313)Key(EKeys::One,IE_Released);
        if(Frame==300)D->SetActorLocation(FVector(650,0,90));
        if(TPCompose){
            if(Frame==180)Key(EKeys::D,IE_Pressed);
            if(Frame==192)Key(EKeys::D,IE_Released);
            if(Frame>=180&&Frame<192)Key(EKeys::MouseX,IE_Axis,2.f);
            if(Frame>=194&&Frame<204)Key(EKeys::MouseY,IE_Axis,2.f);
        }
        // One interruption case; deliberately no double-parry scenario.
        if(Pilot){
            if(Frame==470){P->ResetAt(FVector(100,0,90),FRotator::ZeroRotator);D->ResetAt(FVector(250,0,90),FRotator(0,180,0));}
            if(Frame==480)D->Combat->Strike(0,0);
            if(Frame==500)Key(EKeys::One,IE_Pressed);
            if(Frame==501)Key(EKeys::One,IE_Released);
        }
        if(ReadabilitySmoke){
            if(Frame>=210&&Frame<218)Key(EKeys::MouseX,IE_Axis,2.f);
            if(Frame>=218&&Frame<226)Key(EKeys::MouseY,IE_Axis,-2.f);
            if(Frame==610){P->ResetAt(FVector(100,0,90),FRotator::ZeroRotator);D->ResetAt(FVector(650,0,90),FRotator(0,180,0));}
            if(Frame==620||Frame==682)Key(EKeys::One,IE_Pressed);
            if(Frame==621||Frame==683)Key(EKeys::One,IE_Released);
        }
    }else{
    if(Frame==12||Frame==180||Frame==348||Frame==510)Key(EKeys::LeftMouseButton,IE_Pressed);
    if(Frame==13||Frame==181||Frame==349||Frame==511)Key(EKeys::LeftMouseButton,IE_Released);
    if(Frame==30)Key(EKeys::D,IE_Pressed);
    if(Frame==42)Key(EKeys::D,IE_Released);
    if(Frame>=30&&Frame<48)Key(EKeys::MouseX,IE_Axis,6.f);
    if(Frame>=195&&Frame<212)Key(EKeys::MouseY,IE_Axis,6.f);
    if(Frame==160)Key(EKeys::W,IE_Pressed);
    if(Frame==170)Key(EKeys::W,IE_Released);
    if(Frame==326)D->SetActorLocation(FVector(650,0,90));
    if(Frame==528)Key(EKeys::Q,IE_Pressed);
    if(Frame==529)Key(EKeys::Q,IE_Released);
    if(Frame==532)Key(EKeys::RightMouseButton,IE_Pressed);
    if(Frame==533)Key(EKeys::RightMouseButton,IE_Released);
    if(Frame>=580&&Frame<598)Key(EKeys::MouseX,IE_Axis,-6.f);
    if(Frame>=580&&Frame<597)Key(EKeys::MouseY,IE_Axis,-6.f);
    if(Frame==600){D->ResetAt(P->GetActorLocation()+FVector(150,0,0),FRotator(0,180,0));D->Combat->Strike(0,0);}
    if(Frame==643)Key(EKeys::RightMouseButton,IE_Pressed);
    if(Frame==644)Key(EKeys::RightMouseButton,IE_Released);
    if(!Riposted&&Frame>643&&S.state.riposteRemaining>0){Key(EKeys::One,IE_Pressed);Riposted=true;}
    else if(Riposted)Key(EKeys::One,IE_Released);
    if(Frame==756)D->Combat->Strike(0,0);
    }
    if(ReviewCamera){
        const FVector Offset=TPPoseReview?(View==TEXT("side")?FVector(0,370,45):FVector(300,250,65)):FVector(-160,300,100);
        const FVector At=P->GetActorLocation()+Offset;
        const FVector Focus=P->GetActorLocation()+FVector(35,0,35);
        ReviewCamera->SetActorLocationAndRotation(At,(Focus-At).Rotation());
        ReviewCamera->GetCameraComponent()->SetFieldOfView(74.f);
    }
    if(PC->PlayerCameraManager)PC->PlayerCameraManager->UpdateCamera(0.f);
    Rows+=FString::Printf(TEXT("%d,%.9f,%llu,%s,%.9f,%.9f,%d,%d,%d,%.6f,%.6f,%.6f,%.6f,%.9f,%.9f,%.9f,%.9f,%.9f\n"),
        Frame,Lab->Combat.time,S.state.serial,UTF8_TO_TCHAR(mcl::phaseName(S.state.phase)),S.state.elapsed,S.exSourceTime,
        S.state.exActive,D->Combat->Simulation.hitsTaken,S.hitsTaken,S.position.x,S.position.y,S.view.yaw,S.view.pitch,P->EXPresentation->BladeError,P->EXPresentation->PoseError,
        P->EXPresentation->BranchGripError,P->EXPresentation->BranchAnchorError,P->EXPresentation->BranchReachScale);
    if(TPProof){
        Rows.RemoveAt(Rows.Len()-1);
        Rows+=FString::Printf(TEXT(",%d,%d,%d,%.9f,%.9f,%.9f,%.9f,%.9f,%.9f,%.9f,%.9f\n"),
            P->Knight->TPSelected,P->Knight->TPActive,P->Knight->TPAuthored,P->Knight->TPSourceTime,
            P->Knight->TPBlendWeight,P->Knight->TPPoseErrorCm,P->Knight->TPWeaponErrorCm,
            P->Knight->TPBladeBaseErrorCm,P->Knight->TPBladeTipErrorCm,P->Knight->TPGripErrorCm,P->Knight->TPArmReachScale);
    }
    for(const auto& E:Lab->Combat.events)Events+=FString::Printf(TEXT("%d,%.9f,%s,%d,%d\n"),Frame,E.time,UTF8_TO_TCHAR(mcl::resultName(E.result)),E.attacker,E.defender);
    if(Pilot){
        const auto B=P->Knight->TPBladeBase,T=P->Knight->TPBladeTip;
        const mcl::Segment Visible{{B.X,B.Y,B.Z},{T.X,T.Y,T.Z}},Canonical{S.weapon.hilt,S.weapon.tip};
        double CanonicalGap=1.e9,VisibleGap=1.e9;
        for(const auto Axis:D->Combat->Simulation.hurtAxes()){
            const double Radius=D->Combat->Simulation.bodyRadius+Lab->Combat.tuning.BladeRadius;
            CanonicalGap=FMath::Min(CanonicalGap,mcl::segmentDistance(Canonical,Axis)-Radius);
            VisibleGap=FMath::Min(VisibleGap,mcl::segmentDistance(Visible,Axis)-Radius);
        }
        ContactRows+=FString::Printf(TEXT("%d,%.9f,%d,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n"),
            Frame,S.state.attackAge,S.state.damaging(),P->Knight->TPActive,CanonicalGap,VisibleGap,
            S.weapon.hilt.x,S.weapon.hilt.y,S.weapon.hilt.z,S.weapon.tip.x,S.weapon.tip.y,S.weapon.tip.z,B.X,B.Y,B.Z,T.X,T.Y,T.Z);
    }
    FScreenshotRequest::RequestScreenshot(Directory/TEXT("frames")/FString::Printf(TEXT("%04d.png"),Frame),false,false);
    ++Frame;
}
