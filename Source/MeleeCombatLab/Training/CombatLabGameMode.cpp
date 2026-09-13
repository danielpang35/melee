#include "CombatLabGameMode.h"
#include "TrainingDummy.h"
#include "Character/MeleeCharacter.h"
#include "Combat/CombatComponent.h"
#include "Debug/CombatDebugHUD.h"
#include "Debug/CombatDrawTracers.h"
#include "Debug/CombatTuningPanel.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/PostProcessVolume.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Camera/CameraActor.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Components/StaticMeshComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
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
#include "Tests/EXGameplayCapture.h"
#include "Visual/VisualBenchmark.h"
#include "Visual/TournamentCourtyard.h"
#include "Visual/TournamentGraphics.h"
#include "Components/SkyAtmosphereComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Debug/SwingTelemetry.h"
#include "Audio/CombatAudio.h"
#include <sstream>

namespace { FVector V(mcl::Vec P){return {P.x,P.y,P.z};} }
ACombatLabGameMode::ACombatLabGameMode()
{
    DefaultPawnClass=AMeleeCharacter::StaticClass();HUDClass=ACombatDebugHUD::StaticClass();
    PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickGroup=TG_PostPhysics;
}
void ACombatLabGameMode::Register(UCombatComponent* C)
{
    if(Tracers)Tracers->AddTickPrerequisiteActor(C->GetOwner());
    Combatants.AddUnique(C);C->Simulation.id=NextId++;
    const FVector P=C->GetOwner()->GetActorLocation();const FRotator R=C->GetOwner()->GetActorRotation();
    C->Simulation.reset({P.X,P.Y,P.Z},{R.Yaw,R.Pitch},Combat.tuning);Combat.actors.push_back(&C->Simulation);
}
void ACombatLabGameMode::Unregister(UCombatComponent* C)
{
    if(CombatAudio)CombatAudio->Forget(C->Simulation.id);
    if(Tracers){Tracers->RemoveTickPrerequisiteActor(C->GetOwner());Tracers->Clear();}
    Combatants.Remove(C);auto& A=Combat.actors;A.erase(std::remove(A.begin(),A.end(),&C->Simulation),A.end());
}
void ACombatLabGameMode::StartPlay()
{
    TournamentGraphics::Initialize();LoadTuning();BuildArena();Super::StartPlay();
    Combat.worldSweep=[this](int Attacker,mcl::Segment Sweep,double Radius,mcl::Vec& Point,mcl::Vec& Normal){
        FCollisionQueryParams Params(SCENE_QUERY_STAT(MeleeBlade),false);
        for(const auto& C:Combatants)if(IsValid(C))Params.AddIgnoredActor(C->GetOwner());
        FHitResult Hit;
        bool bHit=GetWorld()->SweepSingleByChannel(Hit,V(Sweep.a),V(Sweep.b),FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(static_cast<float>(Radius)),Params);
        if(bHit){Point={Hit.ImpactPoint.X,Hit.ImpactPoint.Y,Hit.ImpactPoint.Z};Normal={Hit.ImpactNormal.X,Hit.ImpactNormal.Y,Hit.ImpactNormal.Z};}return bHit;
    };
    Combat.constrainLean=[this](const mcl::Combatant& S){
        if(FMath::Abs(S.view.pitch*S.torsoPitchScale)<.001)return 1.;
        FCollisionQueryParams Params(SCENE_QUERY_STAT(MeleeLean),false);
        for(const auto& C:Combatants)if(IsValid(C))Params.AddIgnoredActor(C->GetOwner());
        const double Pitch=mcl::clamp(S.view.pitch,-85.,85.)*S.torsoPitchScale;
        const auto Frame=[&](double Fraction){return mcl::BodyFrame::make(S.uprightEye(),S.view,Pitch*Fraction);};
        const auto Upright=Frame(0.);
        const mcl::Vec Top=S.position+mcl::Vec{0,0,S.bodyHalfHeight-S.bodyRadius};
        const auto ClearSphere=[&](mcl::Vec A,mcl::Vec B,double Radius){
            FHitResult Hit;
            return !GetWorld()->SweepSingleByChannel(Hit,V(A),V(B),FQuat::Identity,ECC_Visibility,
                FCollisionShape::MakeSphere(static_cast<float>(Radius)),Params);
        };
        return mcl::clearLeanFraction([&](double A,double B){
            const auto From=Frame(A),To=Frame(B);
            // The stationary hip volume is already governed by movement.
            // Sweep the moving torso and head along small angular intervals.
            for(double Along:{.5,1.}){
                const auto P=mcl::lerp(Upright.hip,Top,Along);
                if(!ClearSphere(From.transform(P),To.transform(P),S.bodyRadius))return false;
            }
            return ClearSphere(From.eye(),To.eye(),6.);
        });
    };
    Combat.beforeStep=[this](double Dt){
        auto* Player=Cast<AMeleeCharacter>(UGameplayStatics::GetPlayerPawn(this,0));
        if(AttackingDummy&&Player)AttackingDummy->Pattern.update(AttackingDummy->Combat->Simulation,Player->Combat->Simulation,Dt,Combat.tuning);
    };
    if(!FParse::Param(FCommandLine::Get(),TEXT("LegacyCombatAudio"))){
        CombatAudio=NewObject<UCombatAudio>(this);CombatAudio->Initialize(GetWorld());
    }
    Tracers=NewObject<UCombatDrawTracers>(this);AddInstanceComponent(Tracers);Tracers->RegisterComponent();
    for(const auto& C:Combatants)if(IsValid(C))Tracers->AddTickPrerequisiteActor(C->GetOwner());
    Combat.sampleStep=[this](const mcl::Combatant& S,double Time){
        if(CombatAudio)CombatAudio->Sample(S,Time);
        if(Tracers)Tracers->Sample(S,Time);
        if(!SwingLogPath.IsEmpty()){
            std::ostringstream Row;mcl::swingSample(Row,S,Time);SwingLog+=UTF8_TO_TCHAR(Row.str().c_str());
        }
    };
    if(FParse::Param(FCommandLine::Get(),TEXT("SwingTelemetry"))){
        SwingLogPath=FPaths::ProjectSavedDir()/TEXT("SwingTelemetry.csv");
        std::ostringstream Header;mcl::swingHeader(Header);
        FFileHelper::SaveStringToFile(UTF8_TO_TCHAR(Header.str().c_str()),*SwingLogPath);
    }
    GetWorldTimerManager().SetTimerForNextTick(this,&ACombatLabGameMode::ResetLab);
#if !UE_BUILD_SHIPPING
    FString EXCaptureTag;
    if(FParse::Value(FCommandLine::Get(),TEXT("EXGameplayCapture="),EXCaptureTag)){
        auto* Capture=NewObject<UEXGameplayCapture>(this);AddInstanceComponent(Capture);Capture->RegisterComponent();Capture->AddTickPrerequisiteActor(this);Capture->AddTickPrerequisiteComponent(Tracers);
    }
    FString VisualBenchmarkTag;
    if(FParse::Value(FCommandLine::Get(),TEXT("VisualBenchmark="),VisualBenchmarkTag)){auto* Benchmark=NewObject<UVisualBenchmark>(this);AddInstanceComponent(Benchmark);Benchmark->RegisterComponent();}
    if(FParse::Param(FCommandLine::Get(),TEXT("CombatPlaytest"))){
        auto* Test=NewObject<UCombatPlaytest>(this,TEXT("CombatPlaytest"));AddInstanceComponent(Test);Test->RegisterComponent();Test->AddTickPrerequisiteActor(this);
    }
#endif
}
void ACombatLabGameMode::BuildArena()
{
    ImpactParticles=NewObject<UInstancedStaticMeshComponent>(this,TEXT("ImpactParticles"));
    ImpactParticles->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Sphere.Sphere")));
    ImpactParticles->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Visual/Citadel/Materials/M_CitadelSparks.M_CitadelSparks")));
    ImpactParticles->SetCollisionEnabled(ECollisionEnabled::NoCollision);ImpactParticles->SetCastShadow(false);
    ImpactParticles->NumCustomDataFloats=4;ImpactParticles->RegisterComponent();
    for(int I=0;I<128;++I)ImpactParticles->AddInstance(FTransform(FQuat::Identity,FVector::ZeroVector,FVector::ZeroVector));
    // Retain the complete courtyard and its assets as an opt-in archive.
    const bool bArchivedCourtyard=FParse::Param(FCommandLine::Get(),TEXT("ArchivedCourtyard"));
    if(bArchivedCourtyard)GetWorld()->SpawnActor<ATournamentCourtyard>();
    else{
        auto* Floor=GetWorld()->SpawnActor<AStaticMeshActor>(FVector(0,0,-25),FRotator::ZeroRotator);
        auto* Surface=Floor->GetStaticMeshComponent();
        Surface->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));
        Surface->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/UserKnight/KN_v001/M_WhiteFloor.M_WhiteFloor")));
        Floor->SetActorScale3D(FVector(200,200,.5));
        Surface->SetCollisionProfileName(TEXT("BlockAll"));
        Floor->Tags.Add(TEXT("WhiteTestFloor"));

        // Unrigged supplied art is a scene asset, separate from combat actors.
        if(FParse::Param(FCommandLine::Get(),TEXT("UserKnightStudy"))){
            auto* Knight=GetWorld()->SpawnActor<AStaticMeshActor>(FVector(180,-220,0),FRotator(0,90,0));
            Knight->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/UserKnight/KN_v001/SM_UserKnight.SM_UserKnight")));
            Knight->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            Knight->Tags.Add(TEXT("UserKnight"));
        }
    }
    GetWorld()->SpawnActor<ASkyAtmosphere>();
    auto* Light=GetWorld()->SpawnActor<ADirectionalLight>(FVector(0,0,700),FRotator(-32,-38,0));
    auto* Sun=CastChecked<UDirectionalLightComponent>(Light->GetLightComponent());Sun->SetMobility(EComponentMobility::Movable);Sun->SetIntensity(5.2f);Sun->SetLightColor(FLinearColor(1.f,.89f,.70f));Sun->SetAtmosphereSunLight(true);Sun->SetForwardShadingPriority(1);
    Sun->DynamicShadowDistanceMovableLight=6500;Sun->DynamicShadowCascades=4;
    if(!bArchivedCourtyard)Sun->SetLightColor(FLinearColor::White);
    // Runtime-spawned reflection captures have no baked cubemap in -game.
    // The atmosphere skylight supplies diffuse fill AND steel reflections.
    auto* Sky=GetWorld()->SpawnActor<ASkyLight>();
    Sky->GetLightComponent()->SetMobility(EComponentMobility::Movable);
    Sky->GetLightComponent()->SetIntensity(1.8f);
    Sky->GetLightComponent()->SetLightColor(FLinearColor(.88f,.93f,1.f));
    Sky->GetLightComponent()->SetRealTimeCapture(true);
    auto* Mist=GetWorld()->SpawnActor<AExponentialHeightFog>();
    Mist->GetComponent()->SetFogDensity(bArchivedCourtyard?.008f:0.f);
    Mist->GetComponent()->SetFogHeightFalloff(.25f);
    Mist->GetComponent()->SetStartDistance(1200.f);
    Mist->GetComponent()->SetFogMaxOpacity(.30f);
    auto* Grade=GetWorld()->SpawnActor<APostProcessVolume>();Grade->bUnbound=true;
    auto& Look=Grade->Settings;
    Look.bOverride_BloomIntensity=true;Look.BloomIntensity=.18f;
    Look.bOverride_VignetteIntensity=true;Look.VignetteIntensity=.16f;
    Look.bOverride_AmbientOcclusionIntensity=true;Look.AmbientOcclusionIntensity=.8f;
    Look.bOverride_AmbientOcclusionRadius=true;Look.AmbientOcclusionRadius=70.f;
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
    if(FParse::Param(FCommandLine::Get(),TEXT("CascadeurPreview"))){
        RightCutReload.Update(Dt);
        for(auto* Actor:Combat.actors)if(Actor->state.phase==mcl::Phase::Idle&&Actor->returnAge>.25)Actor->rightCut=RightCutReload.Clip;
    }
    for(const auto& C:Combatants){const FVector P=C->GetOwner()->GetActorLocation();C->Simulation.frameTarget={P.X,P.Y,P.Z};
        if(auto* Character=Cast<AMeleeCharacter>(C->GetOwner())){
            C->Simulation.bodyHalfHeight=Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
            C->Simulation.eyeHeight=C->Simulation.bodyHalfHeight-6.;
        }
    }
    Combat.advance(Dt);
    if(!SwingLog.IsEmpty()){
        FFileHelper::SaveStringToFile(SwingLog,*SwingLogPath,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,
            &IFileManager::Get(),FILEWRITE_Append);SwingLog.Reset();
    }
    for(int I=Sparks.Num()-1;I>=0;--I){
        auto& S=Sparks[I];S.Life-=Dt;
        if(S.Life<=0){Sparks.RemoveAtSwap(I);continue;}
        S.Velocity.Z-=700.f*Dt;S.Position+=S.Velocity*Dt;
    }
    if(ImpactParticles){
        for(int I=0;I<128;++I){
            if(I<Sparks.Num()){
                const auto& S=Sparks[I];const float Fade=FMath::Clamp(S.Life*8.f,0.f,1.f);
                const FVector Scale(FMath::Clamp(S.Velocity.Size()*.00015,.018,.08),.0025*Fade,.0025*Fade);
                ImpactParticles->UpdateInstanceTransform(I,FTransform(S.Velocity.Rotation(),S.Position,Scale),true,false,true);
                ImpactParticles->SetCustomDataValue(I,0,S.Color.R);ImpactParticles->SetCustomDataValue(I,1,S.Color.G);
                ImpactParticles->SetCustomDataValue(I,2,S.Color.B);ImpactParticles->SetCustomDataValue(I,3,Fade);
            }else ImpactParticles->UpdateInstanceTransform(I,FTransform(FQuat::Identity,FVector::ZeroVector,FVector::ZeroVector),true,false,true);
        }
        ImpactParticles->MarkRenderStateDirty();
    }
    for(const auto& E:Combat.events){
        if(E.result==mcl::Resolution::Parry||E.result==mcl::Resolution::Chamber||E.result==mcl::Resolution::Wall||E.result==mcl::Resolution::Hit){
            auto* Player=Cast<AMeleeCharacter>(UGameplayStatics::GetPlayerPawn(this,0));
            if(Player&&Player->Combat->Simulation.id==E.defender&&(E.result==mcl::Resolution::Parry||E.result==mcl::Resolution::Chamber)){FeedbackResult=E.result;FeedbackUntil=Combat.time+.65;}
            FLinearColor Color=E.result==mcl::Resolution::Chamber?FLinearColor(.15f,.85f,1.f):
                E.result==mcl::Resolution::Hit?FLinearColor(.5f,.025f,.015f):FLinearColor(1.f,.65f,.15f);
            FVector SparkOrigin=V(E.point);
            // Body-contact chambers can resolve beside the camera. Keep their cosmetic burst visible.
            if(Player&&Player->Combat->Simulation.id==E.defender&&E.result==mcl::Resolution::Chamber){
                const auto& Defender=Player->Combat->Simulation;
                FVector Forward=V(Defender.view.forward());
                FVector Eye=V(Defender.eye());
                SparkOrigin+=Forward*FMath::Max(0.,55.-FVector::DotProduct(SparkOrigin-Eye,Forward));
            }
            const int Count=E.result==mcl::Resolution::Hit?12:28;
            for(int I=0;I<Count&&Sparks.Num()<128;++I)Sparks.Add({SparkOrigin,V(E.normal)*130.f+
                FMath::VRand()*FMath::FRandRange(60.f,220.f),FMath::FRandRange(.12f,.3f),Color});
        }
        PlayImpact(E);
        for(const auto& C:Combatants)if(C->Simulation.id==E.attacker||C->Simulation.id==E.defender){
            if(auto* Character=Cast<AMeleeCharacter>(C->GetOwner()))Character->Feedback(E);
        }
        FColor Color=E.result==mcl::Resolution::Chamber?FColor::Cyan:E.result==mcl::Resolution::Parry?FColor::Yellow:FColor(255,70,35);
        if(bDebug)DrawDebugSphere(GetWorld(),V(E.point),9,8,Color,false,static_cast<float>(Combat.tuning.HitEmphasis),0,2);
    }
    if(bDebug)DrawCombatDebug();
    if(bInspection&&InspectionCamera){if(auto* Pawn=UGameplayStatics::GetPlayerPawn(this,0)){
        const FVector Focus=Pawn->GetActorLocation();const FVector At=Focus+
            (FParse::Param(FCommandLine::Get(),TEXT("MotionReview"))?FVector(210,260,80):FVector(-260,390,180));
        InspectionCamera->SetActorLocationAndRotation(At,(Focus+FVector(30,0,0)-At).Rotation());
    }}
}
void ACombatLabGameMode::ResetLab()
{
    const bool Pilot=FParse::Param(FCommandLine::Get(),TEXT("RightHorizontalPilot"));
    if(CombatAudio)CombatAudio->Reset();
    if(Tracers)Tracers->Clear();
    if(auto* Player=Cast<AMeleeCharacter>(UGameplayStatics::GetPlayerPawn(this,0)))Player->ResetAt(FVector(100,0,90),FRotator::ZeroRotator);
    if(AttackingDummy){AttackingDummy->ResetAt(FVector(Pilot?250:350,0,90),FRotator(0,180,0));AttackingDummy->Pattern.wait=1.5;AttackingDummy->Pattern.sequence=0;
        if(Pilot){AttackingDummy->Pattern.mode=mcl::TrainingMode::Passive;AttackingDummy->Combat->Simulation.infiniteHealth=true;}}
    if(PassiveDummy)PassiveDummy->ResetAt(FVector(350,550,90),FRotator(0,180,0));
    Combat.accumulator=0;Sparks.Reset();FeedbackUntil=0;
    if(Pilot){bDebug=false;UE_LOG(LogTemp,Display,TEXT("RIGHT_HORIZONTAL_PILOT close passive defender; EX timing/contact unchanged; F2 patterns, F5 external, R reset"));}
}
void ACombatLabGameMode::NextPattern()
{
    if(AttackingDummy){auto& P=AttackingDummy->Pattern;P.mode=static_cast<mcl::TrainingMode>((static_cast<int>(P.mode)+1)%static_cast<int>(mcl::TrainingMode::Count));ResetLab();}
}
void ACombatLabGameMode::PlayImpact(const mcl::CombatEvent& E)
{
    if(CombatAudio){CombatAudio->Contact(E);return;}
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
        auto DrawHurt=[&](FColor Color,float Thickness){for(const auto Axis:S.hurtAxes()){
            const FVector A=V(Axis.a),B=V(Axis.b);
            DrawDebugCapsule(GetWorld(),(A+B)*.5,(B-A).Size()*.5+S.bodyRadius,S.bodyRadius,
                FQuat::FindBetweenNormals(FVector::UpVector,(B-A).GetSafeNormal()),Color,false,-1,0,Thickness);
        }};
        if(!bOwn||bInspection)DrawHurt(FColor(90,110,130),.7f);
        if(!Tracers||!Tracers->Enabled()){
        DrawDebugLine(GetWorld(),V(S.previousWeapon.hilt),V(S.previousWeapon.tip),FColor::Silver,false,-1,0,1);
        DrawDebugLine(GetWorld(),V(S.weapon.hilt),V(S.weapon.tip),S.state.damaging()?FColor::Red:FColor::Green,false,-1,0,3);
        if(S.state.phase==mcl::Phase::Release)for(auto Sweep:S.traces){
            const float Speed=FMath::Clamp(static_cast<float>(S.speed/2000.),0.f,1.f);
            const FColor Color=FLinearColor::LerpUsingHSV(FLinearColor(.1f,.4f,1),FLinearColor(1,.12f,.02f),Speed).ToFColor(true);
            DrawDebugLine(GetWorld(),V(Sweep.a),V(Sweep.b),Color,false,.08f,0,.5f);
        }
        }
        if(S.state.phase==mcl::Phase::Parry){
            DrawDebugBox(GetWorld(),V(G.center),V(G.half),FRotator(G.boxRotation.pitch,G.boxRotation.yaw,0).Quaternion(),FColor::Blue,false,-1,0,1);
            DrawDebugCone(GetWorld(),V(G.coneOrigin),V(G.coneRotation.forward()),G.coneLength/std::cos(G.coneAngle*mcl::Rad),G.coneAngle*mcl::Rad,G.coneAngle*mcl::Rad,24,FColor::Yellow,false,-1,0,.8f);
        }
        if(S.state.chamberActive(Combat.tuning)){
            if(!bOwn||bInspection)DrawHurt(FColor::Cyan,2.f);
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
    FString Message;const bool bOk=TuningPersistence.Save(Combat.tuning,bPromote,Message);
    PublishTuning(Message);return bOk;
}
bool ACombatLabGameMode::LoadTuning()
{
    if(!bTuningConfigured){
        TuningPersistence.ProjectPath=FPaths::ConvertRelativePathToFull(FPaths::ProjectConfigDir()/TEXT("CombatDefaults.json"));
        TuningPersistence.PromotionPath=TuningPersistence.ProjectPath;
        TuningPersistence.SavedPath=FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/TEXT("Config/CombatTuning.json"));
        TuningPersistence.bDefaultsOnly=FParse::Param(FCommandLine::Get(),TEXT("CombatDefaultsOnly"));
        FString Override;
        if(FParse::Value(FCommandLine::Get(),TEXT("CombatDefaults="),Override)){
            TuningPersistence.ProjectPath=FPaths::ConvertRelativePathToFull(Override);TuningPersistence.bExplicitProjectPath=true;
        }
        FParse::Value(FCommandLine::Get(),TEXT("CombatTuningReceipt="),TuningReceiptPath);
        bTuningConfigured=true;
    }
    const bool bOk=TuningPersistence.Load(Combat.tuning);PublishTuning();return bOk;
}
void ACombatLabGameMode::ResetTuning()
{
    TuningPersistence.Reset(Combat.tuning);PublishTuning(TEXT("Built-in defaults restored; SAVE to persist"));
}
void ACombatLabGameMode::SetTuningValue(const FString& Name,double Value)
{
    if(TuningPersistence.SetValue(Combat.tuning,Name,Value))PublishTuning();
}
void ACombatLabGameMode::PublishTuning(const FString& Message)
{
    TuningStatus=(Message.IsEmpty()?FString():Message+TEXT("\n"))+TuningPersistence.Describe();
    UE_LOG(LogTemp,Display,TEXT("CombatTuning: %s"),*TuningStatus);
    if(!TuningReceiptPath.IsEmpty()){
        const bool bInputCollision=FPaths::IsSamePath(TuningReceiptPath,TuningPersistence.ProjectPath)||
            FPaths::IsSamePath(TuningReceiptPath,TuningPersistence.SavedPath)||FPaths::IsSamePath(TuningReceiptPath,TuningPersistence.PromotionPath);
        if(bInputCollision||!TuningPersistence.WriteReceipt(Combat.tuning,TuningReceiptPath)){
            TuningStatus+=TEXT("\nRECEIPT WRITE FAILED: ")+TuningReceiptPath;
            UE_LOG(LogTemp,Error,TEXT("CombatTuning receipt write failed (requires separate absolute output path): %s"),*TuningReceiptPath);
        }
    }
}
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
