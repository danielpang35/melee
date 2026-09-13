#include "Misc/AutomationTest.h"
#include "Training/CombatTuningPersistence.h"
#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Guid.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace
{
struct FTuningFixture
{
    FString Directory=FPaths::ConvertRelativePathToFull(FPaths::ProjectIntermediateDir()/TEXT("CombatTuningTests")/FGuid::NewGuid().ToString());
    FCombatTuningPersistence Store;
    mcl::Tuning Values;
    FTuningFixture()
    {
        IFileManager::Get().MakeDirectory(*Directory,true);
        Store.ProjectPath=Directory/TEXT("project.json");Store.SavedPath=Directory/TEXT("user.json");
    }
    ~FTuningFixture(){IFileManager::Get().DeleteDirectory(*Directory,false,true);}
    bool Project(const FString& Text){return FFileHelper::SaveStringToFile(Text,*Store.ProjectPath);}
    bool Saved(const FString& Text){return FFileHelper::SaveStringToFile(Text,*Store.SavedPath);}
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCombatTuningLayers,"MeleeCombatLab.Tuning.OverlayAndIdentity",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCombatTuningLayers::RunTest(const FString&)
{
    FTuningFixture F;
    TestTrue(TEXT("Project fixture written"),F.Project(TEXT("{\"SchemaVersion\":1,\"StrikeWindup\":0.8,\"Damage\":42,\"BladeLength\":999}")));
    TestTrue(TEXT("Saved fixture written"),F.Saved(TEXT("{\"StrikeWindup\":0.9}")));
    TestTrue(TEXT("Normal layered load succeeds"),F.Store.Load(F.Values));
    TestEqual(TEXT("Saved wins"),F.Values.StrikeWindup,.9);
    TestEqual(TEXT("Project survives partial Saved overlay"),F.Values.Damage,42.);
    TestEqual(TEXT("Finite input clamped"),F.Values.BladeLength,160.);
    TestEqual(TEXT("Unspecified entry remains built-in"),F.Values.StabWindup,mcl::Tuning{}.StabWindup);
    TestEqual(TEXT("Project clamp disclosed"),F.Store.ActiveProject.ClampedFields,1);
    TestFalse(TEXT("Loaded full path is absolute"),FPaths::IsRelative(F.Store.ActiveProject.Path));
    const FString Previous=F.Store.EffectiveIdentity;
    TestTrue(TEXT("Schema-only change fixture written"),F.Saved(TEXT("{\"SchemaVersion\":900,\"StrikeWindup\":0.9}")));
    TestTrue(TEXT("Reload succeeds"),F.Store.Load(F.Values));
    TestEqual(TEXT("Effective identity measures values, not schema"),F.Store.EffectiveIdentity,Previous);
    TestTrue(TEXT("Value change fixture written"),F.Saved(TEXT("{\"StrikeWindup\":1.0}")));
    TestTrue(TEXT("Changed load succeeds"),F.Store.Load(F.Values));
    TestNotEqual(TEXT("Value change alters identity"),F.Store.EffectiveIdentity,Previous);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCombatTuningDefaultsOnly,"MeleeCombatLab.Tuning.DefaultsOnlyReload",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCombatTuningDefaultsOnly::RunTest(const FString&)
{
    FTuningFixture F;
    TestTrue(TEXT("Project fixture written"),F.Project(TEXT("{\"StrikeWindup\":0.8}")));
    TestTrue(TEXT("Invalid Saved fixture written"),F.Saved(TEXT("broken JSON")));
    TArray<uint8> Before,After;
    TestTrue(TEXT("Saved bytes captured"),FFileHelper::LoadFileToArray(Before,*F.Store.SavedPath));
    F.Store.bDefaultsOnly=true;
    TestTrue(TEXT("Defaults-only ignores malformed Saved"),F.Store.Load(F.Values));
    TestEqual(TEXT("Project value loaded"),F.Values.StrikeWindup,.8);
    TestEqual(TEXT("Saved ignore explicit"),F.Store.ActiveSaved.Status,FString(TEXT("ignored-defaults-only")));
    TestTrue(TEXT("Ignored Saved not hashed/read"),F.Store.ActiveSaved.ContentIdentity.IsEmpty());
    const FString Initial=F.Store.EffectiveIdentity;
    TestTrue(TEXT("Live edit still permitted"),F.Store.SetValue(F.Values,TEXT("StrikeWindup"),1.2));
    TestNotEqual(TEXT("Live identity updated"),F.Store.EffectiveIdentity,Initial);
    TestTrue(TEXT("Reload retains defaults-only mode"),F.Store.Load(F.Values));
    TestEqual(TEXT("Reload restores initial effective values"),F.Store.EffectiveIdentity,Initial);
    TestTrue(TEXT("Saved fixture remains readable"),FFileHelper::LoadFileToArray(After,*F.Store.SavedPath));
    TestTrue(TEXT("Defaults-only never modifies Saved bytes"),Before==After);
    F.Store.Reset(F.Values);
    TestEqual(TEXT("Reset is built-ins"),F.Store.EffectiveIdentity,FCombatTuningPersistence::Identity(mcl::Tuning{}));
    TestTrue(TEXT("Reload after reset still ignores Saved"),F.Store.Load(F.Values));
    TestEqual(TEXT("Project restored after reset"),F.Store.EffectiveIdentity,Initial);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCombatTuningFailure,"MeleeCombatLab.Tuning.AbsentInvalidAtomicLoad",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCombatTuningFailure::RunTest(const FString&)
{
    FTuningFixture F;
    TestTrue(TEXT("Optional missing files use built-ins"),F.Store.Load(F.Values));
    TestEqual(TEXT("Project absence disclosed"),F.Store.ActiveProject.Status,FString(TEXT("missing")));
    TestEqual(TEXT("Saved absence disclosed"),F.Store.ActiveSaved.Status,FString(TEXT("missing")));
    TestTrue(TEXT("Valid project fixture written"),F.Project(TEXT("{\"Damage\":49}")));
    TestTrue(TEXT("Valid project loaded"),F.Store.Load(F.Values));
    const FString Active=F.Store.EffectiveIdentity,ActiveSource=F.Store.ActiveProject.ContentIdentity;
    TestTrue(TEXT("Changed project fixture written"),F.Project(TEXT("{\"Damage\":70}")));
    TestTrue(TEXT("Invalid Saved fixture written"),F.Saved(TEXT("{invalid")));
    TestFalse(TEXT("Malformed overlay fails load"),F.Store.Load(F.Values));
    TestEqual(TEXT("Failed load leaves previous values"),F.Values.Damage,49.);
    TestEqual(TEXT("Failed load keeps active identity"),F.Store.EffectiveIdentity,Active);
    TestEqual(TEXT("Failed load keeps active source identity"),F.Store.ActiveProject.ContentIdentity,ActiveSource);
    TestNotEqual(TEXT("Attempt tracks different project bytes"),F.Store.AttemptProject.ContentIdentity,ActiveSource);
    TestEqual(TEXT("Invalid Saved outcome disclosed"),F.Store.AttemptSaved.Status,FString(TEXT("invalid")));
    const auto Receipt=F.Store.Receipt(F.Values);
    TestEqual(TEXT("Receipt retains effective identity"),Receipt->GetStringField(TEXT("effectiveIdentity")),Active);
    TestFalse(TEXT("Receipt identifies failed attempt"),Receipt->GetBoolField(TEXT("loadSucceeded")));
    TestEqual(TEXT("Receipt separates active source"),Receipt->GetObjectField(TEXT("activeSources"))->GetObjectField(TEXT("project"))->GetStringField(TEXT("contentIdentity")),ActiveSource);
    TestTrue(TEXT("Wrong type fixture written"),F.Saved(TEXT("{\"Damage\":\"oops\"}")));
    TestFalse(TEXT("Wrong-type known field fails atomically"),F.Store.Load(F.Values));
    TestTrue(TEXT("Non-finite numeric fixture written"),F.Saved(TEXT("{\"Damage\":1e999}")));
    TestFalse(TEXT("Overflow/non-finite field fails atomically"),F.Store.Load(F.Values));
    TestEqual(TEXT("Invalid inputs cannot change values"),F.Store.EffectiveIdentity,Active);
    F.Store.bExplicitProjectPath=true;F.Store.ProjectPath=F.Directory/TEXT("missing-explicit.json");
    TestFalse(TEXT("Missing explicit defaults input fails"),F.Store.Load(F.Values));
    TestEqual(TEXT("Explicit absence preserves values"),F.Store.EffectiveIdentity,Active);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCombatTuningSaveResetReceipt,"MeleeCombatLab.Tuning.SaveResetAndReceipt",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCombatTuningSaveResetReceipt::RunTest(const FString&)
{
    FTuningFixture F;
    TestTrue(TEXT("Initial load succeeds"),F.Store.Load(F.Values));
    const FString Initial=F.Store.EffectiveIdentity;
    TestFalse(TEXT("Non-finite live edit rejected"),F.Store.SetValue(F.Values,TEXT("Damage"),std::numeric_limits<double>::infinity()));
    TestTrue(TEXT("Finite live edit accepted/clamped"),F.Store.SetValue(F.Values,TEXT("Damage"),200.));
    TestEqual(TEXT("Live clamp applied"),F.Values.Damage,100.);
    const FString Edited=F.Store.EffectiveIdentity;
    FString Message;
    TestTrue(TEXT("Normal Save writes isolated Saved fixture"),F.Store.Save(F.Values,false,Message));
    F.Store.Reset(F.Values);
    TestEqual(TEXT("Reset updates identity"),F.Store.EffectiveIdentity,Initial);
    TestEqual(TEXT("Reset clears active file contribution"),F.Store.ActiveSaved.Status,FString(TEXT("not-attempted")));
    TestTrue(TEXT("Normal reload restores Saved edit"),F.Store.Load(F.Values));
    TestEqual(TEXT("Saved values restored"),F.Store.EffectiveIdentity,Edited);
    F.Store.PromotionPath=F.Directory/TEXT("promoted.json");
    TestTrue(TEXT("Promote uses separate project destination"),F.Store.Save(F.Values,true,Message));
    TestTrue(TEXT("Promotion file exists"),IFileManager::Get().FileExists(*F.Store.PromotionPath));
    TestFalse(TEXT("Snapshot input not modified by promote"),IFileManager::Get().FileExists(*F.Store.ProjectPath));
    const FString ReceiptPath=F.Directory/TEXT("receipt.json");
    TestTrue(TEXT("Engine JSON receipt written"),F.Store.WriteReceipt(F.Values,ReceiptPath));
    FString Text;TestTrue(TEXT("Receipt readable"),FFileHelper::LoadFileToString(Text,*ReceiptPath));
    TSharedPtr<FJsonObject> Receipt;
    if(TestTrue(TEXT("Receipt is JSON"),FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text),Receipt))&&Receipt.IsValid()){
        TestEqual(TEXT("Receipt measures effective edit"),Receipt->GetStringField(TEXT("effectiveIdentity")),Edited);
        TestEqual(TEXT("Receipt retains startup identity"),Receipt->GetStringField(TEXT("startupIdentity")),Initial);
        TestEqual(TEXT("Receipt includes effective values"),Receipt->GetObjectField(TEXT("effectiveValues"))->GetNumberField(TEXT("Damage")),100.);
        TestEqual(TEXT("Receipt identifies latest operation"),Receipt->GetStringField(TEXT("event")),FString(TEXT("save")));
    }
    TestFalse(TEXT("Relative receipt path rejected"),F.Store.WriteReceipt(F.Values,TEXT("relative-receipt.json")));
    return true;
}
#endif
