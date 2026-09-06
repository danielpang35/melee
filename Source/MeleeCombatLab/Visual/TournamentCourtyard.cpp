#include "TournamentCourtyard.h"
#include "TournamentAssets.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/StaticMesh.h"

ATournamentCourtyard::ATournamentCourtyard(){RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("CourtyardRoot"));}
void ATournamentCourtyard::Part(const FString& Kind,FVector At,FVector Size,FLinearColor Color,FRotator Rotation,bool Collision,const FString& Shape)
{
    FString Key=Kind+Shape+(Collision?TEXT("Solid"):TEXT("Detail"));auto* Mesh=Groups.FindRef(Key).Get();
    if(!Mesh){
        Mesh=NewObject<UInstancedStaticMeshComponent>(this);Mesh->SetupAttachment(RootComponent);Mesh->SetMobility(EComponentMobility::Static);
        Mesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*(TEXT("/Engine/BasicShapes/")+Shape+TEXT(".")+Shape)));
        Mesh->SetCollisionEnabled(Collision?ECollisionEnabled::QueryAndPhysics:ECollisionEnabled::NoCollision);if(Collision)Mesh->SetCollisionProfileName(TEXT("BlockAll"));
        FString Surface=Kind.Contains(TEXT("Water"))?TEXT("Water"):Kind.Contains(TEXT("Banner"))?TEXT("Cloth"):Kind.Contains(TEXT("GateIron"))?TEXT("Iron"):Kind.Contains(TEXT("Gate"))?TEXT("Wood"):Kind.Contains(TEXT("Paving"))?TEXT("Paving"):TEXT("Stone");
        auto* Material=TournamentAssets::Material(this,Surface,Color);Mesh->SetMaterial(0,Material);Mesh->RegisterComponent();Groups.Add(Key,Mesh);
    }
    Mesh->AddInstance(FTransform(Rotation,At,Size/100.),false);
}
void ATournamentCourtyard::Beam(const FString& Kind,FVector A,FVector B,float Width,float Depth,FLinearColor Color)
{Part(Kind,(A+B)*.5f,FVector((B-A).Size()+3,Width,Depth),Color,(B-A).Rotation());}
void ATournamentCourtyard::BeginPlay()
{
    Super::BeginPlay();
    const FLinearColor Stone(.63f,.55f,.41f),Trim(.76f,.68f,.52f),DarkStone(.42f,.4f,.34f),Wood(.21f,.13f,.075f),Blue(.055f,.15f,.24f),Red(.30f,.065f,.05f);
    // Original 32 x 28 m footprint, shifted north to keep the established duel coordinates clear.
    Part(TEXT("Foundation"),{0,650,-25},{3200,2800,50},DarkStone,{},true);
    for(int X=0;X<40;++X)for(int Y=0;Y<35;++Y){int Variant=(X*17+Y*11)%3;
        Part(FString::Printf(TEXT("Paving%d"),Variant),{-1560.+80*X,-710.+80*Y,.2f},{78,78,.4f},FLinearColor(.44f+Variant*.035f,.42f+Variant*.03f,.35f+Variant*.025f));}
    for(int Sign:{-1,1}){
        double Y=650+Sign*1400;
        Part(TEXT("Wall"),{0,Y,240},{3200,90,480},Stone,{},true);
        Part(TEXT("Cornice"),{0,Y- Sign*12,448},{3240,120,32},Trim);
        Part(TEXT("Wall"),{Sign*1600.,650,240},{90,2800,480},Stone,{},true);
        Part(TEXT("Cornice"),{Sign*1588.,650,448},{120,2840,32},Trim);
        for(int I=-7;I<=7;++I){Part(TEXT("Battlement"),{I*210.,Y,510},{85,100,90},Trim);}
        for(int I=-6;I<=6;++I)Part(TEXT("Battlement"),{Sign*1600.,650+I*210.,510},{100,85,90},Trim);
        for(int I=-3;I<=3;++I){
            Part(TEXT("Buttress"),{I*450.,Y-Sign*70,205},{90,95,410},Trim);
            Part(TEXT("ButtressFoot"),{I*450.,Y-Sign*82,30},{118,120,60},DarkStone);
        }
        for(int I=-2;I<=2;++I)Part(TEXT("Buttress"),{Sign*1530.,650+I*480.,205},{95,90,410},Trim);
        // Closed arched gates retain the predictable perimeter collision.
        Part(TEXT("Gate"),{0,Y-Sign*49,148},{250,12,296},Wood);
        for(int I=-5;I<=5;++I)Part(TEXT("GateIron"),{I*22.,Y-Sign*57,130},{3,3,260},FLinearColor(.055f,.065f,.07f));
        for(int I=0;I<16;++I){double A=PI*I/16.,B=PI*(I+1)/16.;
            Beam(TEXT("Arch"),{145*FMath::Cos(A),Y-Sign*60,238+145*FMath::Sin(A)},{145*FMath::Cos(B),Y-Sign*60,238+145*FMath::Sin(B)},68,34,Trim);}
        for(int Side:{-1,1})Part(TEXT("ArchPier"),{Side*145.,Y-Sign*60,119},{38,68,238},Trim);
        for(int I:{-2,-1,1,2}){
            Part(I<0?TEXT("BlueBanner"):TEXT("RedBanner"),{I*530.,Y-Sign*55,290},{92,4,190},I<0?Blue:Red);
            Part(TEXT("BannerStripe"),{I*530.,Y-Sign*59,290},{12,3,165},Trim);
            Part(TEXT("BannerCross"),{I*530.,Y-Sign*60,326},{ 60,3,12},Trim);
        }
    }
    for(int X:{-1,1})for(int Y:{-1,1}){
        FVector Center(X*1570.,650+Y*1370.,320);Part(TEXT("Tower"),Center,{300,300,640},Stone,{},true,TEXT("Cylinder"));
        Part(TEXT("TowerCrown"),Center+FVector(0,0,310),{334,334,40},Trim,{},false,TEXT("Cylinder"));
        for(int I=0;I<12;++I){double A=I*PI/6;Part(TEXT("TowerMerlon"),Center+FVector(145*FMath::Cos(A),145*FMath::Sin(A),355),{60,65,70},Trim,FRotator(0,I*30.,0));}
    }
    const FVector F(0,650,0);
    Part(TEXT("BasinFoot"),F+FVector(0,0,12),{385,385,24},DarkStone,{},false,TEXT("Cylinder"));
    Part(TEXT("BasinCore"),F+FVector(0,0,25),{255,255,50},Stone,{},true);
    for(int I=0;I<8;++I){double A=I*PI/4;
        FVector At=F+FVector(165*FMath::Cos(A),165*FMath::Sin(A), 40);
        Part(TEXT("BasinWall"),At,{145, 40,80},Stone,FRotator(0,I*45.+90,0),true);
        Part(TEXT("BasinRim"),At+FVector(0,0, 40),{151,52,16},Trim,FRotator(0,I*45.+90,0));}
    Part(TEXT("BasinWater"),F+FVector(0,0,65),{298,298,4},FLinearColor(.09f,.26f,.28f),{},false,TEXT("Cylinder"));
    Part(TEXT("FountainPedestal"),F+FVector(0,0,100),{60,60,160},Trim,{},false,TEXT("Cylinder"));
    Part(TEXT("FountainBowl"),F+FVector(0,0,175),{140,140,24},Stone,{},false,TEXT("Cylinder"));
    Part(TEXT("FountainFinial"),F+FVector(0,0,204),{ 40,40,48},Trim,{},false,TEXT("Sphere"));
}
