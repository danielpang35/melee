using UnrealBuildTool;
public class MeleeCombatLab : ModuleRules
{
    public MeleeCombatLab(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        CppStandard = CppStandardVersion.Cpp20;
        PublicIncludePaths.Add(ModuleDirectory);
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput", "Slate", "SlateCore", "Json", "RHI", "MeshDescription", "StaticMeshDescription"
        });
        if (Target.bBuildEditor) PrivateDependencyModuleNames.Add("AssetRegistry");
    }
}
