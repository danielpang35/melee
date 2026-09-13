exec(open('Docs/MordhauRightReference/confirmed_extract.py').read().split('subprocess.run')[0])
p=subprocess.run([ff,'-hide_banner','-i',source,'-vf',"select='between(t,12.7,13.8)',showinfo",'-vsync','0','-enc_time_base','1:30000','-q:v','2','-y',str(out/'repeat-%03d.jpg')],capture_output=True,text=True)
import re,json
pts=[float(x) for x in re.findall(r'pts_time:([0-9.]+)',p.stderr)];(out/'repeat_pts.json').write_text(json.dumps(pts))
s=Image.new('RGB',(1920,1168));d=ImageDraw.Draw(s)
for z,j in enumerate(range(0,len(pts),2)):
 x=z%4*480;y=z//4*224;s.paste(Image.open(out/f'repeat-{j+1:03d}.jpg').resize((480,200)),(x,y+24));d.text((x,y),str(pts[j]),fill='white')
s.save(out/'repeat-sheet.jpg')
