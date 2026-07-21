"""Telegram Bot API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class TelegramConnector:
    """TelegramConnector for DataForge AI."""

    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self):
        """Initialize connector, reading bot token from environment."""
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if not self.token:
            logger.warning("TELEGRAM_BOT_TOKEN not set.")

    def send_message(self, chat_id: str, text: str) -> dict:
        """Send a message via Telegram Bot API.

        Args:
            chat_id: Telegram chat identifier.
            text: Message text.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.post(f"{self.BASE_URL}{self.token}/sendMessage",
                json={"chat_id": chat_id, "text": text}, timeout=30)
            response.raise_for_status()
            logger.info("Telegram message sent to chat %s.", chat_id)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Telegram send_message error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_updates(self, offset: int = 0) -> dict:
        """Get Telegram bot updates.

        Args:
            offset: Update offset for pagination (default 0).

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}{self.token}/getUpdates",
                params={"offset": offset}, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Telegram get_updates error: %s", e)
            return {"status": "error", "message": str(e)}
