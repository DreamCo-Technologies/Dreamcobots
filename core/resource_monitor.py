"""Resource monitoring for the DreamCobots platform using psutil."""
import threading
import time

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ResourceMonitor:
    """Monitors system resources: CPU, RAM, Disk, and Network."""

    def __init__(self, interval: float = 5.0):
        """Initialize the resource monitor with a polling interval in seconds."""
        self.interval = interval
        self._running = False
        self._thread = None
        self._latest_metrics = {}
        self._lock = threading.Lock()

    def get_metrics(self) -> dict:
        """Return current system resource metrics."""
        if not PSUTIL_AVAILABLE:
            return {
                "cpu_percent": 0.0,
                "ram_percent": 0.0,
                "disk_percent": 0.0,
                "ram_total_gb": 0.0,
                "ram_used_gb": 0.0,
                "net_bytes_sent": 0,
                "net_bytes_recv": 0,
            }
        try:
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            net = psutil.net_io_counters()
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "ram_percent": ram.percent,
                "disk_percent": disk.percent,
                "ram_total_gb": round(ram.total / (1024 ** 3), 2),
                "ram_used_gb": round(ram.used / (1024 ** 3), 2),
                "net_bytes_sent": net.bytes_sent,
                "net_bytes_recv": net.bytes_recv,
            }
        except Exception:
            return {
                "cpu_percent": 0.0,
                "ram_percent": 0.0,
                "disk_percent": 0.0,
                "ram_total_gb": 0.0,
                "ram_used_gb": 0.0,
                "net_bytes_sent": 0,
                "net_bytes_recv": 0,
            }

    def score_hardware(self) -> int:
        """Return a 1-100 hardware capability score based on available resources."""
        metrics = self.get_metrics()
        cpu_score = max(0, 100 - metrics["cpu_percent"])
        ram_score = max(0, 100 - metrics["ram_percent"])
        disk_score = max(0, 100 - metrics["disk_percent"])
        score = int((cpu_score * 0.4) + (ram_score * 0.4) + (disk_score * 0.2))
        return max(1, min(100, score))

    def recommend_bots(self, available_bots: list) -> list:
        """Return list of bots that can safely run given current resource availability."""
        metrics = self.get_metrics()
        cpu = metrics["cpu_percent"]
        ram = metrics["ram_percent"]

        if cpu < 50 and ram < 60:
            return available_bots
        elif cpu < 70 and ram < 75:
            return [b for i, b in enumerate(available_bots) if i < len(available_bots) // 2 + 1]
        elif cpu < 85 and ram < 85:
            return available_bots[:3] if len(available_bots) > 3 else available_bots
        else:
            return available_bots[:1] if available_bots else []

    def _monitor_loop(self):
        """Background loop that refreshes metrics at the configured interval."""
        while self._running:
            metrics = self.get_metrics()
            with self._lock:
                self._latest_metrics = metrics
            time.sleep(self.interval)

    def start_monitoring(self):
        """Start background resource monitoring thread."""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()

    def stop_monitoring(self):
        """Stop the background monitoring thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
            self._thread = None

    def get_cached_metrics(self) -> dict:
        """Return the most recently cached metrics (non-blocking)."""
        with self._lock:
            return dict(self._latest_metrics) if self._latest_metrics else self.get_metrics()
