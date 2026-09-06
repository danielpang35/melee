#include "CombatLabGameMode.h"
#include "TrainingDummy.h"
#include "Character/MeleeCharacter.h"
#include "Combat/CombatComponent.h"
#include "Debug/CombatDebugHUD.h"
#include "Debug/CombatTuningPanel.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Camera/CameraActor.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Components/StaticMeshComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/TextRenderComponent.h"
#include "Components/CapsuleComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/PlayerController.h"
#include "Engine/StaticMesh.h"
#include "Kismet/GameplayStatics.h"
#include "DrawDebugHelpers.h"
#include "Components/LineBatchComponent.h"
#include "Sound/SoundWaveProcedural.h"
#include "Serialization/JsonSerializer.h"
#include "Dom/JsonObject.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "TimerManager.h"
#include "Tests/CombatPlaytest.h"
#include "Visual/VisualBenchmark.h"
#include "Visual/TournamentCourtyard.h"
#include "Visual/TournamentGraphics.h"
#include "Components/SkyAtmosphereComponent.h"
#include "Engine/SphereReflectionCapture.h"
#include "Components/SphereReflectionCaptureComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

namespace { FVector V(mcl::Vec P){return {P.x,P.y,P.z};} }
ACombatLabGameMode::ACombatLabGameMode()
{
    DefaultPawnClass=AMeleeCharacter::StaticClass();HUDClass=ACombatDebugHUD::StaticClass();
    PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickGroup=TG_PostPhysics;
}
void ACombatLabGameMode::Register(UCombatComponent* C)
{
    Combatants.AddUnique(C);C->Simulation.id=NextId++;
    const FVector P=C->GetOwner()->GetActorLocation();const FRotator R=C->GetOwner()->GetActorRotation();
    C->Simulation.reset({P.X,P.Y,P.Z},{R.Yaw,R.Pitch},Combat.tuning);Combat.actors.push_back(&C->Simulation);
}
void ACombatLabGameMode::Unregister(UCombatComponent* C)
{
    Combatants.Remove(C);auto& A=Combat.actors;A.erase(std::remove(A.begin(),A.end(),&C->Simulation),A.end());
}
void ACombatLabGameMode::StartPlay()
{
    TournamentGraphics::Initialize();LoadTuning();BuildArena();Super::StartPlay();
    Combat.worldSweep=[this](int Attacker,mcl::Segment Sweep,double Radius,mcl::Vec& Point){
        FCollisionQueryParams Params(SCENE_QUERY_STAT(MeleeBlade),false);
        for(const auto& C:Combatants)if(IsValid(C))Params.AddIgnoredActor(C->GetOwner());
        FHitResult Hit;
        bool bHit=GetWorld()->SweepSingleByChannel(Hit,V(Sweep.a),V(Sweep.b),FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(static_cast<float>(Radius)),Params);
        if(bHit)Point={Hit.ImpactPoint.X,Hit.ImpactPoint.Y,Hit.ImpactPoint.Z};return bHit;
    };
    Combat.beforeStep=[this](double Dt){
        auto* Player=Cast<AMeleeCharacter>(UGameplayStatics::GetPlayerPawn(this,0));
        if(AttackingDummy&&Player)AttackingDummy->Pattern.update(AttackingDummy->Combat->Simulation,Player->Combat->Simulation,Dt,Combat.tuning);
    };
    GetWorldTimerManager().SetTimerForNextTick(this,&ACombatLabGameMode::ResetLab);
#if !UE_BUILD_SHIPPING
    if(FParse::Value(FCommandLine::Get(),TEXT("VisualBenchmark="),TuningStatus)){auto* Benchmark=NewObject<UVisualBenchmark>(this);AddInstanceComponent(Benchmark);Benchmark->RegisterComponent();}
    if(FParse::Param(FCommandLine::Get(),TEXT("CombatPlaytest"))){
        auto* Test=NewObject<UCombatPlaytest>(this,TEXT("CombatPlaytest"));AddInstanceComponent(Test);Test->RegisterComponent();Test->AddTickPrerequisiteActor(this);
    }
#endif
}
void ACombatLabGameMode::BuildArena()
{
    GetWorld()->SpawnActor<ATournamentCourtyard>();
    GetWorld()->SpawnActor<ASkyAtmosphere>();
    auto* Light=GetWorld()->SpawnActor<ADirectionalLight>(FVector(0,0,700),FRotator(-48,-35,0));
    auto* Sun=CastChecked<UDirectionalLightComponent>(Light->GetLightComponent());Sun->SetMobility(EComponentMobility::Movable);Sun->SetIntensity(4.f);Sun->SetLightColor(FLinearColor(1.f,.91f,.76f));Sun->SetAtmosphereSunLight(true);Sun->SetForwardShadingPriority(1);
    Sun->DynamicShadowDistanceMovableLight=4000;Sun->DynamicShadowCascades=2;
    auto* Sky=GetWorld()->SpawnActor<ASkyLight>();Sky->GetLightComponent()->SetMobility(EComponentMobility::Movable);Sky->GetLightComponent()->SetIntensity(.8f);Sky->GetLightComponent()->SetLightColor(FLinearColor(.72f,.84f,1.f));Sky->GetLightComponent()->RecaptureSky();
    auto* Capture=GetWorld()->SpawnActor<ASphereReflectionCapture>(FVector(0,650,180),FRotator::ZeroRotator);
    if(auto* Sphere=Cast<USphereReflectionCaptureComponent>(Capture->GetCaptureComponent())){Sphere->InfluenceRadius=2300;Sphere->MarkDirtyForRecapture();}
    FActorSpawnParameters Params;Params.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    AttackingDummy=GetWorld()->SpawnActor<ATrainingDummy>(FVector(350,0,90),FRotator(0,180,0),Params);
    PassiveDummy=GetWorld()->SpawnActor<ATrainingDummy>(FVector(350,550,90),FRotator(0,180,0),Params);
    if(AttackingDummy)AttackingDummy->Combat->Simulation.externalView=false;
    if(PassiveDummy){PassiveDummy->bPassive=true;PassiveDummy->Combat->Simulation.infiniteHealth=true;PassiveDummy->Pattern.mode=mcl::TrainingMode::Passive;PassiveDummy->Combat->Simulation.externalView=false;}
}
void ACombatLabGameMode::Tick(float Dt)
{
    Super::Tick(Dt);
    if(bTuningOpen)return;
    for(const auto& C:Combatants){const FVector P=C->GetOwner()->GetActorLocation();C->Simulation.frameTarget={P.X,P.Y,P.Z};
        if(auto* Character=Cast<AMeleeCharacter>(C->GetOwner())){
            C->Simulation.bodyHalfHeight=Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
            C->Simulation.eyeHeight=Character->Camera->GetRelativeLocation().Z;
        }
    }
    Combat.advance(Dt);
    for(int I=Sparks.Num()-1;I>=0;--I){
        auto& S=Sparks[I];S.Life-=Dt;
        if(S.Life<=0){Sparks.RemoveAtSwap(I);continue;}
        S.Velocity.Z-=700.f*Dt;S.Position+=S.Velocity*Dt;
        GetWorld()->GetLineBatcher(UWorld::ELineBatcherType::World)->DrawLine(S.Position,S.Position-S.Velocity*.025f,S.Color*FMath::Min(1.f,S.Life*8.f),0,.15f,0.f);
    }
    for(const auto& E:Combat.events){
        if(E.result==mcl::Resolution::Parry||E.result==mcl::Resolution::Chamber){
            auto* Player=Cast<AMeleeCharacter>(UGameplayStatics::GetPlayerPawn(this,0));
            if(Player&&Player->Combat->Simulation.id==E.defender){FeedbackResult=E.result;FeedbackUntil=Combat.time+.65;}
            FLinearColor Color=E.result==mcl::Resolution::Chamber?FLinearColor(.15f,.85f,1.f):FLinearColor(1.f,.65f,.15f);
            FVector SparkOrigin=V(E.point);
            // Body-contact chambers can resolve beside the camera. Keep their cosmetic burst visible.
            if(Player&&Player->Combat->Simulation.id==E.defender&&E.result==mcl::Resolution::Chamber){
                const auto& Defender=Player->Combat->Simulation;
                FVector Forward=V(Defender.view.forward());
                FVector Eye=V(Defender.position)+FVector(0,0,Defender.eyeHeight);
                SparkOrigin+=Forward*FMath::Max(0.,55.-FVector::DotProduct(SparkOrigin-Eye,Forward));
            }
            for(int I=0;I<28;++I)Sparks.Add({SparkOrigin,FMath::VRand()*FMath::FRandRange(110.f,360.f)+FVector(0,0,90),FMath::FRandRange(.18f,.4f),Color});
        }
        PlayImpact(E);
        for(const auto& C:Combatants)if(C->Simulation.id==E.attacker||C->Simulation.id==E.defender){
            if(auto* Dummy=Cast<ATrainingDummy>(C->GetOwner()))Dummy->React(E.result);
            else if(auto* Character=Cast<AMeleeCharacter>(C->GetOwner()))Character->Feedback(E.result);
        }
        FColor Color=E.result==mcl::Resolution::Chamber?FColor::Cyan:E.result==mcl::Resolution::Parry?FColor::Yellow:FColor(255,70,35);
        if(bDebug)DrawDebugSphere(GetWorld(),V(E.point),9,8,Color,false,static_cast<float>(Combat.tuning.HitEmphasis),0,2);
    }
    if(bDebug)DrawCombatDebug();
    if(bInspection&&InspectionCamera){if(auto* Pawn=UGameplayStatics::GetPlayerPawn(this,0)){
        const FVector Focus=Pawn->GetActorLocation();const FVector At=Focus+FVector(-260,390,180);
        InspectionCamera->SetActorLocationAndRotation(At,(Focus+FVector(30,0,0)-At).Rotation());
    }}
}
void ACombatLabGameMode::ResetLab()
{
    if(auto* Player=Cast<AMeleeCharacter>(UGameplayStatics::GetPlayerPawn(this,0)))Player->ResetAt(FVector(100,0,90),FRotator::ZeroRotator);
    if(AttackingDummy){AttackingDummy->ResetAt(FVector(350,0,90),FRotator(0,180,0));AttackingDummy->Pattern.wait=1.5;AttackingDummy->Pattern.sequence=0;}
    if(PassiveDummy)PassiveDummy->ResetAt(FVector(350,550,90),FRotator(0,180,0));
    Combat.accumulator=0;Sparks.Reset();FeedbackUntil=0;
}
void ACombatLabGameMode::NextPattern()
{
    if(AttackingDummy){auto& P=AttackingDummy->Pattern;P.mode=static_cast<mcl::TrainingMode>((static_cast<int>(P.mode)+1)%static_cast<int>(mcl::TrainingMode::Count));ResetLab();}
}
void ACombatLabGameMode::PlayImpact(const mcl::CombatEvent& E)
{
    auto* Wave=NewObject<USoundWaveProcedural>(this);Wave->SetSampleRate(22050);Wave->NumChannels=1;Wave->Duration=.16f;Wave->bLooping=false;
    TArray<int16> PCM;PCM.SetNum(3528);uint32 Seed=static_cast<uint32>(E.attacker*7919+Combat.time*1000);
    bool Metal=E.result==mcl::Resolution::Parry||E.result==mcl::Resolution::Chamber;
    double Frequency=E.result==mcl::Resolution::Chamber?1500:Metal?950:E.result==mcl::Resolution::Wall?300:100;
    for(int I=0;I<PCM.Num();++I){double Time=I/22050.;Seed=1664525*Seed+1013904223;
        double Noise=(double(Seed&65535)/32768.-1.);double Tone=std::sin(2*mcl::Pi*Frequency*Time)+.4*std::sin(2*mcl::Pi*Frequency*2.71*Time);
        PCM[I]=static_cast<int16>(FMath::Clamp((Tone*(Metal?.55:.25)+Noise*(Metal?.2:.65))*std::exp(-Time*(Metal?28:42))*12000.,-32767.,32767.));}
    Wave->QueueAudio(reinterpret_cast<const uint8*>(PCM.GetData()),PCM.Num()*sizeof(int16));ActiveSounds.Add(Wave);
    if(ActiveSounds.Num()>64)ActiveSounds.RemoveAt(0);
    UGameplayStatics::PlaySoundAtLocation(this,Wave,V(E.point),.6f);
}
void ACombatLabGameMode::DrawCombatDebug()
{
#if !UE_BUILD_SHIPPING
    for(const auto& C:Combatants){auto& S=C->Simulation;const auto& G=S.defense;
        const bool bOwn=C->GetOwner()==UGameplayStatics::GetPlayerPawn(this,0);
        if(!bOwn||bInspection)DrawDebugCapsule(GetWorld(),V(S.position),S.bodyHalfHeight,S.bodyRadius,FQuat::Identity,FColor(90,110,130),false,-1,0,.7f);
        DrawDebugLine(GetWorld(),V(S.previousWeapon.hilt),V(S.previousWeapon.tip),FColor::Silver,false,-1,0,1);
        DrawDebugLine(GetWorld(),V(S.weapon.hilt),V(S.weapon.tip),S.state.damaging()?FColor::Red:FColor::Green,false,-1,0,3);
        if(S.state.phase==mcl::Phase::Release)for(auto Sweep:S.traces)DrawDebugLine(GetWorld(),V(Sweep.a),V(Sweep.b),FColor(250,150,40),false,.08f,0,.5f);
        if(S.state.phase==mcl::Phase::Parry){
            DrawDebugBox(GetWorld(),V(G.center),V(G.half),FRotator(G.boxRotation.pitch,G.boxRotation.yaw,0).Quaternion(),FColor::Blue,false,-1,0,1);
            DrawDebugCone(GetWorld(),V(G.coneOrigin),V(G.coneRotation.forward()),G.coneLength/std::cos(G.coneAngle*mcl::Rad),G.coneAngle*mcl::Rad,G.coneAngle*mcl::Rad,24,FColor::Yellow,false,-1,0,.8f);
        }
        if(S.state.chamberActive(Combat.tuning)){
            if(!bOwn||bInspection)DrawDebugCapsule(GetWorld(),V(S.position),S.bodyHalfHeight,S.bodyRadius,FQuat::Identity,FColor::Cyan,false,-1,0,2);
            mcl::Vec A{0,std::cos(S.state.attack.angle*mcl::Rad),std::sin(S.state.attack.angle*mcl::Rad)};
            DrawDebugDirectionalArrow(GetWorld(),V(S.position),V(S.position+S.view.world(A)*70),12,FColor::Cyan,false,-1,0,2);
        }
    }
#endif
}
void ACombatLabGameMode::ToggleInspection()
{
    auto* PC=GetWorld()->GetFirstPlayerController();if(!PC)return;
    bInspection=!bInspection;
    if(bInspection){bDebug=true;if(!InspectionCamera)InspectionCamera=GetWorld()->SpawnActor<ACameraActor>();PC->SetViewTarget(InspectionCamera);}
    else if(auto Pawn=PC->GetPawn())PC->SetViewTarget(Pawn);
}
bool ACombatLabGameMode::SaveTuning(bool bPromote)
{
    auto Object=MakeShared<FJsonObject>();Object->SetNumberField(TEXT("SchemaVersion"),1);
    for(auto E:Combat.tuning.entries())Object->SetNumberField(UTF8_TO_TCHAR(E.name),*E.value);
    FString Text;auto Writer=TJsonWriterFactory<TCHAR,TPrettyJsonPrintPolicy<TCHAR>>::Create(&Text);FJsonSerializer::Serialize(Object,Writer);
    FString Path=bPromote?FPaths::ProjectConfigDir()/TEXT("CombatDefaults.json"):FPaths::ProjectSavedDir()/TEXT("Config/CombatTuning.json");
    IFileManager::Get().MakeDirectory(*FPaths::GetPath(Path),true);
    bool Ok=FFileHelper::SaveStringToFile(Text,*(Path+TEXT(".tmp")));
    if(Ok)Ok=IFileManager::Get().Move(*Path,*(Path+TEXT(".tmp")),true,true);
    TuningStatus=Ok?TEXT("Saved: ")+Path:TEXT("SAVE FAILED: ")+Path;return Ok;
}
bool ACombatLabGameMode::LoadTuning()
{
    mcl::Tuning Candidate;
    bool Any=false;
    for(const FString& Path:{FPaths::ProjectConfigDir()/TEXT("CombatDefaults.json"),FPaths::ProjectSavedDir()/TEXT("Config/CombatTuning.json")}){
        FString Text;if(!FFileHelper::LoadFileToString(Text,*Path))continue;
        TSharedPtr<FJsonObject> Object;auto Reader=TJsonReaderFactory<>::Create(Text);
        if(!FJsonSerializer::Deserialize(Reader,Object)||!Object.IsValid()){TuningStatus=TEXT("Invalid JSON: ")+Path;return false;}
        for(auto E:Candidate.entries()){double Value;if(Object->TryGetNumberField(UTF8_TO_TCHAR(E.name),Value)&&FMath::IsFinite(Value))*E.value=FMath::Clamp(Value,E.minimum,E.maximum);}
        Any=true;
    }
    Combat.tuning=Candidate;TuningStatus=Any?TEXT("Tuning loaded"):TEXT("Using built-in defaults");return true;
}
void ACombatLabGameMode::ResetTuning(){Combat.tuning=mcl::Tuning{};TuningStatus=TEXT("Built-in defaults restored; SAVE to persist");}
void ACombatLabGameMode::ToggleTuning()
{
    auto* PC=GetWorld()->GetFirstPlayerController();if(!PC||!GEngine||!GEngine->GameViewport)return;
    bTuningOpen=!bTuningOpen;
    if(bTuningOpen){Panel=SNew(SCombatTuningPanel).Lab(this);GEngine->GameViewport->AddViewportWidgetContent(Panel.ToSharedRef(),10);
        PC->bShowMouseCursor=true;PC->SetInputMode(FInputModeGameAndUI().SetWidgetToFocus(Panel).SetHideCursorDuringCapture(false));PC->SetIgnoreMoveInput(true);PC->SetIgnoreLookInput(true);}
    else{if(Panel.IsValid())GEngine->GameViewport->RemoveViewportWidgetContent(Panel.ToSharedRef());Panel.Reset();PC->bShowMouseCursor=false;
        PC->SetInputMode(FInputModeGameOnly());PC->SetIgnoreMoveInput(false);PC->SetIgnoreLookInput(false);}
}
void ACombatLabGameMode::EndPlay(const EEndPlayReason::Type Reason)
{
    if(Panel.IsValid()&&GEngine&&GEngine->GameViewport)GEngine->GameViewport->RemoveViewportWidgetContent(Panel.ToSharedRef());Panel.Reset();Super::EndPlay(Reason);
}
