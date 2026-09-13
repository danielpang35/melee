"""Focused receipt checks; no Blender session or media rendering."""
import copy
import tempfile
import unittest
from pathlib import Path
import AnimationLab as lab

class RequiredViewsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.primary = dict(source_sha256='source-a', fps=30, source_fps=60,
            first_source_frame=19, source_stride=2, frames=68, playback_rate=1)
        self.evidence = dict(policy=lab.VIEW_POLICY, views={})
        for name, file in [('primary', 'preview.mp4'), ('rear-quarter', 'preview-rear-quarter.mp4')]:
            (self.folder/file).write_bytes(name.encode())
            self.evidence['views'][name] = dict(file=file, sha256=lab.digest(self.folder/file),
                source_sha256='source-a', timing={k:v for k,v in self.primary.items() if k!='source_sha256'},
                camera=dict(name=name, location=[1,2,3]))
        self.save()

    def save(self):
        lab.write(self.folder/'preview-views.json', self.evidence)

    def test_matching_source_timing_and_cameras(self):
        cameras = lab.checked_views(self.folder, self.primary)
        self.assertEqual(lab.checked_views(self.folder, self.primary, cameras), cameras)

    def test_missing_required_view(self):
        del self.evidence['views']['rear-quarter']; self.save()
        with self.assertRaisesRegex(ValueError, 'Missing required view'):
            lab.checked_views(self.folder, self.primary)

    def test_stale_source(self):
        self.evidence['views']['rear-quarter']['source_sha256']='old'; self.save()
        with self.assertRaisesRegex(ValueError, 'stale'):
            lab.checked_views(self.folder, self.primary)

    def test_different_timing(self):
        self.evidence['views']['rear-quarter']['timing']['frames']-=1; self.save()
        with self.assertRaisesRegex(ValueError, 'identical source timing'):
            lab.checked_views(self.folder, self.primary)

    def test_different_candidate_cameras(self):
        cameras=lab.checked_views(self.folder, self.primary)
        cameras['rear-quarter']['location']=[8,9,10]
        with self.assertRaisesRegex(ValueError, 'same camera'):
            lab.checked_views(self.folder, self.primary, cameras)

    def test_missing_media(self):
        (self.folder/'preview-rear-quarter.mp4').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing or changed'):
            lab.checked_views(self.folder, self.primary)

    def test_historical_receipt_preserved(self):
        historical={'historical':True}
        lab.write(self.folder/'preview.json', historical)
        (self.folder/'preview-views.json').unlink()
        with self.assertRaisesRegex(ValueError, 'Historical/single-view'):
            lab.checked_views(self.folder, self.primary)
        self.assertEqual(lab.read(self.folder/'preview.json'),historical)

if __name__ == '__main__':
    unittest.main()
