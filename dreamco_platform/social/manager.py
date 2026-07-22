"""Governed social media draft, schedule, and publishing contracts."""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol


class SocialManagerError(ValueError):
    """Raised when social content or publishing violates an owner control."""


@dataclass(frozen=True)
class SocialDraft:
    owner_user_id: str
    account_ref: str
    platform: str
    content: str
    objective: str
    media_refs: tuple[str, ...] = ()
    synthetic_media: bool = False
    rights_confirmed: bool = False

    def validate(self) -> None:
        if not self.owner_user_id or not self.account_ref.startswith("social-account:"):
            raise SocialManagerError("Use an owner ID and an opaque social account reference.")
        if len(self.content.strip()) < 2 or len(self.content) > 10_000:
            raise SocialManagerError("Social content must be between 2 and 10,000 characters.")
        if not self.objective.strip():
            raise SocialManagerError("A campaign objective is required.")
        if self.media_refs and not self.rights_confirmed:
            raise SocialManagerError("Media rights must be confirmed before scheduling or publishing.")


@dataclass
class PublishApproval:
    owner_user_id: str
    account_ref: str
    draft_id: str
    draft_fingerprint: str
    action: str = "publish_one_social_draft"
    approved_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    revoked_at: float | None = None
    approval_id: str = field(default_factory=lambda: f"social-approval-{uuid.uuid4().hex[:16]}")

    def validate(
        self,
        *,
        draft_id: str,
        draft_fingerprint: str,
        owner_user_id: str,
        account_ref: str,
    ) -> None:
        now = time.time()
        if self.revoked_at is not None or (self.expires_at is not None and now > self.expires_at):
            raise SocialManagerError("Publish approval is expired or revoked.")
        if self.action != "publish_one_social_draft":
            raise SocialManagerError("Approval must be scoped to one social draft.")
        if (self.draft_id, self.owner_user_id, self.account_ref) != (draft_id, owner_user_id, account_ref):
            raise SocialManagerError("Publish approval does not match the draft, owner, and account.")
        if self.draft_fingerprint != draft_fingerprint:
            raise SocialManagerError("Publish approval does not match the reviewed content and media.")


class SocialPublisher(Protocol):
    name: str
    platform: str

    def publish(self, *, account_ref: str, content: str, media_refs: tuple[str, ...]) -> str: ...


class BuddySocialManager:
    """Create campaign packets and publish through owner-approved adapters."""

    def __init__(self) -> None:
        self._used_approvals: set[str] = set()
        self._publishing_approvals: set[str] = set()

    @staticmethod
    def _draft_fingerprint(
        *,
        account_ref: str,
        platform: str,
        content: str,
        media_refs: tuple[str, ...] | list[str],
    ) -> str:
        payload = json.dumps(
            {
                "account_ref": account_ref,
                "platform": platform.lower(),
                "content": content,
                "media_refs": list(media_refs),
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def prepare(self, draft: SocialDraft) -> dict[str, Any]:
        draft.validate()
        draft_id = f"social-draft-{uuid.uuid4().hex[:16]}"
        draft_fingerprint = self._draft_fingerprint(
            account_ref=draft.account_ref,
            platform=draft.platform,
            content=draft.content,
            media_refs=draft.media_refs,
        )
        label = "AI-assisted media" if draft.synthetic_media else None
        return {
            "schema": "dreamco.social_campaign_packet.v1",
            "draft_id": draft_id,
            "draft_fingerprint": draft_fingerprint,
            "status": "awaiting_owner_publish_approval",
            "platform": draft.platform,
            "account_ref": draft.account_ref,
            "content": draft.content,
            "objective": draft.objective,
            "media_refs": list(draft.media_refs),
            "synthetic_media_label": label,
            "workflow": [
                "draft",
                "brand and safety review",
                "owner preview",
                "one-action publish approval",
                "adapter publish",
                "analytics and comment triage",
            ],
            "guardrails": [
                "no credential access in content workers",
                "no spam or unsolicited bulk messaging",
                "no deceptive impersonation or fake endorsements",
                "no autonomous direct messages without recipient and campaign approval",
                "platform rules and rate limits apply",
                "owner can revoke scheduled content",
            ],
            "publish_requires_owner_approval": True,
        }

    def publish(
        self,
        packet: dict[str, Any],
        *,
        owner_user_id: str,
        approval: PublishApproval,
        publisher: SocialPublisher | None,
    ) -> dict[str, Any]:
        if publisher is None:
            return {
                "status": "publisher_adapter_configuration_required",
                "draft_id": packet["draft_id"],
                "live_action_taken": False,
            }
        if publisher.platform.lower() != str(packet["platform"]).lower():
            raise SocialManagerError("Publisher adapter does not match the selected platform.")
        approval.validate(
            draft_id=packet["draft_id"],
            draft_fingerprint=self._draft_fingerprint(
                account_ref=packet["account_ref"],
                platform=packet["platform"],
                content=packet["content"],
                media_refs=packet["media_refs"],
            ),
            owner_user_id=owner_user_id,
            account_ref=packet["account_ref"],
        )
        if approval.approval_id in self._used_approvals or approval.approval_id in self._publishing_approvals:
            raise SocialManagerError("Publish approval has already been used.")
        self._publishing_approvals.add(approval.approval_id)
        try:
            post_ref = publisher.publish(
                account_ref=packet["account_ref"],
                content=packet["content"],
                media_refs=tuple(packet["media_refs"]),
            )
            if not post_ref:
                raise SocialManagerError("Publisher did not return a post reference.")
        except Exception:
            self._publishing_approvals.discard(approval.approval_id)
            raise
        self._publishing_approvals.discard(approval.approval_id)
        self._used_approvals.add(approval.approval_id)
        return {
            "schema": "dreamco.social_publish_receipt.v1",
            "status": "published",
            "draft_id": packet["draft_id"],
            "post_ref": post_ref,
            "publisher": publisher.name,
            "approval_id": approval.approval_id,
            "raw_credentials_returned": False,
        }
