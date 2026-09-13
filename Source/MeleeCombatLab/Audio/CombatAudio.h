#pragma once
#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "Combat/CombatSimulation.h"
#include "Audio/CombatAudioRules.h"
#include "CombatAudio.generated.h"

class UAudioComponent;class USoundWave;class USoundAttenuation;class USoundConcurrency;

UCLASS()
class MELEECOMBATLAB_API UCombatAudio : public UObject
{
    GENERATED_BODY()
public:
    void Initialize(UWorld* InWorld);
    void Sample(const mcl::Combatant& Fighter,double Time);
    void Contact(const mcl::CombatEvent& Event);
    void Reset();
    void Forget(int FighterId);
private:
    TWeakObjectPtr<UWorld> World;
    UPROPERTY() TArray<TObjectPtr<USoundWave>> Bank;
    UPROPERTY() TObjectPtr<USoundAttenuation> Attenuation;
    UPROPERTY() TObjectPtr<USoundConcurrency> SwingConcurrency;
    UPROPERTY() TObjectPtr<USoundConcurrency> ContactConcurrency;
    UPROPERTY() TObjectPtr<USoundConcurrency> ArmorConcurrency;
    UPROPERTY() TObjectPtr<USoundAttenuation> ArmorAttenuation;
    TMap<int,mcl::ReleaseAudioGate> Gates;
    TMap<int,mcl::ArmorAudioGate> ArmorGates;
    TMap<int,TArray<TWeakObjectPtr<UAudioComponent>>> Swings;
    TMap<int,TWeakObjectPtr<UAudioComponent>> ArmorVoices;
    int NextVariant[mcl::AudioCueCount]={};
    UAudioComponent* Play(mcl::AudioCue Cue,FVector Position,float Gain);
};
