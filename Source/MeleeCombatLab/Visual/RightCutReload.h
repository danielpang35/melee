#pragma once
#include "Combat/Attacks/AuthoredRightCut.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "BakedPerformance.h"

struct FRightCutReload {
    FDateTime Stamp;
    double Poll=1.;
    std::shared_ptr<const mcl::AuthoredRightCut> Clip;
    void Update(double Dt) {
        Poll+=Dt;if(Poll<1.)return;Poll=0.;
        const FString Selector=FPaths::ProjectConfigDir()/TEXT("RightCutCandidate.txt");
        const auto Next=IFileManager::Get().GetTimeStamp(*Selector);if(Next==Stamp)return;
        FString Id;if(!FFileHelper::LoadFileToString(Id,*Selector))return;Id.TrimStartAndEndInline();
        if(Id.IsEmpty())return;
        for(TCHAR C:Id)if(!FChar::IsAlnum(C)&&C!=TEXT('_'))return;
        const FString Directory=FPaths::ConvertRelativePathToFull(FPaths::ProjectDir()/TEXT("ArtSource/Cascadeur/Candidates")/Id);
        const FString Path=Directory/TEXT("RightCutWeapon.csv");
        FString Text;if(!FFileHelper::LoadFileToString(Text,*Path))return;
        std::istringstream Input(TCHAR_TO_UTF8(*Text));
        auto Candidate=std::make_shared<mcl::AuthoredRightCut>();
        if(!Candidate->read(Input)){UE_LOG(LogTemp,Error,TEXT("RIGHT CUT rejected invalid weapon track"));return;}
        FString ViewText;if(!FFileHelper::LoadFileToString(ViewText,*(Directory/TEXT("RightCutView.csv"))))return;
        std::istringstream ViewInput(TCHAR_TO_UTF8(*ViewText));
        if(!Candidate->readView(ViewInput)){UE_LOG(LogTemp,Error,TEXT("RIGHT CUT rejected unsafe view offsets"));return;}
        const FString Body=Directory/TEXT("CascadeurPreview.csv"),FP=Directory/TEXT("CascadeurFirstPerson.csv");
        FBakedPerformance BodyCheck,FPCheck;BodyCheck.Reload(1.,*Body);FPCheck.Reload(1.,*FP);
        if(BodyCheck.Frames.Num()!=271||FPCheck.Frames.Num()!=271||BodyCheck.Names.Num()!=20||FPCheck.Names!=BodyCheck.Names||BodyCheck.Fps!=120.||FPCheck.Fps!=120.){
            UE_LOG(LogTemp,Error,TEXT("RIGHT CUT rejected incomplete skeletal bundle %s"),*Id);return;
        }
        Candidate->bodyPath=TCHAR_TO_UTF8(*Body);Candidate->firstPersonPath=TCHAR_TO_UTF8(*FP);
        Clip=Candidate;Stamp=Next;
        UE_LOG(LogTemp,Display,TEXT("RIGHT CUT coherent candidate loaded: %s %s"),*Id,*Stamp.ToString());
    }
};
