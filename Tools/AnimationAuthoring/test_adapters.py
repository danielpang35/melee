"""Targeted authoring boundaries; no Blender render, imports or gameplay tests."""
import argparse
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import AnimationLab as lab
from AnimationAuthoring.performance import seed_score, validate_score


class Boundaries(unittest.TestCase):
    def test_current_working_body_requires_supported_adapter(self):
        args = argparse.Namespace(adapter=None, batch='unsupported-working-body')
        with self.assertRaisesRegex(ValueError, 'Working AccuRig body has no AnimationLab'):
            lab.make_batch(args)

    def test_exploration_time_is_not_legacy_clock(self):
        score=seed_score();validate_score(score)
        with self.assertRaises(ValueError):lab.validate_score(score)
        for channel in score['channels'].values():channel[-1][0]=121
        score['frame_end']=121;score['fps']=24
        validate_score(score)
        score['channels']['body'][2][0]=9
        with self.assertRaises(ValueError):validate_score(score)

    def test_containment_and_immutable_native_preview(self):
        with tempfile.TemporaryDirectory() as td,patch.object(lab,'LAB',Path(td)):
            with self.assertRaises(ValueError):lab.batch_path('../production')
            batch=lab.batch_path('test');folder=batch/'source/Candidates/A/TP_v001';folder.mkdir(parents=True)
            with self.assertRaises(ValueError):lab.candidate_folder(batch,{'folder':'../../TP_v001'})
            for name in ['pose-controls.json','TP_v001_RightHorizontal.blend','preview.mp4','native-input.blend']:
                (folder/name).write_bytes(b'fixture')
            receipt={key:lab.digest(folder/name) for key,name in [('controls_sha256','pose-controls.json'),('source_sha256','TP_v001_RightHorizontal.blend'),('preview_sha256','preview.mp4'),('native_input_sha256','native-input.blend')]}
            lab.write(folder/'preview.json',receipt);lab.checked_preview(folder)
            (folder/'native-input.blend').write_bytes(b'edited native curve')
            with self.assertRaisesRegex(ValueError,'native input changed'):lab.checked_preview(folder)

    def test_shared_render_lock_is_preserved(self):
        with tempfile.TemporaryDirectory() as td,patch.object(lab,'LAB',Path(td)):
            batch=lab.batch_path('test');batch.mkdir()
            lab.write(batch/'batch.json',dict(adapter='cf-controls-v1',inputs={},candidates=[]))
            lock=Path(td)/'render.lock';lock.write_text('other renderer')
            args=argparse.Namespace(batch='test',candidate=None,camera=None)
            with self.assertRaises(FileExistsError):lab.render_batch(args)
            self.assertEqual(lock.read_text(),'other renderer')
            args.camera='Defender'
            with self.assertRaisesRegex(ValueError,'saved MEL-36'):lab.render_batch(args)

    def test_refinement_retains_native_source(self):
        with tempfile.TemporaryDirectory() as td,patch.object(lab,'LAB',Path(td)):
            batch=lab.batch_path('test');folder=batch/'source/Candidates/A/TP_v001';folder.mkdir(parents=True)
            lab.write(folder/'pose-controls.json',seed_score())
            (folder/'TP_v001_RightHorizontal.blend').write_bytes(b'editable native curves')
            (folder/'preview.mp4').write_bytes(b'preview')
            lab.write(folder/'preview.json',{key:lab.digest(folder/name) for key,name in [('controls_sha256','pose-controls.json'),('source_sha256','TP_v001_RightHorizontal.blend'),('preview_sha256','preview.mp4')]})
            lab.write(batch/'batch.json',dict(adapter='cf-controls-v1',batch='test',selected={'id':'A','reason':'fixture selection'},candidates=[dict(id='A',folder='source/Candidates/A/TP_v001',hypothesis='x',state='preview_ready')]))
            lab.refine(argparse.Namespace(batch='test',candidate='B',reason='edit wrist'))
            self.assertEqual((batch/'source/Candidates/B/TP_v001/native-input.blend').read_bytes(),b'editable native curves')


if __name__=='__main__':unittest.main()
