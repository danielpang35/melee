#include "CombatDebugHUD.h"
#include "Visual/TournamentGraphics.h"
#include "Character/MeleeCharacter.h"
#include "Character/MeleeCharacterMovementComponent.h"
#include "Combat/CombatComponent.h"
#include "Training/CombatLabGameMode.h"
#include "Training/TrainingDummy.h"
#include "GameFramework/PlayerController.h"
#include "Engine/Canvas.h"
#include "Engine/World.h"

void ACombatDebugHUD::DrawHUD()
{
    Super::DrawHUD();if(!Canvas||!PlayerOwner)return;
    auto* C=Cast<AMeleeCharacter>(PlayerOwner->GetPawn());auto* Lab=GetWorld()->GetAuthGameMode<ACombatLabGameMode>();if(!C||!Lab)return;
    const auto& S=C->Combat->Simulation;const auto& State=S.state;const auto& T=Lab->Combat.tuning;
    auto* M=Cast<UMeleeCharacterMovementComponent>(C->GetCharacterMovement());
    const float W=Canvas->SizeX,H=Canvas->SizeY;
    DrawRect(FLinearColor(.02f,.03f,.05f,.8f),22,22,430,92);
    DrawText(TEXT("MELEE / COMBAT LAB"),FColor(180,220,240),38,32,nullptr,1.35f);
    DrawText(FString::Printf(TEXT("%s    %.0f HP    %.0f STAMINA%s"),UTF8_TO_TCHAR(mcl::phaseName(State.phase)),S.health,State.stamina,State.infiniteStamina?TEXT("  [INF]"):TEXT("")),FColor::White,38,63);
    if(Lab->AttackingDummy)DrawText(FString::Printf(TEXT("F2  %s"),UTF8_TO_TCHAR(mcl::trainingName(Lab->AttackingDummy->Pattern.mode))),FColor(250,190,100),38,86);
    FColor Cross=State.chamberActive(T)?FColor::Cyan:State.phase==mcl::Phase::Parry?FColor::Yellow:FColor::White;
    DrawLine(W*.5f-4,H*.5f,W*.5f+4,H*.5f,Cross);DrawLine(W*.5f,H*.5f-4,W*.5f,H*.5f+4,Cross);
    DrawRect(FLinearColor(.05f,.06f,.08f,.8f),W*.5f-100,H-95,200,5);
    DrawRect(FLinearColor(.25f,.7f,.85f),W*.5f-100,H-95,200*State.progress(),5);
    DrawText(UTF8_TO_TCHAR(mcl::resultName(State.last)),FColor(180,225,240),W*.5f-35,H-82,nullptr,1.1f);
    DrawRect(FLinearColor(.02f,.03f,.05f,.88f),0,H-58,W,58);
    DrawText(TEXT("LMB strike  |  Wheel up / E stab  |  RMB parry  |  Q feint  |  Shift sprint  |  Ctrl crouch  |  Space jump"),FColor::White,24,H-48);
    DrawText(TEXT("1-6 origins  |  F2 pattern  |  F3 geometry  |  F4 tuning  |  F5 inspection  |  F6 stamina  |  R reset"),FColor(170,195,210),24,H-27);
    if(State.isRiposte&&(State.phase==mcl::Phase::Windup||State.phase==mcl::Phase::Release))DrawText(TEXT("RIPOSTE"),FColor(255,195,65),W*.5f-45,H*.5f+68,nullptr,1.35f);
    if(S.health<=0)DrawText(TEXT("DOWNED - PRESS R TO RESET"),FColor::Red,W*.5f-160,H*.4f,nullptr,1.7f);
    if(Lab->FeedbackUntil>Lab->Combat.time){
        const bool Chamber=Lab->FeedbackResult==mcl::Resolution::Chamber;
        FColor Color=Chamber?FColor::Cyan:FColor(255,195,65);
        DrawText(Chamber?TEXT("CHAMBER"):TEXT("PARRY"),Color,W*.5f-55,H*.5f+38,nullptr,1.7f);
        const float Radius=18.f+float((Lab->FeedbackUntil-Lab->Combat.time)*25.);
        for(int I=0;I<4;++I){float A=(45.f+90.f*I)*PI/180.f;
            DrawLine(W*.5f+FMath::Cos(A)*Radius,H*.5f+FMath::Sin(A)*Radius,W*.5f+FMath::Cos(A)*(Radius+9),H*.5f+FMath::Sin(A)*(Radius+9),Color,2);}
    }
    if(Lab->AttackingDummy){
        const auto& Enemy=Lab->AttackingDummy->Combat->Simulation;
        if(Enemy.state.phase==mcl::Phase::Windup||Enemy.state.phase==mcl::Phase::Release){
            auto Incoming=mcl::ChamberSystem::inDefenderView(Enemy.state.attack,Enemy.view,S.view);
            int Sector=(FMath::RoundToInt(Incoming.angle/60.)+6)%6;
            DrawText(State.isCombo&&State.phase==mcl::Phase::Windup?TEXT("COMBO: no chamber window"):
                Enemy.state.attack.kind==mcl::AttackKind::Stab?TEXT("CHAMBER: E just before contact"):
                FString::Printf(TEXT("CHAMBER: %d just before contact (%.0f ms window)"),Sector+1,T.ChamberDuration*1000),FColor(130,210,220),W*.5f-175,H-125);
        }
    }
    DrawText(TEXT("F7  ")+TournamentGraphics::Profile,FColor(175,195,210),W-210,30);
    if(!Lab->bDebug)return;
    DrawText(FString::Printf(TEXT("Strike release %.0f ms / damage active %.0f ms"),T.StrikeRelease*1000,T.StrikeRelease*(T.DamageEnd-T.DamageStart)*1000),FColor::White,34,390);
    FString Debug=FString::Printf(TEXT("STATE %s | %s | angle %.1f | raw %.1f\nphase %.3f / %.3f | release %.3f | spin %.1f / %.1f\nweapon %.0f cm/s | angular %.0f deg/s | yaw cap %.0f | pitch cap %.0f\nfeint %d | morph %d | combo %d | queued %d | riposte %.3f\nparry active %d | remaining %.3f | guard yaw %.1f pitch %.1f\nchamber %d | remaining %.3f | incoming %.1f | difference %.1f / %.1f\nspeed %.0f | momentum %.2f | turn %.0f deg/s | loss %.3f\nlunge %.0f cm/s | displacement %.1f cm\ncombat steps %d | collision queries %d | overload %d"),
        UTF8_TO_TCHAR(mcl::phaseName(State.phase)),State.attack.kind==mcl::AttackKind::Stab?TEXT("STAB"):TEXT("STRIKE"),State.attack.angle,State.attack.rawAngle,
        State.elapsed,State.duration(),State.phase==mcl::Phase::Release?State.progress():0,State.releaseRotation,T.AntiSpinThreshold,
        S.speed,S.angularSpeed,State.yawCap(T),T.PitchCap,State.canFeint(T),State.canMorph(T),State.canCombo(T),State.comboQueued,State.riposteRemaining,
        State.phase==mcl::Phase::Parry,State.phase==mcl::Phase::Parry?FMath::Max(0.,T.ParryDuration-State.elapsed):0,S.guard.yaw,S.guard.pitch,
        State.chamberActive(T),State.chamberActive(T)?FMath::Max(0.,T.ChamberDuration-State.attackAge):0,S.incomingAngle,S.chamberDifference,T.ChamberTolerance,
        C->GetVelocity().Size2D(),M?M->Momentum.value:0,M?M->Momentum.turnRate:0,M?M->Momentum.loss:0,M?M->Lunge.velocity:0,M?M->Lunge.displacement:0,
        Lab->Combat.stepsLastFrame,Lab->Combat.queriesLastFrame,Lab->Combat.overload);
    DrawRect(FLinearColor(.015f,.025f,.04f,.88f),22,130,800,255);DrawText(Debug,FColor(190,220,230),34,140);
}
