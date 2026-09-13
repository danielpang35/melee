#include "CombatAudio.h"
#include "Components/AudioComponent.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundWave.h"
#include "Sound/SoundAttenuation.h"
#include "Sound/SoundConcurrency.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TimerManager.h"

void UCombatAudio::Initialize(UWorld* InWorld)
{
    World=InWorld;
    for(int Cue=0;Cue<mcl::AudioCueCount;++Cue)for(int Variant=0;Variant<mcl::AudioVariantCount;++Variant){
        const FString Name=FString::Printf(TEXT("S_%s_%02d"),UTF8_TO_TCHAR(mcl::AudioCueNames[Cue]),Variant);
        auto* Wave=LoadObject<USoundWave>(nullptr,*(TEXT("/Game/Visual/CombatAudio/")+Name+TEXT(".")+Name));
        Bank.Add(Wave);
        if(!Wave)UE_LOG(LogTemp,Error,TEXT("Missing combat audio asset: %s. Run Tools/ImportCombatAudio.py."),*Name);
    }
    Attenuation=NewObject<USoundAttenuation>(this);
    auto& Settings=Attenuation->Attenuation;
    Settings.bAttenuate=true;Settings.bSpatialize=true;
    Settings.AttenuationShape=EAttenuationShape::Sphere;
    Settings.AttenuationShapeExtents=FVector(160,0,0);
    Settings.FalloffDistance=1800;
    // Separate pools ensure a contact does not lose its voice to swing air.
    SwingConcurrency=NewObject<USoundConcurrency>(this);
    SwingConcurrency->Concurrency.MaxCount=8;
    SwingConcurrency->Concurrency.ResolutionRule=EMaxConcurrentResolutionRule::StopOldest;
    ContactConcurrency=NewObject<USoundConcurrency>(this);
    ContactConcurrency->Concurrency.MaxCount=8;
    ContactConcurrency->Concurrency.ResolutionRule=EMaxConcurrentResolutionRule::StopOldest;
    ArmorConcurrency=NewObject<USoundConcurrency>(this);
    ArmorConcurrency->Concurrency.MaxCount=4;
    ArmorConcurrency->Concurrency.ResolutionRule=EMaxConcurrentResolutionRule::StopOldest;
    ArmorAttenuation=NewObject<USoundAttenuation>(this);
    ArmorAttenuation->Attenuation=Settings;
    ArmorAttenuation->Attenuation.AttenuationShapeExtents=FVector(110,0,0);
    ArmorAttenuation->Attenuation.FalloffDistance=650;
}

UAudioComponent* UCombatAudio::Play(mcl::AudioCue Cue,FVector Position,float Gain)
{
    if(Cue==mcl::AudioCue::None||!World.IsValid())return nullptr;
    const int Family=static_cast<int>(Cue);
    const int Variant=NextVariant[Family];
    NextVariant[Family]=(Variant+1)%mcl::AudioVariantCount;
    const int Index=Family*mcl::AudioVariantCount+Variant;
    if(!Bank.IsValidIndex(Index)||!Bank[Index])return nullptr;
    const bool bSwing=Cue==mcl::AudioCue::Swing||Cue==mcl::AudioCue::Stab;
    const bool bArmor=Cue==mcl::AudioCue::Armor;
    auto* Voice=UGameplayStatics::SpawnSoundAtLocation(World.Get(),Bank[Index],Position,FRotator::ZeroRotator,
        Gain,1.f,0.f,bArmor?ArmorAttenuation.Get():Attenuation.Get(),
        bArmor?ArmorConcurrency.Get():(bSwing?SwingConcurrency.Get():ContactConcurrency.Get()),true);
    if(FParse::Param(FCommandLine::Get(),TEXT("CombatAudioLog")))
        UE_LOG(LogTemp,Display,TEXT("COMBAT AUDIO cue=%s variant=%d gain=%.3f voice_created=%d"),
            UTF8_TO_TCHAR(mcl::AudioCueNames[Family]),Variant,Gain,Voice!=nullptr);
    return Voice;
}

void UCombatAudio::Sample(const mcl::Combatant& Fighter,double Time)
{
    const auto AirPosition=mcl::lerp(Fighter.weapon.hilt,Fighter.weapon.tip,.55);
    const FVector BladeLocation(AirPosition.x,AirPosition.y,AirPosition.z);
    const auto& P=Fighter.position;
    const FVector ArmorLocation(P.x,P.y,P.z+25);
    // Let the mono sources travel with the blade/body so nearby passes pan
    // naturally and equipment does not hang behind a moving fighter.
    if(auto* Voices=Swings.Find(Fighter.id))for(auto& Voice:*Voices)
        if(Voice.IsValid())Voice->SetWorldLocation(BladeLocation);
    if(auto* Voice=ArmorVoices.Find(Fighter.id);Voice&&Voice->IsValid())Voice->Get()->SetWorldLocation(ArmorLocation);
    const float Rustle=ArmorGates.FindOrAdd(Fighter.id).sample(Time,Fighter.position,Fighter.view,Fighter.state.phase,Fighter.state.serial);
    if(Rustle>0){
        ArmorVoices.Add(Fighter.id,Play(mcl::AudioCue::Armor,ArmorLocation,mcl::AudioBaseGain*Rustle));
    }
    auto& Gate=Gates.FindOrAdd(Fighter.id);
    const auto Cue=Gate.sample(Fighter.state.phase,Fighter.state.serial,Fighter.state.attack.kind);
    if(Cue==mcl::AudioCue::None)return;
    // Every committed air passage plays its natural tail, including through
    // hits, parries, flinch and combo transitions. Only reset/removal stops it.
    auto& Voices=Swings.FindOrAdd(Fighter.id);
    Voices.RemoveAll([](const TWeakObjectPtr<UAudioComponent>& Voice){return !Voice.IsValid();});
    Voices.Add(Play(Cue,BladeLocation,mcl::AudioBaseGain));
}

void UCombatAudio::Contact(const mcl::CombatEvent& Event)
{
    const auto Cue=mcl::contactAudio(Event.result,Event.region);
    if(Cue==mcl::AudioCue::None)return;
    const float Energy=static_cast<float>(mcl::clamp(Event.energy,0.,1.));
    // The bank is loudness matched offline. Head replaces body; it is never
    // stacked as a louder bonus impact. Energy changes level by at most 1 dB.
    const float Gain=mcl::AudioBaseGain*(.89f+.11f*Energy);
    Play(Cue,FVector(Event.point.x,Event.point.y,Event.point.z),Gain);
    if(FParse::Param(FCommandLine::Get(),TEXT("CombatAudioLog"))&&World.IsValid()){
        if(auto* Voices=Swings.Find(Event.attacker);Voices&&!Voices->IsEmpty()){
            const auto Air=Voices->Last();
            FTimerHandle Check;
            World->GetTimerManager().SetTimer(Check,[Air]{
                UE_LOG(LogTemp,Display,TEXT("COMBAT AUDIO air_after_contact_80ms playing=%d"),
                    Air.IsValid()&&Air->GetPlayState()==EAudioComponentPlayState::Playing);
            },.08f,false);
        }
    }
}

void UCombatAudio::Reset()
{
    for(auto& Pair:Swings)for(auto& Voice:Pair.Value)if(Voice.IsValid())Voice->Stop();
    for(auto& Pair:ArmorVoices)if(Pair.Value.IsValid())Pair.Value->Stop();
    Swings.Reset();Gates.Reset();ArmorGates.Reset();ArmorVoices.Reset();
    for(int& Variant:NextVariant)Variant=0;
}

void UCombatAudio::Forget(int FighterId)
{
    if(auto* Voices=Swings.Find(FighterId))for(auto& Voice:*Voices)if(Voice.IsValid())Voice->Stop();
    if(auto* Voice=ArmorVoices.Find(FighterId);Voice&&Voice->IsValid())Voice->Get()->Stop();
    Swings.Remove(FighterId);Gates.Remove(FighterId);ArmorGates.Remove(FighterId);ArmorVoices.Remove(FighterId);
}
