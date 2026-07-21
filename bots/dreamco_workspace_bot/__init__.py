"""DreamCo Workspace Bot — GitHub Codespaces competitor for cloud dev workspaces."""
from .dreamco_workspace_bot import (
    DreamCoWorkspaceBot,
    DreamCoWorkspaceBotTierError,
    DreamCoWorkspaceBotError,
    WorkspaceEnvironment,
)
from .tiers import Tier, get_bot_tier_info

__all__ = [
    "DreamCoWorkspaceBot",
    "DreamCoWorkspaceBotTierError",
    "DreamCoWorkspaceBotError",
    "WorkspaceEnvironment",
    "Tier",
    "get_bot_tier_info",
]
