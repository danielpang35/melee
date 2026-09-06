using UnrealBuildTool;
using System.Collections.Generic;
public class MeleeCombatLabTarget : TargetRules
{
    public MeleeCombatLabTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        ExtraModuleNames.Add("MeleeCombatLab");
    }
}
