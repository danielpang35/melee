"""Run with python Tests/UnrealStyleCaptureValidationTests.py."""
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Tools'))
from UnrealStyleCaptureValidation import validate_png, validate_motion,validate_capture_receipt


def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)


def png(rows, width=2, color=2):
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, len(rows), 8, color, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(b''.join(rows))) + chunk(b'IEND', b''))


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'test.png'

    def tearDown(self):
        self.temp.cleanup()

    def validate(self, data):
        self.path.write_bytes(data)
        return validate_png(self.path, (2, 1))

    def test_decode_all_filters(self):
        # Reconstructed row always [(10,20,30),(80,90,100)].
        for method, tail in [(0,[80,90,100]),(1,[70,70,70]),(2,[80,90,100]),(3,[75,80,85]),(4,[70,70,70])]:
            result = self.validate(png([bytes([method,10,20,30]+tail)]))
            self.assertEqual(result['rgb_max'], [80,90,100])
            self.assertTrue(result['complete_image_validated'])

    def test_reject_header_truncation_crc_blank_and_dimensions(self):
        valid = png([bytes([0,10,20,30,80,90,100])])
        for data in [valid[:24], valid[:-8], valid[:-20]+bytes([valid[-20]^1])+valid[-19:],
                     png([bytes([0,10,20,30,10,20,30])]), valid + b'extra',
                     png([bytes([0,10,20,30,80,90,100])], width=3)]:
            with self.assertRaises(ValueError):
                self.validate(data)

    def test_alpha_alone_is_blank(self):
        with self.assertRaises(ValueError):
            self.validate(png([bytes([0,10,20,30,0,10,20,30,255])], color=6))

    def frames(self):
        return [dict(file=str(i)+'.png', motion='rotation', sequence_frame=i,
                     request_engine_frame=100+i, completion_engine_frame=101+i,
                     world_delta_seconds=1/30, complete_image_validated=True,
                     helmet_rotation_deg=[0,i,0], key_rotation_deg=[0,0,0],
                     camera_location_cm=[0,0,0], camera_rotation_deg=[0,0,0]) for i in range(3)]

    def test_motion_requires_complete_consecutive_evidence(self):
        self.assertTrue(validate_motion(self.frames(), {'rotation':3})[0]['continuous'])
        with self.assertRaises(ValueError):
            validate_motion(self.frames()[:2], {'rotation':3})
        for key, value in [('request_engine_frame',110),('completion_engine_frame',110),
                           ('complete_image_validated',False),('sequence_frame',8),
                           ('helmet_rotation_deg',[0,float('nan'),0]),('world_delta_seconds',.1),('world_delta_seconds',float('nan')),('file','0.png')]:
            frames = self.frames()
            frames[1][key] = value
            with self.assertRaises(ValueError, msg=key):
                validate_motion(frames, {'rotation':3})

    def test_receipt_binds_evidence_and_declared_motion(self):
        result=self.validate(png([bytes([0,10,20,30,80,90,100])]))
        entry=dict(result,file=str(self.path))
        receipt=dict(completed=True,revision='USP_v012',captures=[entry],motion_requirements={})
        validate_capture_receipt(self.path.parent,receipt,'USP_v012')
        for key,value in [('sha256','0'*64),('file',str(self.path.parent.parent/'outside.png')),('complete_image_validated',False)]:
            changed=dict(receipt,captures=[dict(entry,**{key:value})])
            with self.assertRaises(ValueError):
                validate_capture_receipt(self.path.parent,changed,'USP_v012')
        with self.assertRaises(ValueError):
            validate_capture_receipt(self.path.parent,receipt,'USP_v013')
        (self.path.parent/'extra.png').write_bytes(self.path.read_bytes())
        with self.assertRaises(ValueError):
            validate_capture_receipt(self.path.parent,receipt,'USP_v012')

    def test_shade_requires_physical_occluder_evidence(self):
        frames=self.frames()
        for frame in frames:frame['motion']='shade_transition'
        with self.assertRaises(ValueError):
            validate_motion(frames,{'shade_transition':3})
        for i,frame in enumerate(frames):frame['shade_occluder_location_cm']=[i,0,85]
        self.assertTrue(validate_motion(frames,{'shade_transition':3})[0]['continuous'])


if __name__ == '__main__':
    unittest.main()
