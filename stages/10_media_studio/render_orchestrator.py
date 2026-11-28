"""Render adapter contract with explicit plan-only fallback."""
from __future__ import annotations
from typing import Any, Protocol
from .rights_gate import authorize_model, require_allowed

class Renderer(Protocol):
    renderer_id: str
    def render(self, *, packet: dict[str, Any], output_dir: str) -> list[dict[str, Any]]:
        """Return actual output records with path, SHA-256, and source shot ID."""

def execute_render(packet: dict[str, Any], *, renderer: Renderer | None = None,
                   output_dir: str = "", models: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if renderer is None:
        return {**packet, "render_status": "planned_not_rendered", "renderer_id": None}
    model_map = {str(row.get("model_id")): row for row in (models or [])}
    for model_id in packet.get("model_decisions", []):
        record = model_map.get(str(model_id.get("model_id")))
        if record is None:
            raise PermissionError(f"Renderer model is not in the supplied registry: {model_id}")
        require_allowed(authorize_model(record, commercial=bool(packet.get("commercial_use"))))
    outputs = renderer.render(packet=packet, output_dir=output_dir)
    if not isinstance(outputs, list) or not outputs:
        raise RuntimeError("Renderer returned no verifiable output records.")
    return {**packet, "render_status": "rendered_pending_quality_gate",
            "renderer_id": renderer.renderer_id, "rendered_assets": outputs}
