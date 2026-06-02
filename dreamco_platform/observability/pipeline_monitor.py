"""Pipeline monitoring for throughput, latency, and incident hints."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class PipelineRun:
    pipeline: str
    duration_seconds: float
    succeeded: bool
    queue_seconds: float = 0.0


class PipelineMonitor:
    def __init__(self) -> None:
        self.runs: List[PipelineRun] = []

    def record_run(self, pipeline: str, duration_seconds: float, succeeded: bool, queue_seconds: float = 0.0) -> PipelineRun:
        run = PipelineRun(pipeline, duration_seconds, succeeded, queue_seconds)
        self.runs.append(run)
        return run

    def health_score(self) -> Dict[str, float]:
        if not self.runs:
            return {'success_rate': 0.0, 'latency_score': 0.0, 'overall': 0.0}
        success_rate = sum(run.succeeded for run in self.runs) / len(self.runs)
        avg_duration = sum(run.duration_seconds + run.queue_seconds for run in self.runs) / len(self.runs)
        latency_score = max(0.0, min(1.0, 1 - avg_duration / 1800))
        overall = success_rate * 0.7 + latency_score * 0.3
        return {'success_rate': round(success_rate, 3), 'latency_score': round(latency_score, 3), 'overall': round(overall, 3)}

    def per_pipeline(self) -> Dict[str, Dict[str, float]]:
        grouped: Dict[str, List[PipelineRun]] = {}
        for run in self.runs:
            grouped.setdefault(run.pipeline, []).append(run)
        summary: Dict[str, Dict[str, float]] = {}
        for name, runs in grouped.items():
            summary[name] = {
                'count': float(len(runs)),
                'success_rate': round(sum(run.succeeded for run in runs) / len(runs), 3),
                'avg_total_seconds': round(sum(run.duration_seconds + run.queue_seconds for run in runs) / len(runs), 3),
            }
        return summary

    def incident_candidates(self) -> List[Dict[str, object]]:
        incidents = []
        for run in self.runs:
            if not run.succeeded or run.duration_seconds + run.queue_seconds > 1200:
                incidents.append({
                    'pipeline': run.pipeline,
                    'duration_seconds': run.duration_seconds,
                    'queue_seconds': run.queue_seconds,
                    'reason': 'failure' if not run.succeeded else 'latency',
                })
        return incidents


def monitor_snapshot(runs: Iterable[Dict[str, object]]) -> Dict[str, object]:
    monitor = PipelineMonitor()
    for run in runs:
        monitor.record_run(str(run['pipeline']), float(run['duration_seconds']), bool(run['succeeded']), float(run.get('queue_seconds', 0.0)))
    return {'health': monitor.health_score(), 'by_pipeline': monitor.per_pipeline(), 'incidents': monitor.incident_candidates()}
