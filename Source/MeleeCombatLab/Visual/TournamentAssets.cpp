#include "TournamentAssets.h"
#include "Misc/Paths.h"
#include "Engine/StaticMesh.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"
#include "StaticMeshResources.h"
#include "Materials/MaterialInstanceDynamic.h"

namespace TournamentAssets
{
static TMap<FName,TWeakObjectPtr<UStaticMesh>> Meshes;
static void Surface(FMeshDescription& D,const TArray<FVector3f>& P,const TArray<FIntVector>& Faces,bool Smooth=false,bool AlongX=false)
{
    FStaticMeshAttributes A(D);A.Register();auto Positions=A.GetVertexPositions();auto Normals=A.GetVertexInstanceNormals();auto Tangents=A.GetVertexInstanceTangents();auto Signs=A.GetVertexInstanceBinormalSigns();auto UV=A.GetVertexInstanceUVs();UV.SetNumChannels(1);
    FPolygonGroupID Group=D.CreatePolygonGroup();A.GetPolygonGroupMaterialSlotNames()[Group]=TEXT("Surface");
    TArray<FVertexID> Vertices;for(auto V:P){auto ID=D.CreateVertex();Positions[ID]=V;Vertices.Add(ID);}
    TArray<FVector3f> Averaged;Averaged.Init(FVector3f::ZeroVector,P.Num());
    if(Smooth)for(auto F:Faces){
        const FVector3f N=FVector3f::CrossProduct(P[F.Y]-P[F.X],P[F.Z]-P[F.X]).GetSafeNormal();
        if(FMath::Abs(AlongX?N.X:N.Z)<.999f)for(int Index:{F.X,F.Y,F.Z})Averaged[Index]+=N;
    }
    for(auto F:Faces){FVector3f N=FVector3f::CrossProduct(P[F.Y]-P[F.X],P[F.Z]-P[F.X]).GetSafeNormal();TArray<FVertexInstanceID> Instances;
        for(int Index:{F.X,F.Y,F.Z}){auto ID=D.CreateVertexInstance(Vertices[Index]);
            const FVector3f Normal=Smooth&&FMath::Abs(AlongX?N.X:N.Z)<.999f?Averaged[Index].GetSafeNormal():N;
            Normals[ID]=Normal;
            // Longitudinal UVs keep steel/leather detail from collapsing along a limb.
            FVector2f Coord(P[Index].Y*.01f+.5f,P[Index].Z*.01f+.5f);
            if(AlongX)Coord=FVector2f(P[Index].X*.01f+.5f,FMath::Atan2(P[Index].Z,P[Index].Y)/(2.f*PI)+.5f);
            Tangents[ID]=(AlongX?FVector3f(1,0,0)-Normal*Normal.X:FVector3f::CrossProduct(FVector3f(0,0,1),Normal)).GetSafeNormal();
            if(Tangents[ID].IsNearlyZero())Tangents[ID]=FVector3f::CrossProduct(FVector3f(0,1,0),Normal).GetSafeNormal();
            Signs[ID]=1;UV.Set(ID,0,Coord);Instances.Add(ID);}
        D.CreatePolygon(Group,Instances);
    }
}
static void Lathe(FMeshDescription& D,const TArray<FVector2f>& Profile,int Sides,bool AlongX)
{
    TArray<FVector3f> P;TArray<FIntVector> Faces;
    for(auto Ring:Profile)for(int I=0;I<Sides;++I){float A=2.f*PI*I/Sides;FVector3f V(Ring.Y*FMath::Cos(A),Ring.Y*FMath::Sin(A),Ring.X);if(AlongX)V=FVector3f(V.Z,V.X,V.Y);P.Add(V);}
    for(int R=0;R<Profile.Num()-1;++R)for(int I=0;I<Sides;++I){int A=R*Sides+I,B=R*Sides+(I+1)%Sides,C=B+Sides,E=A+Sides;Faces.Add({A,B,C});Faces.Add({A,C,E});}
    int Bottom=P.Add(AlongX?FVector3f(Profile[0].X,0,0):FVector3f(0,0,Profile[0].X));int Top=P.Add(AlongX?FVector3f(Profile.Last().X,0,0):FVector3f(0,0,Profile.Last().X));
    for(int I=0;I<Sides;++I){Faces.Add({Bottom,(I+1)%Sides,I});int A=(Profile.Num()-1)*Sides+I,B=(Profile.Num()-1)*Sides+(I+1)%Sides;Faces.Add({Top,A,B});}
    Surface(D,P,Faces,true,AlongX);
}
UStaticMesh* Mesh(const FName& Shape)
{
    if(auto* Existing=Meshes.Find(Shape);Existing&&Existing->IsValid())return Existing->Get();
    auto* Result=NewObject<UStaticMesh>(GetTransientPackage(),MakeUniqueObjectName(GetTransientPackage(),UStaticMesh::StaticClass(),Shape));
    Result->GetStaticMaterials().Add(FStaticMaterial(nullptr,TEXT("Surface")));TArray<FMeshDescription> Lods;Lods.SetNum(2);
    for(int L=0;L<2;++L){
        TArray<FVector2f> Profile;
        bool AlongX=Shape==TEXT("Arm")||Shape==TEXT("Grip")||Shape==TEXT("Blade")||Shape==TEXT("Crossguard")||Shape==TEXT("Pauldron")||Shape==TEXT("Gauntlet")||Shape==TEXT("Pommel");
        if(Shape==TEXT("Helmet"))Profile={{-50,34},{-38,46},{10,48},{32,39},{46,22},{50,2}};
        else if(Shape==TEXT("Body"))Profile={{-50,33},{-30,35},{0,43},{24,50},{40,43},{50,28}};
        else if(Shape==TEXT("Arm"))Profile={{-50,37},{-40,46},{-22,50},{15,44},{42,32},{50,30}};
        else if(Shape==TEXT("Boot"))Profile={{-50,45},{-30,50},{-10,47},{20,34},{50,29}};
        else if(Shape==TEXT("Grip"))Profile={{-50,38},{-43,46},{40,42},{50,35}};
        else if(Shape==TEXT("Crossguard"))Profile={{-50,42},{-44,50},{-34,27},{-9,24},{0,38},{9,24},{34,27},{44,50},{50,42}};
        else if(Shape==TEXT("Pauldron"))Profile={{-50,27},{-36,43},{-8,50},{24,44},{43,35},{50,36}};
        else if(Shape==TEXT("Gauntlet"))Profile={{-50,48},{-35,40},{-15,34},{4,47},{25,50},{43,38},{50,26}};
        else if(Shape==TEXT("Pommel"))Profile={{-50,16},{-35,35},{-12,49},{12,49},{35,35},{50,16}};
        else Profile={{-50,8},{-42,28},{-22,44},{0,50},{22,44},{42,28},{50,8}};
        if(Shape==TEXT("Blade")){
            TArray<FVector3f> P={{-50,0,50},{-50,50,0},{-50,0,-50},{-50,-50,0},{34,0,30},{34,30,0},{34,0,-30},{34,-30,0},{50,0,0}};
            TArray<FIntVector> F={{0,2,1},{0,3,2}};for(int I=0;I<4;++I){int J=(I+1)%4;F.Add({I,J,J+4});F.Add({I,J+4,I+4});F.Add({I+4,J+4,8});}
            for(auto& Face:F)Swap(Face.Y,Face.Z); // Outward faces: the old blade was inside-out.
            Surface(Lods[L],P,F,false,true);
        }else Lathe(Lods[L],Profile,L==0?24:10,AlongX);
    }
    UStaticMesh::FBuildMeshDescriptionsParams Params;Params.bFastBuild=true;Params.bBuildSimpleCollision=false;Params.bMarkPackageDirty=false;Params.bCommitMeshDescription=false;
    Result->BuildFromMeshDescriptions({&Lods[0],&Lods[1]},Params);
    if(Result->GetRenderData()){Result->GetRenderData()->ScreenSize[0].Default=1.f;Result->GetRenderData()->ScreenSize[1].Default=.12f;}
    Meshes.Add(Shape,Result);return Result;
}
UMaterialInstanceDynamic* Material(UObject* Owner,const FString& Surface,FLinearColor Tint)
{
    // Resolve package paths, not loose files: cooked assets may live in IoStore.
    const bool Citadel=Surface==TEXT("Stone")||Surface==TEXT("Paving")||Surface==TEXT("Roof")||Surface==TEXT("Cloth");
    auto* Base=LoadObject<UMaterialInterface>(nullptr,*(Surface==TEXT("Trim")?FString(TEXT("/Game/Visual/Materials/M_Surface.M_Surface")):Citadel?
        TEXT("/Game/Visual/Citadel/Materials/M_Citadel")+Surface+TEXT(".M_Citadel")+Surface:
        TEXT("/Game/Visual/Materials/M_")+Surface+TEXT(".M_")+Surface));
    if(!Base)Base=LoadObject<UMaterialInterface>(nullptr,TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
    auto* M=UMaterialInstanceDynamic::Create(Base,Owner);M->SetVectorParameterValue(TEXT("Color"),Tint);M->SetVectorParameterValue(TEXT("BaseColor"),Tint);
    if(Surface==TEXT("Trim")){M->SetScalarParameterValue(TEXT("Roughness"),.78f);M->SetScalarParameterValue(TEXT("NormalIntensity"),.12f);M->SetScalarParameterValue(TEXT("DirtAmount"),.09f);}
    return M;
}
}
