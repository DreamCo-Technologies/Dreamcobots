from __future__ import annotations
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("data_observability",ROOT/"tools"/"build_command_center_data_observability.py")
MODULE=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)

class DataObservabilityTests(unittest.TestCase):
    def test_snapshot_has_source_and_training_coverage_without_private_rows(self):
        payload=MODULE.build()
        self.assertEqual(payload["schema"],"dreamco.command_center.data_observability.v1")
        self.assertGreaterEqual(payload["summary"]["external_sources_with_metadata_adapters"],4)
        self.assertEqual(len(payload["sources"]),8)
        self.assertFalse(payload["privacy"]["raw_dataset_rows_exposed"])
        self.assertFalse(payload["privacy"]["credentials_exposed"])
        self.assertIn("training_job_manifests",payload["summary"])
    def test_inventory_counts_files_but_not_contents(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); dataset=root/"datasets"; dataset.mkdir()
            (dataset/"sample.jsonl").write_text('{"secret":"do not expose"}')
            found=MODULE.files_under("datasets")
            self.assertEqual(len(found),1)
            self.assertNotIn("do not expose",str([p.relative_to(MODULE.ROOT).as_posix() for p in found]))
if __name__=="__main__": unittest.main()
