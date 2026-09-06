#include "TournamentGraphics.h"
#include "HAL/IConsoleManager.h"
#include "Misc/ConfigCacheIni.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
namespace TournamentGraphics
{
FString Profile=TEXT("Competitive");int Tier=0;
void Apply(const FString& Name)
{
    if(Name==TEXT("Baseline")){Profile=Name;Tier=0;return;}
    Profile=Name==TEXT("High")||Name==TEXT("Showcase")?Name:TEXT("Competitive");Tier=Profile==TEXT("Showcase")?2:Profile==TEXT("High")?1:0;
    FString File=FPaths::ProjectConfigDir()/TEXT("GraphicsProfiles.ini");GConfig->LoadFile(File);TArray<FString> Lines;GConfig->GetSection(*Profile,Lines,File);
    for(const FString& Line:Lines){FString Key,Value;if(Line.Split(TEXT("="),&Key,&Value))if(auto* C=IConsoleManager::Get().FindConsoleVariable(*Key))C->Set(*Value,ECVF_SetByCode);}
}
void Initialize(){FString Name;FParse::Value(FCommandLine::Get(),TEXT("LabProfile="),Name);Apply(Name);}
void Cycle(){Apply(Tier==0?TEXT("High"):Tier==1?TEXT("Showcase"):TEXT("Competitive"));}
}
