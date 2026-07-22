from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.social import (
    BuddySocialManager,
    LocalSocialOutboxPublisher,
    PublishApproval,
    SocialDraft,
    SocialManagerError,
)


class Publisher:
    name = "test-publisher"
    platform = "ExampleSocial"

    def publish(self, *, account_ref, content, media_refs):
        self.payload = (account_ref, content, media_refs)
        return "post:test-1"


class FailingPublisher(Publisher):
    def publish(self, *, account_ref, content, media_refs):
        raise RuntimeError("provider unavailable")


class BuddySocialManagerTests(unittest.TestCase):
    def test_prepares_content_without_publishing(self):
        packet = BuddySocialManager().prepare(SocialDraft(
            owner_user_id="owner-1",
            account_ref="social-account:owner:primary",
            platform="ExampleSocial",
            content="A useful product update.",
            objective="Inform existing customers",
        ))
        self.assertEqual(packet["status"], "awaiting_owner_publish_approval")
        self.assertTrue(packet["publish_requires_owner_approval"])

    def test_media_requires_rights_confirmation(self):
        with self.assertRaisesRegex(SocialManagerError, "rights"):
            BuddySocialManager().prepare(SocialDraft(
                owner_user_id="owner-1",
                account_ref="social-account:owner:primary",
                platform="ExampleSocial",
                content="New video.",
                objective="Share a demonstration",
                media_refs=("asset:video:1",),
            ))

    def test_publishes_once_with_matching_owner_approval(self):
        manager = BuddySocialManager()
        packet = manager.prepare(SocialDraft(
            owner_user_id="owner-1",
            account_ref="social-account:owner:primary",
            platform="ExampleSocial",
            content="Approved product update.",
            objective="Inform existing customers",
        ))
        approval = PublishApproval(
            owner_user_id="owner-1",
            account_ref=packet["account_ref"],
            draft_id=packet["draft_id"],
            draft_fingerprint=packet["draft_fingerprint"],
        )
        receipt = manager.publish(packet, owner_user_id="owner-1", approval=approval, publisher=Publisher())
        self.assertEqual(receipt["status"], "published")
        with self.assertRaisesRegex(SocialManagerError, "already been used"):
            manager.publish(packet, owner_user_id="owner-1", approval=approval, publisher=Publisher())

    def test_approval_is_bound_to_the_reviewed_content(self):
        manager = BuddySocialManager()
        packet = manager.prepare(SocialDraft(
            owner_user_id="owner-1",
            account_ref="social-account:owner:primary",
            platform="ExampleSocial",
            content="Approved product update.",
            objective="Inform existing customers",
        ))
        approval = PublishApproval(
            owner_user_id="owner-1",
            account_ref=packet["account_ref"],
            draft_id=packet["draft_id"],
            draft_fingerprint=packet["draft_fingerprint"],
        )
        packet["content"] = "Changed after approval."
        with self.assertRaisesRegex(SocialManagerError, "reviewed content"):
            manager.publish(packet, owner_user_id="owner-1", approval=approval, publisher=Publisher())

    def test_approved_post_can_move_to_a_private_local_outbox(self):
        manager = BuddySocialManager()
        packet = manager.prepare(SocialDraft(
            owner_user_id="owner-1",
            account_ref="social-account:owner:primary",
            platform="ExampleSocial",
            content="Approved local preview.",
            objective="Review before external publishing",
        ))
        approval = PublishApproval(
            owner_user_id="owner-1",
            account_ref=packet["account_ref"],
            draft_id=packet["draft_id"],
            draft_fingerprint=packet["draft_fingerprint"],
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            publisher = LocalSocialOutboxPublisher("ExampleSocial", Path(temp_dir))
            receipt = manager.publish(packet, owner_user_id="owner-1", approval=approval, publisher=publisher)
            self.assertEqual(receipt["status"], "published")
            self.assertTrue(receipt["post_ref"].startswith("local-social-outbox:"))
            files = list(Path(temp_dir).glob("*.json"))
            self.assertEqual(len(files), 1)
            self.assertFalse(json.loads(files[0].read_text())["live_external_action_taken"])

    def test_failed_provider_does_not_consume_the_one_time_approval(self):
        manager = BuddySocialManager()
        packet = manager.prepare(SocialDraft(
            owner_user_id="owner-1",
            account_ref="social-account:owner:primary",
            platform="ExampleSocial",
            content="Approved retry test.",
            objective="Test safe provider retry",
        ))
        approval = PublishApproval(
            owner_user_id="owner-1",
            account_ref=packet["account_ref"],
            draft_id=packet["draft_id"],
            draft_fingerprint=packet["draft_fingerprint"],
        )
        with self.assertRaisesRegex(RuntimeError, "provider unavailable"):
            manager.publish(packet, owner_user_id="owner-1", approval=approval, publisher=FailingPublisher())
        receipt = manager.publish(packet, owner_user_id="owner-1", approval=approval, publisher=Publisher())
        self.assertEqual(receipt["status"], "published")


if __name__ == "__main__":
    unittest.main()
