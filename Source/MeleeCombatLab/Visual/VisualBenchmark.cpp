#include "VisualBenchmark.h"
#include "Training/CombatLabGameMode.h"
#include "Training/TrainingDummy.h"
#include "Combat/CombatComponent.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"
#include "Engine/GameViewportClient.h"
#include "UnrealClient.h"
#include "HAL/PlatformTime.h"
#include "HAL/PlatformMemory.h"
#include "HAL/PlatformMisc.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "RHI.h"
#include "RHIStats.h"
#include "Serialization/JsonSerializer.h"
#include "Dom/JsonObject.h"
#if WITH_EDITOR
#include "AssetCompilingManager.h"
#include "ShaderCompiler.h"
#endif

UVisualBenchmark::UVisualBenchmark(){PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.TickGroup=TG_PostUpdateWork;}
void UVisualBenchmark::TickComponent(float Dt,ELevelTick Type,FActorComponentTickFunction* Function)
{
    Super::TickComponent(Dt,Type,Function);if(Finished)return;
    auto* Lab=Cast<ACombatLabGameMode>(GetOwner());auto* PC=GetWorld()->GetFirstPlayerController();if(!Lab||!PC)return;
    const double Now=FPlatformTime::Seconds();const double WallDt=LastClock>0?Now-LastClock:Dt;LastClock=Now;Age+=WallDt;
    if(!Started){
#if WITH_EDITOR
        // Captures and timing start only after the newly imported art is ready.
        if(FAssetCompilingManager::Get().GetNumRemainingAssets()>0||(GShaderCompilingManager&&GShaderCompilingManager->IsCompiling())){Age=0;return;}
#endif
        if(Age<1)return;Started=true;Label=TEXT("baseline");FParse::Value(FCommandLine::Get(),TEXT("VisualBenchmark="),Label);
        Label=FPaths::MakeValidFileName(Label);Lab->bDebug=false;Lab->ResetLab();
        Camera=GetWorld()->SpawnActor<ACameraActor>();Camera->GetCameraComponent()->SetFieldOfView(100);PC->SetViewTarget(Camera);
        if(!FParse::Param(FCommandLine::Get(),TEXT("CitadelCapture")))PC->ConsoleCommand(TEXT("stat unit"),false);
        else PC->ConsoleCommand(TEXT("DisableAllScreenMessages"),false);
        PC->ConsoleCommand(TEXT("csvprofile start"),false);
        Rows=TEXT("elapsed_s,frame_ms,game_ms,render_ms,gpu_ms,draw_calls,primitives,process_mb\n");
    }
    // Frozen route v1: human eye-height tour of the duel lane and fountain ring.
    const FVector Points[]={FVector(0,-110,154),FVector(-350,-180,154),FVector(-650,450,154),FVector(-500,1150,154),FVector(500,1150,154),FVector(650,450,154),FVector(450,-180,154),FVector(0,-110,154)};
    const double Route=FMath::Clamp((Age-6.)/24.,0.,.999999)*7.;int Index=FMath::FloorToInt(Route);
    FVector At=FMath::Lerp(Points[Index],Points[Index+1],Route-Index);
    FVector Focus=Age<11?FVector(300,0,115):FVector(0,650,110);
    Camera->SetActorLocationAndRotation(At,(Focus-At).Rotation());
    if(Age<6)return;
    if(Age>=30){Finish();return;}
    auto* View=GetWorld()->GetGameViewport();const FStatUnitData* Unit=View?View->GetStatUnitData():nullptr;
    double G=Unit?Unit->RawGameThreadTime:0,R=Unit?Unit->RawRenderThreadTime:0,U=Unit?Unit->RawGPUFrameTime[0]:0;
    Frames.Add(WallDt*1000.);Game.Add(G);Render.Add(R);Gpu.Add(U);Draws.Add(GNumDrawCallsRHI[0]);Primitives.Add(GNumPrimitivesDrawnRHI[0]);
    const auto Memory=FPlatformMemory::GetStats();
    Rows+=FString::Printf(TEXT("%.4f,%.4f,%.4f,%.4f,%.4f,%d,%d,%.2f\n"),Age-6,WallDt*1000,G,R,U,GNumDrawCallsRHI[0],GNumPrimitivesDrawnRHI[0],Memory.UsedPhysical/1048576.);
    if(Shot<3&&Age>8+Shot*9){
        FString Folder=FPaths::ProjectSavedDir()/TEXT("VisualPerformance")/Label;IFileManager::Get().MakeDirectory(*Folder,true);
        FScreenshotRequest::RequestScreenshot(Folder/FString::Printf(TEXT("route_%d.png"),Shot++),true,false,false);
    }
}
void UVisualBenchmark::Finish()
{
    Finished=true;auto* PC=GetWorld()->GetFirstPlayerController();if(PC)PC->ConsoleCommand(TEXT("csvprofile stop"),false);
    auto Root=MakeShared<FJsonObject>();Root->SetStringField(TEXT("route"),TEXT("courtyard-eye-height-v1; 6s warmup, 24s sample; screenshot frames retained"));
    Root->SetStringField(TEXT("startup"),TEXT("Wait for asset and shader compilation, reset fixture, then start route warmup."));
    Root->SetStringField(TEXT("label"),Label);Root->SetStringField(TEXT("build"),TEXT("Development Editor executable -game; editor-linked overhead included; not packaged"));
    Root->SetStringField(TEXT("cpu"),FPlatformMisc::GetCPUBrand());Root->SetStringField(TEXT("gpu"),GRHIAdapterName);
    Root->SetNumberField(TEXT("physical_ram_gb"),FPlatformMemory::GetConstants().TotalPhysical/1073741824.);
    if(auto* V=GetWorld()->GetGameViewport();V&&V->Viewport){Root->SetNumberField(TEXT("width"),V->Viewport->GetSizeXY().X);Root->SetNumberField(TEXT("height"),V->Viewport->GetSizeXY().Y);}
    auto Mean=[](const TArray<double>& Values){double Sum=0;for(double V:Values)Sum+=V;return Values.Num()?Sum/Values.Num():0.;};
    Frames.Sort();Root->SetNumberField(TEXT("samples"),Frames.Num());Root->SetNumberField(TEXT("frame_mean_ms"),Mean(Frames));Root->SetNumberField(TEXT("fps_from_mean"),1000./FMath::Max(.001,Mean(Frames)));
    if(Frames.Num()){Root->SetNumberField(TEXT("frame_p95_ms"),Frames[FMath::Min(Frames.Num()-1,int(Frames.Num()*.95))]);Root->SetNumberField(TEXT("frame_p99_ms"),Frames[FMath::Min(Frames.Num()-1,int(Frames.Num()*.99))]);}
    Root->SetNumberField(TEXT("game_mean_ms"),Mean(Game));Root->SetNumberField(TEXT("render_mean_ms"),Mean(Render));Root->SetNumberField(TEXT("gpu_mean_ms"),Mean(Gpu));Root->SetNumberField(TEXT("draw_calls_mean"),Mean(Draws));Root->SetNumberField(TEXT("primitives_mean"),Mean(Primitives));
    Root->SetStringField(TEXT("limitations"),TEXT("Zero counters mean unavailable. Shadow/translucency timing requires external GPU event capture; CSV GPU scopes are retained where supported. RTX 5070 is above target GPU tier; Ryzen 1600 is below modern target CPU tier. No target-hardware claim."));
    auto Settings=MakeShared<FJsonObject>();for(const TCHAR* Name:{TEXT("r.ScreenPercentage"),TEXT("r.ShadowQuality"),TEXT("r.Shadow.Virtual.Enable"),TEXT("r.DynamicGlobalIlluminationMethod"),TEXT("r.ReflectionMethod"),TEXT("r.AntiAliasingMethod"),TEXT("r.VSync"),TEXT("t.MaxFPS"),TEXT("sg.EffectsQuality"),TEXT("sg.PostProcessQuality")})if(auto* C=IConsoleManager::Get().FindConsoleVariable(Name))Settings->SetStringField(Name,C->GetString());Root->SetObjectField(TEXT("settings"),Settings);
    FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Root,Writer);
    FString Folder=FPaths::ProjectSavedDir()/TEXT("VisualPerformance")/Label;IFileManager::Get().MakeDirectory(*Folder,true);FFileHelper::SaveStringToFile(Text,*(Folder/TEXT("summary.json")));FFileHelper::SaveStringToFile(Rows,*(Folder/TEXT("frames.csv")));
    UE_LOG(LogTemp,Display,TEXT("VISUAL BENCHMARK COMPLETE %s: %.2f ms mean"),*Label,Mean(Frames));
    FPlatformMisc::RequestExit(false);
}
