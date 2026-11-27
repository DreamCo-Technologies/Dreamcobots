import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from tools.train_buddy_division_model import validate_cli_authorization, validate_private_paths


class DivisionModelTrainingCliGateTests(unittest.TestCase):
    def test_runtime_flag_and_approval_record_are_required(self):
        args = SimpleNamespace(
            authorize_weight_updates=False,
            authorization_reference="owner-approval-2026-001",
            approved_by="DreamCo owner",
        )
        with self.assertRaisesRegex(PermissionError, "--authorize-weight-updates"):
            validate_cli_authorization(args)
        args.authorize_weight_updates = True
        args.authorization_reference = "short"
        with self.assertRaisesRegex(PermissionError, "authorization reference"):
            validate_cli_authorization(args)
        args.authorization_reference = "owner-approval-2026-001"
        args.approved_by = "x"
        with self.assertRaisesRegex(PermissionError, "owner identity"):
            validate_cli_authorization(args)
        args.approved_by = "DreamCo owner"
        self.assertIsNone(validate_cli_authorization(args))

    def test_dataset_checkpoint_and_resume_paths_must_stay_in_private_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "private"
            root.mkdir()
            dataset = root / "dataset.txt"
            output = root / "checkpoints/model.pt"
            resume = root / "checkpoints/previous.pt"
            resolved = validate_private_paths(dataset, output, resume, root)
            self.assertEqual(resolved, (dataset.resolve(), output.resolve(), resume.resolve()))
            with self.assertRaisesRegex(PermissionError, "dataset path"):
                validate_private_paths(Path(temp) / "outside.txt", output, None, root)
            with self.assertRaisesRegex(PermissionError, "checkpoint output"):
                validate_private_paths(dataset, Path(temp) / "outside.pt", None, root)
            with self.assertRaisesRegex(PermissionError, "resume checkpoint"):
                validate_private_paths(dataset, output, Path(temp) / "outside.pt", root)


if __name__ == "__main__":
    unittest.main()
