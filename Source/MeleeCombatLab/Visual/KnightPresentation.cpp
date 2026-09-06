#include "KnightPresentation.h"
#include "TournamentAssets.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/StaticMesh.h"

void UKnightPresentation::BeginPlay()
{
    Super::BeginPlay();
    UpperBody=NewObject<USceneComponent>(GetOwner());UpperBody->SetupAttachment(this);UpperBody->RegisterComponent();
    auto* Steel=TournamentAssets::Material(this,TEXT("Steel"),FLinearColor(.38f,.43f,.47f));
    auto* Iron=TournamentAssets::Material(this,TEXT("Iron"),FLinearColor(.055f,.065f,.075f));
    auto* Leather=TournamentAssets::Material(this,TEXT("Leather"),FLinearColor(.12f,.07f,.035f));
    Cloth=TournamentAssets::Material(this,TEXT("Cloth"),FLinearColor(.30f,.055f,.035f));
    auto Add=[&](const FName& Shape,FVector At,FVector Size,UMaterialInterface* Material,bool Upper=true){
        auto* Part=NewObject<UStaticMeshComponent>(GetOwner());Part->SetupAttachment(Upper?UpperBody.Get():this);Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);Part->SetStaticMesh(Shape==TEXT("Cube")?LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")):TournamentAssets::Mesh(Shape));
        Part->SetMaterial(0,Material);Part->SetRelativeLocation(At);Part->SetRelativeScale3D(Size/100.);Part->RegisterComponent();Parts.Add(Part);return Part;
    };
    Add(TEXT("Body"),{0,0,12},{42,58, 60},Iron);
    Add(TEXT("Body"),{3,0,16},{46,58,58},Steel);
    Add(TEXT("Body"),{5,0,13},{46,27,62},Cloth);
    Add(TEXT("Body"),{0,0,-22},{43,57,18},Leather);
    for(int I=0;I<3;++I)Add(TEXT("Body"),{0,0,-24.-I*6},{46.+I*2,59.+I*2,12},Steel);
    Add(TEXT("Body"),{2,0,-36},{47,30,30},Cloth);
    Add(TEXT("Helmet"),{0,0,66},{42,40, 40},Steel);
    Add(TEXT("Orb"),{0,0,44},{28,29,18},Iron);
    Add(TEXT("Cube"),{20.5,0,70},{1,29,2.1},Iron);
    Add(TEXT("Cube"),{21,0, 60},{1.2,2,19},Steel);
    for(int Side:{-1,1}){
        Add(TEXT("Orb"),{18,Side*13.,55},{3,2,2},Iron);
        Add(TEXT("Orb"),{15,Side*15., 60},{3,2,2},Iron);
        Add(TEXT("Body"),{0,Side*14.,-47},{23,22,38},Steel,false);
        Add(TEXT("Orb"),{3,Side*14.,- 60},{23,22,18},Steel,false);
        Add(TEXT("Body"),{0,Side*14.,- 70},{20,18, 30},Steel,false);
        Add(TEXT("Boot"),{7,Side*14.,-82},{ 30, 20,14},Leather,false);
    }
}
void UKnightPresentation::Present(bool Blue,float Reaction,bool Dead,float Dt)
{
    if(Cloth&&Blue!=WasBlue){WasBlue=Blue;FLinearColor Tint=Blue?FLinearColor(.045f,.14f,.25f):FLinearColor(.30f,.055f,.035f);Cloth->SetVectorParameterValue(TEXT("Color"),Tint);Cloth->SetVectorParameterValue(TEXT("BaseColor"),Tint);}
    Fall=FMath::FInterpTo(Fall,Dead?1.f:0.f,Dt,5.f);SetRelativeRotation(FRotator(Fall*78,0,0));SetRelativeLocation(FVector(0,0,-Fall*45));
    if(UpperBody)UpperBody->SetRelativeRotation(FRotator(Reaction*5,0,0));
}
