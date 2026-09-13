"""Replace a Cascadeur return's display mesh without changing its rig or motion.

Call apply_working_body(imported_rig) from an isolated Blender return, never an
uncoordinated live authoring session. Original returned mesh remains archived.
"""
import bpy, json, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def apply_working_body(rig, source=None):
    if source is None:
        selection=json.loads((ROOT/'Config/WorkingCharacter.json').read_text(encoding='utf-8-sig'))
        source=ROOT/selection['native_source']
    source=Path(source).resolve()
    assert source.is_relative_to(ROOT)
    scene=bpy.context.scene
    previous=[o for o in scene.objects if o.type=='MESH' and
              (o.name.startswith('SK_MB_Body_LOD0') or o.name.startswith('MB_Rigged_LOD0'))]
    assert previous, 'Expected one identifiable returned MB body'
    identity=hashlib.sha256(source.read_bytes()).hexdigest()
    with bpy.data.libraries.load(str(source),link=False) as (src,dst):
        assert 'MB_Rigged_LOD0' in src.objects
        dst.objects=['MB_Rigged_LOD0']
    body=dst.objects[0]; reference=body.find_armature()
    assert reference and len(reference.data.bones)==118
    # Appended, unlinked objects have unevaluated world transforms. Evaluate the
    # reference hierarchy before comparing bind positions or preserving placement.
    temporary=[]
    parent=reference
    while parent:
        if parent.name not in scene.objects:
            scene.collection.objects.link(parent);temporary.append(parent)
        parent=parent.parent
    scene.collection.objects.link(body)
    bpy.context.view_layer.update()
    for bone in reference.data.bones:
        other=rig.data.bones.get(bone.name)
        assert other is not None, 'Return is missing a body bone: '+bone.name
        assert (other.parent.name if other.parent else None)==(bone.parent.name if bone.parent else None)
        error=100*(rig.matrix_world@other.head_local-reference.matrix_world@bone.head_local).length
        assert error<.01, (bone.name,error)
        target_bind=rig.matrix_world@other.matrix_local
        source_bind=reference.matrix_world@bone.matrix_local
        bind_error=max(abs(a-b) for row_a,row_b in zip(target_bind,source_bind) for a,b in zip(row_a,row_b))
        assert bind_error<1e-4, ('Incompatible bind orientation/scale',bone.name,bind_error)
    for old in previous:
        old.name=old.name+'_BeforeSurfaceRepair'
        old.hide_render=True;old.hide_set(True)
    world=body.matrix_world.copy()
    body.parent=rig;body.matrix_parent_inverse=rig.matrix_world.inverted();body.matrix_world=world
    for mod in body.modifiers:
        if mod.type=='ARMATURE':mod.object=rig
    body.name='MB_Rigged_LOD0';body.hide_viewport=False;body.hide_render=False;body.hide_set(False)
    for obj in temporary:scene.collection.objects.unlink(obj)
    scene['working_body_source']=str(source.relative_to(ROOT))
    scene['working_body_source_sha256']=identity
    bpy.context.view_layer.update()
    return body
