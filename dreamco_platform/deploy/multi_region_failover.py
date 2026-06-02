from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List


@dataclass
class FailoverResult:
    source_region: str
    target_region: str
    switched: bool
    dns_record: str
    synced_at: str


class HealthMonitor:
    def __init__(self, interval_seconds: int = 30) -> None:
        self.interval_seconds = interval_seconds
        self.last_checked: Dict[str, datetime] = {}
        self.region_health: Dict[str, bool] = {}

    def update(self, region: str, healthy: bool) -> None:
        self.region_health[region] = healthy
        self.last_checked[region] = datetime.utcnow()

    def is_healthy(self, region: str) -> bool:
        checked = self.last_checked.get(region, datetime.min)
        fresh = datetime.utcnow() - checked <= timedelta(seconds=self.interval_seconds * 2)
        return fresh and self.region_health.get(region, False)


class MultiRegionFailover:
    REGIONS = ['us-east-1', 'eu-west-1', 'ap-southeast-1', 'us-west-2']

    def __init__(self) -> None:
        self.monitor = HealthMonitor()
        self.dns_records = {region: f'{region}.dreamco.internal' for region in self.REGIONS}
        self.active_region = 'us-east-1'
        self.history: List[FailoverResult] = []

    def trigger(self, source_region: str, target_region: str) -> FailoverResult:
        if not self.monitor.is_healthy(target_region):
            return FailoverResult(source_region, target_region, False, self.dns_records[source_region], datetime.utcnow().isoformat())
        synced_at = self._sync_data(source_region, target_region)
        self.active_region = target_region
        result = FailoverResult(source_region, target_region, True, self.dns_records[target_region], synced_at)
        self.history.append(result)
        return result

    def _sync_data(self, source_region: str, target_region: str) -> str:
        return f'{source_region}->{target_region}@{datetime.utcnow().isoformat()}'
