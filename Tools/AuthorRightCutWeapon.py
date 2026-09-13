"""Coauthor a curved hand drive and delayed blade turn for the RC_v006 pilot.

Produces editable local-space weapon samples; the game applies its legal aim,
reach and collision rules. Resample that evaluator before Cascadeur posing.
"""
from pathlib import Path
import csv,math
ROOT=Path(__file__).resolve().parents[1]
def unit(v):
    d=math.sqrt(sum(x*x for x in v));return [x/d for x in v]
depth=110*.175/1.103061375617981
ready_axis=unit([.75,.10,.65])
ready=[42-ready_axis[0]*depth,12-ready_axis[1]*depth,-20-ready_axis[2]*depth]
# frame, grip centre relative to eye-18, blade azimuth, blade elevation.
# The hands accelerate forward while the blade still trails to the right.
keys=[
 (0,*ready,math.degrees(math.atan2(.10,.75)),math.degrees(math.asin(ready_axis[2]))),
 (30,*ready,math.degrees(math.atan2(.10,.75)),math.degrees(math.asin(ready_axis[2]))),
 (65,16,22,-13,65,34),
 (90,7,27,-4,112,23),
 (99,9,27,-4,110,18),
 (110,25,23,-8,83,10),
 (124,37,8,-15,22,1),
 (137,31,-13,-22,-42,-8),
 (159,20,-24,-24,-94,-10),
 (177,16,-23,-27,-104,0),
 (199,20,-9,-29,-58,30),
 (221,27,7,-32,-4,42),
 (240,*ready,math.degrees(math.atan2(.10,.75)),math.degrees(math.asin(ready_axis[2]))),
 (270,*ready,math.degrees(math.atan2(.10,.75)),math.degrees(math.asin(ready_axis[2])))]
def sample(f):
    i=next((i for i in range(len(keys)-1) if keys[i][0]<=f<keys[i+1][0]),len(keys)-2)
    a,b=keys[i],keys[i+1];dt=b[0]-a[0];t=(f-a[0])/dt
    def slope(j,c):
        if j in (0,1,len(keys)-2,len(keys)-1):return 0.
        return (keys[j+1][c]-keys[j-1][c])/(keys[j+1][0]-keys[j-1][0])
    return [(2*t**3-3*t*t+1)*a[c]+(t**3-2*t*t+t)*dt*slope(i,c)+(-2*t**3+3*t*t)*b[c]+(t**3-t*t)*dt*slope(i+1,c) for c in range(1,6)]
if __name__=='__main__':
    out=ROOT/'Config/RightCutWeapon.csv'
    with out.with_suffix('.tmp').open('w',newline='') as file:
        w=csv.writer(file,lineterminator='\n');w.writerow(['RIGHT_CUT_WEAPON_V1',120,271])
        for f in range(271):
            x,y,z,az,el=sample(f);az=math.radians(az);el=math.radians(el)
            axis=[math.cos(az)*math.cos(el),math.sin(az)*math.cos(el),math.sin(el)]
            h=[p+d*depth for p,d in zip([x,y,z],axis)]
            w.writerow([f,*h,*axis])
    out.with_suffix('.tmp').replace(out)
    print(out)
