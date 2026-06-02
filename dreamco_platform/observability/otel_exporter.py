"""OpenTelemetry exporter setup for DreamCo distributed tracing."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor, SpanExporter

try:
    from opentelemetry.exporter.zipkin.json import ZipkinExporter
except ImportError:  # pragma: no cover - optional at runtime
    ZipkinExporter = None


def _build_exporter() -> SpanExporter:
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or os.getenv("JAEGER_ENDPOINT")
    if endpoint:
        return OTLPSpanExporter(endpoint=endpoint, insecure=True)
    if os.getenv("ZIPKIN_ENDPOINT") and ZipkinExporter is not None:
        return ZipkinExporter(endpoint=os.environ["ZIPKIN_ENDPOINT"])
    return ConsoleSpanExporter()


def configure_tracing(service_name: str = "dreamco-platform") -> trace.Tracer:
    """Configure and register the global tracer provider."""
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.namespace": "dreamco",
            "deployment.environment": os.getenv("DREAMCO_ENV", "development"),
        }
    )
    provider = TracerProvider(resource=resource)
    exporter = _build_exporter()
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    if os.getenv("OTEL_DEBUG", "").lower() in {"1", "true", "yes"}:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)


_TRACER = configure_tracing()


@contextmanager
def trace_bot_execution(bot_id: str, span_name: str) -> Iterator[object]:
    """Create a traced execution scope enriched with DreamCo bot metadata."""
    with _TRACER.start_as_current_span(span_name) as span:
        span.set_attribute("dreamco.bot_id", bot_id)
        span.set_attribute("dreamco.component", "bot")
        span.set_attribute("dreamco.trace.origin", "otel_exporter")
        try:
            yield span
        except Exception as exc:  # noqa: BLE001
            span.record_exception(exc)
            span.set_attribute("dreamco.status", "error")
            raise
        else:
            span.set_attribute("dreamco.status", "ok")


class OtelTracingManager:
    """Helper object for code that wants explicit access to provider objects."""

    def __init__(self, service_name: str = "dreamco-platform") -> None:
        self.service_name = service_name
        self.tracer = trace.get_tracer(service_name)
        self.provider = trace.get_tracer_provider()

    def force_flush(self) -> None:
        flush = getattr(self.provider, "force_flush", None)
        if callable(flush):
            flush()

    def shutdown(self) -> None:
        shutdown = getattr(self.provider, "shutdown", None)
        if callable(shutdown):
            shutdown()
