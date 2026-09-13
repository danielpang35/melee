"""Read a UE static-mesh render-buffer FBX into the transfer corner contract.

UE export must use export_source_mesh=False, level_of_detail=False,
collision=False and force_front_x_axis=False. This reads mesh-local buffers;
it does not evaluate arbitrary FBX scenes or apply node transforms.
"""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def one(parent, name, required=True):
    matches = [child for child in parent.elems if child.id == name]
    require(len(matches) <= 1, "Ambiguous FBX element: " + name.decode())
    require(matches or not required, "Missing FBX element: " + name.decode())
    return matches[0] if matches else None


def prop(parent, name):
    element = one(parent, name)
    require(len(element.props) == 1, "Malformed FBX property: " + name.decode())
    return element.props[0]


def layer_zero(geometry, name):
    matches = [child for child in geometry.elems if child.id == name and child.props and child.props[0] == 0]
    require(len(matches) == 1, "Missing/ambiguous UV0 FBX layer: " + name.decode())
    return matches[0]


def vector_reader(layer, values_name, width):
    mapping = prop(layer, b"MappingInformationType")
    reference = prop(layer, b"ReferenceInformationType")
    require(mapping in (b"ByPolygonVertex", b"ByVertice", b"ByVertex", b"ByControlPoint", b"ByPolygon", b"AllSame"), "Unsupported FBX layer mapping")
    require(reference in (b"Direct", b"IndexToDirect", b"Index"), "Unsupported FBX layer reference")
    values = prop(layer, values_name)
    require(len(values) % width == 0, "Malformed FBX vector array: " + values_name.decode())
    indices = prop(layer, values_name+b"Index") if reference != b"Direct" else None
    def read(corner_index, vertex_index, polygon_index):
        index = (corner_index if mapping == b"ByPolygonVertex" else polygon_index if mapping == b"ByPolygon" else
                 0 if mapping == b"AllSame" else vertex_index)
        if indices is not None:
            require(0 <= index < len(indices), "FBX attribute index array is incomplete")
            index = indices[index]
        require(isinstance(index, int) and 0 <= index < len(values)//width, "FBX attribute index outside direct array")
        result = [float(x) for x in values[index*width:(index+1)*width]]
        require(all(math.isfinite(x) for x in result), "Nonfinite FBX attribute")
        return result
    return read


def read_render_fbx(path, *, structural_fixture=False):
    # bpy registers bundled addon paths; no Blender scene is loaded or modified.
    sys.path[:0] = [str(ROOT / "Saved/ArtRuntime")]
    import bpy  # noqa: F401
    from io_scene_fbx import parse_fbx
    root, version = parse_fbx.parse(str(path))
    objects = one(root, b"Objects")
    geometries = [node for node in objects.elems if node.id == b"Geometry" and len(node.props) >= 3 and node.props[2] == b"Mesh"]
    require(len(geometries) == 1, "Expected exactly one static-mesh geometry; disable LOD/collision export")
    geometry = geometries[0]
    vertices = prop(geometry, b"Vertices")
    require(len(vertices) % 3 == 0, "Malformed position array")
    polygon_indices = prop(geometry, b"PolygonVertexIndex")
    positions = [[float(x) for x in vertices[i:i+3]] for i in range(0, len(vertices), 3)]
    require(all(math.isfinite(x) for row in positions for x in row), "Nonfinite FBX positions")
    readers = {name: vector_reader(layer_zero(geometry, layer), name, width) for name,layer,width in
               ((b"Normals",b"LayerElementNormal",3), (b"Tangents",b"LayerElementTangent",3),
                (b"Binormals",b"LayerElementBinormal",3), (b"UV",b"LayerElementUV",2))}
    material_layer = layer_zero(geometry, b"LayerElementMaterial")
    material_mapping = prop(material_layer, b"MappingInformationType")
    require(material_mapping in (b"ByPolygon", b"AllSame"), "Unsupported material-slot mapping")
    require(prop(material_layer,b"ReferenceInformationType") in (b"IndexToDirect",b"Direct",b"Index"), "Unsupported material reference")
    # In FBX material layers, Materials already contains node material indices.
    slots = prop(material_layer,b"Materials")
    connections = [c.props for c in one(root,b"Connections").elems if c.id == b"C" and len(c.props) >= 3 and c.props[0] == b"OO"]
    models = [c[2] for c in connections if c[1] == geometry.props[0]]
    require(len(models) == 1, "Mesh must have exactly one model instance")
    material_objects = {o.props[0]: o for o in objects.elems if o.id == b"Material"}
    materials = [material_objects[c[1]] for c in connections if c[2] == models[0] and c[1] in material_objects]
    require(materials, "Missing FBX model material-slot connections")
    names = [m.props[1].split(b"\x00",1)[0].decode("utf-8",errors="strict") for m in materials]
    triangles, corners = [], []
    for corner_index, encoded_index in enumerate(polygon_indices):
        vertex_index = -encoded_index-1 if encoded_index < 0 else encoded_index
        require(0 <= vertex_index < len(positions), "Position index outside FBX control points")
        polygon_index = len(triangles)
        values = {name: read(corner_index,vertex_index,polygon_index) for name,read in readers.items()}
        p = positions[vertex_index]
        n, t, b = values[b"Normals"], values[b"Tangents"], values[b"Binormals"]
        # FbxMainExport.cpp render path exports P/N/T=(x,-y,z), B=(-x,y,-z).
        p, n, t, b = [p[0],-p[1],p[2]], [n[0],-n[1],n[2]], [t[0],-t[1],t[2]], [-b[0],b[1],-b[2]]
        cross = [n[1]*t[2]-n[2]*t[1], n[2]*t[0]-n[0]*t[2], n[0]*t[1]-n[1]*t[0]]
        determinant = sum(x*y for x,y in zip(cross,b))
        require(math.isfinite(determinant) and abs(determinant) > .5, "Missing/degenerate signed tangent basis")
        sign = -1. if determinant < 0 else 1.
        uv = values[b"UV"]
        corners.append([*p, uv[0], 1-uv[1], *n, *t, sign])
        require(len(corners) <= 3, "Nontriangulated FBX polygon")
        if encoded_index < 0:
            require(len(corners) == 3, "Nontriangulated FBX polygon")
            slot_index = polygon_index if material_mapping == b"ByPolygon" else 0
            require(slot_index < len(slots), "Missing polygon material slot")
            slot = slots[slot_index]
            require(isinstance(slot,int) and 0 <= slot < len(materials), "Material index outside FBX exported slot order")
            triangles.append({"slot":slot, "corners":corners})
            corners = []
    require(not corners and triangles, "Incomplete or empty FBX polygon stream")
    return {"schema_version":1, "triangles":triangles, "material_slot_names":names,
            "evidence_kind":"structural_source_fixture_not_unreal_evidence" if structural_fixture else "declared_unreal_render_buffer_export",
            "source_fbx":str(path.resolve()), "source_fbx_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "fbx_version":version, "mapping":"Inverse UE render exporter: P/N/T=(x,-y,z), B=(-x,y,-z), UV=(u,1-v); sign from cross(N,T) dot B"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fbx", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--structural-fixture", action="store_true", help="Explicitly label source-FBX smoke test as non-Unreal evidence")
    args = parser.parse_args()
    require(args.fbx.is_file(), "FBX file does not exist")
    require(not args.output.exists(), "Preserve existing corner evidence; choose a new output path")
    result = read_render_fbx(args.fbx, structural_fixture=args.structural_fixture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(args.output,"wt",encoding="utf-8") as stream:
        json.dump(result,stream,separators=(",",":"),allow_nan=False)
    print(json.dumps({"output":str(args.output.resolve()), "triangles":len(result["triangles"]),
                      "slots":len(result["material_slot_names"]), "evidence_kind":result["evidence_kind"]}))


if __name__ == "__main__":
    main()
