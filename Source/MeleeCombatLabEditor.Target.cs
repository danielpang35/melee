using UnrealBuildTool;
using System.Collections.Generic;
public class MeleeCombatLabEditorTarget : TargetRules
{
    public MeleeCombatLabEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        ExtraModuleNames.Add("MeleeCombatLab");
    }
}
