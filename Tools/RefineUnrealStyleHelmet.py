"""Shape v011: expose existing two-facet temple cover toward fitted camera."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Saved/ArtRuntime'))
import bpy
from mathutils import Vector
SOURCE=ROOT/'ArtSource/StyleReference/MEL17/UnrealProof/Shape_v009/Helmet_Shape_v009.blend';OUT=ROOT/'ArtSource/StyleReference/MEL17/UnrealProof/Shape_v011'
if OUT.exists():raise SystemExit('Immutable Shape_v011 exists')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));ob=bpy.data.objects['Left angular temple overlap'];old=[list(v.co) for v in ob.data.vertices];z=(old[0][2]+old[2][2])/2
center=Vector((-.321,-.132,z));tangent=Vector((.6,-.8,0));normal=Vector((-.8,-.6,0));ridge=center+normal*.0025
points=[ridge+Vector((0,0,.042)),center+tangent*.025,ridge-Vector((0,0,.042)),center-tangent*.025]
for v,co in zip(ob.data.vertices,points):v.co=co
ob.data.update()
for q in ob.data.polygons:
 if q.normal.dot(normal)<0:q.flip()
OUT.mkdir(parents=True);destination=OUT/'Helmet_Shape_v011.blend';bpy.ops.wm.save_as_mainfile(filepath=str(destination))
r={'source':SOURCE.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'old_cover_vertices':old,'new_cover_vertices':[list(p) for p in points],'target_facing':list(normal),'retained':'Same4vertices/2broadfaces, .084 vertical extent, material/modifiers, shell/slit anchors, no global hinge scaling','shape_change':'Reoriented local diamond plane and shifted onto forward temple; narrow shallow ridge retained','fields':'Same USP10 contour recipe, strength1; roughness preserved from USP10 only if UVs remain identical','acceptance':'Pending occlusion-aware source checks and actual Unreal comparison'}
(OUT/'edit_receipt.json').write_text(json.dumps(r,indent=2));(OUT/'generator.py').write_text(Path(__file__).read_text());print('HINGE_REORIENTED')
