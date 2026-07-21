# Bot command handler for Dreamcobots.
# Implements: /run-bot, /pause-bot, /bot-status, /broadcast-message,
#             /analytics, /device-register

import time


class CommandHandler:
    """Handles slash commands for managing Dreamcobots bots and devices."""

    COMMANDS = [
        "/run-bot",
        "/pause-bot",
        "/bot-status",
        "/broadcast-message",
        "/analytics",
        "/device-register",
    ]

    def __init__(self):
        self.bots = {}
        self.devices = {}
        self.analytics = {
            "commands_executed": 0,
            "messages_broadcast": 0,
            "devices_registered": 0,
            "bot_runs": 0,
            "bot_pauses": 0,
        }
        self._start_time = time.time()

    # ------------------------------------------------------------------
    # /run-bot
    # ------------------------------------------------------------------
    def run_bot(self, bot_id):
        """Start or resume a bot by ID."""
        if bot_id not in self.bots:
            self.bots[bot_id] = {"status": "running", "started_at": time.time()}
        else:
            self.bots[bot_id]["status"] = "running"
            self.bots[bot_id]["started_at"] = time.time()
        self.analytics["commands_executed"] += 1
        self.analytics["bot_runs"] += 1
        result = {"command": "/run-bot", "bot_id": bot_id, "status": "running"}
        print(f"[/run-bot] Bot '{bot_id}' is now running.")
        return result

    # ------------------------------------------------------------------
    # /pause-bot
    # ------------------------------------------------------------------
    def pause_bot(self, bot_id):
        """Pause a running bot by ID."""
        if bot_id not in self.bots:
            result = {"command": "/pause-bot", "bot_id": bot_id, "error": "Bot not found"}
            print(f"[/pause-bot] Bot '{bot_id}' not found.")
            return result
        self.bots[bot_id]["status"] = "paused"
        self.analytics["commands_executed"] += 1
        self.analytics["bot_pauses"] += 1
        result = {"command": "/pause-bot", "bot_id": bot_id, "status": "paused"}
        print(f"[/pause-bot] Bot '{bot_id}' is now paused.")
        return result

    # ------------------------------------------------------------------
    # /bot-status
    # ------------------------------------------------------------------
    def bot_status(self, bot_id=None):
        """Return the current status of a specific bot or all bots."""
        self.analytics["commands_executed"] += 1
        if bot_id:
            status = self.bots.get(bot_id, {"status": "unknown"})
            result = {"command": "/bot-status", "bot_id": bot_id, "status": status}
            print(f"[/bot-status] Bot '{bot_id}': {status}")
        else:
            result = {"command": "/bot-status", "bots": dict(self.bots)}
            print(f"[/bot-status] All bots: {self.bots}")
        return result

    # ------------------------------------------------------------------
    # /broadcast-message
    # ------------------------------------------------------------------
    def broadcast_message(self, message, target_bots=None):
        """Broadcast a message to all or selected bots."""
        targets = target_bots if target_bots else list(self.bots.keys())
        self.analytics["commands_executed"] += 1
        self.analytics["messages_broadcast"] += 1
        result = {
            "command": "/broadcast-message",
            "message": message,
            "targets": targets,
            "delivered": len(targets),
        }
        print(f"[/broadcast-message] '{message}' sent to {len(targets)} bot(s): {targets}")
        return result

    # ------------------------------------------------------------------
    # /analytics
    # ------------------------------------------------------------------
    def get_analytics(self):
        """Return aggregated analytics data."""
        self.analytics["commands_executed"] += 1
        uptime = time.time() - self._start_time
        result = {
            "command": "/analytics",
            "uptime_seconds": round(uptime, 2),
            "total_bots": len(self.bots),
            "total_devices": len(self.devices),
            **self.analytics,
        }
        print(f"[/analytics] {result}")
        return result

    # ------------------------------------------------------------------
    # /device-register
    # ------------------------------------------------------------------
    def device_register(self, device_id, device_type, metadata=None):
        """Register a new device with the bot network."""
        self.devices[device_id] = {
            "type": device_type,
            "metadata": metadata or {},
            "registered_at": time.time(),
            "status": "active",
        }
        self.analytics["commands_executed"] += 1
        self.analytics["devices_registered"] += 1
        result = {
            "command": "/device-register",
            "device_id": device_id,
            "device_type": device_type,
            "status": "registered",
        }
        print(f"[/device-register] Device '{device_id}' ({device_type}) registered.")
        return result

    # ------------------------------------------------------------------
    # Generic dispatcher
    # ------------------------------------------------------------------
    def dispatch(self, command, **kwargs):
        """Dispatch a slash command by name."""
        handlers = {
            "/run-bot": lambda: self.run_bot(kwargs.get("bot_id", "")),
            "/pause-bot": lambda: self.pause_bot(kwargs.get("bot_id", "")),
            "/bot-status": lambda: self.bot_status(kwargs.get("bot_id")),
            "/broadcast-message": lambda: self.broadcast_message(
                kwargs.get("message", ""), kwargs.get("target_bots")
            ),
            "/analytics": lambda: self.get_analytics(),
            "/device-register": lambda: self.device_register(
                kwargs.get("device_id", ""),
                kwargs.get("device_type", "unknown"),
                kwargs.get("metadata"),
            ),
        }
        handler = handlers.get(command)
        if handler:
            return handler()
        return {"error": f"Unknown command: {command}"}
