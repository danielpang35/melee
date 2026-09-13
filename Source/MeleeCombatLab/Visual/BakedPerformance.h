#pragma once
#include "CoreMinimal.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"

// Component-space skeletal deltas from the saved Cascadeur solve. Weapon
// choreography is loaded separately by authoritative simulation.
struct FBakedPerformance
{
    TArray<TArray<FTransform>> Frames;
    TArray<FName> Names;
    double Fps=120.;
    FDateTime Stamp;
    FString LoadedPath;
    double Poll=1.,Clock=0.;
    void Reload(double Dt,const TCHAR* Filename=TEXT("CascadeurPreview.csv"))
    {
        Poll+=Dt;if(Poll<1.)return;Poll=0.;
        const FString Path=FPaths::IsRelative(Filename)?FPaths::ProjectConfigDir()/Filename:FString(Filename);
        const auto NewStamp=IFileManager::Get().GetTimeStamp(*Path);
        if(NewStamp==Stamp&&Path==LoadedPath)return;
        TArray<FString> Lines;if(!FFileHelper::LoadFileToStringArray(Lines,*Path)||Lines.Num()<3)return;
        TArray<FString> Header;Lines[0].ParseIntoArray(Header,TEXT(","));
        if(Header.Num()!=3||Header[0]!=TEXT("CASCADEUR_SKELETON_V1"))return;
        const double Rate=FCString::Atod(*Header[1]);const int32 Count=FCString::Atoi(*Header[2]);
        if(!FMath::IsFinite(Rate)||Rate<1.||Rate>240.||Count<2||Count>10000)return;
        TArray<FName> NewNames;TArray<TArray<FTransform>> NewFrames;NewFrames.SetNum(Count);
        for(int32 Row=1;Row<Lines.Num();++Row){
            TArray<FString> Cells;Lines[Row].ParseIntoArray(Cells,TEXT(","));if(Cells.Num()!=9)return;
            const int32 Frame=FCString::Atoi(*Cells[0]);if(Frame<0||Frame>=Count)return;
            const FName Name(*Cells[1]);const int32 Slot=NewFrames[Frame].Num();
            if(Frame==0){if(NewNames.Contains(Name))return;NewNames.Add(Name);}
            else if(!NewNames.IsValidIndex(Slot)||NewNames[Slot]!=Name)return;
            double V[7];for(int32 I=0;I<7;++I){V[I]=FCString::Atod(*Cells[I+2]);if(!FMath::IsFinite(V[I]))return;}
            FQuat Q(V[3],V[4],V[5],V[6]);if(Q.SizeSquared()<.5||Q.SizeSquared()>1.5)return;Q.Normalize();
            NewFrames[Frame].Add(FTransform(Q,FVector(V[0],V[1],V[2])));
        }
        if(NewNames.IsEmpty())return;
        for(const auto& Frame:NewFrames)if(Frame.Num()!=NewNames.Num())return;
        Names=MoveTemp(NewNames);Frames=MoveTemp(NewFrames);Fps=Rate;Stamp=NewStamp;LoadedPath=Path;
        UE_LOG(LogTemp,Display,TEXT("CASCADEUR PREVIEW loaded %d frames, %d bones, %.1f fps"),Frames.Num(),Names.Num(),Fps);
    }
    bool Sample(double Seconds,const TMap<FName,int32>& Indices,const TArray<FTransform>& Reference,TArray<FTransform>& Out) const
    {
        if(Frames.IsEmpty())return false;
        for(const auto& Name:Names)if(!Indices.Contains(Name))return false;
        const double Frame=FMath::Clamp(Seconds*Fps,0.,double(Frames.Num()-1));
        const int32 A=int32(Frame),B=FMath::Min(A+1,Frames.Num()-1);Out=Reference;
        for(int32 I=0;I<Names.Num();++I){
            FTransform Delta;Delta.Blend(Frames[A][I],Frames[B][I],Frame-A);
            const int32 Bone=Indices.FindChecked(Names[I]);Out[Bone]=Reference[Bone]*Delta;
        }
        return true;
    }
};
