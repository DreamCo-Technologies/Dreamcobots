"""CrashGuard watchdog for monitoring and protecting running bots."""
import threading
import time
from datetime import datetime

from core.resource_monitor import ResourceMonitor


class WatchDog:
    """Monitors running bots, detects crashes, and responds to resource pressure."""

    def __init__(self, check_interval: float = 5.0):
        """Initialize the watchdog with a check interval in seconds."""
        self.check_interval = check_interval
        self._bots = {}
        self._running = False
        self._thread = None
        self._log = []
        self._lock = threading.Lock()
        self._resource_monitor = ResourceMonitor()

    def register_bot(self, name: str, bot_instance):
        """Register a bot for watchdog monitoring."""
        with self._lock:
            self._bots[name] = bot_instance
        self._write_log(f"Registered bot: {name}")

    def deregister_bot(self, name: str):
        """Remove a bot from watchdog monitoring."""
        with self._lock:
            self._bots.pop(name, None)
        self._write_log(f"Deregistered bot: {name}")

    def restart_bot(self, name: str):
        """Attempt to restart a crashed bot."""
        with self._lock:
            bot = self._bots.get(name)
        if bot is None:
            self._write_log(f"Cannot restart unknown bot: {name}")
            return False
        try:
            if hasattr(bot, "start"):
                bot.start()
            self._write_log(f"Restarted bot: {name}")
            return True
        except Exception as e:
            self._write_log(f"Failed to restart {name}: {e}")
            return False

    def _write_log(self, message: str):
        """Append a timestamped entry to the event log."""
        entry = {"timestamp": datetime.utcnow().isoformat(), "message": message}
        with self._lock:
            self._log.append(entry)
            if len(self._log) > 500:
                self._log = self._log[-500:]

    def get_log(self) -> list:
        """Return a copy of the watchdog event log."""
        with self._lock:
            return list(self._log)

    def _check_bots(self):
        """Check health of all registered bots and respond to resource pressure."""
        metrics = self._resource_monitor.get_metrics()
        cpu = metrics.get("cpu_percent", 0)
        ram = metrics.get("ram_percent", 0)

        with self._lock:
            bot_names = list(self._bots.keys())

        for name in bot_names:
            with self._lock:
                bot = self._bots.get(name)
            if bot is None:
                continue

            # Check for crashed bots
            try:
                status = getattr(bot, "_status", None)
                if status == "error":
                    self._write_log(f"Bot {name} in error state - attempting restart")
                    self.restart_bot(name)
            except Exception as e:
                self._write_log(f"Error checking bot {name}: {e}")

            # Throttle if CPU is high
            if cpu > 85:
                try:
                    if hasattr(bot, "throttle"):
                        bot.throttle()
                    self._write_log(f"Throttled {name} due to high CPU ({cpu:.1f}%)")
                except Exception:
                    pass

            # Pause low-priority bots if RAM is high
            if ram > 80:
                try:
                    priority = getattr(bot, "priority", "low")
                    if priority == "low" and hasattr(bot, "stop"):
                        bot.stop()
                        self._write_log(f"Paused low-priority bot {name} due to high RAM ({ram:.1f}%)")
                except Exception:
                    pass

    def _watch_loop(self):
        """Main watchdog loop that runs in a background thread."""
        while self._running:
            try:
                self._check_bots()
            except Exception as e:
                self._write_log(f"Watchdog loop error: {e}")
            time.sleep(self.check_interval)

    def start(self):
        """Start the watchdog monitoring thread."""
        if not self._running:
            self._running = True
            self._resource_monitor.start_monitoring()
            self._thread = threading.Thread(target=self._watch_loop, daemon=True)
            self._thread.start()
            self._write_log("WatchDog started")

    def stop(self):
        """Stop the watchdog monitoring thread."""
        self._running = False
        self._resource_monitor.stop_monitoring()
        if self._thread:
            self._thread.join(timeout=10)
            self._thread = None
        self._write_log("WatchDog stopped")
