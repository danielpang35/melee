"""Smoke-test the saved-scene loader's missing-file/licensing/load failures."""
import json,sys,tempfile,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'Tools/SetupCascadeur.py').read_text()
for exists,licensed,loads in [(False,True,True),(True,False,True),(True,True,False),(True,True,True)]:
    called=[]
    app=types.SimpleNamespace(is_export_available=lambda:licensed,get_data_source_manager=lambda:types.SimpleNamespace(load_scene=lambda path:called.append(path) or loads))
    sys.modules['csc']=types.SimpleNamespace(app=types.SimpleNamespace(get_application=lambda:app))
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory)
        if exists:
            scene=root/'ArtSource/Cascadeur/RightCut_120.casc';scene.parent.mkdir(parents=True);scene.write_bytes(b'test')
        changed=source.replace("ROOT=Path(r'C:/Users/Daniel Pang/OneDrive/Documents/ChatGPT/swingmanipulation')",'ROOT=Path('+repr(str(root))+')')
        assert changed!=source
        exec(compile(changed,'SetupCascadeur.py','exec'),{})
        report=json.loads((root/'Saved/Cascadeur/setup-result.json').read_text())
        assert (report['status']=='authoring_scene_opened')==(exists and licensed and loads)
        assert bool(called)==(exists and licensed)
print('PASS: starter loader failure handling. Actual scene save/reopen is verified separately in Cascadeur.')
