import unittest

from buddy.capabilities.runtime import Action, Session, distill_observations


class FixtureAdapter:
    id, revision, transport = "fixture-speaker", "1", "bluetooth"

    def __init__(self):
        self.calls = []

    def discover(self):
        return (Action("play", "Choose a track and press Play."),
                Action("inspect", "Read supported formats.", "read_only"),
                Action("erase", "Review device reset.", "destructive"))

    def execute(self, action, arguments):
        self.calls.append((action, arguments))
        return True


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.adapter, self.events = FixtureAdapter(), []
        self.connected, self.now = True, 100
        self.session = Session(self.adapter, paired=lambda: self.connected,
                               emit=self.events.append, clock=lambda: self.now)

    def test_approval_exact_one_use_and_redacted(self):
        arguments = {"track": "private-title"}
        grant = self.session.approve("play", arguments)
        self.assertEqual(self.session.step("play", {"track": "different"}, grant=grant)["status"], "approval_required")
        self.assertEqual(self.session.step("play", arguments, grant=grant)["status"], "verified")
        self.assertEqual(self.session.step("play", arguments, grant=grant)["status"], "approval_required")
        self.assertEqual(len(self.adapter.calls), 1)
        self.assertNotIn("private-title", str(self.events))

    def test_unknown_and_guided_do_not_execute(self):
        self.assertEqual(self.session.step("video", {})["status"], "guided")
        self.assertEqual(self.session.step("play", {}, mode="guided")["status"], "guided")
        self.assertFalse(self.adapter.calls)

    def test_expiration_revision_disconnect_and_stop(self):
        grant = self.session.approve("play", {}, ttl=1)
        self.now += 2
        self.assertEqual(self.session.step("play", {}, grant=grant)["status"], "approval_required")
        grant = self.session.approve("play", {})
        self.adapter.revision = "2"
        self.assertEqual(self.session.step("play", {}, grant=grant)["status"], "approval_required")
        self.connected = False
        self.assertEqual(self.session.step("inspect", {})["status"], "pairing_required")
        self.connected = True
        self.session.stop()
        self.assertEqual(self.session.step("inspect", {})["status"], "stopped")
        self.assertFalse(self.adapter.calls)

    def test_readonly_and_higher_risk_gate(self):
        self.assertEqual(self.session.step("inspect", {})["status"], "verified")
        grant = self.session.approve("erase", {})
        self.assertEqual(self.session.step("erase", {}, grant=grant)["status"], "host_gate_required")
        self.assertEqual(len(self.adapter.calls), 1)

    def test_uncertain_effect_is_not_retried(self):
        def fail(*args):
            raise RuntimeError("secret-token")
        self.adapter.execute = fail
        grant = self.session.approve("play", {})
        self.assertEqual(self.session.step("play", {}, grant=grant)["status"], "needs_review")
        self.assertEqual(self.session.step("play", {}, grant=grant)["status"], "approval_required")
        self.assertNotIn("secret-token", str(self.events))

    def test_stop_from_progress_observer(self):
        self.session.emit = lambda event: self.session.stop()
        self.assertEqual(self.session.step("inspect", {})["status"], "interrupted")
        self.assertFalse(self.adapter.calls)

    def test_dataset_permissions_and_holdout_isolation(self):
        row = dict(data_authorized=True, teacher_terms_allow=True, training_consent=True,
                   verified=True, redacted=True, split="train", source="owner-demo",
                   revision="abc", input="request", output="result", customization="my layout",
                   hidden_reasoning="must not export")
        self.assertEqual(len(distill_observations([row])), 1)
        self.assertNotIn("hidden_reasoning", distill_observations([row])[0])
        for key in ("data_authorized", "teacher_terms_allow", "training_consent", "verified", "redacted"):
            self.assertEqual(distill_observations([{**row, key: False}]), [])
        self.assertEqual(distill_observations([{**row, "split": "holdout"}]), [])


if __name__ == "__main__":
    unittest.main()
