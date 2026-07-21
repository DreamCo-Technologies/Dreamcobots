"""Hardware stress tests for DreamCobots platform."""
import sys
import os
import time
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class HardwareStressTest:
    """Safe, throttled hardware stress testing for system scoring."""

    CPU_INTENSITY_CAP = 80  # Max CPU target percent

    def __init__(self):
        """Initialize the hardware stress test suite."""
        self._stop_event = threading.Event()

    def safety_check(self) -> dict:
        """Verify system can handle stress testing before running."""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            safe = cpu < 70 and ram.percent < 80 and disk.percent < 90
            return {
                "safe_to_proceed": safe,
                "current_cpu_percent": cpu,
                "current_ram_percent": ram.percent,
                "current_disk_percent": disk.percent,
                "available_ram_gb": round(ram.available / (1024 ** 3), 2),
                "warnings": [] if safe else [
                    f"CPU at {cpu:.1f}% - may be too high" if cpu >= 70 else None,
                    f"RAM at {ram.percent:.1f}% - may be too high" if ram.percent >= 80 else None,
                ],
            }
        except ImportError:
            return {"safe_to_proceed": True, "note": "psutil not available; proceeding with caution"}

    def test_cpu(self, intensity: int = 50, duration: int = 5) -> dict:
        """Run a safe, throttled CPU stress test."""
        intensity = min(intensity, self.CPU_INTENSITY_CAP)
        start = time.time()
        iterations = 0
        while time.time() - start < duration and not self._stop_event.is_set():
            result = sum(i * i for i in range(10000))
            iterations += 1
            time.sleep(max(0, (1 - intensity / 100) * 0.01))
        elapsed = time.time() - start
        return {
            "test_type": "cpu",
            "intensity_percent": intensity,
            "duration_seconds": round(elapsed, 2),
            "iterations_completed": iterations,
            "iterations_per_second": round(iterations / elapsed, 1) if elapsed > 0 else 0,
            "status": "COMPLETED",
        }

    def test_ram(self, mb_to_use: int = 50) -> dict:
        """Run a safe RAM allocation stress test."""
        mb_to_use = min(mb_to_use, 256)
        start = time.time()
        try:
            data = [bytearray(1024 * 1024) for _ in range(mb_to_use)]
            for block in data:
                block[0] = 1
            del data
            elapsed = time.time() - start
            return {
                "test_type": "ram",
                "mb_allocated": mb_to_use,
                "duration_seconds": round(elapsed, 3),
                "status": "PASSED",
            }
        except MemoryError:
            return {
                "test_type": "ram",
                "mb_requested": mb_to_use,
                "status": "FAILED - MemoryError",
            }

    def test_disk_io(self, mb_to_write: int = 10) -> dict:
        """Run a disk I/O stress test by writing and reading a temporary file."""
        mb_to_write = min(mb_to_write, 100)
        test_file = "/tmp/dreamcobots_disk_test.tmp"
        chunk = b"x" * (1024 * 1024)
        start = time.time()
        try:
            with open(test_file, "wb") as f:
                for _ in range(mb_to_write):
                    f.write(chunk)
            write_time = time.time() - start
            read_start = time.time()
            with open(test_file, "rb") as f:
                _ = f.read()
            read_time = time.time() - read_start
            os.remove(test_file)
            return {
                "test_type": "disk_io",
                "mb_written": mb_to_write,
                "write_speed_mbps": round(mb_to_write / write_time, 1) if write_time > 0 else 0,
                "read_speed_mbps": round(mb_to_write / read_time, 1) if read_time > 0 else 0,
                "total_seconds": round(time.time() - start, 2),
                "status": "PASSED",
            }
        except Exception as e:
            return {"test_type": "disk_io", "error": str(e), "status": "FAILED"}
        finally:
            if os.path.exists(test_file):
                try:
                    os.remove(test_file)
                except OSError:
                    pass

    def score_system(self) -> dict:
        """Run all hardware tests and compute an overall system score."""
        print("[HardwareTest] Running safety check...")
        safety = self.safety_check()
        if not safety.get("safe_to_proceed", True):
            return {"error": "Safety check failed - system resources too high", "details": safety}

        print("[HardwareTest] Testing CPU...")
        cpu_result = self.test_cpu(intensity=40, duration=3)

        print("[HardwareTest] Testing RAM...")
        ram_result = self.test_ram(mb_to_use=20)

        print("[HardwareTest] Testing Disk I/O...")
        disk_result = self.test_disk_io(mb_to_write=5)

        cpu_score = min(40, cpu_result.get("iterations_per_second", 0) / 100)
        ram_score = 30 if ram_result.get("status") == "PASSED" else 10
        disk_write = disk_result.get("write_speed_mbps", 0)
        disk_score = min(30, disk_write / 10)
        total_score = int(cpu_score + ram_score + disk_score)
        total_score = max(1, min(100, total_score))

        return {
            "overall_score": total_score,
            "rating": "Excellent" if total_score >= 80 else "Good" if total_score >= 60 else "Fair" if total_score >= 40 else "Low",
            "cpu_test": cpu_result,
            "ram_test": ram_result,
            "disk_test": disk_result,
            "recommendations": [
                "Add more RAM to improve bot concurrency" if total_score < 60 else "System is well-equipped for DreamCobots",
                f"Can safely run {max(1, total_score // 10)} bots concurrently based on resources",
            ],
        }
