"""Shared revisioned proof-stage setup for capture and saved-map review."""
import unreal as u

def configure_stage(find_actor,destination,revision,neutral=False,read_only=False):
    assert revision in ['Stage_v001','Stage_v002','Stage_v003']
    raised=revision in ['Stage_v002','Stage_v003'];offset=145.0 if raised else 0.0
    material_path=destination+'/Materials/'+('MI_StageNeutral' if neutral else 'MI_StageWarm_Stage_v002' if raised else 'MI_StageWarm')
    material=u.load_asset(material_path)
    if material is None and raised and not neutral:
        assert not read_only,('Missing preserved stage material',material_path)
        material=u.AssetToolsHelpers.get_asset_tools().create_asset('MI_StageWarm_Stage_v002',destination+'/Materials',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
    if raised and not neutral:
        lib=u.MaterialEditingLibrary;parent=u.load_asset(destination+'/Materials/M_SteelAuthored');assert parent
        # UE5.8's vector setter updates the value but returns false unconditionally.
        # Verify the stored parameters instead of relying on the setter result.
        parameters=[('Metallic',0),('Roughness',.85),('NormalStrength',0),('RoughnessVariation',0)]
        color=lib.get_material_instance_vector_parameter_value(material,'BaseColor')
        correct=material.get_editor_property('parent')==parent and all(abs(a-b)<1e-5 for a,b in zip((color.r,color.g,color.b),(.50,.42,.29))) and all(abs(lib.get_material_instance_scalar_parameter_value(material,key)-value)<1e-5 for key,value in parameters)
        if not correct:
            assert not read_only,('Preserved stage material settings changed',material_path)
            lib.set_material_instance_parent(material,parent)
            lib.set_material_instance_vector_parameter_value(material,'BaseColor',u.LinearColor(.50,.42,.29,1))
            for key,value in parameters:lib.set_material_instance_scalar_parameter_value(material,key,value)
            lib.update_material_instance(material);u.EditorAssetLibrary.save_loaded_asset(material)
        color=lib.get_material_instance_vector_parameter_value(material,'BaseColor')
        assert all(abs(a-b)<1e-5 for a,b in zip((color.r,color.g,color.b),(.50,.42,.29)))
        for key,value in parameters:assert abs(lib.get_material_instance_scalar_parameter_value(material,key)-value)<1e-5
    assert material,material_path
    find_actor('ProofHelmet').set_actor_location(u.Vector(0,0,offset),False,False)
    wall_location=(0,-100,160) if raised else (0,-100,70);wall_scale=(6,.1,4) if raised else (6,.1,1.5)
    opening_location=(60,-93,180) if raised else (60,-93,50);opening_scale=(.6,.04,1.8) if raised else (.6,.04,.9)
    if revision=='Stage_v003':opening_location=(115,-93,180)
    for tag,location,scale in [('ProofWall',wall_location,wall_scale),('ProofOpening',opening_location,opening_scale)]:
        actor=find_actor(tag);actor.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE)
        actor.set_actor_location(u.Vector(*location),False,False);actor.set_actor_scale3d(u.Vector(*scale))
    for tag in ['ProofGround','ProofWall']:find_actor(tag).static_mesh_component.set_material(0,material)
    return {'revision':revision,'helmet_and_camera_elevation_cm':offset,'limestone_base_color_linear':[.5,.42,.29] if raised and not neutral else [.2,.2,.2] if neutral else [.24,.19,.13],'material_asset':material.get_path_name(),'wall_location_cm':list(wall_location),'wall_scale':list(wall_scale),'opening_location_cm':list(opening_location),'opening_scale':list(opening_scale)}
