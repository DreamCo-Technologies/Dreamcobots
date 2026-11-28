import json
import struct
import tempfile
import unittest
from pathlib import Path
from buddy.certification.weight_header_inspector import inspect_safetensors

class WeightHeaderInspectorTests(unittest.TestCase):
    def test_valid_header(self):
        header = json.dumps({"layer.weight":{"dtype":"F16","shape":[2,3],"data_offsets":[0,12]}}).encode()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "model.safetensors"
            p.write_bytes(struct.pack("<Q", len(header)) + header + bytes(12))
            result = inspect_safetensors(str(p))
            self.assertEqual(result["parameter_count"], 6)
            self.assertEqual(result["parameters_by_dtype"]["F16"], 6)
            self.assertFalse(result["training_performed"])

    def test_truncated(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.safetensors"
            p.write_bytes(b"abc")
            with self.assertRaises(ValueError):
                inspect_safetensors(str(p))

    def test_wrong_byte_count(self):
        header = json.dumps({"w":{"dtype":"F32","shape":[2],"data_offsets":[0,4]}}).encode()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.safetensors"
            p.write_bytes(struct.pack("<Q", len(header)) + header + bytes(4))
            with self.assertRaises(ValueError):
                inspect_safetensors(str(p))

if __name__ == "__main__":
    unittest.main()
