"""Apply visually reviewed labels; original captures remain untouched."""
from pathlib import Path
import json,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Saved/VideoRuntime'))
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).parent
OLD=ROOT/'Saved/ReferenceVideos/Mordhau_KMA2nf278No/defender'
# Each code is a visual landmark, NOT an engine phase boundary.
ROWS=[
('LH-A','left_horizontal_accel',38,'left','left','horizontal','accel','P T W D H C R I I I I P T W H C'),
('LH-D','left_horizontal_drag',66,'left','left','horizontal','drag','D D H R I I I I I P T W D D H R'),
('XR-A','left_parry_right_overhead_a',92,'left','right','overhead','unlabelled A','I I I P T W D H C R I I I I I P'),
('XR-B','left_parry_right_overhead_b',122,'left','right','overhead','unlabelled B','I I I P T W D C H R I I I I I I'),
('RH-A','right_horizontal_accel',154,'right','right','horizontal','accel','W D H R R I I I I P T W D H R R'),
('RH-D','right_horizontal_drag',178,'right','right','horizontal','drag','X I P T W D D H R I I I I P T W'),
('RO-A','right_overhead_accel',208,'right','right','overhead','accel','T W D H C R I I I I P W D H C R'),
('RO-D','right_overhead_drag',238,'right','right','overhead','drag','I P W D D D H R I I I I I I P T'),
('LO-A','left_overhead_accel',266,'left','left','overhead','accel','I P T D D H C R I I I I I P D D'),
('XL-A','right_parry_left_overhead_accel',292,'right','left','overhead','accel','R I I I I I P W D H C R R I I I'),
('XL-D','right_parry_left_overhead_drag',322,'right','left','overhead','drag','I I I I I I P W D D H C R I I I'),
('RU-A','right_underhand_accel',350,'right','right','underhand','accel','I I P T W D H C R I I I I P W D'),
('RU-D','right_underhand_drag',378,'right','right','underhand','drag','I P T W D H C R I I I I P T W D'),
('LU-A','left_underhand_accel',410,'left','left','underhand','accel','H C R I I I I I P T W D H C R R'),
('LU-D','left_underhand_drag',442,'left','left','underhand','drag','R I I I I I P T W D H C X X X X'),
]
STATES={'I':'ready / waiting','P':'parry / defensive entry','T':'parry-to-riposte transition','W':'riposte preparation','D':'riposte delivery / passage','H':'hit feedback / carry','C':'riposte carry','R':'return toward ready','X':'edit / fade / outro'}
COLORS={'I':'#b9c1cc','P':'#ffce73','T':'#ffb678','W':'#c6a4ff','D':'#8cd9ff','H':'#ff9baf','C':'#98dfbc','R':'#b9c1cc','X':'#9c9c9c'}
FONT=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
SMALL=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
def sheet(dest,title,records):
    im=Image.new('RGB',(1920,1360),'#151a22');d=ImageDraw.Draw(im)
    d.text((14,12),title,fill='white',font=FONT)
    d.text((14,40),'Read left to right. Labels describe the specified actor; transitions are approximate visual landmarks.',fill='#d0d7e2',font=SMALL)
    for j,r in enumerate(records):
        x=j%4*480;y=80+j//4*320
        im.paste(Image.open(ROOT/r['capture']).resize((480,270)),(x,y))
        d.text((x+8,y+274),f"{r['source_pts_s']:.3f}s | {r['visual_state']}",fill=COLORS.get(r['code'],'white'),font=SMALL)
        d.text((x+8,y+296),r.get('visibility','Phase inferred from ordered samples'),fill='#bdc5d0',font=SMALL)
    im.save(dest,quality=88)
def main():
    (OUT/'categorized').mkdir(exist_ok=True)
    catalogue=[]
    for rid,name,start,parry,origin,family,manip,codes in ROWS:
        codes=codes.split();assert len(codes)==16
        records=[]
        for j,code in enumerate(codes):
            capture=OLD/name/f'{j+1:03}.jpg';assert capture.exists()
            state=STATES[code]
            records.append({'id':f'{rid}/{j+1:03}','chapter':rid,'source_video_id':'KMA2nf278No','source_pts_s':start+j/4,
                'timestamp_basis':'legacy extraction seek + 60fps/15 frame step; source CFR; not gameplay time',
                'capture':capture.relative_to(ROOT).as_posix(),'actor':'black/red fighter, 240 Turbo Wanker','view':'external in Defender POV',
                'code':code,'visual_state':state,'depicted_attack_type':'riposte' if code in 'TWDHCR' else None,
                'context_attack_family':family,'context_attack_origin':origin,'preceding_parry_side':parry,'manipulation':manip,
                'confidence':'medium visual landmark; chapter identity supported by captions','game_phase':None,
                'visibility':'Foreground weapon may occlude actor' if code!='X' else 'Exclude from pose matching'})
        sheet(OUT/'categorized'/f'{rid}.jpg',f'{rid} | BLACK/RED FIGHTER | {parry.upper()} parry -> {origin.upper()} {family} RIPOSTE | {manip}',records)
        catalogue.extend(records)
    for name,origin in [('neutral-RH','right'),('neutral-LH','left')]:
        records=[]
        source=json.loads((OUT/'review'/name/'frames.json').read_text())
        for j,r in enumerate(source):
            code=('I' if j<2 else 'W' if j<8 else 'D' if j<10 else 'R') if name=='neutral-RH' else ('I' if j<2 else 'W' if j<9 else 'D' if j<12 else 'R')
            state={'I':'ready before neutral','W':'neutral horizontal preparation','D':'neutral strike meets parry','R':'post-parry / obscured return'}[code]
            records.append({'id':f'{name}/{j+1:03}','chapter':'LH-A' if origin=='right' else 'RH-D','source_video_id':'KMA2nf278No','source_pts_s':r['source_pts_s'],
                'timestamp_basis':'decoded source PTS','capture':(OUT/r['file']).relative_to(ROOT).as_posix(),'actor':'yellow-mask fighter, nbc (Paid Actor)',
                'view':'external in Attacker POV','code':code,'visual_state':state,'depicted_attack_type':'neutral' if code in 'WD' else None,
                'context_attack_family':'horizontal','context_attack_origin':origin,'preceding_parry_side':None,'manipulation':'not isolated/measured',
                'confidence':'medium-high visual origin and no preceding parry in this initiation','game_phase':None,
                'visibility':'Partner/FP weapon occludes return; not clean recovery reference' if j>=8 else 'Yellow-mask actor is the neutral initiator'})
        sheet(OUT/'categorized'/f'{name}.jpg',f'NEUTRAL {origin.upper()} HORIZONTAL | YELLOW-MASK INITIATOR | Foreground hands belong to the parrier/riposter',records)
        catalogue.extend(records)
    (OUT/'frame-catalogue.json').write_text(json.dumps({'version':2,'review_date':'2026-09-09','method':'Ordered frame inspection only; actor-specific labels; not recovered game phases','frames':catalogue},indent=2),encoding='utf8')
    assert len(catalogue)==272 and len({r['id'] for r in catalogue})==272
    print(f'Categorized {len(catalogue)} captures into 17 sheets; originals preserved.')
if __name__=='__main__':main()
