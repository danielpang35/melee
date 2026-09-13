"""Read-only whole-cheek WorldNormal screenshot audit; uses bundled Python dependencies."""
from pathlib import Path
from collections import deque
import argparse,json,hashlib
import numpy as np
from PIL import Image,ImageDraw

parser=argparse.ArgumentParser();parser.add_argument('run_dir');args=parser.parse_args()
root=Path(args.run_dir).resolve()
paths=[root/('WorldNormal_'+v+'.png') for v in ['control','normals']]
control,authored=[np.asarray(Image.open(p).convert('RGB')).astype(np.int16) for p in paths]
assert control.shape==authored.shape
polygon=[(662,425),(862,423),(828,550),(789,570),(687,544)]
mask_image=Image.new('1',(control.shape[1],control.shape[0]));ImageDraw.Draw(mask_image).polygon(polygon,fill=1)
mask=np.asarray(mask_image).copy()
# Exclude the silhouette/slit/chin AA boundary from the manually fitted whole-cheek polygon.
for dy in range(-3,4):
    for dx in range(-3,4):mask &= np.roll(np.roll(np.asarray(mask_image),dy,0),dx,1)
delta=authored-control;strength=np.abs(delta).max(2)
edge=np.zeros(mask.shape,dtype=bool)
for dy,dx in [(1,0),(-1,0),(0,1),(0,-1)]:edge|=(np.abs(control-np.roll(np.roll(control,dy,0),dx,1)).max(2)>12)
edge_margin=edge.copy()
for dy in range(-3,4):
    for dx in range(-3,4):edge_margin|=np.roll(np.roll(edge,dy,0),dx,1)
face_interior=mask&~edge_margin
def components(active):
    points=set(map(tuple,np.argwhere(active)));result=[]
    while points:
        first=points.pop();queue=deque([first]);region=[first]
        while queue:
            y,x=queue.popleft()
            for p in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
                if p in points:points.remove(p);queue.append(p);region.append(p)
        if len(region)<10:continue
        y,x=np.asarray(region).T;d=delta[y,x]
        result.append({'pixels':len(region),'bbox_xyxy':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],'mean_signed_rgb_delta':d.mean(0).tolist()})
    return sorted(result,key=lambda r:r['pixels'],reverse=True)
thresholds={}
interior_thresholds={}
for threshold in [2,3,4,6]:
    active=mask&(strength>threshold)
    thresholds[str(threshold)]={'changed_pixels':int(active.sum()),'cheek_pct':float(100*active.sum()/mask.sum()),'components_over_9pixels':components(active)}
    active=face_interior&(strength>threshold)
    interior_thresholds[str(threshold)]={'changed_pixels':int(active.sum()),'face_interior_pct':float(100*active.sum()/face_interior.sum()),'components_over_9pixels':components(active)}
bins=[]
for y in range(425,566,20):
    row=[]
    for x in range(660,861,20):
        m=mask[y:y+20,x:x+20];a=(strength[y:y+20,x:x+20]>2)&m
        row.append({'x':x,'mask_pixels':int(m.sum()),'changed_pixels':int(a.sum())})
    bins.append({'y':y,'cells':row})
result={'method':'Unchanged 8-bit actual PIE WorldNormal control/authored RGB difference across whole lower-cheek silhouette, manually fitted fixed-camera polygon eroded3pixels to exclude AA edges. No angular-error inference from display RGB.',
        'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'polygon_xy':polygon,'erode_px':3,'cheek_pixels':int(mask.sum()),'thresholds_max_channel_delta_greater_than':thresholds,'spatial_bins_20px':bins,
        'face_interior_pixels':int(face_interior.sum()),'face_interior_edge_exclusion':'Exclude3px around control normal discontinuities greater than12 RGBlevels; avoids central ridge/slit/UV-seam differences being attributed to authored cheek field. Whole-cheek results remain separately retained.','face_interior_thresholds':interior_thresholds,
        'quiet_wall_max_delta':int(strength[430:530,470:550].max()),'limits':'Mask includes visible side and main cheek faces. Threshold2 is above observed outside-field compression/dither differences in prior buffer audit; multiple thresholds show sensitivity. Connected components are display-space footprints, not exact source UV mask area.'}
(root/'whole_cheek_worldnormal_analysis.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'cheek_pixels':int(mask.sum()),'face_interior_pixels':int(face_interior.sum()),'face_interior_thresholds':interior_thresholds},indent=2))
