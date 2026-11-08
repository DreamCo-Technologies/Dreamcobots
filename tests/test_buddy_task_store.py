import tempfile
import unittest
from pathlib import Path
from buddy.capabilities.task_store import TaskStore

class TaskStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "tasks.sqlite3")
        self.store = TaskStore(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_persistence_and_owner_isolation(self):
        self.store.put("alice", {"task_id": "task1", "goal": "study", "status": "proposed"})
        self.assertEqual(TaskStore(self.path).get("alice", "task1")["goal"], "study")
        self.assertIsNone(self.store.get("bob", "task1"))
        self.assertEqual(self.store.list("bob"), [])

    def test_approval_lifecycle_and_audit(self):
        self.store.put("alice", {"task_id": "task1"})
        for old, new in [("proposed", "approved"), ("approved", "running"),
                         ("running", "verified")]:
            self.store.transition("alice", "task1", expected=old, target=new)
        self.assertEqual(self.store.get("alice", "task1")["status"], "verified")
        self.assertEqual([e["status"] for e in self.store.history("alice", "task1")],
                         ["proposed", "approved", "running", "verified"])

    def test_reject_invalid_or_cross_user_transition(self):
        self.store.put("alice", {"task_id": "task1"})
        with self.assertRaises(ValueError):
            self.store.transition("bob", "task1", expected="proposed", target="approved")
        with self.assertRaises(ValueError):
            self.store.transition("alice", "task1", expected="proposed", target="verified")
        with self.assertRaises(Exception):
            self.store.put("alice", {"task_id": "task1"})

if __name__ == "__main__":
    unittest.main()
