#include "TournamentCourtyard.h"
#include "TournamentAssets.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/StaticMesh.h"

ATournamentCourtyard::ATournamentCourtyard()
{
    RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("CitadelCourt"));
    RootComponent->SetMobility(EComponentMobility::Static);
}
void ATournamentCourtyard::Part(const FString& Kind,FVector At,FVector Size,FLinearColor Color,FRotator Rotation,bool Collision,const FString& Shape)
{
    const FString Key=Kind+Shape+(Collision?TEXT("Solid"):TEXT("Detail"));
    auto* Mesh=Groups.FindRef(Key).Get();
    if(!Mesh){
        Mesh=NewObject<UInstancedStaticMeshComponent>(this);Mesh->SetupAttachment(RootComponent);Mesh->SetMobility(EComponentMobility::Static);
        const bool Authored=Shape.StartsWith(TEXT("SM_"))||Shape==TEXT("Cube");
        const FString Asset=Shape==TEXT("Cube")?TEXT("SM_DressedBlock"):Shape;
        const FString Path=Authored?TEXT("/Game/Visual/Citadel/Meshes/")+Asset+TEXT(".")+Asset:TEXT("/Engine/BasicShapes/")+Shape+TEXT(".")+Shape;
        Mesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*Path));
        // Imported presentation geometry has no collision body. Keep simple,
        // explicitly authored gameplay hulls for the perimeter and basin.
        if(Collision)Mesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Shape==TEXT("Cylinder")?TEXT("/Engine/BasicShapes/Cylinder.Cylinder"):TEXT("/Engine/BasicShapes/Cube.Cube")));
        Mesh->SetCollisionEnabled(Collision?ECollisionEnabled::QueryAndPhysics:ECollisionEnabled::NoCollision);
        if(Collision)Mesh->SetCollisionProfileName(TEXT("BlockAll"));
        const FString Surface=Kind.Contains(TEXT("Water"))?TEXT("Water"):Kind.Contains(TEXT("Banner"))?TEXT("Cloth"):
            Kind.Contains(TEXT("Metal"))?TEXT("Iron"):Kind.Contains(TEXT("Wood"))?TEXT("Wood"):
            Kind.Contains(TEXT("Roof"))?TEXT("Roof"):Kind.Contains(TEXT("Paving"))?TEXT("Paving"):
            Kind.Contains(TEXT("Pier"))||Kind.Contains(TEXT("Capital"))||Kind.Contains(TEXT("Cornice"))||Kind.Contains(TEXT("Arch"))||Kind.Contains(TEXT("Rim"))||Kind.Contains(TEXT("Inlay"))?TEXT("Trim"):TEXT("Stone");
        Mesh->SetMaterial(0,TournamentAssets::Material(this,Surface,Color));
        if(Kind.Contains(TEXT("Hull")))Mesh->SetVisibility(false);
        Mesh->RegisterComponent();Groups.Add(Key,Mesh);
    }
    Mesh->AddInstance(FTransform(Rotation,At,Size/100.),false);
}
void ATournamentCourtyard::Beam(const FString& Kind,FVector A,FVector B,float Width,float Depth,FLinearColor Color)
{Part(Kind,(A+B)*.5f,FVector((B-A).Size(),Width,Depth),Color,(B-A).Rotation());}
void ATournamentCourtyard::BeginPlay()
{
    Super::BeginPlay();
    const FLinearColor Stone(.76f,.73f,.65f),Pale(.74f,.70f,.61f),Shade(.45f,.48f,.48f),Slate(.10f,.17f,.23f),
        Oxblood(.21f,.024f,.018f),Azure(.025f,.09f,.15f),Gold(.64f,.43f,.16f),Wood(.10f,.062f,.036f);
    Part(TEXT("Foundation"),{0,650,-25},{3200,2800,50},Stone,{},true);
    Part(TEXT("CourtPaving"),{0,650,.5},{3190,2790,1},Pale);
    // Wide, quiet dueling lanes framed by cream stone bands.
    for(int Sign:{-1,1}){
        Part(TEXT("PavingBorder"),{Sign*1330.,650,1.2},{16,2680,1},Shade);
        Part(TEXT("PavingBorder"),{0,650+Sign*1120.,1.2},{2670,16,1},Shade);
        Part(TEXT("PerimeterHull"),{0,650+Sign*1400.,240},{3200,90,480},Stone,{},true);
        Part(TEXT("PerimeterHull"),{Sign*1600.,650,240},{90,2800,480},Stone,{},true);
    }
    auto Arcade=[&](FVector Origin,FRotator Facing,int Bays){
        auto Place=[&](const FString& Kind,FVector P,FVector Size,FLinearColor Color,const FString& Shape=TEXT("Cube"),FRotator R=FRotator::ZeroRotator){
            Part(Kind,Origin+Facing.RotateVector(P),Size,Color,FRotator(0,Facing.Yaw+R.Yaw,0),false,Shape);
        };
        const double Width=Bays*390.;
        Place(TEXT("GalleryBacking"),{0,95,230},{Width+80,80,460},Shade);
        Place(TEXT("GalleryPlinth"),{0,-45,22},{Width+110,340,44},Stone);
        Place(TEXT("GalleryUpper"),{0,70,455},{Width+90,300,120},Stone);
        Place(TEXT("GalleryCornice"),{0,-35,520},{Width+150,360,26},Pale);
        Place(TEXT("GalleryRoof"),{0,60,533},{Width+230,510,270},Slate,TEXT("SM_SlateRoof"));
        for(int I=0;I<=Bays;++I){
            const double X=(I-Bays*.5)*390;
            Place(TEXT("ArcadePier"),{X,-130,155},{64,100,266},Stone);
            Place(TEXT("ArcadeBase"),{X,-130,45},{100,135,46},Pale);
            Place(TEXT("ArcadeCapital"),{X,-130,286},{96,132,28},Pale);
            Place(TEXT("GalleryCorbel"),{X,-126,476},{40,56,65},Pale);
        }
        for(int I=0;I<Bays;++I){
            const double X=(I+.5-Bays*.5)*390;
            // Continuous modeled intrados; deep shaded recesses behind each bay.
            Place(TEXT("ArcadeArch"),{X,-130,287},{390,105,260},Pale,TEXT("SM_ArcadeArch"));
            Place(TEXT("GallerySpandrel"),{X,-115,425},{390,75,62},Stone);
            Place(TEXT("GallerySeatWood"),{X,40,78},{270,58,20},Wood);
            for(int J:{-1,1})Place(TEXT("GallerySeatLegWood"),{X+J*102,40,50},{15,40,55},Wood);
        }
    };
    Arcade({-1560,650,0},FRotator(0,90,0),7);
    Arcade({1560,650,0},FRotator(0,-90,0),7);
    Arcade({-935,2010,0},FRotator(0,0,0),3);
    Arcade({935,2010,0},FRotator(0,0,0),3);
    Arcade({0,-710,0},FRotator(0,180,0),8);
    // Royal gatehouse: asymmetrical skyline focus above the opponent band.
    Part(TEXT("GatehouseMass"),{0,2075,460},{640,500,920},Stone);
    Part(TEXT("GatehouseRoof"),{0,2075,925},{750,650,560},Slate,{},false,TEXT("SM_SlateRoof"));
    Part(TEXT("GatehouseCornice"),{0,1800,910},{700,90,40},Pale);
    Part(TEXT("GateDoorWood"),{0,1804,170},{276,20,340},Wood);
    Part(TEXT("GreatArch"),{0,1780,300},{360,85,340},Pale,{},false,TEXT("SM_ArcadeArch"));
    for(int Sign:{-1,1}){
        Part(TEXT("GatePier"),{Sign*180.,1780,150},{60,100,300},Pale);
        Part(TEXT("GatehouseButtress"),{Sign*320.,1830,450},{65,110,900},Pale);
        for(int Row=0;Row<2;++Row){
            Part(TEXT("WindowRecess"),{Sign*170.,1814,590.+Row*185},{75,12,120},Shade);
            Part(TEXT("WindowLintel"),{Sign*170.,1804,658.+Row*185},{105,30,16},Pale);
            Part(TEXT("WindowMullion"),{Sign*170.,1799,595.+Row*185},{8,18,125},Pale);
        }
        // One tall watch tower gives the composition a recognisable silhouette.
        const FVector T(Sign*1590.,1980,0);
        const double Height=Sign<0?1080:810;
        Part(TEXT("Watchtower"),T+FVector(0,0,Height*.5),{330,330,Height},Stone);
        Part(TEXT("WatchtowerCrown"),T+FVector(0,0,Height),{385,385,50},Pale);
        Part(TEXT("WatchtowerRoof"),T+FVector(0,0,Height+30),{460,460,440},Slate,{},false,TEXT("SM_SlateRoof"));
        for(int Row=0;Row<3;++Row)Part(TEXT("TowerWindow"),T+FVector(0,-168,400+Row*180),{46,8,104},Shade);
    }
    // Swallowtail fabrics with modeled folds. The gold cross sits above the
    // main fighting silhouette band; long pennants mark the gallery rhythm.
    for(int Side:{-1,1})for(int I=-2;I<=2;++I){
        const FVector At(Side*1357.,650+I*485.,460);
        Part(Side<0?TEXT("AzureBanner"):TEXT("OxbloodBanner"),At,{100,100,230},Side<0?Azure:Oxblood,FRotator(0,90,0),false,TEXT("SM_HeraldicCloth"));
        Part(TEXT("BannerMetalRod"),At+FVector(0,0,8),{7,135,7},Gold);
    }
    for(int Side:{-1,1}){
        Part(TEXT("RoyalBanner"),{Side*88.,1759,815},{90,100,275},Oxblood,{},false,TEXT("SM_HeraldicCloth"));
        Part(TEXT("BannerGold"),{Side*88.,1748,742},{12,4,78},Gold);
        Part(TEXT("BannerGold"),{Side*88.,1748,748},{46,4,12},Gold);
    }
    // Existing octagonal basin remains a spacing obstacle; its stone body now
    // uses the scanned palette and concentric paving as a ceremonial centre.
    const FVector F(0,650,0);
    for(int Ring=0;Ring<3;++Ring)for(int I=0;I<8;++I){
        const double A=I*PI/4.,B=(I+1)*PI/4.,R=250+Ring*28;
        Beam(TEXT("BasinInlay"),F+FVector(R*FMath::Cos(A),R*FMath::Sin(A),1.3),F+FVector(R*FMath::Cos(B),R*FMath::Sin(B),1.3),Ring==1?12:4,.6f,Shade);
    }
    Part(TEXT("BasinFoot"),F+FVector(0,0,12),{385,385,24},Shade,{},false,TEXT("Cylinder"));
    Part(TEXT("BasinCoreHull"),F+FVector(0,0,25),{255,255,50},Stone,{},true);
    for(int I=0;I<8;++I){
        const double A=I*PI/4;const FVector At=F+FVector(165*FMath::Cos(A),165*FMath::Sin(A),40);
        Part(TEXT("BasinWallHull"),At,{145,40,80},Stone,FRotator(0,I*45.+90,0),true);
        Part(TEXT("BasinWall"),At,{145,40,80},Stone,FRotator(0,I*45.+90,0));
        Part(TEXT("BasinRim"),At+FVector(0,0,40),{151,52,16},Pale,FRotator(0,I*45.+90,0));
    }
    Part(TEXT("BasinWater"),F+FVector(0,0,65),{298,298,4},FLinearColor(.025f,.11f,.12f),{},false,TEXT("Cylinder"));
    Part(TEXT("FountainPier"),F+FVector(0,0,48),{125,125,145},Pale,{},false,TEXT("SM_FountainBaluster"));
    Part(TEXT("FountainRim"),F+FVector(0,0,184),{150,150,150},Pale,{},false,TEXT("SM_FountainBowl"));
    Part(TEXT("FountainUpperWater"),F+FVector(0,0,211),{129,129,1},FLinearColor(.04f,.13f,.14f),{},false,TEXT("Cylinder"));
}
