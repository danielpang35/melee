"""Read-only P3/P4 transfer preflight; standard library, usable outside Blender/UE.

Schema 2 is documented by the executable fixture in
Tests/UnrealStyleTransferContractTests.py. Package file paths are relative to the
manifest directory; source identities are relative to project_root. Both are
contained, hash-verified files. Runtime receipts must record manifest_sha256.
Unversioned current-exporter manifests require explicit allow_legacy=True;
they retain their historical flat-to-final normal meaning, never schema 2.
"""
from dataclasses import dataclass
import hashlib
import json
import math
import itertools
from pathlib import Path, PurePosixPath
import re

SCHEMA_VERSION = 2
NORMAL_RUNTIME = "normalize(lerp(N0,N1,Blend))"
IDENTITY_KEYS = ("geometry", "triangles", "uv", "split_normals", "tangents")
SOURCE_KEYS = ("accepted_geometry", "accepted_material", "working_copy",
               "region_recipe", "protected_regions", "source_rig", "comparator")
FILE_KEYS = ("source_blend", "fbx", "normal_base", "normal_final", "masks", "render_contract")


class ContractError(ValueError):
    """The package must not be imported or baked."""


@dataclass(frozen=True)
class TransferPackage:
    manifest: dict
    manifest_sha256: str
    schema_version: int
    files: dict
    sources: dict


def _require(condition, message):
    if not condition:
        raise ContractError(message)


def _fields(value, keys, label):
    _require(isinstance(value, dict), label + " must be an object")
    _require(all(k in value for k in keys), label + " requires " + ", ".join(keys))
    return value


def _number(value, label, lower=None, upper=None):
    _require(type(value) in (int, float) and math.isfinite(value), label + " must be finite")
    _require(lower is None or value >= lower, label + " is below range")
    _require(upper is None or value <= upper, label + " is above range")
    return value


def _vector(value, n, label):
    _require(isinstance(value, list) and len(value) == n, label + " has wrong size")
    return [_number(v, label) for v in value]


def _matrix(value, label):
    _require(isinstance(value, list) and len(value) == 4, label + " requires 4x4 matrix")
    for row in value:
        _vector(row, 4, label)
    _require(value[3] == [0, 0, 0, 1], label + " must be affine")
    a, b, c = [row[:3] for row in value[:3]]
    det = a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
    _require(abs(det) > 1e-12, label + " must be invertible")


def _digest(value, label):
    _require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value), label + " requires lowercase SHA-256")


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def contained_path(root, relative):
    """Reject traversal, absolute/drive/UNC/ADS paths and escaping symlinks."""
    _require(isinstance(relative, str) and relative, "file path must be nonempty")
    _require(not any(c in relative for c in ("\\", ":", "\x00")), "file path must use relative POSIX syntax")
    pure = PurePosixPath(relative)
    _require(not pure.is_absolute() and all(p not in ("", ".", "..") for p in relative.split("/")), "file path must be contained and normalized")
    _require(all(p == p.rstrip(" .") for p in pure.parts), "ambiguous Windows path component")
    root = Path(root).resolve()
    path = (root / relative).resolve()
    _require(path.is_relative_to(root), "file path escapes root")
    _require(path.is_file(), "file missing: " + relative)
    return path


def file_reference(path, root):
    path, root = Path(path).resolve(), Path(root).resolve()
    _require(path.is_relative_to(root), "reference is outside root")
    relative = path.relative_to(root).as_posix()
    contained_path(root, relative)
    return {"path": relative, "sha256": sha256_file(path)}


def _references(entries, keys, root, label):
    _fields(entries, keys, label)
    result = {}
    for name, ref in entries.items():
        _fields(ref, ("path", "sha256"), label + "." + name)
        _digest(ref["sha256"], name)
        path = contained_path(root, ref["path"])
        _require(sha256_file(path) == ref["sha256"], "hash mismatch: " + name)
        result[name] = path
    return result


def canonical_sha256(value):
    """Stable JSON identity; caller supplies ordered mesh data, never sets."""
    try:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ContractError("identity contains unsupported/nonfinite values") from error
    return hashlib.sha256(payload).hexdigest()


def inverse_interpolated_frame(desired, tangent, normal, sign):
    """Reference math for UE's raw interpolated T/cross(N,T)*sign/N frame.
    Returns unencoded source tangent coordinates; DirectX encoding negates Y.
    """
    def cross(a,b):
        return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
    def dot(a,b):
        return sum(x*y for x,y in zip(a,b))
    for value in (desired, tangent, normal):
        _vector(value, 3, "interpolated frame vector")
    _number(sign, "interpolated tangent sign")
    bitangent = [x*sign for x in cross(normal, tangent)]
    cofactors = [cross(bitangent,normal), cross(normal,tangent), cross(tangent,bitangent)]
    determinant = dot(tangent,cofactors[0])
    _require(abs(determinant) > 1e-12, "singular interpolated tangent frame")
    return [dot(desired,c)/determinant for c in cofactors]


def mesh_identity(*, vertices, triangles, uv, split_normals, tangents):
    """Ordered coordinates; vertex-index triangles; per-loop UV/normals;
    per-loop tangent XYZ plus bitangent sign. Include every exported slot and
    part assignment in triangles (e.g. [v0,v1,v2,slot_index,part_id]).
    Caller must calculate tangents on the final triangulated UV mesh.
    """
    values = dict(geometry=vertices, triangles=triangles, uv=uv,
                  split_normals=split_normals, tangents=tangents)
    return {key: canonical_sha256(value) for key, value in values.items()}


def require_frozen_identity(prepared, current):
    for name, identity in (("prepared", prepared), ("current", current)):
        _fields(identity, IDENTITY_KEYS, name)
        for key in IDENTITY_KEYS:
            _digest(identity[key], name + "." + key)
    _require(all(prepared[k] == current[k] for k in IDENTITY_KEYS), "frozen geometry/triangle/UV/normal/tangent identity changed")


def verify_imported_triangles(expected, actual):
    """Compare all rendered triangle corners despite FBX vertex reindexing.

    expected={schema_version:1,triangles:[{slot:int,corners:[12 floats]*3}]}.
    actual is its triangles list. Corner: position cm XYZ, UV0 XY, normal XYZ,
    tangent XYZ, sign (-1 for UE ProcMeshTangent.flip_tangent_y else +1).
    Triangle corner order is ignored; complete triangle multiplicity is checked.
    """
    _fields(expected, ("schema_version", "triangles"), "render contract")
    _require(type(expected["schema_version"]) is int and expected["schema_version"] == 1, "unknown render contract")
    wanted = expected["triangles"]
    _require(isinstance(wanted, list) and wanted and isinstance(actual, list) and len(wanted) == len(actual), "render triangle count mismatch")
    def validate(triangle):
        _fields(triangle, ("slot", "corners"), "render triangle")
        _require(type(triangle["slot"]) is int and triangle["slot"] >= 0, "invalid render slot")
        _require(isinstance(triangle["corners"], list) and len(triangle["corners"]) == 3, "render triangle needs three corners")
        for corner in triangle["corners"]:
            _vector(corner, 12, "render corner")
            _require(corner[11] in (-1, 1), "invalid tangent sign")
            for start in (5, 8):
                _require(abs(sum(x*x for x in corner[start:start+3])-1) < .002, "nonunit render basis")
            _require(abs(sum(x*y for x,y in zip(corner[5:8],corner[8:11]))) < .001, "nonorthogonal render basis")
    def bucket(triangle):
        return tuple(math.floor(sum(c[i] for c in triangle["corners"])/3/.01) for i in range(3))
    buckets = {}
    for index, triangle in enumerate(wanted):
        validate(triangle)
        buckets.setdefault((triangle["slot"], *bucket(triangle)), set()).add(index)
    cosine_limit = math.cos(math.radians(.15))
    maxima = {"position_cm": 0., "uv": 0., "normal_deg": 0., "tangent_deg": 0.}
    offsets = list(itertools.product((-1, 0, 1), repeat=3))
    def comparison(a, b):
        position = math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))
        uv = max(abs(a[i]-b[i]) for i in (3, 4))
        if position > .001 or uv > 2e-5 or a[11] != b[11]:
            return None
        angles = []
        for start in (5, 8):
            av, bv = a[start:start+3], b[start:start+3]
            dot = sum(x*y for x,y in zip(av,bv))/math.sqrt(sum(x*x for x in av)*sum(x*x for x in bv))
            if dot < cosine_limit:
                return None
            angles.append(math.degrees(math.acos(max(-1, min(1, dot)))))
        return (position, uv, *angles)
    for index, triangle in enumerate(actual):
        validate(triangle)
        cell = bucket(triangle)
        candidates = set()
        for offset in offsets:
            candidates.update(buckets.get((triangle["slot"], *(cell[i]+offset[i] for i in range(3))), ()))
        found = None
        for candidate in candidates:
            for corners in itertools.permutations(wanted[candidate]["corners"]):
                errors = [comparison(a,b) for a,b in zip(triangle["corners"], corners)]
                if all(e is not None for e in errors):
                    found = candidate
                    for error in errors:
                        for key, value in zip(maxima, error):
                            maxima[key] = max(maxima[key], value)
                    break
            if found is not None:
                break
        _require(found is not None, "Imported triangle/basis mismatch at triangle " + str(index) + " slot " + str(triangle["slot"]))
        matched = wanted[found]
        buckets[(matched["slot"], *bucket(matched))].remove(found)
    return {"verified": True, "triangles": len(actual), "corners": 3*len(actual), "max_errors": maxima,
            "tolerances": {"position_cm": .001, "uv": 2e-5, "normal_tangent_deg": .15},
            "scope": "Complete unordered triangle-corner multiset with material slots and signed tangent bases; visual winding/handedness gate remains required"}


def _slots(slots):
    _require(isinstance(slots, list) and slots, "material_slots must be nonempty")
    names = set()
    for i, slot in enumerate(slots):
        _fields(slot, ("index", "name", "source_material", "kind", "base_color_linear", "metallic", "roughness"), "slot")
        _require(type(slot["index"]) is int and slot["index"] == i, "slots must have contiguous ordered indices")
        _require(isinstance(slot["name"], str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", slot["name"]) and slot["name"] not in names, "slot names must be unique import-safe identifiers")
        names.add(slot["name"])
        _require(isinstance(slot["source_material"], str) and slot["source_material"], "source material missing")
        _require(slot["kind"] in ("steel", "nonsteel"), "explicit steel/nonsteel kind required")
        for v in _vector(slot["base_color_linear"], 3, "base color"):
            _number(v, "base color", 0, 1)
        for key in ("metallic", "roughness"):
            _number(slot[key], key, 0, 1)


def _v2(m, package_dir, project_root):
    _fields(m, ("files", "sources", "assembly", "material_slots", "bake", "review"), "manifest")
    files = _references(m["files"], FILE_KEYS, package_dir, "files")
    sources = _references(m["sources"], SOURCE_KEYS, project_root, "sources")
    _require(len(set(files.values())) == len(files), "package file roles must name distinct files")
    _slots(m["material_slots"])
    a = _fields(m["assembly"], ("parts", "mesh_node", "origin", "height_cm", "bounds_blender_cm", "source_to_export", "axis", "landmarks"), "assembly")
    _require(isinstance(a["mesh_node"], str) and re.fullmatch(r"SM_[A-Za-z0-9_]+", a["mesh_node"]) and "USP" not in a["mesh_node"].upper(), "mesh node must be import-safe and exclude USP")
    _require(a["origin"] == "combined_bottom_center", "unsupported proof origin")
    _number(a["height_cm"], "height", 1e-6)
    _matrix(a["source_to_export"], "source_to_export")
    transform = a["source_to_export"]
    scale = transform[0][0]
    _require(scale > 0 and all(abs(transform[i][j] - (scale if i == j else 0)) < 1e-8 for i in range(3) for j in range(3)), "normalization must preserve proportions with positive uniform scale")
    bounds = a["bounds_blender_cm"]
    _require(isinstance(bounds, list) and len(bounds) == 2, "bounds require min/max")
    lo, hi = [_vector(b, 3, "bounds") for b in bounds]
    _require(all(lo[i] < hi[i] for i in range(3)), "bounds must have positive extents")
    _require(abs(hi[2]-lo[2]-a["height_cm"]) < 1e-5 and abs(lo[2]) < 1e-5 and abs(lo[0]+hi[0]) < 1e-5 and abs(lo[1]+hi[1]) < 1e-5, "height/bottom-center bounds mismatch")
    _require(a["axis"] == {"blender_forward": "-Y", "blender_up": "Z", "unreal_mapping": ["x", "-y", "z"]}, "unsupported axis mapping")
    parts = a["parts"]
    _require(isinstance(parts, list) and parts, "explicit included parts required")
    names, used = set(), set()
    for part in parts:
        _fields(part, ("source_object", "slot_indices", "source_to_assembly"), "part")
        name = part["source_object"]
        _require(isinstance(name, str) and name and name not in names, "duplicate/empty part")
        names.add(name)
        indices = part["slot_indices"]
        _require(isinstance(indices, list) and indices and all(type(i) is int and 0 <= i < len(m["material_slots"]) for i in indices), "unmapped part slot")
        _require(len(indices) == len(set(indices)), "duplicate part slot")
        used.update(indices)
        _matrix(part["source_to_assembly"], "part transform")
    _require(used == set(range(len(m["material_slots"]))), "unused declared slot")
    _fields(a["landmarks"], ("front", "ridge", "slit"), "landmarks")
    for name, landmark in a["landmarks"].items():
        _fields(landmark, ("part", "source_position", "blender_cm", "unreal_cm"), name)
        _require(landmark["part"] in names, "landmark part is not included")
        source = _vector(landmark["source_position"], 3, name)
        point = _vector(landmark["blender_cm"], 3, name)
        unreal = _vector(landmark["unreal_cm"], 3, name)
        expected = [sum(transform[i][j]*source[j] for j in range(3))+transform[i][3] for i in range(3)]
        _require(all(abs(point[i]-expected[i]) < 1e-5 and lo[i]-1e-5 <= point[i] <= hi[i]+1e-5 for i in range(3)), "landmark normalization/bounds mismatch")
        _require(all(abs(unreal[i]-point[i]*(1, -1, 1)[i]) < 1e-5 for i in range(3)), "landmark axis mapping mismatch")
    b = _fields(m["bake"], ("normal_representation", "runtime", "final_contains_influence", "runtime_influence_multiplier", "identities", "textures", "masks", "recipe_sha256", "normal_space"), "bake")
    _require(b["normal_representation"] == "base_and_final" and b["runtime"] == NORMAL_RUNTIME, "unsupported normal endpoint contract")
    _require(b["final_contains_influence"] is True and b["runtime_influence_multiplier"] is False, "authored influence must be applied exactly once")
    _require(b["normal_space"] == "DirectX_tangent", "normal space must be DirectX tangent")
    _require(b["recipe_sha256"] == m["sources"]["region_recipe"]["sha256"], "bake recipe identity mismatch")
    identities = _fields(b["identities"], ("prepared", "baked", "exported"), "identities")
    for key in ("baked", "exported"):
        require_frozen_identity(identities["prepared"], identities[key])
    _fields(b["textures"], ("normal_base", "normal_final", "masks"), "textures")
    resolutions = []
    for key in ("normal_base", "normal_final", "masks"):
        t = _fields(b["textures"][key], ("resolution", "srgb", "compression", "flip_green_channel"), key)
        _require(isinstance(t["resolution"], list) and len(t["resolution"]) == 2 and all(type(n) is int and n > 0 for n in t["resolution"]), "invalid texture resolution")
        resolutions.append(t["resolution"])
        _require(t["srgb"] is False and t["flip_green_channel"] is False, "textures must be linear; DirectX green is already inverted")
        _require(t["compression"] == ("TC_MASKS" if key == "masks" else "TC_NORMALMAP"), "texture compression mismatch")
    _require(all(r == resolutions[0] for r in resolutions), "texture endpoint/mask resolution mismatch")
    masks = _fields(b["masks"], ("channels", "padding_pixels", "protected_regions_sha256"), "masks")
    _require(masks["channels"] == {"R": "roughness", "G": "selective_edge", "B": "authored_influence_diagnostic"}, "mask channels mismatch")
    _require(type(masks["padding_pixels"]) is int and masks["padding_pixels"] > 0, "positive UV padding required")
    _require(masks["protected_regions_sha256"] == m["sources"]["protected_regions"]["sha256"], "protection identity mismatch")
    r = _fields(m["review"], ("source_camera", "comparator_transform", "source_rig_sha256"), "review")
    camera = _fields(r["source_camera"], ("projection", "matrix_world", "framing"), "source_camera")
    _require(camera["projection"] in ("orthographic", "perspective"), "unknown camera projection")
    _matrix(camera["matrix_world"], "source camera")
    _number(camera["framing"], "source camera framing (ortho scale or horizontal FOV degrees)", 1e-6)
    if camera["projection"] == "perspective":
        _require(camera["framing"] < 180, "invalid perspective FOV")
    _matrix(r["comparator_transform"], "comparator placement")
    _require(r["source_rig_sha256"] == m["sources"]["source_rig"]["sha256"], "source rig identity mismatch")
    return files, sources


def _legacy(m, package_dir, project_root):
    _fields(m, ("fbx", "textures", "sha256", "source", "source_sha256", "material_slots", "height_cm", "bounds_blender_cm", "normal_import", "masks_import", "zero_strength"), "legacy manifest")
    _require(m["zero_strength"] == "normalize(lerp(float3(0,0,1),decoded_normal,strength)); strength0 exactly mesh normals", "unrecognized legacy normal contract")
    _require(m["normal_import"] == {"srgb": False, "compression": "TC_NORMALMAP", "flip_green_channel": False}, "unsupported legacy normal import")
    _fields(m["textures"], ("normal", "masks"), "legacy textures")
    entries = {"fbx": m["fbx"]}
    for key in ("normal", "masks"):
        entries[key] = _fields(m["textures"][key], ("path",), key)["path"]
    refs = {}
    _require(isinstance(m["sha256"], dict), "legacy hashes must be an object")
    for key, path in entries.items():
        _require(isinstance(path, str) and path in m["sha256"], "legacy payload hash missing")
        refs[key] = {"path": path, "sha256": m["sha256"][path]}
    files = _references(refs, entries.keys(), package_dir, "legacy files")
    sources = _references({"source": {"path": m["source"], "sha256": m["source_sha256"]}}, ("source",), project_root, "legacy source")
    slots = m["material_slots"]
    _require(isinstance(slots, list) and slots and all(isinstance(s, dict) for s in slots), "unsupported legacy slots")
    _slots([dict(s, kind="steel" if _number(s.get("metallic"), "metallic", 0, 1) > .5 else "nonsteel") for s in slots])
    _number(m["height_cm"], "legacy height", 1e-6)
    _require(m["masks_import"].get("srgb") is False and m["masks_import"].get("compression") == "TC_MASKS", "unsupported legacy masks")
    return files, sources


def validate_manifest(manifest, package_dir, project_root, *, expected_revision=None, allow_legacy=False):
    """Validate structure, references and fingerprints without writing anything.
    Return (schema_version, resolved_files, resolved_sources). Absence of a
    schema_version is legacy 1 only when explicitly enabled. Explicit unknown
    versions, including null/string/bool, always fail.
    """
    _fields(manifest, ("revision",), "manifest")
    revision = manifest["revision"]
    _require(isinstance(revision, str) and re.fullmatch(r"USP_v[0-9]{3}", revision), "invalid revision")
    _require(expected_revision is None or expected_revision == revision, "requested revision mismatch")
    version = manifest.get("schema_version", 1)
    _require(type(version) is int and version in (1, 2), "unsupported schema version")
    if version == 1:
        _require(allow_legacy, "legacy schema requires explicit allow_legacy=True")
        files, sources = _legacy(manifest, package_dir, project_root)
    else:
        files, sources = _v2(manifest, package_dir, project_root)
    return version, files, sources


def load_manifest(path, project_root, *, expected_revision=None, allow_legacy=False):
    """Full import preflight. Call before directories/assets/material writes."""
    path = Path(path).resolve()
    payload = path.read_bytes()
    try:
        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                _require(key not in result, "duplicate JSON key: " + key)
                result[key] = value
            return result
        manifest = json.loads(payload, object_pairs_hook=unique_object,
                              parse_constant=lambda value: (_ for _ in ()).throw(ContractError("nonfinite JSON: " + value)))
        version, files, sources = validate_manifest(manifest, path.parent, project_root,
                                                  expected_revision=expected_revision, allow_legacy=allow_legacy)
    except (KeyError, TypeError, AttributeError, json.JSONDecodeError) as error:
        raise ContractError("malformed transfer manifest: " + str(error)) from error
    return TransferPackage(manifest, hashlib.sha256(payload).hexdigest(), version, files, sources)
