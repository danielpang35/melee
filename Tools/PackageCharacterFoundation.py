"""Package actual source renders; no generated/concept imagery substitutes for geometry."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Saved/VideoRuntime'))
from PIL import Image,ImageDraw,ImageFont
P=ROOT/'ArtSource/CharacterReset/CF_v001';R=P/'Review'
def font(n):return ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
def sheet(name,entries,cols=3,width=480):
    h=round(width*1150/900);gap=16;header=100;caption=65
    rows=(len(entries)+cols-1)//cols
    im=Image.new('RGB',(cols*width+(cols+1)*gap,header+rows*(h+caption+gap)),(19,27,34));d=ImageDraw.Draw(im)
    d.text((20,15),'CF_v001  /  CHARACTER FOUNDATION',font=font(28),fill=(234,232,220))
    d.text((20,57),'Actual mesh renders • 180 cm adult study • linear skinning • visual review pending',font=font(17),fill=(164,189,199))
    for i,(file,label,detail) in enumerate(entries):
        x=gap+(i%cols)*(width+gap);y=header+(i//cols)*(h+caption+gap)
        src=Image.open(R/file).convert('RGB');src=src.resize((width,h),Image.Resampling.LANCZOS);im.paste(src,(x,y))
        d.text((x,y+h+8),label,font=font(20),fill=(234,232,220));d.text((x,y+h+36),detail,font=font(14),fill=(164,189,199))
    im.save(R/name,quality=92)
sheet('proportions.jpg',[
 ('01_neutral_front.png','01 / Front','Continuous torso, shoulders, arms and hands'),
 ('02_neutral_side.png','02 / Side','Plain surface exposes the silhouette'),
 ('03_neutral_back.png','03 / Back','No detached sleeves or shoulder openings')])
sheet('shoulders.jpg',[
 ('05_shoulders_raised.png','04 / Arm elevation','Clavicle + scapular segment + upper arm'),
 ('06_forward_reach.png','05 / Forward reach','Shoulder protraction accompanies the arms'),
 ('07_elbow_flexion.png','06 / Elbow flexion','Independent wrists and articulated fingers')])
manifest={}
for file in [P/'CF_v001_Character.blend',P/'CF_v001_Character.fbx',P/'character-report.json',R/'proportions.jpg',R/'shoulders.jpg']:
 manifest[str(file.relative_to(P))]={'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
(P/'delivery-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
