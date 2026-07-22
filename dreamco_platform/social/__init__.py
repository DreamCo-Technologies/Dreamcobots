"""Approval-gated social media planning and publishing for Buddy."""

from .manager import (
    BuddySocialManager,
    PublishApproval,
    SocialDraft,
    SocialManagerError,
    SocialPublisher,
)
from .adapters import LocalSocialOutboxPublisher, WebhookSocialPublisher

__all__ = [
    "BuddySocialManager",
    "PublishApproval",
    "SocialDraft",
    "SocialManagerError",
    "SocialPublisher",
    "LocalSocialOutboxPublisher",
    "WebhookSocialPublisher",
]
