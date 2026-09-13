"""Fresh reference-directed MB blocking; native control source owns later edits.

No runtime selection/import. Run run('A_rotational'/'B_grounded'/'C_gathering')
inside Cascadeur. Retain each resulting source; never rerun over it.
"""
import csc,json,math
import numpy as np
from pathlib import Path
O=Path(__file__).resolve().parent
ROOT=O.parents[2]

def unit(x):
 n=np.linalg.norm(x)
 if n<1e-7:raise ValueError('Degenerate direction')
 return x/n
def axisrot(axis,angle):
 axis=unit(np.array(axis,dtype=float));x,y,z=axis;K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
 return np.eye(3)+math.sin(angle)*K+(1-math.cos(angle))*K@K
def yaw(deg):return axisrot([0,1,0],math.radians(deg))
def frame(y,z):
 y=unit(y);z=unit(z-y*np.dot(y,z));return np.column_stack((np.cross(y,z),y,z))
def link(a,b,l1,l2,hint):
 delta=b-a;dist=np.linalg.norm(delta)
 if not abs(l1-l2)+.001<dist<l1+l2+.0001:raise ValueError(f'Unreachable link {dist:.3f} / {l1+l2:.3f}')
 along=delta/dist;side=unit(hint-along*np.dot(along,hint));d=(dist*dist+l1*l1-l2*l2)/(2*dist)
 return a+d*along+math.sqrt(max(0,l1*l1-d*d))*side
def interp(keys,values,t):
 if t<=keys[0]:return np.array(values[0],dtype=float)
 if t>=keys[-1]:return np.array(values[-1],dtype=float)
 i=next(i for i in range(len(keys)-1) if keys[i]<=t<keys[i+1]);span=keys[i+1]-keys[i];u=(t-keys[i])/span
 a,b=np.array(values[i],dtype=float),np.array(values[i+1],dtype=float)
 ma=np.zeros_like(a) if i==0 else (b-np.array(values[i-1]))/(keys[i+1]-keys[i-1])
 mb=np.zeros_like(b) if i+1==len(keys)-1 else (np.array(values[i+2])-a)/(keys[i+2]-keys[i])
 return (2*u**3-3*u*u+1)*a+(u**3-2*u*u+u)*span*ma+(-2*u**3+3*u*u)*b+(u**3-u*u)*span*mb

def run(candidate,dry=False):
 assert candidate in ('A_rotational','B_grounded','C_gathering')
 out=O/candidate
 assert dry or not (out/(candidate+'.casc')).exists(),'Published native take exists'
 app=csc.app.get_application()
 view=app.get_scene_manager().current_scene();scene=view.domain_scene();mv=scene.model_viewer();bv=mv.behaviour_viewer();dv=mv.data_viewer();objects={mv.get_object_name(o):o for o in mv.get_objects()}
 def data(n,p):return bv.get_behaviour_data(bv.get_behaviour_by_name(objects[n],'Transform'),p)
 def pos(n,f=0):return np.array(dv.get_data_value(data(n,'global_position'),f),dtype=float)
 def rot(n,f=0):return np.array(dv.get_data_value(data(n,'global_rotation'),f).to_rotation_matrix(),dtype=float)
 base={n:np.array(p,dtype=float) for n,p in json.loads((O/'restored_control_rest.json').read_text()).items() if 'Point' in n}
 controls={n:data(n,'global_position') for n in base};cal=json.loads((O/'native_grasps_v003.json').read_text())
 # Reuse actual native wrist-to-palm calibration; never inherit old choreography.
 palm={side:(np.array(cal[side]['rotation']),np.array(cal[side]['position'])) for side in 'rl'}
 seed_hand_r=rot('hand_r');rest_hand={side:np.array(cal[side]['rest_rotation']) for side in 'rl'}
 # Guide stays separate: accepted source times converted once to this30FPS clock.
 source=json.loads((ROOT/'ArtSource/CharacterReset/EX_v002/Export/EX_v002_WeaponMotion.json').read_text())
 C=np.array([[1,0,0],[0,0,1],[0,-1,0]],dtype=float);guide={}
 for f in range(22,32):
  sample=source['samples'][18+2*f];M=np.array(sample['weapon_world']['matrix_row_major']);r=C@M[:3,:3];h=C@(M[:3,3]+np.array([0,.115,.020]))*100
  guide[f]=(h-r[:,2]*7.,r,h)
 ready=(pos('hand_r')+rot('hand_r')@palm['r'][1],rot('MB_Weapon'))
 keys=[0,5,12,18,21,22,31,38,48,58,68]
 # Observed opening then gathering, never a compulsory sports/low-waist path.
 gather={'A_rotational':[-32,148,20],'B_grounded':[-29,147,24],'C_gathering':[-35,149,17]}[candidate]
 positions=[ready[0].tolist(),[-17,143,32],[-37,157,29],gather,[-39,155,41],guide[22][0].tolist(),guide[31][0].tolist(),[47,140,27],[30,120,25],[7,128,26],ready[0].tolist()]
 if candidate=='B_grounded':positions[7]=[40,134,31];positions[8]=[23,117,29]
 if candidate=='C_gathering':positions[2]=[-42,159,25];positions[7]=[50,145,16];positions[8]=[33,126,12]
 # Blade rotations interpolate in quaternion space; release rotations are guide landmarks.
 rkeys={0:ready[1],5:yaw(-25)@ready[1],12:yaw(-65)@axisrot([0,0,1],math.radians(30))@ready[1],18:yaw(-75)@axisrot([0,0,1],math.radians(40))@ready[1],21:guide[22][1],22:guide[22][1],31:guide[31][1],38:yaw(25)@guide[31][1],48:yaw(50)@axisrot([1,0,0],math.radians(-35))@guide[31][1],58:ready[1],68:ready[1]}
 def orientation(f):
  if f in guide:return guide[f][1]
  i=next((i for i in range(len(keys)-1) if keys[i]<=f<keys[i+1]),len(keys)-2);a,b=keys[i],keys[i+1];u=min(1,max(0,(f-a)/(b-a)));u=u*u*(3-2*u)
  U,_,V=np.linalg.svd(rkeys[a]*(1-u)+rkeys[b]*u);fix=np.diag([1,1,np.linalg.det(U@V)])
  return U@fix@V
 # Distinct coordinated support strategies; feet stay fixed in actor space.
 chest_yaws=[0,-15,-35,-48,-45,-42,62,75,43,8,0]
 hip_yaws=[0,-5,-15,-23,-17,-12,27,34,19,3,0]
 if candidate=='B_grounded':chest_yaws=[x*.88 for x in chest_yaws];hip_yaws=[x*.8 for x in hip_yaws]
 if candidate=='C_gathering':chest_yaws=[x*.92 for x in chest_yaws]
 pelvis_shift=[[0,0,0],[-1,-.5,0],[-4,-1,0],[-5,-2,1],[-3,-1,2],[-2,0,3],[6,0,4],[7,-1,3],[3,-1,1],[0,0,0],[0,0,0]]
 if candidate=='B_grounded':pelvis_shift=[[0,0,0],[-2,-1,0],[-5,-3,0],[-6,-5,1],[-4,-3,2],[-2,-1,3],[6,-1,4],[7,-4,3],[3,-2,1],[0,0,0],[0,0,0]]
 poses=[];planned=[];root=base['pelvis_MainPoint'];stomach=base['spine_02_MainPoint'];chest=base['spine_04_MainPoint'];neck=base['neck_01_MainPoint'];max_deficit=0
 for f in range(69):
  gp,gr=(guide[f][0],guide[f][1]) if f in guide else (interp(keys,positions,f),orientation(f))
  cy=float(interp(keys,chest_yaws,f));hy=float(interp(keys,hip_yaws,f));shift=interp(keys,pelvis_shift,f);rp=yaw(hy);rc=yaw(cy)
  shift[1]-=2*math.sin(math.pi*f/68)**2
  hip=root+shift
  for side in 'rl':
   offset=rp@(base['thigh_MainPoint_'+side]-root);ankle=base['foot_MainPoint_'+side];knee=base['calf_MainPoint_'+side];thigh0=base['thigh_MainPoint_'+side]
   length=np.linalg.norm(knee-thigh0)+np.linalg.norm(ankle-knee)-.01;horizontal=np.linalg.norm((hip+offset-ankle)[[0,2]])
   hip[1]=min(hip[1],ankle[1]+math.sqrt(max(0,length*length-horizontal*horizontal))-offset[1])
  # Supported body transport first: preserve each torso segment's length instead
  # of translating the chest away from the pelvis to chase the canonical sword.
  lean=float(interp(keys,[0,1,3,5,7,9,9,5,2,0,0],f))
  if candidate=='B_grounded':lean*=1.2
  rl=yaw((hy+cy)*.5)@axisrot([1,0,0],math.radians(lean*.7))
  rc=yaw(cy)@axisrot([1,0,0],math.radians(lean))
  sp=hip+rl@(stomach-root);cp=sp+rc@(chest-stomach)
  # User-authorized smallest common translation of the joined grasps. Dykstra
  # projects the desired grip into the two fixed-length arm reach balls while
  # retaining the authored blade orientation and shared hand spacing.
  desired_gp=gp.copy();centers=[];radii=[]
  for side in 'rl':
   wr=gr@palm[side][0].T;sh=cp+rc@(base['upperarm_MainPoint_'+side]-chest)
   centers.append(sh+wr@palm[side][1]+(gr[:,2]*12.5 if side=='l' else 0))
   radii.append((np.linalg.norm(base['lowerarm_MainPoint_'+side]-base['upperarm_MainPoint_'+side])+np.linalg.norm(base['hand_MainPoint_'+side]-base['lowerarm_MainPoint_'+side]))*.97)
  corrections=[np.zeros(3),np.zeros(3)]
  for _ in range(64):
   for i in range(2):
    y=gp+corrections[i];delta=y-centers[i];d=np.linalg.norm(delta);new=y if d<=radii[i] else centers[i]+delta*radii[i]/d;corrections[i]=y-new;gp=new
  deficit=max(np.linalg.norm(gp-centers[i])-radii[i] for i in range(2))
  assert deficit<.005,('Shared grasp envelope',f,deficit)
  wrists={side:((gp if side=='r' else gp-gr[:,2]*12.5)-gr@palm[side][0].T@palm[side][1],gr@palm[side][0].T) for side in 'rl'}
  p={n:v.copy() for n,v in base.items()}
  # Pelvis and torso bend as a supported chain, neck/head remain facing opponent.
  for n in p:
   if n.startswith('pelvis_'):p[n]=hip+rp@(base[n]-root)
   elif n.startswith('spine_02_'):p[n]=sp+rl@(base[n]-stomach)
   elif n.startswith(('spine_04_','clavicle_','upperarm_')):p[n]=cp+rc@(base[n]-chest)
   elif n.startswith('neck_01_'):p[n]=cp+rc@(base[n]-chest)
   elif n.startswith('head_'):p[n]=cp+rc@(neck-chest)+yaw(cy*.12)@(base[n]-neck)
  for side in 'rl':
   w,wr=wrists[side];a=base['upperarm_MainPoint_'+side];b=base['lowerarm_MainPoint_'+side];c=base['hand_MainPoint_'+side];sh=p['upperarm_MainPoint_'+side]
   elbow=link(sh,w,np.linalg.norm(b-a),np.linalg.norm(c-b),np.array([-1 if side=='r' else 1,-.55,-.15]))
   lr=frame(w-elbow,np.cross(w-elbow,sh-elbow))@frame(c-b,np.cross(c-b,a-b)).T
   for n in p:
    if n.startswith('lowerarm_') and n.endswith('_'+side):p[n]=elbow+lr@(base[n]-b)
    elif n.startswith('hand_') and n.endswith('_'+side):p[n]=w+wr@rest_hand[side].T@(base[n]-c)
   thigh=hip+rp@(base['thigh_MainPoint_'+side]-root);ankle=base['foot_MainPoint_'+side];kneebase=base['calf_MainPoint_'+side];thighbase=base['thigh_MainPoint_'+side]
   knee=link(thigh,ankle,np.linalg.norm(kneebase-thighbase),np.linalg.norm(ankle-kneebase),np.array([-.08 if side=='r' else .08,0,1.]))
   p['thigh_MainPoint_'+side]=thigh;p['calf_MainPoint_'+side]=knee
   lr=frame(ankle-knee,np.array([1,0,0]))@frame(ankle-kneebase,np.array([1,0,0])).T
   p['calf_AdditionalPoint_'+side]=knee+lr@(base['calf_AdditionalPoint_'+side]-kneebase)
  poses.append(p);planned.append({'frame':f,'chest_cm':cp.tolist(),'primary_cm':gp.tolist(),'chest_yaw':cy,'path_adjustment_cm':(gp-desired_gp).tolist(),'path_adjustment_length_cm':float(np.linalg.norm(gp-desired_gp))})
 if dry:
  (O/(candidate+'_support_plan.json')).write_text(json.dumps(planned,indent=2));print('Reach plan passes',candidate,max_deficit);return
 out.mkdir(exist_ok=True)
 def edit(model,update,up):
  de=model.data_editor();le=model.layers_editor();layers=scene.layers_viewer()
  for layer in layers.all_layer_ids():
   if not layer.is_null():le.set_section(csc.layers.layer.Section(),69,layer)
  model.fit_animation_size_by_layers();up.generate_update()
  for f,p in enumerate(poses):
   actual=set()
   for n,d in controls.items():de.set_data_value(d,f,p[n]);actual.add(d)
   for layer in layers.all_layer_ids():
    if not layer.is_null():le.set_fixed_interpolation_or_key_if_need(layer,f,True)
   try:
    model.set_fixed_interpolation_if_need(actual,f);up.run_update(actual,f)
   except Exception as error:raise RuntimeError(f'Native update frame {f}: {error}') from error
 if not scene.modify_update('Fresh MB '+candidate+' full-body blocking',edit):raise RuntimeError('Native pose edit rejected')
 # Saved native result, not an offline reconstruction, is the downstream source.
 view.save(str(out/(candidate+'.casc')));loader=csc.fbx.FbxLoader(30.,scene.get_event_log_or_null(),view);settings=csc.fbx.FbxSettings();settings.bake_animation=True;loader.set_settings(settings);loader.export_all_objects(csc.Path(str(out/(candidate+'.fbx'))))
 report={'candidate':candidate,'native_export_fps':30,'first_native_index':0,'release_native_indices':[22,31],'last_native_index':68,'body':'MB_AccuRig','body_mesh':'SK_MB_Body_LOD0','guidance':'Fresh Mordhau opening then gathering; recovery interpreted','native_source':str(out/(candidate+'.casc')),'limitation':'Unreviewed native blocking; no continuous playback or human acceptance; fingers need finishing','planned_support':planned}
 (out/'receipt.json').write_text(json.dumps(report,indent=2));print('CANDIDATE_SAVED',candidate)
