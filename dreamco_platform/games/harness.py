"""Local-first game build plans and adapter-based game play testing.

Buddy can build progressively larger games from a plain-language brief, but a
large production is represented honestly as milestones and verified vertical
slices. Game playing is limited to owner-authorized sandboxes or adapters; this
module does not bypass anti-cheat systems, account controls, or game terms.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any, Protocol


class GameLabError(ValueError):
    """Raised when a build or game-play request violates a lab rule."""


@dataclass(frozen=True)
class LearningDesign:
    learning_objective: str
    age_or_level: str
    evidence_of_learning: str
    teacher_controls: bool = True

    def validate(self) -> None:
        if len(self.learning_objective.strip()) < 10:
            raise GameLabError("A measurable learning objective is required.")
        if not self.age_or_level.strip() or not self.evidence_of_learning.strip():
            raise GameLabError("Learning level and evidence of learning are required.")


@dataclass(frozen=True)
class GameBuildBrief:
    title: str
    concept: str
    audience: str
    target_platforms: tuple[str, ...] = ("web",)
    scope: str = "prototype"
    multiplayer: bool = False
    learning: LearningDesign | None = None

    def validate(self) -> None:
        if len(self.title.strip()) < 3 or len(self.concept.strip()) < 20:
            raise GameLabError("A title and a detailed game concept are required.")
        if self.scope not in {"prototype", "indie", "studio", "epic"}:
            raise GameLabError("Scope must be prototype, indie, studio, or epic.")
        if not self.audience.strip() or not self.target_platforms:
            raise GameLabError("Audience and at least one target platform are required.")
        if self.learning:
            self.learning.validate()


class GameRuntimeAdapter(Protocol):
    """A supported game or simulator exposed through legal actions."""

    name: str
    owner_authorized: bool
    sandboxed: bool

    def reset(self, seed: int) -> dict[str, Any]: ...

    def legal_actions(self, observation: dict[str, Any]) -> list[str]: ...

    def step(self, action: str) -> tuple[dict[str, Any], float, bool, dict[str, Any]]: ...


class BuddyGameLab:
    """Prepare game production systems and run deterministic play tests."""

    SCOPE_PHASES = {
        "prototype": ["brief", "gameplay_slice", "playtest", "package"],
        "indie": ["brief", "vertical_slice", "content_pipeline", "alpha", "beta", "release"],
        "studio": ["preproduction", "vertical_slice", "systems", "content", "alpha", "beta", "certification", "live_ops"],
        "epic": ["preproduction", "technical_proof", "vertical_slice", "world_partition", "systems", "content_waves", "alpha", "beta", "certification", "launch", "live_ops"],
    }

    def build_plan(self, brief: GameBuildBrief) -> dict[str, Any]:
        brief.validate()
        seed = int(hashlib.sha256(brief.title.encode("utf-8")).hexdigest()[:8], 16)
        phases = [
            {
                "phase": phase,
                "approval_gate": phase in {"vertical_slice", "alpha", "beta", "certification", "launch"},
                "required_evidence": self._phase_evidence(phase),
            }
            for phase in self.SCOPE_PHASES[brief.scope]
        ]
        learning = None
        if brief.learning:
            learning = {
                **asdict(brief.learning),
                "teacher_dashboard": [
                    "assignment settings",
                    "learner progress",
                    "misconception report",
                    "accessibility settings",
                    "exportable rubric evidence",
                ],
                "student_safety": [
                    "no behavioral ads",
                    "no public chat by default",
                    "minimal student data",
                    "teacher-controlled sharing",
                ],
            }
        return {
            "schema": "dreamco.buddy_game_build.v1",
            "status": "production_plan_ready",
            "brief": asdict(brief),
            "scope_truth": "Large games require multiple approved milestones; one prompt starts and steers the production system but does not erase production time or platform certification.",
            "vibe_build_loop": [
                "prompt to design specification",
                "generate the smallest playable slice",
                "run deterministic tests and bot play sessions",
                "show the owner a live preview and evidence",
                "accept natural-language changes",
                "checkpoint before the next milestone",
            ],
            "architecture": {
                "engine_selection": "chosen from target platform, genre, team, licensing, and performance constraints",
                "world_streaming": brief.scope in {"studio", "epic"},
                "multiplayer_services": brief.multiplayer,
                "content_pipeline": True,
                "versioned_save_format": True,
                "asset_rights_manifest": True,
                "rollback_checkpoints": True,
            },
            "phases": phases,
            "learning_design": learning,
            "sandbox": {
                "seed": seed,
                "network_default": "off",
                "checks": [
                    "boot and restart",
                    "legal input handling",
                    "save and rollback",
                    "frame-time budget",
                    "accessibility controls",
                    "content and rights review",
                    "learning evidence" if brief.learning else "gameplay objective",
                ],
            },
            "publish_requires_owner_approval": True,
        }

    def play_test(
        self,
        adapter: GameRuntimeAdapter,
        *,
        max_steps: int = 100,
        seed: int = 42,
    ) -> dict[str, Any]:
        if not adapter.owner_authorized or not adapter.sandboxed:
            raise GameLabError("Game play requires an owner-authorized sandbox adapter.")
        if max_steps < 1 or max_steps > 10_000:
            raise GameLabError("Play tests must contain between 1 and 10,000 steps.")
        observation = adapter.reset(seed)
        trace: list[dict[str, Any]] = []
        total_reward = 0.0
        completed = False
        for index in range(max_steps):
            legal = adapter.legal_actions(observation)
            if not legal:
                break
            action = sorted(legal)[0]
            observation, reward, completed, info = adapter.step(action)
            total_reward += float(reward)
            trace.append({"step": index + 1, "action": action, "reward": reward, "info": info})
            if completed:
                break
        return {
            "schema": "dreamco.buddy_game_playtest.v1",
            "adapter": adapter.name,
            "status": "completed" if completed else "step_limit_or_no_legal_action",
            "steps": len(trace),
            "total_reward": total_reward,
            "trace": trace,
            "policy": {
                "owner_authorized": True,
                "sandboxed": True,
                "anti_cheat_bypass": False,
                "account_takeover": False,
            },
        }

    @staticmethod
    def _phase_evidence(phase: str) -> list[str]:
        base = ["build passes", "automated tests", "playtest trace", "known-risks log"]
        if phase in {"alpha", "beta", "certification", "launch"}:
            base.extend(["performance report", "accessibility report", "rights manifest", "rollback drill"])
        return base
