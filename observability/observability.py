from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Any, Dict, Optional

logger = logging.getLogger("dreamco.observability")

# ---------------------------------------------------------------------------
# Tracing
# ---------------------------------------------------------------------------
def init_tracing(service_name: str = "dreamco", otlp_endpoint: Optional[str] = None):
    """Initialise OpenTelemetry tracing with OTLP export."""
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)

        endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                exporter = OTLPSpanExporter(endpoint=endpoint)
                provider.add_span_processor(BatchSpanProcessor(exporter))
                logger.info(f"OTLP tracing → {endpoint}")
            except ImportError:
                logger.warning("opentelemetry-exporter-otlp not installed")

        trace.set_tracer_provider(provider)
        logger.info("OpenTelemetry tracing initialised")
    except ImportError:
        logger.warning("opentelemetry-sdk not installed; tracing disabled")


def get_tracer(name: str = "dreamco"):
    try:
        from opentelemetry import trace
        return trace.get_tracer(name)
    except ImportError:
        return _NoopTracer()


@contextmanager
def trace_span(name: str, attributes: Dict[str, Any] = None):
    tracer = get_tracer()
    try:
        from opentelemetry import trace as otel_trace
        with tracer.start_as_current_span(name) as span:
            for k, v in (attributes or {}).items():
                span.set_attribute(k, v)
            yield span
    except Exception:
        yield None


class _NoopTracer:
    def start_as_current_span(self, *a, **kw):
        from contextlib import nullcontext
        return nullcontext()


# ---------------------------------------------------------------------------
# Metrics (Prometheus)
# ---------------------------------------------------------------------------
class DreamCoMetrics:
    """Prometheus metrics registry for DreamCo."""

    def __init__(self):
        self._enabled = False
        self._setup()

    def _setup(self):
        try:
            from prometheus_client import Counter, Histogram, Gauge, start_http_server

            self.agent_executions = Counter(
                "dreamco_agent_executions_total",
                "Total agent executions",
                ["agent_name", "category", "method", "status"],
            )
            self.execution_duration = Histogram(
                "dreamco_agent_execution_duration_seconds",
                "Agent execution duration",
                ["agent_name", "category"],
                buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0],
            )
            self.revenue_total = Counter(
                "dreamco_revenue_total",
                "Total revenue generated",
                ["agent_name", "category"],
            )
            self.active_agents = Gauge(
                "dreamco_active_agents",
                "Number of active (non-terminated) agents",
                ["state"],
            )
            self.quarantined_agents = Gauge(
                "dreamco_quarantined_agents_total",
                "Number of quarantined agents",
            )
            self._enabled = True
            logger.info("Prometheus metrics registry initialised")
        except ImportError:
            logger.warning("prometheus-client not installed; metrics disabled")

    def record_execution(
        self,
        agent_name: str,
        category: str,
        method: str,
        status: str,
        duration_s: float,
        revenue: float = 0.0,
    ):
        if not self._enabled:
            return
        self.agent_executions.labels(
            agent_name=agent_name, category=category, method=method, status=status
        ).inc()
        self.execution_duration.labels(
            agent_name=agent_name, category=category
        ).observe(duration_s)
        if revenue > 0:
            self.revenue_total.labels(
                agent_name=agent_name, category=category
            ).inc(revenue)

    def start_metrics_server(self, port: int = 9090):
        if not self._enabled:
            return
        try:
            from prometheus_client import start_http_server
            start_http_server(port)
            logger.info(f"Prometheus metrics server on :{port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")


# ---------------------------------------------------------------------------
# Structured Logging
# ---------------------------------------------------------------------------
def configure_logging(level: str = "INFO", json_logs: bool = False):
    """Configure root logging with optional JSON output."""
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not root.handlers:
        handler = logging.StreamHandler()
        if json_logs:
            try:
                import json_log_formatter
                formatter = json_log_formatter.JSONFormatter()
            except ImportError:
                formatter = logging.Formatter(
                    '{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","msg":"%(message)s"}'
                )
        else:
            formatter = logging.Formatter(
                "%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s"
            )
        handler.setFormatter(formatter)
        root.addHandler(handler)


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------
_metrics: Optional[DreamCoMetrics] = None

def get_metrics() -> DreamCoMetrics:
    global _metrics
    if _metrics is None:
        _metrics = DreamCoMetrics()
    return _metrics