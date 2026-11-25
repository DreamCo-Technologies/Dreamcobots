import os
import tempfile
import unittest
from pathlib import Path

from buddy.capabilities.task_store import TaskStore


class TaskStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "nested" / "tasks.sqlite3")
        self.store = TaskStore(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_persistence_and_owner_isolation(self):
        self.store.put("subject-alice", {"task_id": "task1", "goal": "study", "status": "proposed"})
        self.assertEqual(TaskStore(self.path).get("subject-alice", "task1")["goal"], "study")
        self.assertIsNone(self.store.get("subject-bob", "task1"))
        self.assertEqual(self.store.list("subject-bob"), [])

    def test_approval_lifecycle_and_append_only_history(self):
        self.store.put("subject-alice", {"task_id": "task1"})
        for old, new in [("proposed", "approved"), ("approved", "running"),
                         ("running", "verified")]:
            self.store.transition("subject-alice", "task1", expected=old, target=new)
        self.assertEqual(self.store.get("subject-alice", "task1")["status"], "verified")
        self.assertEqual([event["status"] for event in self.store.history("subject-alice", "task1")],
                         ["proposed", "approved", "running", "verified"])

    def test_rejects_invalid_or_cross_user_transition(self):
        self.store.put("subject-alice", {"task_id": "task1"})
        with self.assertRaises(ValueError):
            self.store.transition("subject-bob", "task1", expected="proposed", target="approved")
        with self.assertRaises(ValueError):
            self.store.transition("subject-alice", "task1", expected="proposed", target="verified")
        with self.assertRaises(Exception):
            self.store.put("subject-alice", {"task_id": "task1"})

    def test_rejects_credentials_and_secret_values(self):
        with self.assertRaisesRegex(ValueError, "credential fields"):
            self.store.put("subject-alice", {"task_id": "bad1", "api_key": "do-not-store"})
        with self.assertRaisesRegex(ValueError, "credential-like value"):
            self.store.put("subject-alice", {"task_id": "bad2", "note": "token sk-abcdefghijklmnopqrstuvwxyz123456"})

    def test_database_directory_and_file_permissions_are_restricted(self):
        self.assertTrue(Path(self.path).parent.is_dir())
        if os.name == "posix":
            self.assertEqual(Path(self.path).stat().st_mode & 0o777, 0o600)

    def test_rejects_untrusted_owner_and_non_object_packets(self):
        with self.assertRaisesRegex(ValueError, "opaque authenticated owner"):
            self.store.put(" subject-alice ", {"task_id": "task1"})
        with self.assertRaisesRegex(ValueError, "packet must be an object"):
            self.store.put("subject-alice", ["not", "an", "object"])


if __name__ == "__main__":
    unittest.main()
