"""Summarize actual pilot contact evidence; instantaneous gaps are not swept tests."""
import argparse
import csv
import json
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('capture',type=Path)
args=parser.parse_args()
def rows(name):
    with (args.capture/name).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
frames=rows('frames.csv'); contacts=rows('contact.csv'); events=rows('events.csv')
assert len(frames)==len(contacts) and len(frames) in (720,960), 'Incomplete pilot capture'
by_frame={int(r['frame']):r for r in contacts}
release=[(r,by_frame[int(r['frame'])]) for r in frames if r['phase']=='RELEASE' and r['ex_active']=='1' and r['tp_active']=='1']
assert release, 'No actual selected TP release evidence'
summary={'capture':str(args.capture),'frames':len(frames),'events':events,
    'instantaneous_gap_definition':'distance from blade segment to current defender hurt axes minus body radius and configured blade radius; <=0 is overlap; not authoritative swept collision',
    'release_frames':len(release),'max_release_base_error_cm':max(float(r['tp_canonical_base_error']) for r,c in release),
    'max_release_tip_error_cm':max(float(r['tp_canonical_tip_error']) for r,c in release),
    'native_import_playback_max_pose_error_cm':max(float(r['tp_pose_error']) for r,c in release),
    'canonical_overlap_visible_clear_frames':[int(r['frame']) for r,c in release if float(c['canonical_gap_cm'])<=0<float(c['visible_gap_cm'])],
    'visible_overlap_canonical_clear_frames':[int(r['frame']) for r,c in release if float(c['visible_gap_cm'])<=0<float(c['canonical_gap_cm'])],
    'contact_event_samples':[{**e,**{'contact':by_frame.get(int(e['frame']))}} for e in events],
    'human_acceptance':False}
summary['contact_disagreement_detected']=bool(summary['canonical_overlap_visible_clear_frames'] or summary['visible_overlap_canonical_clear_frames'])
(args.capture/'contact-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ('events','contact_event_samples')},indent=2))
