import argparse,csv,json,math,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('label');a=p.parse_args()
folder=Path('Saved/VisualPerformance')/a.label
capture=max(Path('Saved/Profiling/CSV').glob('*.csv'),key=lambda x:x.stat().st_mtime)
columns={}
with capture.open(encoding='utf-8-sig') as f:
 for row in csv.DictReader(f):
  for key,value in row.items():
   if key is None or not (key.startswith('GPU/') or key in ['MemoryFreeMB','GPUMem/LocalUsedMB','GPUSceneInstanceCount','ShadowCacheUsageMB']):continue
   try:v=float(value)
   except (ValueError,TypeError):continue
   if math.isfinite(v):columns.setdefault(key,[]).append(v)
result={'source_csv':str(capture),'note':'Unreal CSV GPU scopes, full capture including warmup; nested scopes are not additive.','means':{k:statistics.mean(v) for k,v in columns.items() if v}}
(folder/'gpu_scopes.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result['means'].items() if any(s in k for s in ['ShadowDepth','ShadowProjection','Translucency','LocalUsed','GPUScene','Basepass','Postprocessing'])},indent=2))
