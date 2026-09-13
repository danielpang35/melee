exec(open('Docs/MordhauRightReference/confirmed_extract.py').read().split('subprocess.run')[0])
p=subprocess.run([ff,'-hide_banner','-i',source,'-vf',"select='between(t,13.8,19.8)',showinfo",'-vsync','0','-enc_time_base','1:30000','-q:v','2','-y',str(out/'key-%03d.jpg')],capture_output=True,text=True)
(out/'native_pts.log').write_text(p.stderr)
import re,json
pts=[float(x) for x in re.findall(r'pts_time:([0-9.]+)',p.stderr)]
(out/'pts.json').write_text(json.dumps(pts))
for page in range((len(pts)+23)//24):
 s=Image.new('RGB',(1920,1168));d=ImageDraw.Draw(s)
 for z,t in enumerate(pts[page*24:(page+1)*24]):
  j=page*24+z;x=z%4*480;y=z//4*194;s.paste(Image.open(out/f'key-{j+1:03d}.jpg').resize((480,170)),(x,y+24));d.text((x,y),f'{j+1}: {t:.6f}',fill='white')
 s.save(out/f'native-sheet-{page}.jpg')
print(len(pts),pts[:2],pts[-2:])

