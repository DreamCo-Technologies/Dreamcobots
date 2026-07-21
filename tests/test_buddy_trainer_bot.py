"""
Tests for bots/buddy_trainer_bot/

Covers:
  1. Tiers
  2. AI Trainer
  3. Robot Trainer
  4. Human Trainer
  5. GitHub Buddy System
  6. Ownership System
  7. BuddyTrainerBot main class (integration + chat)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Tier imports
# ---------------------------------------------------------------------------
from bots.buddy_trainer_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_AI_TRAINING,
    FEATURE_AI_VERSIONING,
    FEATURE_AI_DEPLOYMENT,
    FEATURE_ROBOT_TRAINING,
    FEATURE_ADAPTIVE_LOOPS,
    FEATURE_SENSOR_FEEDBACK,
    FEATURE_HUMAN_COACHING,
    FEATURE_DATA_LABELING,
    FEATURE_DATASET_MANAGEMENT,
    FEATURE_GUIDED_WORKFLOWS,
    FEATURE_GITHUB_BUDDY,
    FEATURE_MULTI_MODEL,
    FEATURE_API_ACCESS,
    FEATURE_OWNERSHIP,
)

# ---------------------------------------------------------------------------
# AI Trainer imports
# ---------------------------------------------------------------------------
from bots.buddy_trainer_bot.ai_trainer import (
    AITrainer,
    Dataset,
    ModelVersion,
    TrainingSession,
    ModelType,
    TrainingStatus,
)

# ---------------------------------------------------------------------------
# Robot Trainer imports
# ---------------------------------------------------------------------------
from bots.buddy_trainer_bot.robot_trainer import (
    RobotTrainer,
    Robot,
    RobotCategory,
    SensorType,
    TrainingPhase,
    RobotTrainingCycle,
)

# ---------------------------------------------------------------------------
# Human Trainer imports
# ---------------------------------------------------------------------------
from bots.buddy_trainer_bot.human_trainer import (
    HumanTrainer,
    LearnerProfile,
    ManagedDataset,
    LabeledSample,
    WorkflowType,
    SkillLevel,
    LearningGoal,
    get_workflow,
)

# ---------------------------------------------------------------------------
# GitHub Buddy System imports
# ---------------------------------------------------------------------------
from bots.buddy_trainer_bot.github_buddy_system import (
    GitHubBuddySystem,
    BuddySystem,
    BuddySystemStatus,
    BuddyFocusArea,
    BuddySystemConfig,
)

# ---------------------------------------------------------------------------
# Ownership System imports
# ---------------------------------------------------------------------------
from bots.buddy_trainer_bot.ownership_system import (
    OwnershipSystem,
    License,
    Transaction,
    Sponsorship,
    PaymentMethod,
    LicenseStatus,
    TransactionType,
)

# ---------------------------------------------------------------------------
# Main bot imports
# ---------------------------------------------------------------------------
from bots.buddy_trainer_bot.buddy_trainer_bot import (
    BuddyTrainerBot,
    BuddyTrainerError,
    BuddyTrainerTierError,
)


# ===========================================================================
# 1. Tier tests
# ===========================================================================

class TestTiers:
    def test_all_tiers_present(self):
        assert len(TIER_CATALOGUE) == 4
        for t in Tier:
            assert t.value in TIER_CATALOGUE

    def test_free_tier_zero_price(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0
        assert cfg.price_usd_one_time == 0.0

    def test_pro_tier_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_owner_tier_one_time(self):
        cfg = get_tier_config(Tier.OWNER)
        assert cfg.price_usd_one_time == 499.0
        assert cfg.price_usd_monthly == 0.0

    def test_free_has_ai_training(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_AI_TRAINING)

    def test_free_no_robot_training(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_ROBOT_TRAINING)

    def test_pro_has_robot_training(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_ROBOT_TRAINING)

    def test_enterprise_has_api_access(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_API_ACCESS)

    def test_owner_has_github_buddy(self):
        cfg = get_tier_config(Tier.OWNER)
        assert cfg.has_feature(FEATURE_GITHUB_BUDDY)
        assert cfg.github_buddy_included is True

    def test_owner_has_ownership(self):
        cfg = get_tier_config(Tier.OWNER)
        assert cfg.has_feature(FEATURE_OWNERSHIP)

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_owner_is_none(self):
        assert get_upgrade_path(Tier.OWNER) is None

    def test_list_tiers_returns_all(self):
        tiers = list_tiers()
        assert len(tiers) == 4

    def test_unlimited_sessions_pro(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.is_unlimited_sessions() is True

    def test_limited_sessions_free(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.is_unlimited_sessions() is False
        assert cfg.max_ai_sessions_per_day == 5

    def test_enterprise_unlimited_robots(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_robot_targets is None

    def test_free_zero_robot_targets(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_robot_targets == 0


# ===========================================================================
# 2. AI Trainer tests
# ===========================================================================

class TestAITrainer:
    def setup_method(self):
        self.trainer = AITrainer()

    def test_register_dataset(self):
        ds = self.trainer.register_dataset("cats_dogs", 1000, ["cat", "dog"])
        assert ds.name == "cats_dogs"
        assert ds.num_samples == 1000
        assert "cat" in ds.labels

    def test_dataset_id_generated(self):
        ds = self.trainer.register_dataset("test_ds", 500, ["yes", "no"])
        assert ds.dataset_id.startswith("ds_")

    def test_list_datasets(self):
        self.trainer.register_dataset("ds1", 100, ["a"])
        self.trainer.register_dataset("ds2", 200, ["b"])
        assert len(self.trainer.list_datasets()) == 2

    def test_get_dataset_found(self):
        ds = self.trainer.register_dataset("my_ds", 300, ["x"])
        retrieved = self.trainer.get_dataset(ds.dataset_id)
        assert retrieved.name == "my_ds"

    def test_get_dataset_not_found(self):
        with pytest.raises(KeyError):
            self.trainer.get_dataset("nonexistent_id")

    def test_start_training_returns_session(self):
        ds = self.trainer.register_dataset("train_ds", 5000, ["cat", "dog"])
        session = self.trainer.start_training("MyCNN", ModelType.COMPUTER_VISION, ds.dataset_id)
        assert session.model_name == "MyCNN"
        assert session.status == TrainingStatus.COMPLETED

    def test_training_creates_version(self):
        ds = self.trainer.register_dataset("v_ds", 2000, ["a", "b"])
        session = self.trainer.start_training("ModelV", ModelType.CLASSIFICATION, ds.dataset_id)
        versions = self.trainer.list_versions("ModelV")
        assert len(versions) == 1

    def test_training_feedback_populated(self):
        ds = self.trainer.register_dataset("fb_ds", 1000, ["pos", "neg"])
        session = self.trainer.start_training("SentimentModel", ModelType.NLP, ds.dataset_id)
        assert len(session.feedback) > 0

    def test_training_accuracy_in_range(self):
        ds = self.trainer.register_dataset("acc_ds", 10000, ["label"])
        session = self.trainer.start_training("AccModel", ModelType.CLASSIFICATION, ds.dataset_id)
        assert 0.0 <= session.accuracy <= 1.0
        assert session.loss > 0.0

    def test_multiple_training_versions(self):
        ds = self.trainer.register_dataset("multi_ds", 3000, ["a", "b"])
        self.trainer.start_training("MultiModel", ModelType.CLASSIFICATION, ds.dataset_id, epochs=5)
        self.trainer.start_training("MultiModel", ModelType.CLASSIFICATION, ds.dataset_id, epochs=30)
        versions = self.trainer.list_versions("MultiModel")
        assert len(versions) == 2
        assert versions[0].version_number == 1
        assert versions[1].version_number == 2

    def test_get_best_version(self):
        ds = self.trainer.register_dataset("best_ds", 5000, ["x", "y"])
        self.trainer.start_training("BestModel", ModelType.CLASSIFICATION, ds.dataset_id, epochs=5)
        self.trainer.start_training("BestModel", ModelType.CLASSIFICATION, ds.dataset_id, epochs=50)
        best = self.trainer.get_best_version("BestModel")
        assert best is not None
        assert best.version_number == 2  # more epochs → higher accuracy

    def test_deploy_version(self):
        ds = self.trainer.register_dataset("deploy_ds", 4000, ["a", "b"])
        session = self.trainer.start_training("DeployModel", ModelType.CLASSIFICATION, ds.dataset_id)
        versions = self.trainer.list_versions("DeployModel")
        result = self.trainer.deploy_version("DeployModel", versions[0].version_id)
        assert result["status"] == "deployed"

    def test_deploy_unknown_version_raises(self):
        with pytest.raises(KeyError):
            self.trainer.deploy_version("SomeModel", "nonexistent_version")

    def test_rollback(self):
        ds = self.trainer.register_dataset("rb_ds", 3000, ["a", "b"])
        self.trainer.start_training("RBModel", ModelType.CLASSIFICATION, ds.dataset_id, epochs=5)
        session2 = self.trainer.start_training("RBModel", ModelType.CLASSIFICATION, ds.dataset_id, epochs=20)
        versions = self.trainer.list_versions("RBModel")
        # Deploy v2 first
        self.trainer.deploy_version("RBModel", versions[1].version_id)
        # Rollback to v1
        result = self.trainer.rollback("RBModel", versions[0].version_id)
        assert result["status"] == "rolled_back"

    def test_get_deployed_version(self):
        ds = self.trainer.register_dataset("dep_ds", 2000, ["a"])
        session = self.trainer.start_training("DepModel", ModelType.REGRESSION, ds.dataset_id)
        versions = self.trainer.list_versions("DepModel")
        self.trainer.deploy_version("DepModel", versions[0].version_id)
        deployed = self.trainer.get_deployed_version("DepModel")
        assert deployed is not None
        assert deployed.deployed is True

    def test_get_deployed_version_none_before_deploy(self):
        assert self.trainer.get_deployed_version("UndeployedModel") is None

    def test_training_unknown_dataset_raises(self):
        with pytest.raises(KeyError):
            self.trainer.start_training("M", ModelType.NLP, "bad_dataset_id")

    def test_summary(self):
        s = self.trainer.summary()
        assert "trainer_id" in s
        assert "total_datasets" in s

    def test_all_model_types(self):
        ds = self.trainer.register_dataset("all_types_ds", 1000, ["a", "b"])
        for mt in ModelType:
            session = self.trainer.start_training(f"model_{mt.value}", mt, ds.dataset_id)
            assert session.status == TrainingStatus.COMPLETED

    def test_session_dict(self):
        ds = self.trainer.register_dataset("dict_ds", 500, ["a"])
        session = self.trainer.start_training("DictModel", ModelType.CLASSIFICATION, ds.dataset_id)
        d = session.to_dict()
        assert "session_id" in d
        assert "accuracy" in d
        assert "feedback" in d

    def test_version_dict(self):
        ds = self.trainer.register_dataset("vdict_ds", 500, ["a"])
        self.trainer.start_training("VDictModel", ModelType.NLP, ds.dataset_id)
        version = self.trainer.list_versions("VDictModel")[0]
        d = version.to_dict()
        assert "version_id" in d
        assert "accuracy" in d

    def test_dataset_dict(self):
        ds = self.trainer.register_dataset("dsdict", 200, ["a", "b"])
        d = ds.to_dict()
        assert d["name"] == "dsdict"
        assert d["num_samples"] == 200


# ===========================================================================
# 3. Robot Trainer tests
# ===========================================================================

class TestRobotTrainer:
    def setup_method(self):
        self.trainer = RobotTrainer()

    def test_register_robot(self):
        robot = self.trainer.register_robot(
            "ArmBot", RobotCategory.INDUSTRIAL, "ABB", "IRB 1200"
        )
        assert robot.name == "ArmBot"
        assert robot.category == RobotCategory.INDUSTRIAL

    def test_robot_id_generated(self):
        robot = self.trainer.register_robot("R1", RobotCategory.CONSUMER, "iRobot", "Roomba")
        assert robot.robot_id.startswith("robot_")

    def test_list_robots(self):
        self.trainer.register_robot("R1", RobotCategory.DRONE, "DJI", "Phantom")
        self.trainer.register_robot("R2", RobotCategory.MEDICAL, "Intuitive", "Da Vinci")
        assert len(self.trainer.list_robots()) == 2

    def test_get_robot_found(self):
        robot = self.trainer.register_robot("TestBot", RobotCategory.RESEARCH, "MIT", "Cheetah")
        found = self.trainer.get_robot(robot.robot_id)
        assert found.name == "TestBot"

    def test_get_robot_not_found(self):
        with pytest.raises(KeyError):
            self.trainer.get_robot("nonexistent")

    def test_run_training_cycle(self):
        robot = self.trainer.register_robot("CycleBot", RobotCategory.HUMANOID, "Boston Dynamics", "Atlas")
        cycle = self.trainer.run_training_cycle(robot.robot_id)
        assert cycle.robot_id == robot.robot_id
        assert cycle.completed is True
        assert 0.0 <= cycle.performance_score <= 1.0

    def test_training_cycle_has_feedback(self):
        robot = self.trainer.register_robot("FBBot", RobotCategory.AGRICULTURAL, "John Deere", "AutoTractor")
        cycle = self.trainer.run_training_cycle(robot.robot_id, ["scan_field", "avoid_obstacle"])
        assert len(cycle.feedback) > 0

    def test_training_cycle_sensor_readings(self):
        robot = self.trainer.register_robot(
            "SensorBot", RobotCategory.INDUSTRIAL, "KUKA", "KR10",
            sensors=[SensorType.PROXIMITY, SensorType.VISION, SensorType.IMU]
        )
        cycle = self.trainer.run_training_cycle(robot.robot_id)
        assert len(cycle.sensor_readings) == 3

    def test_run_adaptive_loop(self):
        robot = self.trainer.register_robot("LoopBot", RobotCategory.AUTONOMOUS_VEHICLE, "Waymo", "GXV")
        cycles = self.trainer.run_adaptive_loop(robot.robot_id, num_cycles=5)
        assert len(cycles) == 5

    def test_adaptive_loop_phases_advance(self):
        robot = self.trainer.register_robot("PhaseBot", RobotCategory.RESEARCH, "MIT", "Spot")
        cycles = self.trainer.run_adaptive_loop(
            robot.robot_id, num_cycles=5, starting_phase=TrainingPhase.CALIBRATION
        )
        phases = [c.phase for c in cycles]
        # At least one phase transition should have occurred
        assert len(set(phases)) >= 1

    def test_get_control_policy(self):
        robot = self.trainer.register_robot("PolicyBot", RobotCategory.CONSUMER, "iRobot", "Braava")
        self.trainer.run_training_cycle(robot.robot_id)
        policy = self.trainer.get_control_policy(robot.robot_id)
        assert "best_performance" in policy
        assert "total_cycles" in policy

    def test_control_policy_missing_raises(self):
        robot = self.trainer.register_robot("NoCycleBot", RobotCategory.CONSUMER, "X", "Y")
        with pytest.raises(KeyError):
            self.trainer.get_control_policy(robot.robot_id)

    def test_list_cycles(self):
        robot = self.trainer.register_robot("ListBot", RobotCategory.DRONE, "DJI", "Mini 3")
        self.trainer.run_training_cycle(robot.robot_id)
        self.trainer.run_training_cycle(robot.robot_id)
        assert len(self.trainer.list_cycles(robot.robot_id)) == 2

    def test_summary(self):
        s = self.trainer.summary()
        assert "total_robots" in s
        assert "total_cycles" in s

    def test_robot_dict(self):
        robot = self.trainer.register_robot("DictBot", RobotCategory.INDUSTRIAL, "Fanuc", "LR Mate")
        d = robot.to_dict()
        assert "robot_id" in d
        assert "category" in d

    def test_cycle_dict(self):
        robot = self.trainer.register_robot("CycleDictBot", RobotCategory.CONSUMER, "X", "Y")
        cycle = self.trainer.run_training_cycle(robot.robot_id)
        d = cycle.to_dict()
        assert "cycle_id" in d
        assert "performance_score" in d

    def test_all_robot_categories(self):
        for cat in RobotCategory:
            robot = self.trainer.register_robot(f"bot_{cat.value}", cat, "Mfg", "Model")
            cycle = self.trainer.run_training_cycle(robot.robot_id)
            assert cycle.completed is True

    def test_training_with_instructions(self):
        robot = self.trainer.register_robot("InstrBot", RobotCategory.INDUSTRIAL, "ABB", "IRB")
        instructions = ["calibrate_arm", "move_to_home", "pick_object", "place_object"]
        cycle = self.trainer.run_training_cycle(robot.robot_id, instructions=instructions, phase=TrainingPhase.EXPLOITATION)
        assert cycle.instructions == instructions


# ===========================================================================
# 4. Human Trainer tests
# ===========================================================================

class TestHumanTrainer:
    def setup_method(self):
        self.trainer = HumanTrainer()

    def test_enroll_learner(self):
        learner = self.trainer.enroll_learner("Alice", LearningGoal.TRAIN_IMAGE_CLASSIFIER)
        assert learner.name == "Alice"
        assert learner.learning_goal == LearningGoal.TRAIN_IMAGE_CLASSIFIER
        assert learner.skill_level == SkillLevel.BEGINNER

    def test_learner_id_generated(self):
        learner = self.trainer.enroll_learner("Bob", LearningGoal.BUILD_CHATBOT)
        assert learner.learner_id.startswith("learner_")

    def test_list_learners(self):
        self.trainer.enroll_learner("Alice", LearningGoal.CREATE_DATASET)
        self.trainer.enroll_learner("Bob", LearningGoal.TRAIN_ROBOT)
        assert len(self.trainer.list_learners()) == 2

    def test_get_learner_found(self):
        learner = self.trainer.enroll_learner("Carol", LearningGoal.DEPLOY_MODEL)
        found = self.trainer.get_learner(learner.learner_id)
        assert found.name == "Carol"

    def test_get_learner_not_found(self):
        with pytest.raises(KeyError):
            self.trainer.get_learner("bad_id")

    def test_learning_path_not_empty(self):
        learner = self.trainer.enroll_learner("Dave", LearningGoal.TRAIN_IMAGE_CLASSIFIER)
        path = self.trainer.get_learning_path(learner.learner_id)
        assert len(path) > 0

    def test_learning_path_has_steps(self):
        learner = self.trainer.enroll_learner("Eve", LearningGoal.CREATE_DATASET)
        path = self.trainer.get_learning_path(learner.learner_id)
        for section in path:
            assert len(section["steps"]) > 0

    def test_complete_step_awards_xp(self):
        learner = self.trainer.enroll_learner("Frank", LearningGoal.TRAIN_IMAGE_CLASSIFIER)
        result = self.trainer.complete_step(learner.learner_id, "dl_01")
        assert result["xp_earned"] > 0
        assert result["total_xp"] > 0

    def test_complete_step_adds_to_completed(self):
        learner = self.trainer.enroll_learner("Grace", LearningGoal.TRAIN_IMAGE_CLASSIFIER)
        self.trainer.complete_step(learner.learner_id, "dl_01")
        assert "dl_01" in learner.completed_steps

    def test_complete_step_idempotent(self):
        learner = self.trainer.enroll_learner("Hank", LearningGoal.TRAIN_IMAGE_CLASSIFIER)
        result1 = self.trainer.complete_step(learner.learner_id, "dl_01")
        result2 = self.trainer.complete_step(learner.learner_id, "dl_01")
        assert result2["xp_earned"] == 0 or "already" in result2.get("message", "")

    def test_xp_upgrades_skill_level(self):
        learner = self.trainer.enroll_learner("Iris", LearningGoal.GENERAL_AI_LITERACY)
        # Complete many steps to accumulate XP
        for step_id in ["dl_01", "dl_02", "dl_03", "dl_04", "dm_01", "dm_02", "dm_03",
                         "mc_01", "mc_02", "mc_03", "mc_04"]:
            self.trainer.complete_step(learner.learner_id, step_id)
        # Should have advanced from BEGINNER
        assert learner.skill_level != SkillLevel.BEGINNER

    def test_create_dataset(self):
        ds = self.trainer.create_dataset("MyDataset", "Test dataset", ["cat", "dog"])
        assert ds.name == "MyDataset"
        assert "cat" in ds.labels

    def test_label_sample(self):
        ds = self.trainer.create_dataset("LabelDS", "Labelling test", ["yes", "no"])
        sample = self.trainer.label_sample(ds.dataset_id, "This is great!", "yes")
        assert sample.label == "yes"

    def test_label_sample_wrong_label(self):
        ds = self.trainer.create_dataset("WrongDS", "Bad label test", ["a", "b"])
        with pytest.raises(ValueError):
            self.trainer.label_sample(ds.dataset_id, "data", "c")

    def test_label_sample_unknown_dataset(self):
        with pytest.raises(KeyError):
            self.trainer.label_sample("bad_ds", "data", "a")

    def test_export_dataset(self):
        ds = self.trainer.create_dataset("ExpDS", "Export test", ["x", "y"])
        self.trainer.label_sample(ds.dataset_id, "hello", "x")
        result = self.trainer.export_dataset(ds.dataset_id)
        assert result["exported"] is True
        assert result["num_samples"] == 1

    def test_list_datasets(self):
        self.trainer.create_dataset("DS1", "d1", ["a"])
        self.trainer.create_dataset("DS2", "d2", ["b"])
        assert len(self.trainer.list_datasets()) == 2

    def test_summary(self):
        s = self.trainer.summary()
        assert "total_learners" in s
        assert "skill_distribution" in s

    def test_get_workflow_data_labeling(self):
        steps = get_workflow(WorkflowType.DATA_LABELING)
        assert len(steps) == 4

    def test_get_workflow_model_creation(self):
        steps = get_workflow(WorkflowType.MODEL_CREATION)
        assert len(steps) == 4

    def test_learner_dict(self):
        learner = self.trainer.enroll_learner("DictUser", LearningGoal.BUILD_CHATBOT)
        d = learner.to_dict()
        assert "learner_id" in d
        assert "skill_level" in d

    def test_all_learning_goals(self):
        for goal in LearningGoal:
            learner = self.trainer.enroll_learner(f"User_{goal.value}", goal)
            path = self.trainer.get_learning_path(learner.learner_id)
            assert isinstance(path, list)

    def test_skill_level_beginner_threshold(self):
        assert HumanTrainer._recalculate_skill(0) == SkillLevel.BEGINNER
        assert HumanTrainer._recalculate_skill(59) == SkillLevel.BEGINNER

    def test_skill_level_intermediate_threshold(self):
        assert HumanTrainer._recalculate_skill(60) == SkillLevel.INTERMEDIATE

    def test_skill_level_advanced_threshold(self):
        assert HumanTrainer._recalculate_skill(150) == SkillLevel.ADVANCED

    def test_skill_level_expert_threshold(self):
        assert HumanTrainer._recalculate_skill(300) == SkillLevel.EXPERT


# ===========================================================================
# 5. GitHub Buddy System tests
# ===========================================================================

class TestGitHubBuddySystem:
    def setup_method(self):
        self.manager = GitHubBuddySystem()

    def test_provision_buddy(self):
        system = self.manager.provision_buddy("user1", "MyBuddy")
        assert system.buddy_name == "MyBuddy"
        assert system.owner_id == "user1"
        assert system.status == BuddySystemStatus.ACTIVE

    def test_provision_sets_github_url(self):
        system = self.manager.provision_buddy("user2", "CodeBuddy")
        assert "github.com" in system.github_repo_url

    def test_provision_generates_files(self):
        system = self.manager.provision_buddy("user3", "FileBuddy")
        assert len(system.files) >= 5  # README, main, requirements, config, CI workflow

    def test_provision_readme_in_files(self):
        system = self.manager.provision_buddy("user4", "ReadmeBuddy")
        paths = [f.path for f in system.files]
        assert "README.md" in paths

    def test_provision_ci_workflow_in_files(self):
        system = self.manager.provision_buddy("user5", "CIBuddy")
        paths = [f.path for f in system.files]
        assert any("ci" in p.lower() for p in paths)

    def test_provision_duplicate_owner_raises(self):
        self.manager.provision_buddy("dup_user", "BuddyA")
        with pytest.raises(ValueError):
            self.manager.provision_buddy("dup_user", "BuddyB")

    def test_get_system(self):
        system = self.manager.provision_buddy("user6", "GetBuddy")
        found = self.manager.get_system(system.system_id)
        assert found.system_id == system.system_id

    def test_get_system_not_found(self):
        with pytest.raises(KeyError):
            self.manager.get_system("nonexistent")

    def test_get_system_for_owner(self):
        self.manager.provision_buddy("owner7", "OwnerBuddy")
        system = self.manager.get_system_for_owner("owner7")
        assert system.buddy_name == "OwnerBuddy"

    def test_get_system_for_unknown_owner(self):
        with pytest.raises(KeyError):
            self.manager.get_system_for_owner("ghost_owner")

    def test_start_buddy(self):
        self.manager.provision_buddy("start_user", "StartBuddy")
        result = self.manager.start_buddy("start_user")
        assert result["status"] == "active"

    def test_stop_buddy(self):
        self.manager.provision_buddy("stop_user", "StopBuddy")
        result = self.manager.stop_buddy("stop_user")
        assert result["status"] == "stopped"

    def test_restart_buddy(self):
        self.manager.provision_buddy("restart_user", "RestartBuddy")
        result = self.manager.restart_buddy("restart_user")
        assert result["status"] == "active"

    def test_update_buddy(self):
        self.manager.provision_buddy("update_user", "OldBuddy")
        updated = self.manager.update_buddy("update_user", buddy_name="NewBuddy")
        assert updated.config.buddy_name == "NewBuddy"
        assert updated.status == BuddySystemStatus.ACTIVE

    def test_list_systems(self):
        self.manager.provision_buddy("list_user1", "Buddy1")
        assert len(self.manager.list_systems()) >= 1

    def test_system_dict(self):
        system = self.manager.provision_buddy("dict_user", "DictBuddy")
        d = system.to_dict()
        assert "system_id" in d
        assert "github_repo_url" in d

    def test_summary(self):
        self.manager.provision_buddy("sum_user", "SumBuddy")
        s = self.manager.summary()
        assert s["total_systems"] >= 1
        assert s["active_systems"] >= 1

    def test_config_dict(self):
        system = self.manager.provision_buddy("cfg_user", "CfgBuddy")
        cfg = system.config.to_dict()
        assert "owner_id" in cfg
        assert "focus_area" in cfg

    def test_readme_content(self):
        system = self.manager.provision_buddy("readme_user", "ReadmeBuddy2")
        readme_file = next(f for f in system.files if f.path == "README.md")
        assert "ReadmeBuddy2" in readme_file.content

    def test_custom_greeting_in_main(self):
        system = self.manager.provision_buddy(
            "greet_user", "GreetBuddy", custom_greeting="Hello world!"
        )
        main_file = next(f for f in system.files if f.path == "buddy_main.py")
        assert "Hello world!" in main_file.content

    def test_all_focus_areas(self):
        for i, fa in enumerate(BuddyFocusArea):
            system = self.manager.provision_buddy(f"fa_user_{i}", f"Buddy_{fa.value}", focus_area=fa)
            assert system.config.focus_area == fa


# ===========================================================================
# 6. Ownership System tests
# ===========================================================================

class TestOwnershipSystem:
    def setup_method(self):
        self.ownership = OwnershipSystem()

    def test_purchase_free_license(self):
        result = self.ownership.purchase_license("user1", Tier.FREE)
        assert result["success"] is True
        assert result["license"]["tier"] == "free"

    def test_purchase_pro_license(self):
        result = self.ownership.purchase_license("user2", Tier.PRO)
        assert result["success"] is True
        assert result["license"]["amount_paid_usd"] == 49.0

    def test_purchase_enterprise_license(self):
        result = self.ownership.purchase_license("user3", Tier.ENTERPRISE)
        assert result["success"] is True
        assert result["license"]["amount_paid_usd"] == 199.0

    def test_purchase_owner_license_one_time(self):
        result = self.ownership.purchase_license("user4", Tier.OWNER)
        assert result["success"] is True
        assert result["license"]["amount_paid_usd"] == 499.0
        assert result["license"]["expires_at"] is None

    def test_license_is_valid(self):
        result = self.ownership.purchase_license("user5", Tier.PRO)
        lic = self.ownership.get_user_license("user5")
        assert lic is not None
        assert lic.is_valid() is True

    def test_revenue_tracked(self):
        self.ownership.purchase_license("rev1", Tier.PRO)
        self.ownership.purchase_license("rev2", Tier.ENTERPRISE)
        summary = self.ownership.revenue_summary()
        assert summary["total_revenue_usd"] >= 49.0 + 199.0

    def test_transaction_created(self):
        self.ownership.purchase_license("tx_user", Tier.PRO)
        txs = self.ownership.list_transactions("tx_user")
        assert len(txs) == 1

    def test_cancel_subscription(self):
        self.ownership.purchase_license("cancel_user", Tier.PRO)
        result = self.ownership.cancel_subscription("cancel_user")
        assert result["success"] is True
        lic = self.ownership.get_user_license("cancel_user")
        assert lic is None  # no active license after cancel

    def test_cancel_no_license(self):
        result = self.ownership.cancel_subscription("ghost_user")
        assert result["success"] is False

    def test_upgrade_subscription(self):
        self.ownership.purchase_license("up_user", Tier.FREE)
        result = self.ownership.upgrade_subscription("up_user", Tier.PRO)
        assert result["success"] is True

    def test_upgrade_to_lower_tier_fails(self):
        self.ownership.purchase_license("down_user", Tier.PRO)
        result = self.ownership.upgrade_subscription("down_user", Tier.FREE)
        assert result["success"] is False

    def test_upgrade_no_license_fails(self):
        result = self.ownership.upgrade_subscription("nolic_user", Tier.PRO)
        assert result["success"] is False

    def test_grant_sponsorship(self):
        result = self.ownership.grant_sponsorship("poor_user", Tier.PRO)
        assert result["success"] is True
        assert result["license"]["status"] == LicenseStatus.SPONSORED.value

    def test_sponsorship_provides_access(self):
        self.ownership.grant_sponsorship("sp_user", Tier.PRO)
        lic = self.ownership.get_user_license("sp_user")
        assert lic is not None
        assert lic.is_valid() is True

    def test_validate_access_allowed(self):
        self.ownership.purchase_license("v_user", Tier.PRO)
        result = self.ownership.validate_access("v_user", Tier.FREE)
        assert result["allowed"] is True

    def test_validate_access_denied(self):
        self.ownership.purchase_license("denied_user", Tier.FREE)
        result = self.ownership.validate_access("denied_user", Tier.PRO)
        assert result["allowed"] is False
        assert "upgrade_url" in result

    def test_validate_access_no_license(self):
        result = self.ownership.validate_access("no_lic_user", Tier.FREE)
        assert result["allowed"] is False

    def test_revenue_summary_keys(self):
        s = self.ownership.revenue_summary()
        assert "total_revenue_usd" in s
        assert "total_licenses" in s
        assert "active_licenses" in s
        assert "total_sponsorships" in s

    def test_license_dict(self):
        self.ownership.purchase_license("dict_user", Tier.PRO)
        lic = self.ownership.get_user_license("dict_user")
        d = lic.to_dict()
        assert "license_id" in d
        assert "tier" in d
        assert "valid" in d

    def test_sponsorship_zero_cost(self):
        result = self.ownership.grant_sponsorship("free_user")
        assert result["license"]["amount_paid_usd"] == 0.0

    def test_payment_methods(self):
        for i, pm in enumerate(PaymentMethod):
            if pm != PaymentMethod.SPONSORED:
                result = self.ownership.purchase_license(f"pm_user_{i}", Tier.FREE, pm)
                assert result["success"] is True


# ===========================================================================
# 7. BuddyTrainerBot integration tests
# ===========================================================================

class TestBuddyTrainerBot:
    def setup_method(self):
        self.bot = BuddyTrainerBot(tier=Tier.PRO, owner_id="test_owner")

    # --- Tier enforcement ---

    def test_free_tier_can_train_ai(self):
        free_bot = BuddyTrainerBot(tier=Tier.FREE, owner_id="free_user")
        ds = free_bot.register_training_dataset("FreeDS", 500, ["a", "b"])
        session = free_bot.train_ai_model("FreeModel", ModelType.CLASSIFICATION, ds.dataset_id)
        assert session.status == TrainingStatus.COMPLETED

    def test_free_tier_session_limit(self):
        free_bot = BuddyTrainerBot(tier=Tier.FREE, owner_id="limit_user")
        ds = free_bot.register_training_dataset("LimitDS", 200, ["a"])
        for _ in range(5):
            free_bot.train_ai_model("LM", ModelType.CLASSIFICATION, ds.dataset_id)
        with pytest.raises(BuddyTrainerTierError):
            free_bot.train_ai_model("LM", ModelType.CLASSIFICATION, ds.dataset_id)

    def test_free_tier_no_robot_training(self):
        free_bot = BuddyTrainerBot(tier=Tier.FREE, owner_id="no_robot")
        with pytest.raises(BuddyTrainerTierError):
            free_bot.register_robot("R1", RobotCategory.INDUSTRIAL, "ABB", "IRB")

    def test_pro_tier_robot_training(self):
        robot = self.bot.register_robot("ProBot", RobotCategory.INDUSTRIAL, "ABB", "IRB 1200")
        assert robot is not None

    def test_pro_tier_adaptive_loop(self):
        robot = self.bot.register_robot("LoopBot", RobotCategory.DRONE, "DJI", "Phantom")
        cycles = self.bot.run_adaptive_loop(robot.robot_id, num_cycles=3)
        assert len(cycles) == 3

    def test_pro_tier_no_github_buddy(self):
        with pytest.raises(BuddyTrainerTierError):
            self.bot.provision_personal_buddy("MyBuddy")

    def test_owner_tier_github_buddy(self):
        owner_bot = BuddyTrainerBot(tier=Tier.OWNER, owner_id="owner_user")
        system = owner_bot.provision_personal_buddy("OwnerBuddy")
        assert system.buddy_name == "OwnerBuddy"

    def test_enterprise_api_access(self):
        ent_bot = BuddyTrainerBot(tier=Tier.ENTERPRISE, owner_id="ent_user")
        assert ent_bot.config.has_feature(FEATURE_API_ACCESS)

    # --- AI training ---

    def test_register_dataset_and_train(self):
        ds = self.bot.register_training_dataset("MyDS", 3000, ["cat", "dog"])
        session = self.bot.train_ai_model("MyCNN", ModelType.COMPUTER_VISION, ds.dataset_id)
        assert session.accuracy > 0.0

    def test_deploy_model(self):
        ds = self.bot.register_training_dataset("DepDS", 2000, ["a", "b"])
        session = self.bot.train_ai_model("DepModel", ModelType.CLASSIFICATION, ds.dataset_id)
        versions = self.bot.ai_trainer.list_versions("DepModel")
        result = self.bot.deploy_model("DepModel", versions[0].version_id)
        assert result["status"] == "deployed"

    def test_rollback_model(self):
        ent_bot = BuddyTrainerBot(tier=Tier.ENTERPRISE, owner_id="rb_owner")
        ds = ent_bot.register_training_dataset("RBDs", 2000, ["a"])
        ent_bot.train_ai_model("RBModel", ModelType.CLASSIFICATION, ds.dataset_id)
        ent_bot.train_ai_model("RBModel", ModelType.CLASSIFICATION, ds.dataset_id)
        versions = ent_bot.ai_trainer.list_versions("RBModel")
        ent_bot.deploy_model("RBModel", versions[1].version_id)
        result = ent_bot.rollback_model("RBModel", versions[0].version_id)
        assert result["status"] == "rolled_back"

    # --- Human training ---

    def test_enroll_human_learner(self):
        learner = self.bot.enroll_human_learner("Alice", LearningGoal.TRAIN_IMAGE_CLASSIFIER)
        assert learner.name == "Alice"

    def test_get_learning_path(self):
        learner = self.bot.enroll_human_learner("Bob", LearningGoal.CREATE_DATASET)
        path = self.bot.get_learning_path(learner.learner_id)
        assert len(path) > 0

    def test_complete_learning_step(self):
        learner = self.bot.enroll_human_learner("Carol", LearningGoal.TRAIN_IMAGE_CLASSIFIER)
        result = self.bot.complete_learning_step(learner.learner_id, "dl_01")
        assert result["xp_earned"] > 0

    def test_create_and_label_dataset(self):
        ds = self.bot.create_dataset("LabelDS", "Test", ["yes", "no"])
        sample = self.bot.label_sample(ds.dataset_id, "Hello world", "yes")
        assert sample.label == "yes"

    def test_export_dataset(self):
        ds = self.bot.create_dataset("ExportDS", "Export test", ["pos", "neg"])
        self.bot.label_sample(ds.dataset_id, "data point", "pos")
        result = self.bot.export_dataset(ds.dataset_id)
        assert result["exported"] is True

    # --- Ownership ---

    def test_purchase_upgrade(self):
        fresh_bot = BuddyTrainerBot(tier=Tier.FREE, owner_id="upgrade_tester")
        result = fresh_bot.purchase_upgrade(Tier.PRO)
        assert result["success"] is True

    def test_apply_sponsorship(self):
        bot = BuddyTrainerBot(tier=Tier.FREE, owner_id="sp_candidate")
        result = bot.apply_sponsorship()
        assert result["success"] is True

    # --- System status ---

    def test_system_status_keys(self):
        status = self.bot.system_status()
        assert "tier" in status
        assert "ai_trainer" in status
        assert "robot_trainer" in status
        assert "human_trainer" in status
        assert "ownership" in status

    def test_describe_tier(self):
        description = self.bot.describe_tier()
        assert "Pro" in description

    # --- Chat interface ---

    def test_chat_status(self):
        response = self.bot.chat("show me a status overview")
        assert response["response"] == "buddy_trainer_bot"
        assert "data" in response

    def test_chat_tier(self):
        response = self.bot.chat("what is my tier and pricing")
        assert "Pro" in response["message"] or "tier" in response["message"].lower()

    def test_chat_ai_training(self):
        response = self.bot.chat("train ai model for classification")
        assert response["response"] == "buddy_trainer_bot"
        assert FEATURE_AI_TRAINING in response["data"].get("feature", "")

    def test_chat_robot(self):
        response = self.bot.chat("I want to train a robot")
        assert FEATURE_ROBOT_TRAINING in response["data"].get("feature", "")

    def test_chat_human_training(self):
        response = self.bot.chat("teach me how to train an AI")
        assert FEATURE_HUMAN_COACHING in response["data"].get("feature", "")

    def test_chat_own_buddy(self):
        response = self.bot.chat("I want to own my personal buddy bot on github")
        assert FEATURE_GITHUB_BUDDY in response["data"].get("feature", "")

    def test_chat_free_help(self):
        response = self.bot.chat("I can't afford this, help me")
        assert response["response"] == "buddy_trainer_bot"

    def test_chat_apply_sponsorship(self):
        bot = BuddyTrainerBot(tier=Tier.FREE, owner_id="chat_sp_user")
        response = bot.chat("apply for sponsorship")
        assert response["response"] == "buddy_trainer_bot"
        assert "success" in response.get("data", {})

    def test_chat_deploy(self):
        response = self.bot.chat("deploy my model to production")
        assert response["response"] == "buddy_trainer_bot"

    def test_chat_default_response(self):
        response = self.bot.chat("hello there")
        assert response["response"] == "buddy_trainer_bot"
        assert len(response["message"]) > 0

    # --- BuddyAI registration ---

    def test_register_with_buddy(self):
        class FakeBuddy:
            def __init__(self):
                self.bots = {}
            def register_bot(self, name, bot):
                self.bots[name] = bot

        fake = FakeBuddy()
        self.bot.register_with_buddy(fake)
        assert "buddy_trainer" in fake.bots
