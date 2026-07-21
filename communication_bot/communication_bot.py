"""
Communication and Multi-task Interaction Bot for Dreamcobots platform.

Handles calls, texts, emails, video calls, social media interactions,
chats, business deals, Bluetooth file exchange, and verification notifications.
"""

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


@dataclass
class Message:
    """Represents a communication message across any channel."""
    channel: str           # 'call', 'text', 'email', 'video', 'social', 'chat'
    sender: str
    recipient: str
    content: str
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "pending"  # pending | sent | delivered | failed


@dataclass
class BluetoothTransfer:
    """Represents a Bluetooth file-exchange session."""
    device_id: str
    filename: str
    file_size_bytes: int
    transfer_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "pending"  # pending | in_progress | complete | failed


@dataclass
class VerificationNotification:
    """Notification generated for an unresolved verification action."""
    item: str
    live_link: str
    notification_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resolved: bool = False


class CommunicationBot(BotBase):
    """
    Multi-task communication bot.

    Manages all inbound and outbound communications across multiple channels,
    coordinates Bluetooth file transfers, and generates actionable notifications
    for unresolved verifications.

    Args:
        autonomy: Autonomy level (default SEMI_AUTONOMOUS for comms safety).
        scaling: Scaling level for concurrent communication volume.
    """

    SUPPORTED_CHANNELS = {"call", "text", "email", "video", "social", "chat"}

    def __init__(
        self,
        autonomy: AutonomyLevel = AutonomyLevel.SEMI_AUTONOMOUS,
        scaling: ScalingLevel = ScalingLevel.MODERATE,
    ) -> None:
        super().__init__("CommunicationBot", autonomy, scaling)
        self._inbox: List[Message] = []
        self._outbox: List[Message] = []
        self._bt_transfers: List[BluetoothTransfer] = []
        self._notifications: List[VerificationNotification] = []
        self._deals: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    # ------------------------------------------------------------------
    # Messaging
    # ------------------------------------------------------------------

    def send_message(
        self,
        channel: str,
        sender: str,
        recipient: str,
        content: str,
    ) -> Message:
        """
        Send a message via the specified channel.

        Args:
            channel: One of SUPPORTED_CHANNELS.
            sender: Sender identifier.
            recipient: Recipient identifier.
            content: Message body / subject matter.

        Returns:
            The created Message object.

        Raises:
            ValueError: If the channel is not supported.
        """
        if channel not in self.SUPPORTED_CHANNELS:
            raise ValueError(f"Unsupported channel '{channel}'. Supported: {self.SUPPORTED_CHANNELS}")

        msg = Message(channel=channel, sender=sender, recipient=recipient, content=content)
        msg.status = "sent"
        self._outbox.append(msg)
        self.logger.info("Message sent via %s to %s (id=%s)", channel, recipient, msg.message_id)
        return msg

    def receive_message(self, channel: str, sender: str, recipient: str, content: str) -> Message:
        """Record an incoming message."""
        if channel not in self.SUPPORTED_CHANNELS:
            raise ValueError(f"Unsupported channel '{channel}'.")
        msg = Message(channel=channel, sender=sender, recipient=recipient, content=content, status="delivered")
        self._inbox.append(msg)
        self.logger.info("Message received via %s from %s (id=%s)", channel, sender, msg.message_id)
        return msg

    def get_inbox(self, channel: Optional[str] = None) -> List[Message]:
        """Return all (or channel-filtered) inbox messages."""
        if channel:
            return [m for m in self._inbox if m.channel == channel]
        return list(self._inbox)

    def get_outbox(self, channel: Optional[str] = None) -> List[Message]:
        """Return all (or channel-filtered) outbox messages."""
        if channel:
            return [m for m in self._outbox if m.channel == channel]
        return list(self._outbox)

    # ------------------------------------------------------------------
    # Business deals
    # ------------------------------------------------------------------

    def initiate_deal(self, party: str, terms: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a business deal with a counterparty.

        Args:
            party: The other party's identifier.
            terms: Key/value mapping describing deal terms.

        Returns:
            Deal record with a unique deal_id and status.
        """
        deal = {
            "deal_id": str(uuid.uuid4()),
            "party": party,
            "terms": terms,
            "status": "initiated",
        }
        self._deals.append(deal)
        self.logger.info("Deal initiated with %s (deal_id=%s)", party, deal["deal_id"])
        return deal

    def close_deal(self, deal_id: str) -> bool:
        """Mark a deal as closed. Returns True if found and updated."""
        for deal in self._deals:
            if deal["deal_id"] == deal_id:
                deal["status"] = "closed"
                self.logger.info("Deal %s closed", deal_id)
                return True
        return False

    def get_deals(self) -> List[Dict[str, Any]]:
        """Return all deal records."""
        return list(self._deals)

    # ------------------------------------------------------------------
    # Bluetooth file exchange
    # ------------------------------------------------------------------

    def initiate_bluetooth_transfer(
        self,
        device_id: str,
        filename: str,
        file_size_bytes: int,
    ) -> BluetoothTransfer:
        """
        Initiate a Bluetooth file transfer to a device.

        Args:
            device_id: Target Bluetooth device identifier.
            filename: Name of the file to transfer (e.g., video or music file).
            file_size_bytes: File size in bytes.

        Returns:
            BluetoothTransfer record.
        """
        transfer = BluetoothTransfer(
            device_id=device_id,
            filename=filename,
            file_size_bytes=file_size_bytes,
            status="in_progress",
        )
        self._bt_transfers.append(transfer)
        self.logger.info("Bluetooth transfer started: %s → device %s", filename, device_id)
        return transfer

    def complete_bluetooth_transfer(self, transfer_id: str) -> bool:
        """Mark a Bluetooth transfer as complete. Returns True if found."""
        for t in self._bt_transfers:
            if t.transfer_id == transfer_id:
                t.status = "complete"
                self.logger.info("Bluetooth transfer %s complete", transfer_id)
                return True
        return False

    def get_bluetooth_transfers(self) -> List[BluetoothTransfer]:
        """Return all Bluetooth transfer records."""
        return list(self._bt_transfers)

    # ------------------------------------------------------------------
    # Verification notifications
    # ------------------------------------------------------------------

    def create_verification_notification(self, item: str, live_link: str) -> VerificationNotification:
        """
        Generate a notification for an unresolved verification item.

        Args:
            item: Description of the unresolved item.
            live_link: Direct URL the user must visit to resolve it.

        Returns:
            VerificationNotification record.
        """
        notif = VerificationNotification(item=item, live_link=live_link)
        self._notifications.append(notif)
        self.logger.info("Verification notification created for '%s' → %s", item, live_link)
        return notif

    def resolve_notification(self, notification_id: str) -> bool:
        """Mark a verification notification as resolved. Returns True if found."""
        for n in self._notifications:
            if n.notification_id == notification_id:
                n.resolved = True
                self.logger.info("Notification %s resolved", notification_id)
                return True
        return False

    def get_pending_notifications(self) -> List[VerificationNotification]:
        """Return all unresolved verification notifications."""
        return [n for n in self._notifications if not n.resolved]

    # ------------------------------------------------------------------
    # Overridden task runner
    # ------------------------------------------------------------------

    def _run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "")
        if task_type == "send_message":
            msg = self.send_message(
                channel=task.get("channel", "chat"),
                sender=task.get("sender", "bot"),
                recipient=task.get("recipient", ""),
                content=task.get("content", ""),
            )
            return {"status": "ok", "message_id": msg.message_id}
        if task_type == "initiate_deal":
            deal = self.initiate_deal(task.get("party", ""), task.get("terms", {}))
            return {"status": "ok", "deal_id": deal["deal_id"]}
        return super()._run_task(task)
