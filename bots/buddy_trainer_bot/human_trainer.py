"""
Human Trainer — Guided AI training workflows for human users.

Capabilities
------------
* Enroll human learners and track their skill progression.
* Step-by-step guided workflows for data labeling, dataset management,
  and AI model creation.
* Interactive Q&A coaching sessions with adaptive recommendations.
* Skill-level tracking: Beginner → Intermediate → Advanced → Expert.
* Generate personalised learning paths based on the learner's goal.
* Dataset management: create, curate, and export labelled datasets.

No external ML or NLP dependencies — all logic is deterministic/rule-based.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class SkillLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class WorkflowType(Enum):
    DATA_LABELING = "data_labeling"
    DATASET_MANAGEMENT = "dataset_management"
    MODEL_CREATION = "model_creation"
    MODEL_EVALUATION = "model_evaluation"
    ROBOTICS_PROGRAMMING = "robotics_programming"
    AI_DEPLOYMENT = "ai_deployment"


class LearningGoal(Enum):
    TRAIN_IMAGE_CLASSIFIER = "train_image_classifier"
    TRAIN_TEXT_CLASSIFIER = "train_text_classifier"
    BUILD_CHATBOT = "build_chatbot"
    TRAIN_ROBOT = "train_robot"
    CREATE_DATASET = "create_dataset"
    DEPLOY_MODEL = "deploy_model"
    GENERAL_AI_LITERACY = "general_ai_literacy"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class LabeledSample:
    """A single labelled data sample in a dataset."""
    sample_id: str
    raw_data: str          # text description or file reference
    label: str
    confidence: float = 1.0
    labeled_by: str = "human"
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "sample_id": self.sample_id,
            "raw_data": self.raw_data,
            "label": self.label,
            "confidence": self.confidence,
            "labeled_by": self.labeled_by,
        }


@dataclass
class ManagedDataset:
    """A dataset created and managed through the human trainer workflows."""
    dataset_id: str
    name: str
    description: str
    labels: list[str]
    samples: list[LabeledSample] = field(default_factory=list)
    created_by: str = "user"
    created_at: float = field(default_factory=time.time)
    exported: bool = False

    def to_dict(self) -> dict:
        return {
            "dataset_id": self.dataset_id,
            "name": self.name,
            "description": self.description,
            "labels": self.labels,
            "num_samples": len(self.samples),
            "created_by": self.created_by,
            "exported": self.exported,
        }


@dataclass
class LearnerProfile:
    """Tracks a human learner's progress through the training platform."""
    learner_id: str
    name: str
    skill_level: SkillLevel
    learning_goal: LearningGoal
    completed_steps: list[str] = field(default_factory=list)
    xp: int = 0
    enrolled_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "learner_id": self.learner_id,
            "name": self.name,
            "skill_level": self.skill_level.value,
            "learning_goal": self.learning_goal.value,
            "completed_steps": self.completed_steps,
            "xp": self.xp,
            "enrolled_at": self.enrolled_at,
        }


@dataclass
class WorkflowStep:
    """A single step within a guided training workflow."""
    step_id: str
    title: str
    description: str
    instructions: list[str]
    tips: list[str]
    xp_reward: int

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "title": self.title,
            "description": self.description,
            "instructions": self.instructions,
            "tips": self.tips,
            "xp_reward": self.xp_reward,
        }


# ---------------------------------------------------------------------------
# Workflow definitions
# ---------------------------------------------------------------------------

_WORKFLOWS: dict[WorkflowType, list[WorkflowStep]] = {
    WorkflowType.DATA_LABELING: [
        WorkflowStep(
            step_id="dl_01",
            title="Understand Your Task",
            description="Define what you want the AI to learn.",
            instructions=[
                "Write a clear one-sentence description of your labelling task.",
                "List all possible labels (e.g. 'cat', 'dog', 'bird').",
            ],
            tips=["Keep labels mutually exclusive for best results."],
            xp_reward=10,
        ),
        WorkflowStep(
            step_id="dl_02",
            title="Collect Raw Data",
            description="Gather at least 100 samples per label.",
            instructions=[
                "Upload images, text, or sensor data to Buddy's dataset manager.",
                "Aim for diversity — different lighting, angles, authors, etc.",
            ],
            tips=["More data = better accuracy. Aim for 500+ samples per label."],
            xp_reward=20,
        ),
        WorkflowStep(
            step_id="dl_03",
            title="Label Your Data",
            description="Assign the correct label to each sample.",
            instructions=[
                "For each sample, select the most appropriate label.",
                "Use Buddy's label_sample() method to record your annotations.",
            ],
            tips=["If unsure, mark with low confidence so Buddy can flag for review."],
            xp_reward=30,
        ),
        WorkflowStep(
            step_id="dl_04",
            title="Review and Export",
            description="Check for labelling errors then export your dataset.",
            instructions=[
                "Run Buddy's dataset review to find low-confidence labels.",
                "Correct any mistakes, then call export_dataset().",
            ],
            tips=["Aim for >95% labelling confidence before training."],
            xp_reward=20,
        ),
    ],
    WorkflowType.DATASET_MANAGEMENT: [
        WorkflowStep(
            step_id="dm_01",
            title="Create a Dataset",
            description="Define your dataset schema and metadata.",
            instructions=[
                "Give your dataset a descriptive name.",
                "Specify the label classes and data types.",
            ],
            tips=["Include version numbers in dataset names for traceability."],
            xp_reward=10,
        ),
        WorkflowStep(
            step_id="dm_02",
            title="Ingest Data",
            description="Load raw samples into the dataset.",
            instructions=[
                "Upload files or connect a live data source.",
                "Buddy will auto-detect duplicates and format issues.",
            ],
            tips=["Split data 80/10/10 for train/validation/test from the start."],
            xp_reward=20,
        ),
        WorkflowStep(
            step_id="dm_03",
            title="Curate and Clean",
            description="Remove low-quality or mislabelled samples.",
            instructions=[
                "Use Buddy's quality checker to surface suspicious entries.",
                "Delete or re-label any flagged samples.",
            ],
            tips=["Clean data is more valuable than large, noisy data."],
            xp_reward=25,
        ),
    ],
    WorkflowType.MODEL_CREATION: [
        WorkflowStep(
            step_id="mc_01",
            title="Choose Model Architecture",
            description="Select the right model type for your task.",
            instructions=[
                "Tell Buddy your goal (e.g. 'classify images', 'answer questions').",
                "Buddy will recommend an architecture and starting hyperparameters.",
            ],
            tips=["Start simple — a small model trained well beats a large model trained poorly."],
            xp_reward=15,
        ),
        WorkflowStep(
            step_id="mc_02",
            title="Configure Training",
            description="Set epochs, learning rate, and batch size.",
            instructions=[
                "Use Buddy's start_training() with your dataset ID.",
                "Start with epochs=20, learning_rate=0.001.",
            ],
            tips=["Monitor validation loss — stop if it starts increasing (overfitting)."],
            xp_reward=20,
        ),
        WorkflowStep(
            step_id="mc_03",
            title="Evaluate and Iterate",
            description="Review Buddy's adaptive feedback and improve.",
            instructions=[
                "Read the feedback field in your training session result.",
                "Adjust parameters and re-train as Buddy suggests.",
            ],
            tips=["Three iterations of tuning are usually enough to reach a good baseline."],
            xp_reward=25,
        ),
        WorkflowStep(
            step_id="mc_04",
            title="Deploy Your Model",
            description="Push the best version of your model to production.",
            instructions=[
                "Call deploy_version() with the version ID from get_best_version().",
                "Buddy will confirm the deployment and provide a live endpoint.",
            ],
            tips=["Always test on held-out data before deploying publicly."],
            xp_reward=30,
        ),
    ],
}


def get_workflow(workflow_type: WorkflowType) -> list[WorkflowStep]:
    return list(_WORKFLOWS.get(workflow_type, []))


# ---------------------------------------------------------------------------
# Core class
# ---------------------------------------------------------------------------

class HumanTrainer:
    """
    Trains humans to build, label, and deploy AI models through guided,
    conversational workflows.

    Parameters
    ----------
    trainer_id : str
        Unique identifier for this human trainer instance.
    """

    def __init__(self, trainer_id: str = "buddy_human_trainer_v1") -> None:
        self.trainer_id = trainer_id
        self._learners: dict[str, LearnerProfile] = {}
        self._datasets: dict[str, ManagedDataset] = {}

    # ------------------------------------------------------------------
    # Learner management
    # ------------------------------------------------------------------

    def enroll_learner(
        self,
        name: str,
        learning_goal: LearningGoal,
        skill_level: SkillLevel = SkillLevel.BEGINNER,
    ) -> LearnerProfile:
        """Enroll a new human learner on the platform."""
        learner_id = f"learner_{uuid.uuid4().hex[:10]}"
        profile = LearnerProfile(
            learner_id=learner_id,
            name=name,
            skill_level=skill_level,
            learning_goal=learning_goal,
        )
        self._learners[learner_id] = profile
        return profile

    def get_learner(self, learner_id: str) -> LearnerProfile:
        if learner_id not in self._learners:
            raise KeyError(f"Learner '{learner_id}' not found.")
        return self._learners[learner_id]

    def list_learners(self) -> list[LearnerProfile]:
        return list(self._learners.values())

    # ------------------------------------------------------------------
    # Guided workflows
    # ------------------------------------------------------------------

    def get_learning_path(self, learner_id: str) -> list[dict]:
        """
        Return a personalised learning path for a learner based on their goal.
        """
        learner = self.get_learner(learner_id)
        goal_to_workflows: dict[LearningGoal, list[WorkflowType]] = {
            LearningGoal.TRAIN_IMAGE_CLASSIFIER: [
                WorkflowType.DATA_LABELING,
                WorkflowType.DATASET_MANAGEMENT,
                WorkflowType.MODEL_CREATION,
            ],
            LearningGoal.TRAIN_TEXT_CLASSIFIER: [
                WorkflowType.DATA_LABELING,
                WorkflowType.MODEL_CREATION,
            ],
            LearningGoal.BUILD_CHATBOT: [
                WorkflowType.DATASET_MANAGEMENT,
                WorkflowType.MODEL_CREATION,
                WorkflowType.AI_DEPLOYMENT,
            ],
            LearningGoal.TRAIN_ROBOT: [
                WorkflowType.DATA_LABELING,
                WorkflowType.ROBOTICS_PROGRAMMING,
                WorkflowType.MODEL_CREATION,
            ],
            LearningGoal.CREATE_DATASET: [
                WorkflowType.DATA_LABELING,
                WorkflowType.DATASET_MANAGEMENT,
            ],
            LearningGoal.DEPLOY_MODEL: [
                WorkflowType.MODEL_EVALUATION,
                WorkflowType.AI_DEPLOYMENT,
            ],
            LearningGoal.GENERAL_AI_LITERACY: [
                WorkflowType.DATA_LABELING,
                WorkflowType.DATASET_MANAGEMENT,
                WorkflowType.MODEL_CREATION,
            ],
        }
        workflow_types = goal_to_workflows.get(
            learner.learning_goal,
            [WorkflowType.DATA_LABELING, WorkflowType.MODEL_CREATION],
        )
        path: list[dict] = []
        for wt in workflow_types:
            steps = get_workflow(wt)
            path.append({
                "workflow": wt.value,
                "steps": [s.to_dict() for s in steps],
                "total_xp": sum(s.xp_reward for s in steps),
            })
        return path

    def complete_step(self, learner_id: str, step_id: str) -> dict:
        """
        Mark a workflow step as completed and award XP.

        Returns the updated learner profile summary.
        """
        learner = self.get_learner(learner_id)
        if step_id in learner.completed_steps:
            return {
                "learner_id": learner_id,
                "step_id": step_id,
                "xp_earned": 0,
                "message": f"Step '{step_id}' was already completed.",
                "xp": learner.xp,
                "skill_level": learner.skill_level.value,
            }

        # Find XP reward for the step
        xp_reward = 10  # default
        for steps in _WORKFLOWS.values():
            for step in steps:
                if step.step_id == step_id:
                    xp_reward = step.xp_reward
                    break

        learner.completed_steps.append(step_id)
        learner.xp += xp_reward
        learner.last_active = time.time()
        learner.skill_level = self._recalculate_skill(learner.xp)

        return {
            "learner_id": learner_id,
            "step_id": step_id,
            "xp_earned": xp_reward,
            "total_xp": learner.xp,
            "skill_level": learner.skill_level.value,
            "message": f"Step '{step_id}' completed! You earned {xp_reward} XP.",
        }

    @staticmethod
    def _recalculate_skill(xp: int) -> SkillLevel:
        if xp >= 300:
            return SkillLevel.EXPERT
        if xp >= 150:
            return SkillLevel.ADVANCED
        if xp >= 60:
            return SkillLevel.INTERMEDIATE
        return SkillLevel.BEGINNER

    # ------------------------------------------------------------------
    # Dataset management
    # ------------------------------------------------------------------

    def create_dataset(
        self,
        name: str,
        description: str,
        labels: list[str],
        created_by: str = "user",
    ) -> ManagedDataset:
        dataset_id = f"mds_{uuid.uuid4().hex[:10]}"
        ds = ManagedDataset(
            dataset_id=dataset_id,
            name=name,
            description=description,
            labels=labels,
            created_by=created_by,
        )
        self._datasets[dataset_id] = ds
        return ds

    def label_sample(
        self,
        dataset_id: str,
        raw_data: str,
        label: str,
        confidence: float = 1.0,
        labeled_by: str = "human",
    ) -> LabeledSample:
        """Add a single labelled sample to a dataset."""
        if dataset_id not in self._datasets:
            raise KeyError(f"Dataset '{dataset_id}' not found.")
        ds = self._datasets[dataset_id]
        if label not in ds.labels:
            raise ValueError(
                f"Label '{label}' is not in the dataset's label set: {ds.labels}"
            )
        sample_id = f"samp_{uuid.uuid4().hex[:8]}"
        sample = LabeledSample(
            sample_id=sample_id,
            raw_data=raw_data,
            label=label,
            confidence=confidence,
            labeled_by=labeled_by,
        )
        ds.samples.append(sample)
        return sample

    def get_dataset(self, dataset_id: str) -> ManagedDataset:
        if dataset_id not in self._datasets:
            raise KeyError(f"Dataset '{dataset_id}' not found.")
        return self._datasets[dataset_id]

    def export_dataset(self, dataset_id: str) -> dict:
        """Mark a dataset as exported and return an export manifest."""
        ds = self.get_dataset(dataset_id)
        ds.exported = True
        return {
            "dataset_id": dataset_id,
            "name": ds.name,
            "num_samples": len(ds.samples),
            "labels": ds.labels,
            "samples": [s.to_dict() for s in ds.samples],
            "exported": True,
            "message": f"Dataset '{ds.name}' exported with {len(ds.samples)} samples.",
        }

    def list_datasets(self) -> list[ManagedDataset]:
        return list(self._datasets.values())

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        return {
            "trainer_id": self.trainer_id,
            "total_learners": len(self._learners),
            "total_datasets": len(self._datasets),
            "skill_distribution": {
                level.value: sum(
                    1 for l in self._learners.values() if l.skill_level == level
                )
                for level in SkillLevel
            },
        }
