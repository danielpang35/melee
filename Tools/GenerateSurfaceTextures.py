"""Generate original, seamless shared micro-surface textures (no external assets)."""
from pathlib import Path
import math,random,struct,zlib
out=Path('ArtSource/Textures');out.mkdir(parents=True,exist_ok=True)
N=256
rng=random.Random(518)
grids={s:[[rng.random() for _ in range(s)] for _ in range(s)] for s in (8,16,32,64)}
def noise(x,y,s):
 x=x/N*s;y=y/N*s;i=int(x);j=int(y);u=x-i;v=y-j;u=u*u*(3-2*u);v=v*v*(3-2*v);g=grids[s]
 return (g[j%s][i%s]*(1-u)+g[j%s][(i+1)%s]*u)*(1-v)+(g[(j+1)%s][i%s]*(1-u)+g[(j+1)%s][(i+1)%s]*u)*v
h=[[sum(noise(x,y,s)*w for s,w in [(8,.45),(16,.3),(32,.17),(64,.08)]) for x in range(N)] for y in range(N)]
def png(name,rows):
 def chunk(k,d):return struct.pack('!I',len(d))+k+d+struct.pack('!I',zlib.crc32(k+d)&0xffffffff)
 data=b''.join(b'\0'+bytes(row) for row in rows)
 (out/name).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',N,N,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(data,9))+chunk(b'IEND',b''))
noise_rows=[];normal_rows=[]
for y in range(N):
 row=[];norm=[]
 for x in range(N):
  v=round(h[y][x]*255);row.extend([v,v,v]);dx=(h[y][(x+1)%N]-h[y][(x-1)%N])*3;dy=(h[(y+1)%N][x]-h[(y-1)%N][x])*3;length=math.sqrt(dx*dx+dy*dy+1)
  norm.extend([round(((-dx/length)*.5+.5)*255),round(((-dy/length)*.5+.5)*255),round((1/length*.5+.5)*255)])
 noise_rows.append(row);normal_rows.append(norm)
png('T_SurfaceNoise.png',noise_rows);png('T_SurfaceNormal.png',normal_rows)
print('Generated two original seamless 256px shared textures.')
