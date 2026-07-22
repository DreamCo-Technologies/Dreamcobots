from __future__ import annotations

import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.automation import BuddyTaskRunner, TaskRunnerError
from dreamco_platform.creative import (
    ArtistBrief,
    BuddyLogoGenerator,
    BuddyMusicArtistStudio,
    LogoBrief,
    MusicStudioError,
    ReferenceTrack,
)
from dreamco_platform.customization import BuddyProfile, PersonalityProfile, build_asset_catalog
from dreamco_platform.finance import Bill, BuddySubscriptionManager, Subscription
from dreamco_platform.launch import (
    AppReleaseBrief,
    BuddyLaunchpad,
    BusinessFormationBrief,
    PrototypeBrief,
    ReleaseCouncil,
    StoreTarget,
)
from dreamco_platform.legal_ip import BuddyIPAssistant, IPBrief, IPError, IPType
from dreamco_platform.opensource import BuddyOpenSourceLab, OpenSourceError, UpgradeRequest
from dreamco_platform.privacy import (
    BuddyDataWallet,
    DataCategory,
    DataPermissionRequest,
    DataSource,
    DataWalletError,
)
from tools.generate_buddy_platform_expansion import build_registry


class BuddyPlatformExpansionTests(unittest.TestCase):
    def test_launchpad_prepares_official_handoffs_without_external_action(self):
        launchpad = BuddyLaunchpad()
        formation = launchpad.business_formation_plan(BusinessFormationBrief(
            owner_user_id="owner-1",
            business_name="Signal Works",
            country="US",
            region="Illinois",
            entity_type="LLC",
            business_purpose="Build accessible learning software for families.",
        ))
        prototype = launchpad.prototype_plan(PrototypeBrief(
            owner_user_id="owner-1",
            title="Learning Lab",
            product_type="simulation",
            objective="Build a local science simulation with measurable learning outcomes.",
            target_users="middle school teachers and students",
        ))
        release = launchpad.app_release_plan(AppReleaseBrief(
            owner_user_id="owner-1",
            app_name="Learning Lab",
            package_id="com.dreamco.learninglab",
            version="1.0.0",
            targets=(StoreTarget.WEB, StoreTarget.APPLE, StoreTarget.GOOGLE_PLAY),
            privacy_policy_url="https://example.com/privacy",
            support_url="https://example.com/support",
            handles_personal_data=True,
        ))
        self.assertFalse(formation["filing_submitted"])
        self.assertEqual(prototype["status"], "ready_for_local_build")
        self.assertFalse(release["automatic_submission"])
        self.assertTrue(release["store_review_required"])

    def test_release_council_requires_every_evidence_gate(self):
        council = ReleaseCouncil()
        incomplete = council.review({"build": True, "tests": True})
        complete = council.review({name: True for name in council.REQUIRED})
        self.assertEqual(incomplete["status"], "changes_required")
        self.assertEqual(complete["status"], "approved_for_owner_submission")
        self.assertFalse(complete["automatic_external_submission"])

    def test_data_wallet_separates_use_training_sale_and_opt_out(self):
        wallet = BuddyDataWallet("owner-1")
        source = DataSource(
            source_id="work-notes",
            owner_user_id="owner-1",
            display_name="My work notes",
            encrypted_reference="vault:owner/work-notes",
            categories=(DataCategory.PROFILE, DataCategory.PREFERENCES),
            acquisition="user_upload",
            user_owns_data=True,
            resale_license_confirmed=True,
        )
        receipt = wallet.register_source(source)
        self.assertFalse(receipt["raw_data_stored_here"])
        wallet.choices.third_party_sale_or_share_enabled = True
        grant = wallet.authorize(DataPermissionRequest(
            source_id="work-notes",
            purposes=("licensed_data_package",),
            retention_days=30,
            explicit_collection_consent=True,
            third_party_license_opt_in=True,
            recipient_class="approved research organizations",
        ))
        self.assertTrue(grant["sale_or_share_opt_in"])
        opt_out = wallet.opt_out()
        self.assertEqual(opt_out["grants_revoked"], 1)
        self.assertFalse(opt_out["sale_or_share_enabled"])

    def test_data_wallet_blocks_sensitive_data_licensing(self):
        wallet = BuddyDataWallet("owner-1")
        wallet.register_source(DataSource(
            source_id="voice-notes",
            owner_user_id="owner-1",
            display_name="My voice notes",
            encrypted_reference="vault:owner/voice",
            categories=(DataCategory.VOICE,),
            acquisition="user_upload",
            user_owns_data=True,
            resale_license_confirmed=True,
        ))
        wallet.choices.third_party_sale_or_share_enabled = True
        with self.assertRaisesRegex(DataWalletError, "Sensitive personal data"):
            wallet.authorize(DataPermissionRequest(
                source_id="voice-notes",
                purposes=("licensed_data_package",),
                retention_days=7,
                explicit_collection_consent=True,
                third_party_license_opt_in=True,
                recipient_class="media partners",
            ))

    def test_subscription_manager_finds_duplicates_and_stops_before_payment(self):
        manager = BuddySubscriptionManager()
        due = time.time() + 86400
        manager.add_bill(Bill("bill-1", "Power Utility", "98.20", "USD", due, "vault:power"))
        for subscription_id in ("sub-1", "sub-2"):
            manager.add_subscription(Subscription(
                subscription_id, "Design Suite", "12.00", "USD", due, "monthly", "https://example.com/cancel"
            ))
        dashboard = manager.dashboard()
        approval = manager.payment_approval_packet("bill-1")
        self.assertEqual(dashboard["possible_duplicate_subscriptions"], [["sub-1", "sub-2"]])
        self.assertFalse(approval["payment_executed"])
        self.assertTrue(approval["one_action_only"])

    def test_task_runner_supports_multiple_tasks_and_caps_each_at_24_hours(self):
        class Adapter:
            name = "test-adapter"

            def execute(self, task):
                return {"bot": task.bot_slug, "objective": task.objective}

        runner = BuddyTaskRunner(max_concurrency=2)
        for slug in ("research-bot", "brand-builder"):
            runner.schedule(
                owner_user_id="owner-1",
                bot_slug=slug,
                objective=f"Prepare a sandbox evidence packet for {slug}.",
                max_runtime_seconds=86_400,
            )
        self.assertEqual(len(runner.run_due(Adapter(), now=time.time() + 1)), 2)
        with self.assertRaisesRegex(TaskRunnerError, "24 hours"):
            runner.schedule(
                owner_user_id="owner-1",
                bot_slug="research-bot",
                objective="Run a task for longer than the approved maximum.",
                max_runtime_seconds=86_401,
            )

    def test_live_task_approval_is_one_action_only(self):
        runner = BuddyTaskRunner()
        values = dict(
            owner_user_id="owner-1",
            bot_slug="research-bot",
            objective="Perform exactly one approved external research action.",
            live_external_action=True,
            approval_id="approval-123",
        )
        runner.schedule(**values)
        with self.assertRaisesRegex(TaskRunnerError, "only one task"):
            runner.schedule(**values)

    def test_ip_assistant_prepares_search_and_draft_without_filing(self):
        brief = IPBrief(
            owner_user_id="owner-1",
            ip_type=IPType.TRADEMARK,
            title_or_mark="Signal Works",
            description="Software services for accessible education and guided simulations.",
            owner_attests_rights=True,
        )
        assistant = BuddyIPAssistant()
        search = assistant.search_plan(brief)
        filing = assistant.filing_packet(brief, search_evidence_refs=(search["search_id"],))
        self.assertIsNone(search["legal_conclusion"])
        self.assertFalse(search["comprehensive_clearance_claimed"])
        self.assertFalse(filing["filing_submitted"])
        with self.assertRaises(IPError):
            assistant.filing_packet(IPBrief(**{**brief.__dict__, "owner_attests_rights": False}), search_evidence_refs=("evidence",))

    def test_open_source_lab_is_read_only_and_license_gated(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
            (root / "pyproject.toml").write_text("[project]\nname='sample'\n", encoding="utf-8")
            (root / "main.py").write_text("print('sample')\n", encoding="utf-8")
            lab = BuddyOpenSourceLab()
            inspection = lab.inspect(root)
            plan = lab.upgrade_plan(UpgradeRequest(
                owner_user_id="owner-1",
                buddy_instance_id="buddy-1",
                capability="Add a licensed sample capability",
                repository_path=str(root),
                license_id="MIT",
                allow_sandbox_execution=False,
            ), inspection)
            self.assertFalse(inspection["source_executed"])
            self.assertEqual(plan["status"], "execution_permission_required")
            self.assertFalse(plan["automatic_merge"])

    def test_open_source_lab_blocks_secret_bearing_upgrade_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
            (root / ".env").write_text("DO_NOT_READ=placeholder\n", encoding="utf-8")
            lab = BuddyOpenSourceLab()
            inspection = lab.inspect(root)
            with self.assertRaisesRegex(OpenSourceError, "secret"):
                lab.upgrade_plan(UpgradeRequest(
                    "owner-1", "buddy-1", "Evaluate the repository safely", str(root), "MIT"
                ), inspection)

    def test_custom_buddy_id_is_stable_and_business_tone_disables_slang(self):
        personality = PersonalityProfile({"warmth": 0.9, "directness": 0.7}, adapt_slang=True)
        profile = BuddyProfile("owner-1", "My Buddy", personality)
        self.assertEqual(profile.to_public_dict()["buddy_instance_id"], profile.to_public_dict()["buddy_instance_id"])
        self.assertTrue(personality.tone_for("casual")["slang_allowed"])
        self.assertFalse(personality.tone_for("business_deal")["slang_allowed"])
        assets = build_asset_catalog()
        self.assertEqual(len(assets["voices"]), 12)
        self.assertEqual(len(assets["avatars"]), 12)
        self.assertTrue(all(not item["real_person_reference"] for item in assets["voices"] + assets["avatars"]))

    def test_music_and_logo_systems_preserve_rights_boundaries(self):
        music = BuddyMusicArtistStudio().create_plan(
            ArtistBrief(
                owner_user_id="owner-1",
                artist_name="First Light",
                creative_direction="Original optimistic electronic songs with intimate acoustic details.",
                audience="independent music listeners",
                goals=("finish an original three-song release",),
            ),
            references=(ReferenceTrack("My Demo", "vault:music/demo", "user_owned", ("analysis", "model_training")),),
        )
        logo = BuddyLogoGenerator().generate(LogoBrief(
            brand_name="First Light",
            personality=("clear", "hopeful"),
            primary_color="#1C2A47",
            accent_color="#E2B84A",
            symbol="signal",
        ))
        self.assertFalse(music["copyrighted_catalog_scraped"])
        self.assertFalse(music["automatic_release"])
        self.assertEqual(logo["third_party_assets"], "none")
        self.assertIn("<svg", logo["svg"])
        with self.assertRaisesRegex(MusicStudioError, "model-training"):
            ReferenceTrack("Licensed Song", "vault:music/licensed", "licensed_for_analysis", ("model_training",)).validate()

    def test_generated_registry_has_200_explicitly_unimplemented_ideas(self):
        registry = build_registry()
        self.assertEqual(len(registry["revolutionary_ideas"]), 100)
        self.assertEqual(len(registry["companion_ideas"]), 100)
        ideas = registry["revolutionary_ideas"] + registry["companion_ideas"]
        self.assertEqual(len({item["id"] for item in ideas}), 200)
        self.assertTrue(all(item["status"] == "roadmap_not_implemented" for item in ideas))


if __name__ == "__main__":
    unittest.main()
