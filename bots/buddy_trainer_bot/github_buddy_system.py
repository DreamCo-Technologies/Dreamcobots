"""
GitHub Buddy System — Personal GitHub-hosted Buddy bot for each owner.

Capabilities
------------
* Generate a complete self-hostable Buddy bot repository scaffold upon purchase.
* Scaffold includes: source code, personalised datasets, configuration files,
  README with setup instructions, and a GitHub Actions CI workflow.
* Track provisioned Buddy systems by user.
* Support runtime control: start/stop/restart the user's personal Buddy instance.
* Each system is fully independent — users own the code and data.

No real GitHub API calls are made at runtime; all actions are simulated so
that no credentials or network access are required.  Production deployments
can swap the stub methods with real PyGithub / httpx calls.
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

class BuddySystemStatus(Enum):
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    STOPPED = "stopped"
    UPDATING = "updating"
    ERROR = "error"


class BuddyFocusArea(Enum):
    AI_TRAINING = "ai_training"
    ROBOTICS = "robotics"
    HUMAN_COACHING = "human_coaching"
    FULL_SUITE = "full_suite"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class BuddySystemConfig:
    """Configuration written into the user's personal Buddy repository."""
    owner_id: str
    buddy_name: str
    focus_area: BuddyFocusArea
    tier: str
    ai_model_backend: str = "openai_compatible"
    default_language: str = "en"
    enable_robotics: bool = False
    enable_human_training: bool = True
    enable_dataset_management: bool = True
    custom_greeting: str = ""

    def to_dict(self) -> dict:
        return {
            "owner_id": self.owner_id,
            "buddy_name": self.buddy_name,
            "focus_area": self.focus_area.value,
            "tier": self.tier,
            "ai_model_backend": self.ai_model_backend,
            "default_language": self.default_language,
            "enable_robotics": self.enable_robotics,
            "enable_human_training": self.enable_human_training,
            "enable_dataset_management": self.enable_dataset_management,
            "custom_greeting": self.custom_greeting,
        }


@dataclass
class BuddySystemFile:
    """A file that will be committed into the user's Buddy repository."""
    path: str
    content: str
    description: str = ""


@dataclass
class BuddySystem:
    """A personal GitHub-hosted Buddy bot system provisioned for a user."""
    system_id: str
    owner_id: str
    buddy_name: str
    github_repo_url: str
    status: BuddySystemStatus
    config: BuddySystemConfig
    files: list[BuddySystemFile] = field(default_factory=list)
    provisioned_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    runtime_logs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "system_id": self.system_id,
            "owner_id": self.owner_id,
            "buddy_name": self.buddy_name,
            "github_repo_url": self.github_repo_url,
            "status": self.status.value,
            "config": self.config.to_dict(),
            "file_count": len(self.files),
            "provisioned_at": self.provisioned_at,
            "last_updated": self.last_updated,
        }


# ---------------------------------------------------------------------------
# Scaffold templates
# ---------------------------------------------------------------------------

def _generate_readme(config: BuddySystemConfig) -> str:
    greeting = config.custom_greeting or f"Hi! I'm {config.buddy_name}, your personal AI training companion."
    return f"""# {config.buddy_name} — Personal Buddy Bot

> {greeting}

## Overview
{config.buddy_name} is your self-hosted, GitHub-powered Buddy bot, provisioned by DreamCobots.
Focus area: **{config.focus_area.value.replace('_', ' ').title()}**

## Quick Start
```bash
git clone <this-repo>
cd buddy-{config.buddy_name.lower().replace(' ', '-')}
pip install -r requirements.txt
python buddy_main.py
```

## Configuration
Edit `buddy_config.json` to personalise {config.buddy_name}.

## Features
- AI model training with adaptive feedback
- Robotics training system integration
- Human-guided training workflows
- Dataset management and labelling tools

## Runtime Control
- **Start**: `python buddy_main.py start`
- **Stop**: `python buddy_main.py stop`
- **Status**: `python buddy_main.py status`

---
*Powered by DreamCobots. Owned by you.*
"""


def _generate_main_script(config: BuddySystemConfig) -> str:
    return f'''"""
{config.buddy_name} — Personal Buddy Bot Entry Point
Auto-generated by DreamCobots BuddyTrainerBot.
Owner: {config.owner_id}
"""

import sys
import json

BUDDY_NAME = "{config.buddy_name}"
FOCUS_AREA = "{config.focus_area.value}"


def chat(message: str) -> str:
    """Simple conversational interface."""
    msg = message.lower()
    if "train" in msg and "ai" in msg:
        return f"{{BUDDY_NAME}}: Starting AI training session. Tell me your dataset and model type!"
    if "robot" in msg:
        return f"{{BUDDY_NAME}}: Robotics training mode activated. Register your robot to begin."
    if "help" in msg or "how" in msg:
        return (
            f"{{BUDDY_NAME}}: I can help you train AI models, robots, and guide you through "
            "data labelling workflows. What would you like to do?"
        )
    return f"{{BUDDY_NAME}}: Hey there! I'm your personal AI training companion. Ask me anything!"


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "chat"
    if cmd == "start":
        print(f"{{BUDDY_NAME}} is starting up...")
    elif cmd == "stop":
        print(f"{{BUDDY_NAME}} is shutting down. Goodbye!")
    elif cmd == "status":
        print(f"{{BUDDY_NAME}} is running. Focus: {{FOCUS_AREA}}")
    else:
        # Interactive chat
        print(f"{{BUDDY_NAME}}: {config.custom_greeting or 'Hello! How can I help you today?'}")
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ("exit", "quit", "bye"):
                    print(f"{{BUDDY_NAME}}: Goodbye!")
                    break
                print(chat(user_input))
            except (KeyboardInterrupt, EOFError):
                print(f"\\n{{BUDDY_NAME}}: Session ended.")
                break


if __name__ == "__main__":
    main()
'''


def _generate_requirements() -> str:
    return """# Personal Buddy Bot requirements
# Generated by DreamCobots BuddyTrainerBot
requests>=2.31.0
pydantic>=2.0.0
"""


def _generate_ci_workflow(buddy_name: str) -> str:
    safe_name = buddy_name.lower().replace(" ", "-")
    return f"""name: {buddy_name} CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run {buddy_name} smoke test
        run: python buddy_main.py status
"""


def _generate_config_json(config: BuddySystemConfig) -> str:
    import json
    return json.dumps(config.to_dict(), indent=2)


# ---------------------------------------------------------------------------
# Core class
# ---------------------------------------------------------------------------

class GitHubBuddySystem:
    """
    Provisions and manages personal GitHub-hosted Buddy bot systems.

    Each paying OWNER-tier user receives a complete, self-hostable Buddy
    repository scaffold with source code, configs, datasets, and CI.

    Parameters
    ----------
    system_manager_id : str
        Unique identifier for this manager instance.
    github_org : str
        GitHub organisation or user account under which repos are created.
    """

    def __init__(
        self,
        system_manager_id: str = "buddy_github_system_v1",
        github_org: str = "dreamcobots-users",
    ) -> None:
        self.system_manager_id = system_manager_id
        self.github_org = github_org
        self._systems: dict[str, BuddySystem] = {}   # system_id -> BuddySystem
        self._owner_systems: dict[str, str] = {}     # owner_id -> system_id

    # ------------------------------------------------------------------
    # Provisioning
    # ------------------------------------------------------------------

    def provision_buddy(
        self,
        owner_id: str,
        buddy_name: str,
        focus_area: BuddyFocusArea = BuddyFocusArea.FULL_SUITE,
        tier: str = "owner",
        custom_greeting: str = "",
        enable_robotics: bool = True,
    ) -> BuddySystem:
        """
        Provision a personal GitHub-hosted Buddy bot for an owner.

        Creates the full repository scaffold and returns the BuddySystem record.
        Raises ValueError if the owner already has a provisioned system.
        """
        if owner_id in self._owner_systems:
            existing_id = self._owner_systems[owner_id]
            raise ValueError(
                f"Owner '{owner_id}' already has a Buddy system: {existing_id}. "
                "Use update_buddy() to make changes."
            )

        config = BuddySystemConfig(
            owner_id=owner_id,
            buddy_name=buddy_name,
            focus_area=focus_area,
            tier=tier,
            enable_robotics=enable_robotics,
            custom_greeting=custom_greeting,
        )

        repo_slug = f"buddy-{buddy_name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:6]}"
        github_repo_url = f"https://github.com/{self.github_org}/{repo_slug}"
        system_id = f"sys_{uuid.uuid4().hex[:12]}"

        files = self._generate_scaffold(config)

        system = BuddySystem(
            system_id=system_id,
            owner_id=owner_id,
            buddy_name=buddy_name,
            github_repo_url=github_repo_url,
            status=BuddySystemStatus.ACTIVE,
            config=config,
            files=files,
        )
        system.runtime_logs.append(f"[{time.time():.0f}] Buddy '{buddy_name}' provisioned.")

        self._systems[system_id] = system
        self._owner_systems[owner_id] = system_id
        return system

    def _generate_scaffold(self, config: BuddySystemConfig) -> list[BuddySystemFile]:
        """Generate the full set of repository files for a personal Buddy."""
        return [
            BuddySystemFile("README.md", _generate_readme(config), "Project README"),
            BuddySystemFile("buddy_main.py", _generate_main_script(config), "Main entry point"),
            BuddySystemFile("requirements.txt", _generate_requirements(), "Python dependencies"),
            BuddySystemFile(
                "buddy_config.json", _generate_config_json(config), "Bot configuration"
            ),
            BuddySystemFile(
                ".github/workflows/ci.yml",
                _generate_ci_workflow(config.buddy_name),
                "GitHub Actions CI workflow",
            ),
        ]

    # ------------------------------------------------------------------
    # Runtime control
    # ------------------------------------------------------------------

    def get_system(self, system_id: str) -> BuddySystem:
        if system_id not in self._systems:
            raise KeyError(f"BuddySystem '{system_id}' not found.")
        return self._systems[system_id]

    def get_system_for_owner(self, owner_id: str) -> BuddySystem:
        system_id = self._owner_systems.get(owner_id)
        if system_id is None:
            raise KeyError(f"No Buddy system found for owner '{owner_id}'.")
        return self.get_system(system_id)

    def start_buddy(self, owner_id: str) -> dict:
        system = self.get_system_for_owner(owner_id)
        system.status = BuddySystemStatus.ACTIVE
        system.last_updated = time.time()
        system.runtime_logs.append(f"[{time.time():.0f}] Buddy started.")
        return {"status": "active", "system_id": system.system_id, "message": f"'{system.buddy_name}' is now running."}

    def stop_buddy(self, owner_id: str) -> dict:
        system = self.get_system_for_owner(owner_id)
        system.status = BuddySystemStatus.STOPPED
        system.last_updated = time.time()
        system.runtime_logs.append(f"[{time.time():.0f}] Buddy stopped.")
        return {"status": "stopped", "system_id": system.system_id, "message": f"'{system.buddy_name}' has been stopped."}

    def restart_buddy(self, owner_id: str) -> dict:
        self.stop_buddy(owner_id)
        return self.start_buddy(owner_id)

    def update_buddy(self, owner_id: str, **kwargs) -> BuddySystem:
        """Update configuration fields for an existing Buddy system."""
        system = self.get_system_for_owner(owner_id)
        system.status = BuddySystemStatus.UPDATING
        for key, value in kwargs.items():
            if hasattr(system.config, key):
                setattr(system.config, key, value)
        # Regenerate scaffold with updated config
        system.files = self._generate_scaffold(system.config)
        system.status = BuddySystemStatus.ACTIVE
        system.last_updated = time.time()
        system.runtime_logs.append(f"[{time.time():.0f}] Buddy updated: {list(kwargs.keys())}.")
        return system

    def list_systems(self) -> list[BuddySystem]:
        return list(self._systems.values())

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        active = sum(1 for s in self._systems.values() if s.status == BuddySystemStatus.ACTIVE)
        return {
            "system_manager_id": self.system_manager_id,
            "github_org": self.github_org,
            "total_systems": len(self._systems),
            "active_systems": active,
        }
