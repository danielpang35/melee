"""First-person framing only. Release samples 99–159 are identically zero."""
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
keys=[(0,8,0,9),(30,8,0,9),(65,17,-3,5),(84,27,-7,-3),
      (92,16,-4,-2),(99,0,0,0),(159,0,0,0),(184,0,0,0),
      (211,5,0,4),(240,8,0,9),(270,8,0,9)]
def sample(f):
    a,b=next(((a,b) for a,b in zip(keys,keys[1:]) if a[0]<=f<=b[0]),(keys[-2],keys[-1]))
    t=(f-a[0])/(b[0]-a[0]);t=t*t*(3-2*t)
    return [a[j]+(b[j]-a[j])*t for j in range(1,4)]
if __name__=='__main__':
    out=ROOT/'Config/RightCutView.csv'
    with out.open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['RIGHT_CUT_VIEW_V1',120,271])
        for frame in range(271):w.writerow([frame,*sample(frame)])
    print(out)
