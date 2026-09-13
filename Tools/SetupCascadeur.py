"""Run in Cascadeur Python Console to open the verified authoring starter."""
import json,traceback
from pathlib import Path
import csc
ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/'Saved/Cascadeur/setup-result.json'
RESULT.parent.mkdir(parents=True,exist_ok=True)
report={'script_revision':3,'animation_authored':False}
try:
    path=ROOT/'ArtSource/Cascadeur/RightCut_120.casc'
    if not path.is_file():raise FileNotFoundError('Verified authoring scene is missing: '+str(path))
    app=csc.app.get_application()
    if not app.is_export_available():raise RuntimeError('Cascadeur export entitlement is unavailable')
    if not app.get_data_source_manager().load_scene(str(path)):raise RuntimeError('Cascadeur could not open the saved scene')
    report.update(status='authoring_scene_opened',scene=str(path))
except Exception:
    report.update(status='setup_incomplete',error=traceback.format_exc())
RESULT.write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
