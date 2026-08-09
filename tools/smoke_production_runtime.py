#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import signal
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "generated" / "production-runtime-smoke.json"
PORT = int(os.environ.get("DREAMCO_SMOKE_PORT", "5055"))
URL = f"http://127.0.0.1:{PORT}/api/health"
STARTUP_BUDGET_SECONDS = 30
HEALTH_LATENCY_BUDGET_MS = 1000


def main() -> int:
    env = dict(os.environ)
    env.update({
        "NODE_ENV": "production",
        "PORT": str(PORT),
        "DREAMCO_DISABLE_AUTO_SYNC": "1",
    })
    started = time.perf_counter()
    proc = subprocess.Popen(
        ["npm", "start"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    health = None
    error = None
    latency_ms = None
    try:
        deadline = time.time() + STARTUP_BUDGET_SECONDS
        while time.time() < deadline:
            if proc.poll() is not None:
                break
            try:
                request_started = time.perf_counter()
                with urllib.request.urlopen(URL, timeout=2) as response:
                    latency_ms = round((time.perf_counter() - request_started) * 1000, 2)
                    body = json.loads(response.read().decode("utf-8"))
                    if response.status == 200 and body.get("ok") is True:
                        health = body
                        break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                time.sleep(0.4)
        startup_seconds = round(time.perf_counter() - started, 3)
        if health is None:
            stdout, stderr = proc.communicate(timeout=2) if proc.poll() is not None else ("", "")
            error = f"health endpoint did not become ready; stdout={stdout[-1500:]}; stderr={stderr[-1500:]}"
    finally:
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait(timeout=5)
            except Exception:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except Exception:
                    pass

    passed = bool(
        health
        and startup_seconds <= STARTUP_BUDGET_SECONDS
        and latency_ms is not None
        and latency_ms <= HEALTH_LATENCY_BUDGET_MS
    )
    payload = {
        "schema": "dreamco.production_runtime_smoke.v1",
        "url": URL,
        "startup_seconds": startup_seconds,
        "startup_budget_seconds": STARTUP_BUDGET_SECONDS,
        "health_latency_ms": latency_ms,
        "health_latency_budget_ms": HEALTH_LATENCY_BUDGET_MS,
        "health": health,
        "passed": passed,
        "error": error,
        "truth_boundary": "This proves the built server started and answered the health endpoint in this environment; it does not prove every external integration is connected.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
