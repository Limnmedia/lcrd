# SPDX-License-Identifier: Apache-2.0
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lcrd  # noqa: E402


class LcrdInfrastructureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lcrd.migrate()
        lcrd.build()
        cls.dist = json.loads((ROOT / "dist" / "lcrd.json").read_text(encoding="utf-8"))
        cls.minimum = json.loads((ROOT / "dist" / "lcrd.min.json").read_text(encoding="utf-8"))

    def test_stable_ids_are_unique(self):
        records = []
        for key in ("cameras", "devices", "cameraModules", "sensors", "lenses", "observations", "sources"):
            records.extend(self.dist[key])
        ids = [record["id"] for record in records]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(self.dist["sensors"]), 629)
        research_ids = [item["id"] for item in self.dist["observations"] if item["kind"] == "research_pass"]
        self.assertTrue(all(re.fullmatch(r"observation:research:[0-9a-f]{20}", item) for item in research_ids))

    def test_aliases_and_identifiers_are_not_exif_observations(self):
        eos_100d = next(item for item in self.dist["cameras"] if item["id"] == "camera:canon:eos-100d")
        self.assertIn("EOS Rebel SL1", eos_100d["aliases"])
        a7_iv = next(item for item in self.dist["cameras"] if item["id"] == "camera:sony:alpha-a7-iv")
        self.assertIn("ILCE-7M4", a7_iv["manufacturer_identifiers"])
        self.assertFalse(any("exif" in key.lower() for item in self.dist["observations"] for key in item["legacy"]))

    def test_relationships_and_geometry(self):
        ids = {record["id"] for key in ("cameras", "devices", "cameraModules", "sensors", "lenses", "observations", "sources") for record in self.dist[key]}
        for module in self.dist["cameraModules"]:
            self.assertIn(module["device_id"], ids)
            self.assertIn(module["sensor_id"], ids)
        for sensor in self.dist["sensors"]:
            self.assertIn(sensor["owner_id"], ids)
            for field in ("width_mm", "height_mm"):
                if sensor[field] is not None:
                    self.assertGreater(sensor[field], 0)

    def test_observations_preserve_legacy_rows_and_sources(self):
        ids = {record["id"] for key in ("cameras", "devices", "cameraModules", "sensors", "lenses") for record in self.dist[key]}
        source_ids = {record["id"] for record in self.dist["sources"]}
        self.assertEqual(len(self.dist["observations"]), 1866)
        for observation in self.dist["observations"]:
            self.assertIn(observation["subject_id"], ids)
            self.assertIn("legacy", observation)
            if observation["source_id"]:
                self.assertIn(observation["source_id"], source_ids)

    def test_multicamera_device_has_independent_modules(self):
        device = next(item for item in self.minimum["devices"] if item["id"] == "device:apple:iphone-11-pro")
        self.assertGreaterEqual(len(device["camera_module_ids"]), 2)
        module_ids = set(device["camera_module_ids"])
        modules = [item for item in self.minimum["cameraModules"] if item["id"] in module_ids]
        self.assertEqual(len(modules), len(module_ids))
        self.assertGreaterEqual(len({item["sensor_id"] for item in modules}), 2)

    def test_metadata_and_build_are_deterministic(self):
        self.assertEqual(self.dist["lcrdVersion"], "0.1.0")
        self.assertEqual(self.dist["schemaVersion"], "1.0.0")
        self.assertEqual(self.dist["license"], "CC-BY-4.0")
        self.assertEqual(self.minimum["license"], "CC-BY-4.0")
        first = hashlib.sha256((ROOT / "dist" / "lcrd.json").read_bytes()).hexdigest()
        lcrd.build()
        second = hashlib.sha256((ROOT / "dist" / "lcrd.json").read_bytes()).hexdigest()
        self.assertEqual(first, second)

    def test_public_schemas_are_declared(self):
        schemas = list((ROOT / "schema").glob("*.schema.json"))
        self.assertEqual(len(schemas), 7)
        for path in schemas:
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertIn("$id", schema)
            self.assertIn("required", schema)


if __name__ == "__main__":
    unittest.main()
