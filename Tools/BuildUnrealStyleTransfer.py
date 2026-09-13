"""Schema-2 evaluated helmet preparation and frozen normal-endpoint baking.

Run with the project's bpy Python runtime, after source critique passes:
  python Tools/BuildUnrealStyleTransfer.py --prepare --revision USP_v012 --source-manifest <ST package/source_manifest.json>
  python Tools/BuildUnrealStyleTransfer.py --bake --revision USP_v012
Preparation alone creates UVs. Baking never unwraps or changes topology.
"""
from pathlib import Path
import argparse
import copy
import json
import gzip
import math
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "Tools"), str(ROOT / "Saved/ArtRuntime"), str(ROOT / "Saved/VideoRuntime")]
from UnrealStyleTransferContract import (ContractError, NORMAL_RUNTIME, canonical_sha256,
                                        contained_path, file_reference, mesh_identity,
                                        require_frozen_identity, sha256_file, validate_manifest)


def require(condition, message):
    if not condition:
        raise ContractError(message)


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def matrix_list(matrix):
    return [list(row) for row in matrix]


def check_references(references):
    for key, ref in references.items():
        path = contained_path(ROOT, ref["path"])
        require(sha256_file(path) == ref["sha256"], "Source identity changed: " + key)


def stable_tangent_basis(mesh):
    """MikkTSpace, with analytic UV-derivative fallback at singular corners."""
    mesh.calc_tangents(uvmap="TransferUV")
    result = [[*loop.tangent, loop.bitangent_sign] for loop in mesh.loops]
    repaired = []
    uv = mesh.uv_layers["TransferUV"].data
    for polygon in mesh.polygons:
        ids = list(polygon.loop_indices)
        face_signs = {result[i][3] for i in ids if abs(sum(x*x for x in result[i][:3])-1) < .002 and result[i][3] in (-1, 1)}
        require(len(face_signs) <= 1, "Conflicting nonsingular tangent signs within triangle " + str(polygon.index))
        for i in ids:
            raw = result[i]
            normal = mesh.corner_normals[i].vector
            if all(math.isfinite(x) for x in raw) and abs(sum(x*x for x in raw[:3])-1) < .002 and raw[3] in (-1, 1):
                tangent = mesh.loops[i].tangent.copy()
                tangent -= normal*tangent.dot(normal)
                if tangent.length > 1e-8:
                    tangent.normalize()
                    result[i] = [*tangent, raw[3]]
                    continue
            positions = [mesh.vertices[mesh.loops[j].vertex_index].co for j in ids]
            e1, e2 = positions[1]-positions[0], positions[2]-positions[0]
            du1, dv1 = uv[ids[1]].uv-uv[ids[0]].uv
            du2, dv2 = uv[ids[2]].uv-uv[ids[0]].uv
            determinant = du1*dv2-du2*dv1
            require(abs(determinant) > 1e-15, "Collapsed UV triangle requires UV repair: " + str(polygon.index))
            tangent = (e1*dv2-e2*dv1)/determinant
            bitangent = (e2*du1-e1*du2)/determinant
            tangent -= normal*tangent.dot(normal)
            require(tangent.length > 1e-8, "Singular analytic tangent: " + str(i))
            tangent.normalize()
            # Extend the neighboring valid frame's orientation through the
            # singular corner; signs must never interpolate through zero.
            sign = next(iter(face_signs)) if face_signs else (-1. if normal.cross(tangent).dot(bitangent) < 0 else 1.)
            result[i] = [*tangent, sign]
            repaired.append(i)
        require(len({result[i][3] for i in ids}) == 1, "Mixed signed tangent frame within triangle")
    require(all(all(math.isfinite(x) for x in t) and abs(sum(x*x for x in t[:3])-1) < .002 and t[3] in (-1, 1) for t in result),
            "Every corner requires a finite unit signed tangent")
    require(max(abs(sum(x*y for x,y in zip(t[:3], n.vector))) for t,n in zip(result, mesh.corner_normals)) < 1e-4,
            "Every corner tangent must be orthogonal to its split normal")
    return result, repaired


def stored_tangents(mesh):
    return [[*t.vector, s.value] for t,s in zip(mesh.attributes["TransferTangent"].data, mesh.attributes["TransferBitangentSign"].data)]


def fingerprint(obj, tangent_reference=None):
    mesh = obj.data
    mesh.calc_tangents(uvmap="TransferUV")
    require(all(len(p.vertices) == 3 for p in mesh.polygons), "Prepared mesh must be triangulated")
    part = mesh.attributes["TransferPart"]
    tangents, _ = stable_tangent_basis(mesh)
    if mesh.attributes.get("TransferTangent"):
        stored = stored_tangents(mesh)
        require(all(a[3] == b[3] for a,b in zip(tangents, stored)) and max(abs(x-y) for a,b in zip(tangents,stored) for x,y in zip(a[:3],b[:3])) <= 1e-6,
                "Frozen signed tangent attributes changed")
        tangents = stored
    require(all(all(math.isfinite(x) for x in tangent) and abs(sum(x*x for x in tangent[:3])-1) < .002 and tangent[3] in (-1, 1) for tangent in tangents),
            "Every exported corner requires a finite unit signed tangent")
    if tangent_reference is not None:
        require(len(tangents) == len(tangent_reference), "Frozen tangent corner count changed")
        require(all(a[3] == b[3] for a,b in zip(tangents, tangent_reference)), "Frozen tangent handedness changed")
        error = max(abs(x-y) for a,b in zip(tangents, tangent_reference) for x,y in zip(a[:3], b[:3]))
        require(error <= 1e-6, "Frozen tangent basis changed beyond floating-point recomputation tolerance")
        obj["tangent_recompute_max_delta"] = max(error, obj.get("tangent_recompute_max_delta", 0.))
        # Canonical identity hashes the preserved snapshot, after verifying every
        # current vector. MikkTSpace SIMD reductions vary at float32 ULP scale.
        tangents = tangent_reference
    return mesh_identity(vertices=[list(v.co) for v in mesh.vertices],
                         triangles=[[*p.vertices, p.material_index, part.data[p.index].value] for p in mesh.polygons],
                         uv=[list(d.uv) for d in mesh.uv_layers["TransferUV"].data],
                         split_normals=[list(n.vector) for n in mesh.corner_normals],
                         tangents=tangents)


def shader_input_identity(obj):
    """Freeze source-chart UV/alpha/target inputs alongside the tangent mesh."""
    mesh = obj.data
    values = {"chart": [list(d.uv) for d in mesh.uv_layers["ST_SurfaceChart"].data]}
    for name in ("ST_Alpha", "ST_Target", "TransferConstructionNormal", "TransferBasisNormal", "TransferTangent", "TransferBitangentSign"):
        attr = mesh.attributes.get(name)
        if attr:
            values[name] = {"domain": attr.domain, "type": attr.data_type,
                            "values": [list(d.vector) if attr.data_type == "FLOAT_VECTOR" else d.value for d in attr.data]}
    return canonical_sha256(values)


def material_copy(bpy, original, name, normal_matrix):
    """Keep the source graph; replace object-normal transforms before merging.
    The normalized export object has identity rotation/scale. Its shader must
    still apply each source part's original inverse-transpose normal matrix.
    """
    material = original.copy()
    material.name = name
    require(material.use_nodes, "Only explicit node-based materials are supported")
    tree = material.node_tree
    construction = tree.nodes.new("ShaderNodeAttribute")
    construction.attribute_name = "TransferConstructionNormal"
    normalize = tree.nodes.new("ShaderNodeVectorMath")
    normalize.operation = "NORMALIZE"
    tree.links.new(construction.outputs["Vector"], normalize.inputs[0])
    for node in list(tree.nodes):
        if node.bl_idname == "ShaderNodeNewGeometry":
            for link in list(node.outputs["Normal"].links):
                tree.links.new(normalize.outputs[0], link.to_socket)
        if node.bl_idname == "ShaderNodeBsdfPrincipled" and not node.inputs["Normal"].is_linked:
            tree.links.new(normalize.outputs[0], node.inputs["Normal"])
    for node in list(tree.nodes):
        if node.bl_idname != "ShaderNodeVectorTransform":
            continue
        require(node.vector_type == "NORMAL" and node.convert_from == "OBJECT" and node.convert_to == "WORLD",
                "Unmapped coordinate-dependent shader transform in " + original.name)
        destinations = [link.to_socket for link in list(node.outputs[0].links)]
        combine = tree.nodes.new("ShaderNodeCombineXYZ")
        combine.label = "Frozen source inverse-transpose"
        for i in range(3):
            dot = tree.nodes.new("ShaderNodeVectorMath")
            dot.operation = "DOT_PRODUCT"
            dot.inputs[1].default_value = normal_matrix[i]
            if node.inputs[0].is_linked:
                tree.links.new(node.inputs[0].links[0].from_socket, dot.inputs[0])
            else:
                dot.inputs[0].default_value = node.inputs[0].default_value
            tree.links.new(dot.outputs["Value"], combine.inputs[i])
        for socket in destinations:
            tree.links.new(combine.outputs[0], socket)
        tree.nodes.remove(node)
    return material


def normal_emission(material):
    """Bake the source normal against the exact signed basis exported to FBX."""
    tree = material.node_tree
    principal = next(n for n in tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    output = next(n for n in tree.nodes if n.bl_idname == "ShaderNodeOutputMaterial" and n.is_active_output)
    original = output.inputs["Surface"].links[0].from_socket
    desired = principal.inputs["Normal"].links[0].from_socket
    def attribute(name, scalar=False):
        node = tree.nodes.new("ShaderNodeAttribute")
        node.attribute_name = name
        return node.outputs["Fac" if scalar else "Vector"]
    def vector(operation, a, b=None):
        node = tree.nodes.new("ShaderNodeVectorMath")
        node.operation = operation
        tree.links.new(a, node.inputs[0])
        if b is not None:
            tree.links.new(b, node.inputs[1])
        return node.outputs["Value" if operation == "DOT_PRODUCT" else "Vector"]
    # UE MaterialTemplate.ush AssembleTangentToWorld retains raw interpolated
    # T and N: the frame is deliberately not orthonormal after interpolation.
    normal = attribute("TransferBasisNormal")
    tangent = attribute("TransferTangent")
    bitangent = vector("CROSS_PRODUCT", normal, tangent)
    signed = tree.nodes.new("ShaderNodeVectorMath")
    signed.operation = "SCALE"
    tree.links.new(bitangent, signed.inputs[0])
    tree.links.new(attribute("TransferBitangentSign", True), signed.inputs[3])
    bitangent = signed.outputs[0]
    cofactors = [vector("CROSS_PRODUCT", bitangent, normal), vector("CROSS_PRODUCT", normal, tangent), vector("CROSS_PRODUCT", tangent, bitangent)]
    determinant = vector("DOT_PRODUCT", tangent, cofactors[0])
    combine = tree.nodes.new("ShaderNodeCombineXYZ")
    for i, cofactor in enumerate(cofactors):
        divide = tree.nodes.new("ShaderNodeMath")
        divide.operation = "DIVIDE"
        tree.links.new(vector("DOT_PRODUCT", desired, cofactor), divide.inputs[0])
        tree.links.new(determinant, divide.inputs[1])
        value = divide.outputs[0]
        if i == 1:
            invert = tree.nodes.new("ShaderNodeMath")
            invert.operation = "MULTIPLY"
            invert.inputs[1].default_value = -1
            tree.links.new(value, invert.inputs[0])
            value = invert.outputs[0]
        tree.links.new(value, combine.inputs[i])
    unit = vector("NORMALIZE", combine.outputs[0])
    encoded = tree.nodes.new("ShaderNodeVectorMath")
    encoded.operation = "MULTIPLY_ADD"
    tree.links.new(unit, encoded.inputs[0])
    encoded.inputs[1].default_value = (.5, .5, .5)
    encoded.inputs[2].default_value = (.5, .5, .5)
    emission = tree.nodes.new("ShaderNodeEmission")
    tree.links.new(encoded.outputs[0], emission.inputs["Color"])
    tree.links.new(emission.outputs[0], output.inputs["Surface"])
    return tree, output, original


def export_frozen_fbx(bpy, np, obj, path):
    """Write the verified basis explicitly, bypassing singular Mikk cache data.
    The project export axes (-Y,Z), unit object transform and global_scale=1
    mean FBX mesh-local normal/tangent vectors are unchanged at this writer.
    """
    from io_scene_fbx import export_fbx_bin as exporter
    require(all(abs(obj.matrix_world[i][j]-(1 if i == j else 0)) < 1e-8 for i in range(4) for j in range(4)), "FBX basis writer requires identity object transform")
    basis = np.asarray(stored_tangents(obj.data), dtype=np.float64)
    normals = np.asarray([list(n.vector) for n in obj.data.corner_normals], dtype=np.float64)
    binormals = np.cross(normals, basis[:, :3])*basis[:, 3, None]
    binormals /= np.linalg.norm(binormals, axis=1)[:, None]
    original_writer = exporter.elem_data_single_float64_array
    written = {b"Tangents": 0, b"Binormals": 0}
    def writer(element, name, data):
        if name in written:
            require(np.asarray(data).size == len(basis)*3, "FBX basis corner count changed")
            written[name] += 1
            data = (basis[:, :3] if name == b"Tangents" else binormals).reshape(-1)
        return original_writer(element, name, data)
    original_mesh = obj.data
    export_mesh = original_mesh.copy()
    for layer in list(export_mesh.uv_layers):
        if layer.name != "TransferUV":
            export_mesh.uv_layers.remove(layer)
    obj.data = export_mesh
    try:
        exporter.elem_data_single_float64_array = writer
        bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"MESH"},
                                 axis_forward="-Y", axis_up="Z", global_scale=1, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                                 use_mesh_modifiers=False, mesh_smooth_type="OFF", use_tspace=True, add_leaf_bones=False, bake_anim=False)
        require(written == {b"Tangents": 1, b"Binormals": 1}, "Expected one explicit UV0 signed tangent basis")
        from io_scene_fbx import parse_fbx
        root, _ = parse_fbx.parse(str(path))
        arrays, pending = {}, [root]
        while pending:
            element = pending.pop()
            pending.extend(element.elems)
            if element.id in written:
                require(element.id not in arrays, "Duplicate FBX tangent payload")
                arrays[element.id] = np.asarray(element.props[0], dtype=float).reshape(-1, 3)
        require(set(arrays) == set(written), "Missing written FBX tangent payload")
        errors = {"tangent": float(np.max(abs(arrays[b"Tangents"]-basis[:, :3]))),
                  "binormal": float(np.max(abs(arrays[b"Binormals"]-binormals)))}
        require(max(errors.values()) < 1e-12, "Written FBX differs from frozen tangent basis")
        return {"verified": True, "corners": len(basis), "max_component_errors": errors}
    finally:
        exporter.elem_data_single_float64_array = original_writer
        obj.data = original_mesh
        bpy.data.meshes.remove(export_mesh)


def prepare(args, bpy, np, Matrix, Vector):
    source_path = args.source_manifest.resolve()
    require(source_path.is_relative_to(ROOT), "Source manifest must be in project")
    source = json.loads(source_path.read_text())
    require(source.get("schema") == "helmet-steel-transfer-source-1", "Unsupported P1 source schema")
    source_dir = source_path.parent
    blend = contained_path(source_dir, source["source_blend"])
    recipe = contained_path(source_dir, "regions.json")
    require(source.get("normal_contract", {}).get("uv") == "ST_SurfaceChart", "Corrected texture-target source contract required")
    finalization_path = ROOT / "Saved/ArtReview/UnrealStyle" / source["revision"] / "Review/finalization.json"
    finalization = json.loads(finalization_path.read_text())
    require(finalization.get("source_sha256") == sha256_file(blend) and finalization.get("regions_sha256") == sha256_file(recipe),
            "Source must match its finalized zero-control/comparator review")
    rig = ROOT / "Saved/ArtReview/UnrealStyle/AcceptedSteelTransfer/rig_audit.json"
    identities = {}
    for relative, digest in source["sources"].items():
        path = contained_path(ROOT, relative.replace("\\", "/"))
        require(sha256_file(path) == digest, "Accepted authority changed: " + relative)
        identities[path.name] = file_reference(path, ROOT)
    require("Helmet_Clay_v005.blend" in identities and "Steel_v025.blend" in identities, "Missing accepted geometry/material authorities")
    references = dict(accepted_geometry=identities["Helmet_Clay_v005.blend"], accepted_material=identities["Steel_v025.blend"],
                      working_copy=file_reference(blend, ROOT), region_recipe=file_reference(recipe, ROOT),
                      protected_regions=file_reference(recipe, ROOT), source_rig=file_reference(rig, ROOT),
                      comparator=identities["Steel_v025.blend"], source_manifest=file_reference(source_path, ROOT),
                      source_finalization=file_reference(finalization_path, ROOT))
    for i, (name, digest) in enumerate(finalization.get("texture_hashes", {}).items()):
        texture = contained_path(source_dir, name)
        require(sha256_file(texture) == digest, "Reviewed target texture changed: " + name)
        references["target_texture_"+str(i).zfill(2)] = file_reference(texture, ROOT)
    require(not args.output.exists(), "Immutable revision directory already exists")
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    scene = bpy.context.scene
    require(scene.camera is not None, "Source review camera is missing")
    camera = scene.camera
    review = {"source_camera": {"projection": "orthographic" if camera.data.type == "ORTHO" else "perspective",
                                "matrix_world": matrix_list(camera.matrix_world),
                                "framing": camera.data.ortho_scale if camera.data.type == "ORTHO" else math.degrees(camera.data.angle_x)},
              "comparator_transform": matrix_list(Matrix.Identity(4)), "comparator_placement": "Accepted world matrices preserved; see source-rig receipt",
              "source_rig_sha256": references["source_rig"]["sha256"]}
    parts = [part for part in source["parts"] if part.get("export", True)]
    require(parts, "No included source parts")
    # Source metadata is authoritative; hidden helpers must be explicitly excluded.
    for part in parts:
        obj = bpy.data.objects.get(part["part"])
        require(obj is not None and obj.type in ("MESH", "CURVE"), "Missing included source part: " + part["part"])
        require(not obj.hide_render, "Hidden included part requires explicit export:false in source mapping: " + obj.name)
    deps = bpy.context.evaluated_depsgraph_get()
    vertices, faces, normals, chart, alphas, targets, face_slots, face_parts = [], [], [], [], [], [], [], []
    material_slots, materials, part_contract, part_points = [], [], [], {}
    has_texture_targets = False
    for part_index, part in enumerate(parts):
        obj = bpy.data.objects[part["part"]]
        evaluated = obj.evaluated_get(deps)
        mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=deps)
        mesh.calc_loop_triangles()
        world = obj.matrix_world.copy()
        require(world.determinant() > 0, "Mirrored part needs explicit winding treatment: " + obj.name)
        normal_matrix = world.to_3x3().inverted().transposed()
        # Reuse the P1 geometry receipt's exact evaluated geometry/normal identity.
        if obj.name in source.get("geometry", {}):
            raw = {"vertices": [list(v.co) for v in mesh.vertices], "triangles": [list(t.vertices) for t in mesh.loop_triangles],
                   "normals": [list(n.vector) for n in mesh.corner_normals]}
            import hashlib
            require(hashlib.sha256(json.dumps(raw).encode()).hexdigest() == source["geometry"][obj.name]["sha256"],
                    "Construction geometry/normals changed since P1: " + obj.name)
        mapping = {}
        for slot in part["slots"]:
            index = slot["index"]
            require(index < len(mesh.materials) and mesh.materials[index].name == slot["material"], "Source slot mismatch: " + obj.name)
            original = mesh.materials[index]
            principal = next((n for n in original.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
            require(principal is not None, "Missing explicit Principled material")
            require(not any(principal.inputs[key].is_linked for key in ("Base Color", "Metallic", "Roughness")),
                    "This transfer requires explicit constant steel/nonsteel parameters; linked variation needs a new material contract")
            kind = "steel" if slot["role"] == "steel" else "nonsteel"
            if kind == "steel":
                require(original.node_tree.nodes.get("ST Influence") is not None, "Missing steel influence control")
                require(not any(n.bl_idname == "ShaderNodeAttribute" and n.attribute_name == "ST_Target" for n in original.node_tree.nodes),
                        "Rejected face-target shader remains connected in steel source")
            destination = len(material_slots)
            name = ("Steel_" if kind == "steel" else "Nonsteel_") + str(destination).zfill(2)
            material_slots.append(dict(index=destination, name=name, source_material=original.name, kind=kind,
                                       base_color_linear=list(principal.inputs["Base Color"].default_value)[:3],
                                       metallic=float(principal.inputs["Metallic"].default_value), roughness=float(principal.inputs["Roughness"].default_value),
                                       selective_edge=bool(part.get("selective_edge_roughness") is not None)))
            materials.append(material_copy(bpy, original, name, normal_matrix))
            mapping[index] = destination
            has_texture_targets |= any(n.bl_idname == "ShaderNodeTexImage" and n.image for n in original.node_tree.nodes)
        require(set(p.material_index for p in mesh.polygons).issubset(mapping), "Unmapped evaluated slot")
        part_contract.append(dict(source_object=obj.name, slot_indices=sorted(mapping.values()), source_to_assembly=matrix_list(world)))
        points = [list(world @ v.co) for v in mesh.vertices]
        part_points[obj.name] = points
        offset = len(vertices)
        vertices.extend(points)
        alpha = mesh.attributes.get("ST_Alpha")
        target = mesh.attributes.get("ST_Target")
        surface = mesh.uv_layers.get("ST_SurfaceChart")
        if part.get("normal_region_active"):
            require(alpha is not None and alpha.domain == "POINT" and alpha.data_type == "FLOAT", "Source ST_Alpha contract changed")
            require(surface is not None, "Texture target source must retain ST_SurfaceChart")
        for tri in mesh.loop_triangles:
            faces.append([offset+i for i in tri.vertices])
            face_slots.append(mapping[mesh.polygons[tri.polygon_index].material_index])
            face_parts.append(part_index)
            for loop_index in tri.loops:
                normals.append(list((normal_matrix @ mesh.corner_normals[loop_index].vector).normalized()))
                chart.append(list(surface.data[loop_index].uv) if surface else [0., 0.])
                vertex_index = mesh.loops[loop_index].vertex_index
                alphas.append(alpha.data[vertex_index].value if alpha else 0.)
            # ST_Target remains diagnostic only for texture-target source revisions.
            targets.append(list(target.data[tri.polygon_index].vector) if target and target.domain == "FACE" else [0., 0., 1.])
        bpy.data.meshes.remove(mesh)
    require(has_texture_targets, "P3 requires corrected texture-target source; FACE target source was rejected")
    coords = np.asarray(vertices, dtype=float)
    lo, hi = coords.min(0), coords.max(0)
    origin = np.array([(lo[0]+hi[0])/2, (lo[1]+hi[1])/2, lo[2]])
    scale = 35. / (hi[2]-lo[2])
    normalized = (coords-origin)*scale
    transform = Matrix.Diagonal((scale, scale, scale, 1.))
    transform.translation = Vector(-origin*scale)
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    mesh = bpy.data.meshes.new("FrozenTransferMesh")
    mesh.from_pydata(normalized.tolist(), [], faces)
    mesh.update()
    obj = bpy.data.objects.new("SM_Helmet_StyleProof"+args.revision[-3:], mesh)
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for material in materials:
        mesh.materials.append(material)
    for p, slot in zip(mesh.polygons, face_slots):
        p.material_index = slot
        p.use_smooth = True
    mesh.normals_split_custom_set(normals)
    source_normals = np.asarray(normals)
    frozen_normals = np.asarray([list(n.vector) for n in mesh.corner_normals])
    normal_error = float(np.max(np.degrees(np.arccos(np.clip(np.sum(source_normals*frozen_normals, axis=1) /
                                (np.linalg.norm(source_normals, axis=1)*np.linalg.norm(frozen_normals, axis=1)), -1, 1)))))
    # Blender's compact custom-normal storage can quantize acute corner spaces.
    # The exact Ns is kept below and N0 bakes its correction against this basis.
    require(normal_error < .25, "Unexpected split-normal storage deviation; max degrees="+str(normal_error))
    attr = mesh.attributes.new("TransferConstructionNormal", "FLOAT_VECTOR", "CORNER")
    for data, value in zip(attr.data, normals):
        data.vector = value
    attr = mesh.attributes.new("TransferPart", "INT", "FACE")
    for data, part_index in zip(attr.data, face_parts):
        data.value = part_index
    # Point alpha is converted to corners without changing its interpolation.
    attr = mesh.attributes.new("ST_Alpha", "FLOAT", "CORNER")
    for data, value in zip(attr.data, alphas):
        data.value = value
    attr = mesh.attributes.new("ST_Target", "FLOAT_VECTOR", "FACE")
    for data, value in zip(attr.data, targets):
        data.vector = value
    # Unreal's default TextureCoordinate reads UV0; the bake atlas must be first.
    transfer = mesh.uv_layers.new(name="TransferUV")
    surface = mesh.uv_layers.new(name="ST_SurfaceChart")
    for data, value in zip(surface.data, chart):
        data.uv = value
    mesh.uv_layers.active = transfer
    transfer.active_render = True
    # Disconnected source plates have distinct vertices; islands cannot cross plates.
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(55), island_margin=.012, area_weight=.3)
    bpy.ops.object.mode_set(mode="OBJECT")
    # UV preparation may update normals in edit mode; restore source split normals.
    mesh.normals_split_custom_set(normals)
    basis, repaired_corners = stable_tangent_basis(mesh)
    for name, values in (("TransferTangent", [v[:3] for v in basis]),
                         ("TransferBasisNormal", [list(n.vector) for n in mesh.corner_normals])):
        attr = mesh.attributes.new(name, "FLOAT_VECTOR", "CORNER")
        for data, value in zip(attr.data, values):
            data.vector = value
    attr = mesh.attributes.new("TransferBitangentSign", "FLOAT", "CORNER")
    for data, value in zip(attr.data, basis):
        data.value = value[3]
    landmarks = {}
    require("landmarks_world" in source, "Source must declare front/ridge/slit anchors before preparation")
    # Source anchors describe construction features (including empty aperture
    # centers). Record the nearest actual evaluated vertex for engine matching.
    for name, source_key in (("front", "front_brow_aperture_edge"), ("ridge", "crown_ridge"), ("slit", "slit_center")):
        anchor = np.asarray(source["landmarks_world"][source_key], dtype=float)
        nearest = []
        for part_name, points in part_points.items():
            distances = np.linalg.norm(np.asarray(points)-anchor, axis=1)
            index = int(np.argmin(distances))
            nearest.append((float(distances[index]), part_name, index, points[index]))
        distance, part_name, index, point = min(nearest)
        normalized_point = (np.asarray(point)-origin)*scale
        landmarks[name] = dict(part=part_name, source_position=point, blender_cm=normalized_point.tolist(),
                               unreal_cm=(normalized_point*np.array([1, -1, 1])).tolist(), evaluated_part_vertex=index,
                               source_anchor_key=source_key, source_anchor_world=anchor.tolist(), anchor_distance_source_units=distance)
    assembly = dict(parts=part_contract, mesh_node=obj.name, origin="combined_bottom_center", height_cm=35,
                    bounds_blender_cm=[normalized.min(0).tolist(), normalized.max(0).tolist()], source_to_export=matrix_list(transform),
                    axis={"blender_forward": "-Y", "blender_up": "Z", "unreal_mapping": ["x", "-y", "z"]}, landmarks=landmarks)
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = .01
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 1
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 6
    identity, shader_identity = fingerprint(obj), shader_input_identity(obj)
    check_references(references)
    args.output.mkdir(parents=True)
    prepared = args.output / "Helmet_Prepared.blend"
    bpy.ops.file.pack_all()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(prepared))
    # Tangent caches are derived data, not stable serialized .blend payload.
    # Freeze from the exact reopen path the bake step will consume.
    bpy.ops.wm.open_mainfile(filepath=str(prepared))
    obj = bpy.data.objects[assembly["mesh_node"]]
    mesh = obj.data
    reopened_identity = fingerprint(obj)
    require(all(identity[key] == reopened_identity[key] for key in ("geometry", "triangles", "uv", "split_normals")),
            "Saved preparation changed mesh/UV/construction basis")
    require(shader_identity == shader_input_identity(obj), "Saved preparation changed source shader inputs")
    identity = reopened_identity
    tangent_path = args.output / "FrozenTangents.json.gz"
    with gzip.open(tangent_path, "wt", encoding="utf-8") as stream:
        json.dump(stored_tangents(mesh), stream, separators=(",", ":"))
    receipt = dict(schema_version=2, revision=args.revision, sources=references, material_slots=material_slots,
                   assembly=assembly, review=review, prepared_identity=identity, shader_input_identity=shader_identity,
                   prepared_blend=file_reference(prepared, args.output), resolution=args.resolution, padding_pixels=8,
                   frozen_tangents=file_reference(tangent_path, args.output),
                   uv_method="Once-only 55-degree islands on disconnected evaluated plates; frozen before bake",
                   generator=file_reference(Path(__file__), ROOT), triangles=len(mesh.polygons), vertices=len(mesh.vertices))
    receipt["construction_normal_max_deviation_deg"] = normal_error
    receipt["tangent_repair"] = {"corners": repaired_corners, "count": len(repaired_corners),
                                 "method": "Analytic triangle UV derivative projected into unchanged split-normal plane only where Mikk tangent was singular; geometry and UV unchanged"}
    dump(args.output / "preparation.json", receipt)
    print("TRANSFER_PREPARED", args.output, flush=True)


def bake(args, bpy, np, Image):
    out = args.output
    require(not (out / "manifest.json").exists(), "Immutable manifest already exists")
    preparation = out / "preparation.json"
    receipt = json.loads(preparation.read_text())
    require(receipt["schema_version"] == 2 and receipt["revision"] == args.revision, "Preparation revision/schema mismatch")
    check_references(receipt["sources"])
    check_references({"generator": receipt["generator"]})
    prepared = contained_path(out, receipt["prepared_blend"]["path"])
    require(sha256_file(prepared) == receipt["prepared_blend"]["sha256"], "Frozen prepared blend changed")
    bpy.ops.wm.open_mainfile(filepath=str(prepared))
    scene = bpy.context.scene
    obj = bpy.data.objects[receipt["assembly"]["mesh_node"]]
    tangent_path = contained_path(out, receipt["frozen_tangents"]["path"])
    require(sha256_file(tangent_path) == receipt["frozen_tangents"]["sha256"], "Frozen tangent snapshot changed")
    with gzip.open(tangent_path, "rt", encoding="utf-8") as stream:
        tangent_reference = json.load(stream)
    require_frozen_identity(receipt["prepared_identity"], fingerprint(obj, tangent_reference))
    require(shader_input_identity(obj) == receipt["shader_input_identity"], "Source chart/alpha identity changed")
    output_names = {"normal_base": "T_Helmet_NormalBaseDX.png", "normal_final": "T_Helmet_NormalFinalDX.png", "masks": "T_Helmet_Masks.png", "fbx": obj.name+".fbx", "render_contract": "render_contract.json.gz"}
    require(not any((out / name).exists() for name in output_names.values()), "Partial bake output exists; preserve it and use a new revision")
    for item in scene.objects:
        item.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    materials = list(obj.data.materials)
    controls = [material.node_tree.nodes.get("ST Influence") for material in materials]
    require(any(controls), "Authored source control missing")
    size, padding = receipt["resolution"], receipt["padding_pixels"]
    target = bpy.data.images.new("TransferBakeTarget", width=size, height=size, alpha=False, float_buffer=True)
    target.colorspace_settings.name = "Non-Color"
    target_nodes = []
    for material in materials:
        node = material.node_tree.nodes.new("ShaderNodeTexImage")
        node.image = target
        material.node_tree.nodes.active = node
        target_nodes.append(node)
    validations, normal_pixels = {}, {}
    def save_map(role, bake_type, margin=padding):
        bpy.ops.object.bake(type=bake_type, normal_space="TANGENT", normal_r="POS_X", normal_g="NEG_Y", normal_b="POS_Z",
                            margin=margin, use_clear=True, use_selected_to_active=False)
        pixels = np.empty(size*size*4, dtype=np.float32)
        target.pixels.foreach_get(pixels)
        rgb = pixels.reshape(size, size, 4)[:, :, :3]
        require(np.isfinite(rgb).all(), "Nonfinite baked pixels")
        if role.startswith("normal"):
            normal_pixels[role] = rgb.copy()
        if role == "occupancy":
            return rgb.copy()
        Image.fromarray(np.rint(np.clip(rgb[::-1], 0, 1)*255).astype("uint8"), "RGB").save(out / output_names[role])
    normal_restoration = [normal_emission(material) for material in materials]
    for role, influence in (("normal_base", 0.), ("normal_final", 1.)):
        for control in controls:
            if control:
                control.outputs[0].default_value = influence
        save_map(role, "EMIT")
    for tree, output, socket in normal_restoration:
        tree.links.new(socket, output.inputs["Surface"])
    # Encode the actual source roughness and once-applied influence for diagnostics.
    restoration, emission_links = [], []
    for material, slot in zip(materials, receipt["material_slots"]):
        tree = material.node_tree
        output = next(n for n in tree.nodes if n.bl_idname == "ShaderNodeOutputMaterial" and n.is_active_output)
        principal = next(n for n in tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
        restoration.append((tree, output, output.inputs["Surface"].links[0].from_socket))
        emission = tree.nodes.new("ShaderNodeEmission")
        combine = tree.nodes.new("ShaderNodeCombineXYZ")
        if principal.inputs["Roughness"].is_linked:
            tree.links.new(principal.inputs["Roughness"].links[0].from_socket, combine.inputs[0])
        else:
            combine.inputs[0].default_value = principal.inputs["Roughness"].default_value
        combine.inputs[1].default_value = float(slot["selective_edge"])
        if slot["kind"] == "steel":
            attribute = tree.nodes.new("ShaderNodeAttribute")
            attribute.attribute_name = "ST_Alpha"
            multiply = tree.nodes.new("ShaderNodeMath")
            multiply.operation = "MULTIPLY"
            multiply.inputs[1].default_value = .4
            tree.links.new(attribute.outputs["Fac"], multiply.inputs[0])
            tree.links.new(multiply.outputs[0], combine.inputs[2])
        tree.links.new(combine.outputs[0], emission.inputs["Color"])
        tree.links.new(emission.outputs[0], output.inputs["Surface"])
        emission_links.append((tree, combine.outputs[0], emission.inputs["Color"]))
    # Dedicated white emission with zero dilation is unambiguous UV coverage.
    for tree, socket, color in emission_links:
        tree.links.remove(color.links[0])
        color.default_value = (1., 1., 1., 1.)
    occupancy = save_map("occupancy", "EMIT", margin=0)
    occupied = np.min(occupancy, axis=2) > .99
    require(occupied.any(), "Empty UV occupancy bake")
    for role, rgb in normal_pixels.items():
        lengths = np.linalg.norm(rgb[occupied]*2-1, axis=1)
        error = float(np.max(abs(lengths-1)))
        require(error < .02, "Nonunit normal on actual UV coverage: " + role)
        validations[role] = dict(unit_normal_max_error=error, occupied_pixels=int(occupied.sum()))
    validations["coverage"] = dict(method="Dedicated white emission, black clear background, margin=0", occupied_pixels=int(occupied.sum()),
                                   fraction=float(occupied.mean()), normal_and_mask_padding_pixels=padding)
    for tree, socket, color in emission_links:
        tree.links.new(socket, color)
    save_map("masks", "EMIT")
    for tree, output, socket in restoration:
        tree.links.new(socket, output.inputs["Surface"])
    baked_identity = fingerprint(obj, tangent_reference)
    require_frozen_identity(receipt["prepared_identity"], baked_identity)
    fbx_basis_validation = export_frozen_fbx(bpy, np, obj, out / output_names["fbx"])
    exported_identity = fingerprint(obj, tangent_reference)
    require_frozen_identity(receipt["prepared_identity"], exported_identity)
    mesh = obj.data
    uv = mesh.uv_layers["TransferUV"].data
    stable_basis = stored_tangents(mesh)
    triangles = []
    for polygon in mesh.polygons:
        corners = []
        for i in polygon.loop_indices:
            loop = mesh.loops[i]
            position = mesh.vertices[loop.vertex_index].co
            normal = mesh.corner_normals[i].vector
            tangent = stable_basis[i]
            corners.append([position.x, -position.y, position.z, uv[i].uv.x, 1-uv[i].uv.y,
                            normal.x, -normal.y, normal.z, tangent[0], -tangent[1], tangent[2], tangent[3]])
        triangles.append(dict(slot=polygon.material_index, corners=corners))
    with gzip.open(out / output_names["render_contract"], "wt", encoding="utf-8") as stream:
        json.dump({"schema_version": 1, "space": "Unreal cm; UV0=(u,1-v); normals/tangents=(x,-y,z); sign preserved",
                   "triangles": triangles}, stream, separators=(",", ":"), allow_nan=False)
    check_references(receipt["sources"])
    files = {key: file_reference(out / name, out) for key, name in output_names.items()}
    files.update(source_blend=receipt["prepared_blend"], preparation=file_reference(preparation, out), frozen_tangents=receipt["frozen_tangents"])
    manifest = {key: copy.deepcopy(receipt[key]) for key in ("schema_version", "revision", "sources", "assembly", "material_slots", "review")}
    manifest["files"] = files
    manifest["bake"] = dict(normal_representation="base_and_final", runtime=NORMAL_RUNTIME, final_contains_influence=True,
                             runtime_influence_multiplier=False, normal_space="DirectX_tangent",
                             recipe_sha256=receipt["sources"]["region_recipe"]["sha256"],
                             identities=dict(prepared=receipt["prepared_identity"], baked=baked_identity, exported=exported_identity),
                             shader_input_identity=receipt["shader_input_identity"],
                             textures={key: dict(resolution=[size, size], srgb=False, flip_green_channel=False,
                                                 compression="TC_MASKS" if key == "masks" else "TC_NORMALMAP") for key in ("normal_base", "normal_final", "masks")},
                             masks=dict(channels={"R": "roughness", "G": "selective_edge", "B": "authored_influence_diagnostic"},
                                        padding_pixels=padding, protected_regions_sha256=receipt["sources"]["protected_regions"]["sha256"]))
    manifest["validation"] = dict(normal_maps=validations, triangles=receipt["triangles"], vertices=receipt["vertices"],
                                  frozen_identity_matches=True, source_recipe="Copied material graph, per-part inverse-transpose transforms, explicit original surface-chart UV",
                                  construction_normal_max_deviation_deg=receipt["construction_normal_max_deviation_deg"],
                                  tangent_recompute_max_component_delta=obj.get("tangent_recompute_max_delta", 0.), tangent_recompute_component_tolerance=1e-6,
                                  tangent_repair=receipt["tangent_repair"], all_corner_signed_bases_verified=True,
                                  fbx_basis_payload=fbx_basis_validation,
                                  exported_identity_scope="Frozen mesh supplied to FBX; complete render_contract triangle correspondence must pass in Unreal before transfer acceptance",
                                  engine_seams_handedness_and_zero_control="Pending actual Unreal validation")
    validate_manifest(manifest, out, ROOT, expected_revision=args.revision)
    dump(out / "validation.json", manifest["validation"])
    manifest["files"]["validation"] = file_reference(out / "validation.json", out)
    dump(out / "manifest.json", manifest)
    print("TRANSFER_BAKED", out, flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--bake", action="store_true")
    parser.add_argument("--revision", required=True)
    parser.add_argument("--source-manifest", type=Path)
    parser.add_argument("--resolution", type=int, default=2048)
    args = parser.parse_args(argv)
    require(re.fullmatch(r"USP_v[0-9]{3}", args.revision), "Revision must match USP_vNNN")
    require(args.resolution == 2048, "This proof starts with fixed 2K maps")
    require(not args.prepare or args.source_manifest is not None, "Preparation requires an explicit source manifest")
    args.output = ROOT / "ArtSource/StyleReference/MEL17/UnrealProof" / args.revision
    import bpy
    import numpy as np
    from mathutils import Matrix, Vector
    from PIL import Image
    if args.prepare:
        prepare(args, bpy, np, Matrix, Vector)
    else:
        bake(args, bpy, np, Image)


if __name__ == "__main__":
    main()
