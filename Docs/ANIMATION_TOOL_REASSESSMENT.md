# Animation workflow reassessment

12 September 2026. Workflow efficiency is Daniel's top production priority. Preserve the positively reviewed first-person animation, swing feel, timing and inputs. Improve whole-body performance and opponent communication; step 4 remains deferred. This is a tool recommendation, not a completed tool trial or migration.

## Recommendation

Use the already installed **Cascadeur** for one bounded pose-authoring trial. Version 2026.2.1.0.16599 was read from `C:/Program Files/Cascadeur/cascadeur.exe`; activation, export entitlement and automation access were not tested. Its AI-assisted AutoPosing and explicit weapon controls are a closer fit to our current bottleneck than another procedural joint-repair pass. Coauthor ready, preparation, delivery and recovery with body support and connected hands, then judge one complete source-speed preview with the animation critic. Retain editable controls and curves.

| Tool | Useful role | Important limit / disposition |
|---|---|---|
| [Cascadeur AutoPosing](https://cascadeur.com/help/tools/animation_tools/autoposing), [weapon workflow](https://cascadeur.com/tutor/workingwithweapons) | AI-assisted whole-body posing with weapon controllers; explicit two-handed sword workflow | First trial. [AI inbetweening](https://cascadeur.com/help/category/278) explicitly lacks weapon/prop support and preservation of relative controller relationships. Do not assume it will maintain both grips or produce finished combat automatically. |
| [AccuRIG](https://www.reallusion.com/auto-rig/accurig/), [export documentation](https://manual.reallusion.com/AccuRig-2/2.0/09-add-motions/export.htm) | Automated body/hand rigging and skinning, export for DCC/engine use | Conditional same-mesh deformation comparison if native rig/weights remain limiting after runtime distortion is isolated. It cannot repair programmed weapon placement or hip-pivot lean. |
| [Motorica](https://motorica.com/), [Motion Factory style cloning](https://motorica.com/blog/introducing-motion-factory-style-cloning) | Generative locomotion and motion datasets; promising for broader movement coverage | Consider when locomotion is the active bottleneck. Exact two-handed weapon/contact control is unverified; do not introduce a full locomotion framework for this neutral pilot. |
| [DeepMotion Animate 3D](https://www.deepmotion.com/animate-3d), [SayMotion](https://www.deepmotion.com/doc/saymotion) | Video-to-motion performance acquisition; text-generated rough motion | Optional source of broad performance ideas. Clean reference footage and cleanup are still needed; precise sword grips and occluded hands are unverified for this project. |

These recommendations infer fit from official capabilities. No subscription was purchased, character uploaded or comparative animation trial completed. No measured time or token savings are claimed.

## Avoid fixing the wrong layer

[Diagnosis](READABILITY_REJECTION_DIAGNOSIS.md) found the runtime corrector holding the canonical recovery sword still for about 0.4 seconds while native TP continues moving, with arm fitting reaching about 1.92 times native chain length. Idle weapon placement and look-down hip-pivot behavior also have explicit runtime causes. Native leg performance is absent. Re-rigging alone cannot address these mechanisms.

The smallest useful comparison is the same take with native versus corrected TP presentation at the same clock/camera, followed by a separate look-down check. Protect the FP result. Use that evidence to define the TP ready/recovery and aim constraints supplied to the authoring trial; do not ask a new app to compensate for unexplained runtime deformation.

## Trial acceptance and workflow

Keep the trial isolated: one existing character/action, body and weapon controls, editable native file, and one cheap whole-action preview. Record hands-on time to a reviewable take, cleanup required, ease of a requested pose change, and export fidelity if selected for integration. A critic evaluates balance, windup onset, weapon path, look direction and continuity at normal speed; sampled frames alone cannot establish motion quality. Integrate only a provisionally convincing take through the existing route. Daniel directs and reviews; do not require him to operate Blender or migrate all assets.

Keep implementation and trial evidence local; [Notion's communication pillar](https://app.notion.com/p/3d92e3c3f8f881bbaa96c9f4e800fd8b) owns the player-facing criterion. [TP checkpoint](THIRD_PERSON_CHECKPOINT.md) remains the single resume record.
