"""Run in Cascadeur Python Console: save a version and export the active 120 fps attack."""
from pathlib import Path
from datetime import datetime
import csc
ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/'ArtSource/Cascadeur'
app=csc.app.get_application()
if not app.is_export_available():raise RuntimeError('Cascadeur export entitlement is unavailable')
view=app.get_scene_manager().current_scene()
# A unique filename avoids the existing-file save behavior seen in 2026.2.1.
version=KIT/('RightCut_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.casc')
view.save(str(version))
loader=csc.fbx.FbxLoader(120.,view.domain_scene().get_event_log_or_null(),view)
settings=csc.fbx.FbxSettings();settings.bake_animation=True
loader.set_settings(settings)
loader.export_all_objects(csc.Path(str(KIT/'RightCut_Performance.fbx')))
print('Source save requested: '+str(version))
print('Exported RightCut_Performance.fbx at 120 fps. Run Tools/ConvertCascadeurClip.py on that file to update Unreal.')
