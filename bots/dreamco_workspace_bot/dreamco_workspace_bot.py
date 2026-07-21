"""DreamCo Workspace Bot — GitHub Codespaces competitor for cloud dev workspaces."""
import sys
import os
import uuid
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.dreamco_workspace_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class DreamCoWorkspaceBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class DreamCoWorkspaceBotError(Exception):
    """Raised when a workspace operation fails."""


class WorkspaceEnvironment:
    """Represents a cloud development workspace environment."""

    STATUSES = ("starting", "running", "sleeping", "stopped")

    def __init__(self, env_id: str, name: str, image: str,
                 repo_url: str = "", user_id: str = "user"):
        self.env_id = env_id
        self.name = name
        self.image = image
        self.repo_url = repo_url
        self.user_id = user_id
        self.status = "running"
        self.ports: list = []
        self.created_at = time.time()
        self.dotfiles_repo: str = ""

    def to_dict(self) -> dict:
        return {
            "env_id": self.env_id,
            "name": self.name,
            "image": self.image,
            "repo_url": self.repo_url,
            "user_id": self.user_id,
            "status": self.status,
            "ports": list(self.ports),
            "created_at": self.created_at,
            "dotfiles_repo": self.dotfiles_repo,
            "access_url": f"https://workspace.dreamco.ai/{self.env_id}",
        }


class DreamCoWorkspaceBot:
    """
    DreamCo Workspace Bot — autonomous cloud development workspace competing
    with GitHub Codespaces.

    Provides instantly ready cloud dev environments, IDE integration, port
    forwarding, custom images, and team collaboration.

    Tiers
    -----
    FREE       : 1 workspace, 2 GB storage, 2-hour auto-sleep.
    PRO        : 5 workspaces, 32 GB storage, full IDE, port forwarding.
    ENTERPRISE : Unlimited workspaces, GPU, SSO, SLA, custom images.
    """

    WORKSPACE_LIMITS = {
        Tier.FREE: 1,
        Tier.PRO: 5,
        Tier.ENTERPRISE: None,
    }

    STORAGE_GB = {
        Tier.FREE: 2,
        Tier.PRO: 32,
        Tier.ENTERPRISE: None,
    }

    DEFAULT_IMAGES = [
        "dreamco/ubuntu-22.04",
        "dreamco/python-3.11",
        "dreamco/node-20",
        "dreamco/golang-1.21",
        "dreamco/java-17",
    ]

    def __init__(self, tier: Tier = Tier.FREE, user_id: str = "user"):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.user_id = user_id
        self._environments: dict = {}

    # ------------------------------------------------------------------
    # Tier enforcement
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if feature not in BOT_FEATURES[self.tier.value]:
            upgrade = get_upgrade_path(self.tier)
            raise DreamCoWorkspaceBotTierError(
                f"Feature '{feature}' is not available on the {self.config.name} tier. "
                f"Upgrade to {upgrade} for access."
            )

    def _check_workspace_limit(self) -> None:
        limit = self.WORKSPACE_LIMITS[self.tier]
        if limit is not None and len(self._environments) >= limit:
            raise DreamCoWorkspaceBotTierError(
                f"Workspace limit of {limit} reached on {self.config.name} tier. "
                f"Upgrade to create more workspaces."
            )

    # ------------------------------------------------------------------
    # Environment management
    # ------------------------------------------------------------------

    def create_workspace(self, name: str, image: str = "dreamco/ubuntu-22.04",
                         repo_url: str = "") -> WorkspaceEnvironment:
        """
        Create a new cloud workspace environment.

        Parameters
        ----------
        name : str
            Human-readable name for the workspace.
        image : str
            Base container image for the environment.
        repo_url : str
            Optional Git repository to clone into the workspace.

        Returns
        -------
        WorkspaceEnvironment
        """
        self._check_workspace_limit()
        env = WorkspaceEnvironment(
            env_id=str(uuid.uuid4()),
            name=name,
            image=image,
            repo_url=repo_url,
            user_id=self.user_id,
        )
        self._environments[env.env_id] = env
        return env

    def get_workspace(self, env_id: str) -> WorkspaceEnvironment:
        """Return an existing workspace by ID."""
        if env_id not in self._environments:
            raise DreamCoWorkspaceBotError(f"Workspace '{env_id}' not found.")
        return self._environments[env_id]

    def list_workspaces(self) -> list:
        """Return all workspaces for this user."""
        return [env.to_dict() for env in self._environments.values()]

    def stop_workspace(self, env_id: str) -> dict:
        """Stop a running workspace."""
        env = self.get_workspace(env_id)
        env.status = "stopped"
        return {"env_id": env_id, "status": "stopped"}

    def delete_workspace(self, env_id: str) -> dict:
        """Permanently delete a workspace."""
        if env_id not in self._environments:
            raise DreamCoWorkspaceBotError(f"Workspace '{env_id}' not found.")
        del self._environments[env_id]
        return {"env_id": env_id, "deleted": True}

    # ------------------------------------------------------------------
    # Port forwarding (PRO+)
    # ------------------------------------------------------------------

    def forward_port(self, env_id: str, port: int) -> dict:
        """
        Expose a port from the workspace to a public URL.
        Requires PRO tier or higher.
        """
        if self.tier == Tier.FREE:
            raise DreamCoWorkspaceBotTierError(
                f"Port forwarding not available on {self.config.name} tier. "
                f"Upgrade to PRO or ENTERPRISE."
            )
        env = self.get_workspace(env_id)
        if port not in env.ports:
            env.ports.append(port)
        return {
            "env_id": env_id,
            "port": port,
            "public_url": f"https://{env_id[:8]}-{port}.workspace.dreamco.ai",
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # Dotfiles (PRO+)
    # ------------------------------------------------------------------

    def set_dotfiles(self, env_id: str, dotfiles_repo: str) -> dict:
        """
        Configure a dotfiles repository for automatic setup.
        Requires PRO tier or higher.
        """
        if self.tier == Tier.FREE:
            raise DreamCoWorkspaceBotTierError(
                f"Dotfiles support not available on {self.config.name} tier. "
                f"Upgrade to PRO or ENTERPRISE."
            )
        env = self.get_workspace(env_id)
        env.dotfiles_repo = dotfiles_repo
        return {
            "env_id": env_id,
            "dotfiles_repo": dotfiles_repo,
            "status": "configured",
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # Custom images (ENTERPRISE)
    # ------------------------------------------------------------------

    def create_custom_image(self, image_name: str, dockerfile: str) -> dict:
        """
        Build and register a custom Docker image for workspaces.
        Requires ENTERPRISE tier.
        """
        if self.tier != Tier.ENTERPRISE:
            raise DreamCoWorkspaceBotTierError(
                f"Custom Docker images not available on {self.config.name} tier. "
                f"Upgrade to ENTERPRISE."
            )
        return {
            "image_name": image_name,
            "build_id": str(uuid.uuid4()),
            "status": "building",
            "estimated_minutes": 3,
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # Available images
    # ------------------------------------------------------------------

    def list_images(self) -> list:
        """Return available base images for workspace creation."""
        images = list(self.DEFAULT_IMAGES)
        if self.tier == Tier.ENTERPRISE:
            images.append("dreamco/gpu-cuda-12")
            images.append("dreamco/ml-pytorch-2")
        return images

    # ------------------------------------------------------------------
    # Workspace stats
    # ------------------------------------------------------------------

    def get_workspace_stats(self) -> dict:
        """Return workspace usage statistics."""
        limit = self.WORKSPACE_LIMITS[self.tier]
        storage = self.STORAGE_GB[self.tier]
        return {
            "workspaces_used": len(self._environments),
            "workspaces_limit": limit,
            "workspaces_remaining": (limit - len(self._environments)) if limit is not None else None,
            "storage_gb": storage,
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # Tier info
    # ------------------------------------------------------------------

    def get_tier_info(self) -> dict:
        """Return tier configuration and feature details."""
        return get_bot_tier_info(self.tier)

    # ------------------------------------------------------------------
    # Chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """Unified natural-language chat interface."""
        msg = message.lower()

        if any(kw in msg for kw in ("create workspace", "new workspace", "new environment")):
            env = self.create_workspace("My Workspace")
            return {
                "message": f"Workspace '{env.name}' created. Access it at {env.to_dict()['access_url']}",
                "data": env.to_dict(),
            }

        if any(kw in msg for kw in ("list workspaces", "my workspaces", "environments")):
            workspaces = self.list_workspaces()
            return {
                "message": f"You have {len(workspaces)} workspace(s).",
                "data": workspaces,
            }

        if any(kw in msg for kw in ("images", "what images", "available images")):
            images = self.list_images()
            return {"message": f"Available images: {', '.join(images)}", "data": images}

        if any(kw in msg for kw in ("stats", "usage", "storage")):
            stats = self.get_workspace_stats()
            return {"message": "Workspace statistics retrieved.", "data": stats}

        if "tier" in msg or "features" in msg or "upgrade" in msg:
            info = self.get_tier_info()
            return {"message": f"Current tier: {info['tier']}. Features: {info['features']}", "data": info}

        return {
            "message": (
                "DreamCo Workspace Bot ready. I can create cloud dev environments, "
                "manage workspaces, forward ports (PRO+), and build custom images (ENTERPRISE). "
                "What workspace would you like to create?"
            ),
            "data": {"tier": self.tier.value},
        }
