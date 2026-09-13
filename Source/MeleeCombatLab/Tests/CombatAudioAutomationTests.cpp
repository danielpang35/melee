#include "Misc/AutomationTest.h"
#include "Audio/CombatAudioRules.h"
#include "Sound/SoundWave.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCombatAudioAssets,"MeleeCombatLab.Audio.AssetBank",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCombatAudioAssets::RunTest(const FString&)
{
    for(const char* Family:mcl::AudioCueNames)for(int Variant=0;Variant<mcl::AudioVariantCount;++Variant){
        const FString Name=FString::Printf(TEXT("S_%s_%02d"),UTF8_TO_TCHAR(Family),Variant);
        auto* Wave=LoadObject<USoundWave>(nullptr,*(TEXT("/Game/Visual/CombatAudio/")+Name+TEXT(".")+Name));
        if(!TestNotNull(*Name,Wave))continue;
        TestEqual(TEXT("Mono spatial source"),Wave->NumChannels,1);
        TestTrue(TEXT("Short, nonempty cue"),Wave->GetDuration()>.1f&&Wave->GetDuration()<.6f);
        TestEqual(TEXT("Inline loading survives reload"),Wave->GetLoadingBehavior(),ESoundWaveLoadingBehavior::ForceInline);
        TestEqual(TEXT("Lossless PCM playback"),Wave->GetSoundAssetCompressionType(),ESoundAssetCompressionType::PCM);
    }
    return true;
}
#endif
