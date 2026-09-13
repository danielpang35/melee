#include "CombatTuningPersistence.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/SecureHash.h"
#include <iomanip>
#include <locale>
#include <sstream>

namespace
{
FString TextIdentity(const FString& Text)
{
    FTCHARToUTF8 Utf8(*Text);
    return TEXT("sha1:")+FSHA1::HashBuffer(Utf8.Get(),Utf8.Length()).ToString().ToLower();
}
bool ReadLayer(mcl::Tuning& Values, FCombatTuningSource& Source, bool bRequired)
{
    FString Text;
    if(!FFileHelper::LoadFileToString(Text,*Source.Path)){
        Source.Status=(IFileManager::Get().FileExists(*Source.Path)||IFileManager::Get().DirectoryExists(*Source.Path))?TEXT("unreadable"):TEXT("missing");
        Source.Detail=bRequired?TEXT("Explicit project input is required"):TEXT("Optional input unavailable");
        return !bRequired&&Source.Status==TEXT("missing");
    }
    Source.ContentIdentity=TextIdentity(Text);
    TSharedPtr<FJsonObject> Object;
    if(!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text),Object)||!Object.IsValid()){
        Source.Status=TEXT("invalid");Source.Detail=TEXT("Expected a JSON object");return false;
    }
    for(auto Entry:Values.entries()){
        const FString Name=UTF8_TO_TCHAR(Entry.name);
        if(!Object->HasField(Name))continue;
        double Value;
        if(!Object->HasTypedField<EJson::Number>(Name)||!Object->TryGetNumberField(Name,Value)||!FMath::IsFinite(Value)){
            Source.Status=TEXT("invalid");Source.Detail=TEXT("Expected finite number: ")+Name;return false;
        }
        *Entry.value=FMath::Clamp(Value,Entry.minimum,Entry.maximum);
        ++Source.AppliedFields;if(*Entry.value!=Value)++Source.ClampedFields;
    }
    Source.Status=TEXT("loaded");
    Source.Detail=FString::Printf(TEXT("%d fields, %d clamped"),Source.AppliedFields,Source.ClampedFields);
    return true;
}
TSharedRef<FJsonObject> SourceJson(const FCombatTuningSource& Source)
{
    auto Object=MakeShared<FJsonObject>();
    Object->SetStringField(TEXT("path"),Source.Path);Object->SetStringField(TEXT("status"),Source.Status);
    Object->SetStringField(TEXT("detail"),Source.Detail);Object->SetStringField(TEXT("contentIdentity"),Source.ContentIdentity);
    Object->SetNumberField(TEXT("recognizedFields"),Source.AppliedFields);Object->SetNumberField(TEXT("clampedFields"),Source.ClampedFields);
    return Object;
}
TSharedRef<FJsonObject> SourcesJson(const FCombatTuningSource& Project,const FCombatTuningSource& Saved)
{
    auto Object=MakeShared<FJsonObject>();Object->SetObjectField(TEXT("project"),SourceJson(Project));Object->SetObjectField(TEXT("saved"),SourceJson(Saved));return Object;
}
bool WriteJson(const TSharedRef<FJsonObject>& Object,const FString& Path)
{
    FString Text;
    if(!FJsonSerializer::Serialize(Object,TJsonWriterFactory<TCHAR,TPrettyJsonPrintPolicy<TCHAR>>::Create(&Text)))return false;
    IFileManager::Get().MakeDirectory(*FPaths::GetPath(Path),true);
    if(!FFileHelper::SaveStringToFile(Text,*(Path+TEXT(".tmp")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))return false;
    return IFileManager::Get().Move(*Path,*(Path+TEXT(".tmp")),true,true);
}
FString SourceLine(const FCombatTuningSource& Source)
{
    return FString::Printf(TEXT("%s | %s | %s | %s"),*Source.Path,*Source.Status,*Source.Detail,*Source.ContentIdentity);
}
}

FString FCombatTuningPersistence::Identity(mcl::Tuning Values)
{
    std::ostringstream Canonical;Canonical.imbue(std::locale::classic());Canonical<<std::setprecision(17);
    for(auto Entry:Values.entries())Canonical<<Entry.name<<'='<<(*Entry.value==0.?0.:*Entry.value)<<'\n';
    return TextIdentity(UTF8_TO_TCHAR(Canonical.str().c_str()));
}
void FCombatTuningPersistence::Changed(mcl::Tuning& Values,const TCHAR* NewEvent)
{
    EffectiveIdentity=Identity(Values);Event=NewEvent;++Sequence;
}
bool FCombatTuningPersistence::Load(mcl::Tuning& Values)
{
    AttemptProject={};AttemptSaved={};
    AttemptProject.Path=FPaths::ConvertRelativePathToFull(ProjectPath);
    AttemptSaved.Path=FPaths::ConvertRelativePathToFull(SavedPath);
    if(bDefaultsOnly){AttemptSaved.Status=TEXT("ignored-defaults-only");AttemptSaved.Detail=TEXT("Not read");}
    mcl::Tuning Candidate;
    bLoadSucceeded=ReadLayer(Candidate,AttemptProject,bExplicitProjectPath);
    if(bLoadSucceeded&&!bDefaultsOnly)bLoadSucceeded=ReadLayer(Candidate,AttemptSaved,false);
    if(bLoadSucceeded){
        Values=Candidate;ActiveProject=AttemptProject;ActiveSaved=AttemptSaved;EffectiveOrigin=TEXT("loaded");
    }
    Changed(Values,TEXT("load"));
    if(StartupIdentity.IsEmpty())StartupIdentity=EffectiveIdentity;
    return bLoadSucceeded;
}
void FCombatTuningPersistence::Reset(mcl::Tuning& Values)
{
    Values={};EffectiveOrigin=TEXT("built-in-reset");ActiveProject={};ActiveSaved={};
    Changed(Values,TEXT("reset"));
}
bool FCombatTuningPersistence::SetValue(mcl::Tuning& Values,const FString& Name,double Value)
{
    if(!FMath::IsFinite(Value))return false;
    for(auto Entry:Values.entries())if(Name==UTF8_TO_TCHAR(Entry.name)){
        const double Clamped=FMath::Clamp(Value,Entry.minimum,Entry.maximum);
        if(*Entry.value==Clamped)return false;
        *Entry.value=Clamped;EffectiveOrigin=TEXT("live-edit");Changed(Values,TEXT("edit"));return true;
    }
    return false;
}
bool FCombatTuningPersistence::Save(mcl::Tuning& Values,bool bPromote,FString& Message)
{
    auto Object=MakeShared<FJsonObject>();Object->SetNumberField(TEXT("SchemaVersion"),1);
    for(auto Entry:Values.entries())Object->SetNumberField(UTF8_TO_TCHAR(Entry.name),*Entry.value);
    const FString Path=FPaths::ConvertRelativePathToFull(bPromote?(PromotionPath.IsEmpty()?ProjectPath:PromotionPath):SavedPath);
    const bool bOk=WriteJson(Object,Path);
    Message=(bOk?TEXT("Saved: "):TEXT("SAVE FAILED: "))+Path;
    Changed(Values,bOk?TEXT("save"):TEXT("save-failed"));return bOk;
}
FString FCombatTuningPersistence::Describe() const
{
    return FString::Printf(TEXT("%s | %s | %s\nEffective %s\nActive project: %s\nActive Saved: %s\nLast load %s\nProject: %s\nSaved: %s"),
        bDefaultsOnly?TEXT("DEFAULTS ONLY"):TEXT("NORMAL"),*Event,*EffectiveOrigin,*EffectiveIdentity,
        *SourceLine(ActiveProject),*SourceLine(ActiveSaved),bLoadSucceeded?TEXT("succeeded"):TEXT("FAILED (values retained)"),
        *SourceLine(AttemptProject),*SourceLine(AttemptSaved));
}
TSharedRef<FJsonObject> FCombatTuningPersistence::Receipt(mcl::Tuning Values) const
{
    auto Object=MakeShared<FJsonObject>();Object->SetNumberField(TEXT("schemaVersion"),1);
    Object->SetStringField(TEXT("event"),Event);Object->SetNumberField(TEXT("sequence"),Sequence);
    Object->SetBoolField(TEXT("defaultsOnly"),bDefaultsOnly);Object->SetBoolField(TEXT("loadSucceeded"),bLoadSucceeded);
    Object->SetStringField(TEXT("effectiveOrigin"),EffectiveOrigin);Object->SetStringField(TEXT("effectiveIdentity"),Identity(Values));
    Object->SetStringField(TEXT("startupIdentity"),StartupIdentity);
    Object->SetNumberField(TEXT("contentIdentityVersion"),1);Object->SetNumberField(TEXT("effectiveIdentityVersion"),1);
    Object->SetStringField(TEXT("contentIdentityFormat"),TEXT("sha1 of decoded file text re-encoded as UTF-8 without BOM"));
    Object->SetStringField(TEXT("effectiveIdentityFormat"),TEXT("sha1 of registry-order name=value LF lines; classic-locale 17 significant digits; zero normalized"));
    Object->SetObjectField(TEXT("activeSources"),SourcesJson(ActiveProject,ActiveSaved));
    Object->SetObjectField(TEXT("lastLoadAttempt"),SourcesJson(AttemptProject,AttemptSaved));
    auto Effective=MakeShared<FJsonObject>();for(auto Entry:Values.entries())Effective->SetNumberField(UTF8_TO_TCHAR(Entry.name),*Entry.value);
    Object->SetObjectField(TEXT("effectiveValues"),Effective);return Object;
}
bool FCombatTuningPersistence::WriteReceipt(mcl::Tuning Values,const FString& Path) const
{
    return !Path.IsEmpty()&&!FPaths::IsRelative(Path)&&WriteJson(Receipt(Values),Path);
}
