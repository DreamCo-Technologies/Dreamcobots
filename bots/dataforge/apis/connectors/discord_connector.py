"""Discord API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class DiscordConnector:
    """DiscordConnector for DataForge AI."""

    BASE_URL = "https://discord.com/api/v10"

    def __init__(self):
        """Initialize connector, reading bot token from environment."""
        self.token = os.environ.get("DISCORD_BOT_TOKEN", "")
        if not self.token:
            logger.warning("DISCORD_BOT_TOKEN not set.")

    def get_guild_channels(self, guild_id: str) -> dict:
        """Get channels for a Discord guild.

        Args:
            guild_id: The Discord guild (server) ID.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bot {self.token}"}
        try:
            response = requests.get(f"{self.BASE_URL}/guilds/{guild_id}/channels", headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Discord guild channels fetched for guild %s.", guild_id)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Discord get_guild_channels error: %s", e)
            return {"status": "error", "message": str(e)}

    def send_message(self, channel_id: str, content: str) -> dict:
        """Send a message to a Discord channel.

        Args:
            channel_id: The Discord channel ID.
            content: Message content string.

        Returns:
            API response dict or error dict.
        """
        import requests
        headers = {"Authorization": f"Bot {self.token}", "Content-Type": "application/json"}
        try:
            response = requests.post(f"{self.BASE_URL}/channels/{channel_id}/messages",
                json={"content": content}, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Discord message sent to channel %s.", channel_id)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("Discord send_message error: %s", e)
            return {"status": "error", "message": str(e)}
