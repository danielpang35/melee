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
static void Surface(FMeshDescription& D,const TArray<FVector3f>& P,const TArray<FIntVector>& Faces)
{
    FStaticMeshAttributes A(D);A.Register();auto Positions=A.GetVertexPositions();auto Normals=A.GetVertexInstanceNormals();auto Tangents=A.GetVertexInstanceTangents();auto Signs=A.GetVertexInstanceBinormalSigns();auto UV=A.GetVertexInstanceUVs();UV.SetNumChannels(1);
    FPolygonGroupID Group=D.CreatePolygonGroup();A.GetPolygonGroupMaterialSlotNames()[Group]=TEXT("Surface");
    TArray<FVertexID> Vertices;for(auto V:P){auto ID=D.CreateVertex();Positions[ID]=V;Vertices.Add(ID);}
    for(auto F:Faces){FVector3f N=FVector3f::CrossProduct(P[F.Y]-P[F.X],P[F.Z]-P[F.X]).GetSafeNormal();TArray<FVertexInstanceID> Instances;
        for(int Index:{F.X,F.Y,F.Z}){auto ID=D.CreateVertexInstance(Vertices[Index]);Normals[ID]=N;Tangents[ID]=FVector3f::CrossProduct(FMath::Abs(N.Z)>.9f?FVector3f(0,1,0):FVector3f(0,0,1),N).GetSafeNormal();Signs[ID]=1;UV.Set(ID,0,FVector2f(P[Index].Y*.01f+.5f,P[Index].Z*.01f+.5f));Instances.Add(ID);}
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
    Surface(D,P,Faces);
}
UStaticMesh* Mesh(const FName& Shape)
{
    if(auto* Existing=Meshes.Find(Shape);Existing&&Existing->IsValid())return Existing->Get();
    auto* Result=NewObject<UStaticMesh>(GetTransientPackage(),MakeUniqueObjectName(GetTransientPackage(),UStaticMesh::StaticClass(),Shape));
    Result->GetStaticMaterials().Add(FStaticMaterial(nullptr,TEXT("Surface")));TArray<FMeshDescription> Lods;Lods.SetNum(2);
    for(int L=0;L<2;++L){
        TArray<FVector2f> Profile;
        bool AlongX=Shape==TEXT("Arm")||Shape==TEXT("Grip")||Shape==TEXT("Blade");
        if(Shape==TEXT("Helmet"))Profile={{-50,34},{-38,46},{10,48},{32,39},{46,22},{50,2}};
        else if(Shape==TEXT("Body"))Profile={{-50,33},{-30,35},{0,43},{24,50},{40,43},{50,28}};
        else if(Shape==TEXT("Arm"))Profile={{-50,37},{-40,46},{-22,50},{15,44},{42,32},{50,30}};
        else if(Shape==TEXT("Boot"))Profile={{-50,45},{-30,50},{-10,47},{20,34},{50,29}};
        else if(Shape==TEXT("Grip"))Profile={{-50,38},{-43,46},{40,42},{50,35}};
        else Profile={{-50,8},{-42,28},{-22,44},{0,50},{22,44},{42,28},{50,8}};
        if(Shape==TEXT("Blade")){
            TArray<FVector3f> P={{-50,0,50},{-50,50,0},{-50,0,-50},{-50,-50,0},{34,0,30},{34,30,0},{34,0,-30},{34,-30,0},{50,0,0}};
            TArray<FIntVector> F={{0,2,1},{0,3,2}};for(int I=0;I<4;++I){int J=(I+1)%4;F.Add({I,J,J+4});F.Add({I,J+4,I+4});F.Add({I+4,J+4,8});}Surface(Lods[L],P,F);
        }else Lathe(Lods[L],Profile,L==0?24:10,AlongX);
    }
    UStaticMesh::FBuildMeshDescriptionsParams Params;Params.bFastBuild=true;Params.bBuildSimpleCollision=false;Params.bMarkPackageDirty=false;Params.bCommitMeshDescription=false;
    Result->BuildFromMeshDescriptions({&Lods[0],&Lods[1]},Params);
    if(Result->GetRenderData()){Result->GetRenderData()->ScreenSize[0].Default=1.f;Result->GetRenderData()->ScreenSize[1].Default=.12f;}
    Meshes.Add(Shape,Result);return Result;
}
UMaterialInstanceDynamic* Material(UObject* Owner,const FString& Surface,FLinearColor Tint)
{
    auto* Base=FPaths::FileExists(FPaths::ProjectContentDir()/TEXT("Visual/Materials")/(TEXT("M_")+Surface+TEXT(".uasset")))?LoadObject<UMaterialInterface>(nullptr,*(TEXT("/Game/Visual/Materials/M_")+Surface+TEXT(".M_")+Surface)):nullptr;
    if(!Base)Base=LoadObject<UMaterialInterface>(nullptr,TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
    auto* M=UMaterialInstanceDynamic::Create(Base,Owner);M->SetVectorParameterValue(TEXT("Color"),Tint);M->SetVectorParameterValue(TEXT("BaseColor"),Tint);return M;
}
}
