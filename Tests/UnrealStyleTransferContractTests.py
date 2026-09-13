"""Pure-Python contract tests and a minimal executable schema-2 example.

Run: python Tests/UnrealStyleTransferContractTests.py
Dummy payloads deliberately test preflight identities, not FBX/PNG rendering.
"""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))
import UnrealStyleTransferContract as contract

IDENTITY_MATRIX = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def example_manifest(root, package):
    """Create a minimal fixture; copy this shape when implementing the exporter.
    Landmark source_position is in assembly/world space after each part matrix.
    source_to_export transforms this space to the normalized 35 cm mesh.
    """
    sources, files = {}, {}
    for name in contract.SOURCE_KEYS:
        path = root / (name + ".json")
        path.write_text(name)
        sources[name] = contract.file_reference(path, root)
    for name in contract.FILE_KEYS:
        path = package / (name + ".bin")
        path.write_text(name)
        files[name] = contract.file_reference(path, package)
    identity = contract.mesh_identity(vertices=[[0., 0., 0.]], triangles=[[0, 0, 0, 0, "Crown"]],
                                      uv=[[0., 0.]], split_normals=[[0., 0., 1.]], tangents=[[1., 0., 0., 1.]])
    landmarks = {}
    for name, point in (("front", [0, -8, 20]), ("ridge", [0, 0, 35]), ("slit", [0, -8, 17])):
        landmarks[name] = dict(part="Crown", source_position=point, blender_cm=point,
                               unreal_cm=[point[0], -point[1], point[2]])
    return {
        "schema_version": 2, "revision": "USP_v012", "files": files, "sources": sources,
        "material_slots": [{"index": 0, "name": "Steel", "source_material": "Accepted steel",
                            "kind": "steel", "base_color_linear": [.29, .285, .275], "metallic": 1, "roughness": .30}],
        "assembly": {"parts": [{"source_object": "Crown", "slot_indices": [0], "source_to_assembly": IDENTITY_MATRIX}],
                     "mesh_node": "SM_Helmet_StyleProof012", "origin": "combined_bottom_center", "height_cm": 35,
                     "bounds_blender_cm": [[-10, -8, 0], [10, 8, 35]], "source_to_export": IDENTITY_MATRIX,
                     "axis": {"blender_forward": "-Y", "blender_up": "Z", "unreal_mapping": ["x", "-y", "z"]},
                     "landmarks": landmarks},
        "bake": {"normal_representation": "base_and_final", "runtime": contract.NORMAL_RUNTIME,
                 "final_contains_influence": True, "runtime_influence_multiplier": False, "normal_space": "DirectX_tangent",
                 "recipe_sha256": sources["region_recipe"]["sha256"],
                 "identities": {key: copy.deepcopy(identity) for key in ("prepared", "baked", "exported")},
                 "textures": {key: {"resolution": [2048, 2048], "srgb": False, "flip_green_channel": False,
                                     "compression": "TC_MASKS" if key == "masks" else "TC_NORMALMAP"}
                              for key in ("normal_base", "normal_final", "masks")},
                 "masks": {"channels": {"R": "roughness", "G": "selective_edge", "B": "authored_influence_diagnostic"},
                           "padding_pixels": 8, "protected_regions_sha256": sources["protected_regions"]["sha256"]}},
        "review": {"source_camera": {"projection": "orthographic", "matrix_world": IDENTITY_MATRIX, "framing": 50},
                   "comparator_transform": IDENTITY_MATRIX, "source_rig_sha256": sources["source_rig"]["sha256"]}}


class TransferContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / "USP_v012"
        self.package.mkdir()
        self.manifest = example_manifest(self.root, self.package)
        self.path = self.package / "manifest.json"

    def load(self, manifest=None, **kwargs):
        self.path.write_text(json.dumps(self.manifest if manifest is None else manifest))
        return contract.load_manifest(self.path, self.root, expected_revision="USP_v012", **kwargs)

    def test_valid_and_exact_manifest_identity(self):
        result = self.load()
        self.assertEqual(result.schema_version, 2)
        self.assertEqual(result.manifest_sha256, contract.sha256_file(self.path))
        self.assertEqual(result.files["fbx"], (self.package / "fbx.bin").resolve())
        before = sorted(str(p) for p in self.root.rglob("*"))
        contract.load_manifest(self.path, self.root)
        self.assertEqual(before, sorted(str(p) for p in self.root.rglob("*")))

    def test_missing_required_groups(self):
        for key in ("sources", "files", "assembly", "material_slots", "bake", "review"):
            with self.subTest(key=key), self.assertRaises(contract.ContractError):
                candidate = copy.deepcopy(self.manifest)
                del candidate[key]
                self.load(candidate)

    def test_unknown_or_invalid_schema_and_revision(self):
        for version in (None, True, "2", 3, -1):
            with self.subTest(version=version), self.assertRaises(contract.ContractError):
                self.load(dict(self.manifest, schema_version=version), allow_legacy=True)
        with self.assertRaises(contract.ContractError):
            self.load(dict(self.manifest, revision="USP_v013"))

    def test_path_attacks(self):
        for path in ("../accepted_geometry.json", "/tmp/a", "C:/a", "C:foo", "//server/share/a",
                     "..\\a", "fbx.bin:stream", "./fbx.bin", "folder//a", "folder. /a"):
            with self.subTest(path=path), self.assertRaises(contract.ContractError):
                self.manifest["files"]["fbx"]["path"] = path
                self.load()

    def test_symlink_escape(self):
        link = self.package / "outside.bin"
        try:
            link.symlink_to(self.root / "accepted_geometry.json")
        except (OSError, NotImplementedError):
            self.skipTest("OS does not permit symlink creation")
        with self.assertRaises(contract.ContractError):
            contract.contained_path(self.package, "outside.bin")

    def test_changed_payload_or_authority_hash(self):
        for group, key in (("files", "fbx"), ("sources", "accepted_geometry")):
            with self.subTest(group=group), self.assertRaises(contract.ContractError):
                candidate = copy.deepcopy(self.manifest)
                candidate[group][key]["sha256"] = "0" * 64
                self.load(candidate)

    def test_missing_payload(self):
        (self.package / "normal_base.bin").unlink()
        with self.assertRaises(contract.ContractError):
            self.load()

    def test_normal_contract_rejects_flat_control_and_double_influence(self):
        for key, value in (("normal_representation", "flat_and_final"), ("runtime", "compose(N1,N1)"),
                           ("final_contains_influence", False), ("runtime_influence_multiplier", True),
                           ("normal_space", "OpenGL_tangent")):
            with self.subTest(key=key), self.assertRaises(contract.ContractError):
                candidate = copy.deepcopy(self.manifest)
                candidate["bake"][key] = value
                self.load(candidate)
        self.manifest["files"]["normal_base"] = self.manifest["files"]["normal_final"]
        with self.assertRaises(contract.ContractError):
            self.load()

    def test_frozen_mesh_changes(self):
        for key in contract.IDENTITY_KEYS:
            with self.subTest(key=key), self.assertRaises(contract.ContractError):
                candidate = copy.deepcopy(self.manifest)
                candidate["bake"]["identities"]["exported"][key] = "f" * 64
                self.load(candidate)

    def test_bad_texture_metadata_and_masks(self):
        for key, value in (("srgb", True), ("flip_green_channel", True), ("compression", "TC_DEFAULT"), ("resolution", [0, 2048])):
            with self.subTest(key=key), self.assertRaises(contract.ContractError):
                candidate = copy.deepcopy(self.manifest)
                candidate["bake"]["textures"]["normal_base"][key] = value
                self.load(candidate)
        self.manifest["bake"]["masks"]["channels"]["B"] = "multiply_normal"
        with self.assertRaises(contract.ContractError):
            self.load()

    def test_parts_slots_scale_and_landmarks(self):
        changes = [("part", lambda m: m["assembly"]["parts"][0].update(slot_indices=[5])),
                   ("slot", lambda m: m["material_slots"][0].update(kind="guess")),
                   ("scale", lambda m: m["assembly"].update(height_cm=34)),
                   ("node", lambda m: m["assembly"].update(mesh_node="SM_Helmet_USP012")),
                   ("landmark", lambda m: m["assembly"]["landmarks"]["slit"].update(unreal_cm=[0, -8, 17])),
                   ("axis", lambda m: m["assembly"]["axis"].update(blender_forward="Y"))]
        for label, change in changes:
            with self.subTest(label=label), self.assertRaises(contract.ContractError):
                candidate = copy.deepcopy(self.manifest)
                change(candidate)
                self.load(candidate)

    def test_nonfinite_and_duplicate_json_rejected(self):
        for payload in ('{"revision":"USP_v012","schema_version":2,"schema_version":1}',
                        '{"revision":"USP_v012","schema_version":NaN}'):
            self.path.write_text(payload)
            with self.assertRaises(contract.ContractError):
                contract.load_manifest(self.path, self.root, allow_legacy=True)

    def test_imported_triangle_correspondence_and_basis(self):
        corners = [[x,y,0,u,v,0,0,1,1,0,0,1] for x,y,u,v in ((0,0,0,0),(1,0,1,0),(0,1,0,1))]
        expected = {"schema_version": 1, "triangles": [{"slot": 0, "corners": corners}]}
        actual = [{"slot": 0, "corners": list(reversed(copy.deepcopy(corners)))}]
        self.assertTrue(contract.verify_imported_triangles(expected, actual)["verified"])
        for index, value in ((0,2.), (3,.1), (5,.2), (8,0.), (11,-1)):
            changed = copy.deepcopy(actual)
            changed[0]["corners"][0][index] = value
            with self.subTest(index=index), self.assertRaises(contract.ContractError):
                contract.verify_imported_triangles(expected, changed)
        with self.assertRaises(contract.ContractError):
            contract.verify_imported_triangles(expected, actual*2)
        changed = copy.deepcopy(actual)
        changed[0]["corners"][0][8:11] = [.6, 0, .8]
        with self.assertRaises(contract.ContractError):
            contract.verify_imported_triangles(expected, changed)

    def test_inverse_actual_interpolated_frame_reconstructs_direction(self):
        # Deliberately nonunit/nonorthogonal T,N: dot products alone are wrong.
        tangent, normal, desired = [.8,.1,0], [.1,0,.7], [.1,.4,.9]
        for sign in (-1, 1):
            bitangent = [-.07*sign, .56*sign, .01*sign]
            coordinates = contract.inverse_interpolated_frame(desired,tangent,normal,sign)
            actual = [coordinates[0]*tangent[i]+coordinates[1]*bitangent[i]+coordinates[2]*normal[i] for i in range(3)]
            for a,b in zip(actual,desired):
                self.assertAlmostEqual(a,b,places=12)
        with self.assertRaises(contract.ContractError):
            contract.inverse_interpolated_frame(desired,[1,0,0],[1,0,0],1)

    def test_legacy_is_explicit_and_retains_distinct_meaning(self):
        m = self.manifest
        legacy = {"revision": m["revision"], "fbx": m["files"]["fbx"]["path"],
                  "textures": {"normal": {"path": m["files"]["normal_final"]["path"]}, "masks": {"path": m["files"]["masks"]["path"]}},
                  "sha256": {v["path"]: v["sha256"] for v in m["files"].values()},
                  "source": m["sources"]["working_copy"]["path"], "source_sha256": m["sources"]["working_copy"]["sha256"],
                  "material_slots": [{k: v for k, v in m["material_slots"][0].items() if k != "kind"}],
                  "height_cm": 35, "bounds_blender_cm": m["assembly"]["bounds_blender_cm"],
                  "normal_import": {"srgb": False, "compression": "TC_NORMALMAP", "flip_green_channel": False},
                  "masks_import": {"srgb": False, "compression": "TC_MASKS"},
                  "zero_strength": "normalize(lerp(float3(0,0,1),decoded_normal,strength)); strength0 exactly mesh normals"}
        with self.assertRaises(contract.ContractError):
            self.load(legacy)
        result = self.load(legacy, allow_legacy=True)
        self.assertEqual(result.schema_version, 1)
        self.assertIn("normal", result.files)
        self.assertNotIn("normal_base", result.files)
        del legacy["sha256"][legacy["fbx"]]
        with self.assertRaises(contract.ContractError):
            self.load(legacy, allow_legacy=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
