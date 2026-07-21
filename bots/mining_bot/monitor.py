"""
Smart Monitoring module for the Dreamcobots Mining Bot.

Detects and reports:
  - Miner downtime (hash rate drops to zero)
  - Sub-optimal mining settings (hash rate below configured threshold)
  - Unusual activity (hash rate spikes, revenue anomalies)
  - Energy overconsumption

Alerts are generated as structured dicts and optionally routed to registered
callback handlers.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional


class MonitoringDisabledError(Exception):
    """Raised when monitoring features require PRO or ENTERPRISE tier."""


@dataclass
class Alert:
    """A single monitoring alert."""

    level: str          # "info" | "warning" | "critical"
    category: str       # e.g. "downtime", "sub_optimal", "unusual_activity"
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "level": self.level,
            "category": self.category,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


AlertHandler = Callable[[Alert], None]


class MiningMonitor:
    """
    Monitors mining health and emits alerts when anomalies are detected.

    Parameters
    ----------
    alerts_enabled : bool
        Whether alerts are enabled for this tier.
    expected_hashrate_ths : float
        Baseline expected hash rate in TH/s.
    max_power_kw : float
        Maximum acceptable power consumption in kW.
    downtime_threshold_seconds : float
        Seconds without a hashrate reading before a downtime alert fires.
    hashrate_spike_pct : float
        Percentage above expected hashrate to trigger an unusual-activity alert.
    hashrate_drop_pct : float
        Percentage below expected hashrate to trigger a sub-optimal alert.
    """

    def __init__(
        self,
        alerts_enabled: bool = False,
        expected_hashrate_ths: float = 100.0,
        max_power_kw: float = 10.0,
        downtime_threshold_seconds: float = 300.0,
        hashrate_spike_pct: float = 20.0,
        hashrate_drop_pct: float = 10.0,
    ):
        self.alerts_enabled = alerts_enabled
        self.expected_hashrate_ths = expected_hashrate_ths
        self.max_power_kw = max_power_kw
        self.downtime_threshold_seconds = downtime_threshold_seconds
        self.hashrate_spike_pct = hashrate_spike_pct
        self.hashrate_drop_pct = hashrate_drop_pct

        self._alerts: List[Alert] = []
        self._handlers: List[AlertHandler] = []
        self._last_seen_ts: Optional[float] = None  # monotonic seconds

    # ------------------------------------------------------------------
    # Handler registration
    # ------------------------------------------------------------------

    def register_handler(self, handler: AlertHandler) -> None:
        """Register a callable that will be called for every new alert."""
        self._handlers.append(handler)

    def _emit(self, alert: Alert) -> None:
        self._alerts.append(alert)
        for h in self._handlers:
            h(alert)

    # ------------------------------------------------------------------
    # Internal guard
    # ------------------------------------------------------------------

    def _require_alerts(self) -> None:
        if not self.alerts_enabled:
            raise MonitoringDisabledError(
                "Smart alerts require PRO or ENTERPRISE tier."
            )

    # ------------------------------------------------------------------
    # Public monitoring interface
    # ------------------------------------------------------------------

    def record_hashrate(self, hashrate_ths: float, power_kw: float) -> List[Alert]:
        """
        Record a new hashrate/power reading and return any newly-generated
        alerts.

        Parameters
        ----------
        hashrate_ths : float
            Current hash rate in TH/s (0 = miner offline).
        power_kw : float
            Current power draw in kW.
        """
        self._require_alerts()

        current_monotonic = time.monotonic()
        new_alerts: List[Alert] = []

        # --- downtime check ------------------------------------------------
        if hashrate_ths == 0:
            alert = Alert(
                level="critical",
                category="downtime",
                message="Miner appears to be offline (hash rate = 0).",
                metadata={"hashrate_ths": hashrate_ths},
            )
            self._emit(alert)
            new_alerts.append(alert)

        else:
            # --- sub-optimal check ----------------------------------------
            drop_threshold = self.expected_hashrate_ths * (
                1 - self.hashrate_drop_pct / 100
            )
            if hashrate_ths < drop_threshold:
                alert = Alert(
                    level="warning",
                    category="sub_optimal",
                    message=(
                        f"Hash rate {hashrate_ths:.2f} TH/s is more than "
                        f"{self.hashrate_drop_pct}% below expected "
                        f"{self.expected_hashrate_ths:.2f} TH/s."
                    ),
                    metadata={
                        "current_ths": hashrate_ths,
                        "expected_ths": self.expected_hashrate_ths,
                    },
                )
                self._emit(alert)
                new_alerts.append(alert)

            # --- spike check ----------------------------------------------
            spike_threshold = self.expected_hashrate_ths * (
                1 + self.hashrate_spike_pct / 100
            )
            if hashrate_ths > spike_threshold:
                alert = Alert(
                    level="warning",
                    category="unusual_activity",
                    message=(
                        f"Hash rate {hashrate_ths:.2f} TH/s is more than "
                        f"{self.hashrate_spike_pct}% above expected "
                        f"{self.expected_hashrate_ths:.2f} TH/s."
                    ),
                    metadata={
                        "current_ths": hashrate_ths,
                        "expected_ths": self.expected_hashrate_ths,
                    },
                )
                self._emit(alert)
                new_alerts.append(alert)

        # --- energy overconsumption check -----------------------------------
        if power_kw > self.max_power_kw:
            alert = Alert(
                level="warning",
                category="energy",
                message=(
                    f"Power draw {power_kw:.2f} kW exceeds maximum "
                    f"{self.max_power_kw:.2f} kW."
                ),
                metadata={"power_kw": power_kw, "max_power_kw": self.max_power_kw},
            )
            self._emit(alert)
            new_alerts.append(alert)

        self._last_seen_ts = current_monotonic
        return new_alerts

    def check_downtime(self) -> Optional[Alert]:
        """
        Generate a downtime alert if no reading has been received within
        *downtime_threshold_seconds*.
        """
        self._require_alerts()

        if self._last_seen_ts is None:
            alert = Alert(
                level="critical",
                category="downtime",
                message="No hash rate reading has been received yet.",
            )
            self._emit(alert)
            return alert

        elapsed = time.monotonic() - self._last_seen_ts
        if elapsed > self.downtime_threshold_seconds:
            alert = Alert(
                level="critical",
                category="downtime",
                message=(
                    f"No hash rate reading received for {elapsed:.0f} s "
                    f"(threshold: {self.downtime_threshold_seconds:.0f} s)."
                ),
                metadata={"elapsed_seconds": elapsed},
            )
            self._emit(alert)
            return alert

        return None

    # ------------------------------------------------------------------
    # Alert access
    # ------------------------------------------------------------------

    def all_alerts(self) -> List[Alert]:
        return list(self._alerts)

    def alerts_by_level(self, level: str) -> List[Alert]:
        return [a for a in self._alerts if a.level == level]

    def alerts_by_category(self, category: str) -> List[Alert]:
        return [a for a in self._alerts if a.category == category]

    def clear_alerts(self) -> None:
        self._alerts.clear()
