#pragma once
#include <vector>

// Single registry used by simulation, Slate, JSON persistence and native tests.
#define MCL_TUNABLES(X) \
 X(StrikeWindup,.60,.15,1.5,"Strike") \
 X(StrikeRelease,.50,.15,1.5,"Strike") \
 X(StrikeRecovery,.675,.1,1.5,"Strike") \
 X(StabWindup,.565,.15,1.5,"Stab") \
 X(StabRelease,.35,.15,1.5,"Stab") \
 X(StabRecovery,.675,.1,1.5,"Stab") \
 X(ComboWindup,.65,.15,1.5,"Strike") \
 X(ComboStart,.50,0,1,"Strike") \
 X(ComboEnd,.96,0,1,"Strike") \
 X(DamageStart,.05,0,.45,"Strike") \
 X(DamageEnd,.95,.55,1,"Strike") \
 X(FeintLockout,.05,0,.25,"Strike") \
 X(FeintRecovery,.15,0,.6,"Strike") \
 X(FeintReturnDuration,.18,.05,.4,"Presentation") \
 X(FlinchDuration,.45,.1,.9,"Defense") \
 X(MorphWindow,.65,.1,.95,"Strike") \
 X(MorphAdditionalWindup,.16,0,.5,"Strike") \
 X(RiposteWindup,.32,.15,.7,"Strike") \
 X(RiposteTurnScale,1.50,1,2,"Swing") \
 X(RiposteWindow,.30,.1,.6,"Strike") \
 X(BladeLength,110,50,160,"Weapon") \
 X(BladeRadius,4,2,10,"Weapon") \
 X(Damage,35,1,100,"Weapon") \
 X(WindupYawCap,385,100,1500,"Swing") \
 X(ReleaseEarlyCap,255,30,600,"Swing") \
 X(ReleaseMidCap,245,30,600,"Swing") \
 X(ReleaseLateCap,220,30,600,"Swing") \
 X(StrikeReleaseFrontLoad,.45,0,1.25,"Swing") \
 X(PitchCap,220,30,600,"Swing") \
 X(AntiSpinThreshold,175,60,300,"Swing") \
 X(MouseSensitivity,.70,.01,1,"Input") \
 X(MouseWindow,.095,.02,.2,"Input") \
 X(MouseDeadzone,2,0,20,"Input") \
 X(ParryDuration,.365,.1,.7,"Parry") \
 X(ParryRecovery,.55,.1,1.2,"Parry") \
 X(ParryWidth,130,40,220,"Parry") \
 X(ParryHeight,190,70,260,"Parry") \
 X(ParryDepth,50,10,100,"Parry") \
 X(ParryForward,58,20,110,"Parry") \
 X(ParryVertical,0,-60,60,"Parry") \
 X(BoxPitchInfluence,-.30,-1,1,"Parry") \
 X(BoxZInfluence,-.70,-2,2,"Parry") \
 X(BoxForwardInfluence,.15,-1,1,"Parry") \
 X(ConeLength,175,40,260,"Parry") \
 X(ConeHalfAngle,36,10,65,"Parry") \
 X(ConeForward,24,0,70,"Parry") \
 X(ConeVertical,20,-30,70,"Parry") \
 X(ConePitchInfluence,.35,0,1,"Parry") \
 X(ParryYawRate,180,30,600,"Parry") \
 X(ParryPitchRate,140,30,600,"Parry") \
 X(ChamberDuration,.225,.05,.4,"Chamber") \
 X(ChamberTolerance,32,5,65,"Chamber") \
 X(ChamberFacingAngle,80,30,89,"Chamber") \
 X(ForwardSpeed,306,100,700,"Movement") \
 X(LateralSpeed,261,100,700,"Movement") \
 X(BackwardSpeed,222,100,700,"Movement") \
 X(SprintSpeed,549.5,300,1000,"Movement") \
 X(Acceleration,4070,500,6000,"Movement") \
 X(Deceleration,5000,500,6000,"Movement") \
 X(GroundFriction,10,0,20,"Movement") \
 X(GravityScale,1.4,.5,3,"Movement") \
 X(JumpSpeed,500,250,750,"Movement") \
 X(MomentumBuild,1,.1,3,"Movement") \
 X(MomentumLoss,1.8,.1,5,"Movement") \
 X(SoftTurnThreshold,90,20,150,"Movement") \
 X(HardTurnThreshold,200,160,360,"Movement") \
 X(ReversePenalty,2.5,.1,6,"Movement") \
 X(LungeStrength,600,0,3000,"Lunge") \
 X(LungeDuration,.16,.05,.5,"Lunge") \
 X(LungeMaxDisplacement,42,0,120,"Lunge") \
 X(LungeMomentumScaling,.70,0,1,"Lunge") \
 X(LungeForwardRequirement,.20,0,1,"Lunge") \
 X(FeintCost,10,0,30,"Stamina") \
 X(MorphCost,7,0,30,"Stamina") \
 X(ChamberCost,15,0,40,"Stamina") \
 X(ParryCost,10,0,40,"Stamina") \
 X(MissCost,8,0,30,"Stamina") \
 X(StaminaRegen,18,0,50,"Stamina") \
 X(StaminaDelay,1.2,0,3,"Stamina") \
 X(DummyInterval,2.4,1.7,6,"Training") \
 X(DummyDragRate,90,10,250,"Training") \
 X(DummyMicrodragRate,45,10,150,"Training") \
 X(FOV,120,70,120,"Presentation") \
 X(CameraHitImpulse,1.3,0,4,"Presentation") \
 X(ParryRecoil,3,0,7,"Presentation") \
 X(ChamberRecoil,4,0,7,"Presentation") \
 X(HitEmphasis,.12,0,.3,"Presentation") \
 X(WeaponVisualLag,0,0,.008,"Presentation") \
 X(WeaponVisualSpring,45,20,100,"Presentation")

namespace mcl
{
struct TuningEntry { const char* name; const char* group; double* value; double minimum,maximum; };
struct Tuning
{
#define DECLARE(Name,Value,Min,Max,Group) double Name=Value;
    MCL_TUNABLES(DECLARE)
#undef DECLARE
    std::vector<TuningEntry> entries()
    {
        return {
#define ENTRY(Name,Value,Min,Max,Group) {#Name,Group,&Name,Min,Max},
            MCL_TUNABLES(ENTRY)
#undef ENTRY
        };
    }
};
}
