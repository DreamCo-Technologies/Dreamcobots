"""
DreamCo Platform — Model Router
================================

Exposes the OpenRouter adapter, arbitration engine, and the top-level
``DreamCoModelRouter`` that wires them together.

Layer 4 of the DreamCobots reference architecture:

    Agent Runtime + Workflow Graph
            ↓
    Model Router (OpenRouter / internal arbitration)   ← this layer
            ↓
    Reasoning Providers (OpenAI, Anthropic, Mistral, …)
"""

from dreamco_platform.model_router.openrouter import (  # noqa: F401
    OpenRouterAdapter,
    OpenRouterRequest,
    OpenRouterResponse,
)
from dreamco_platform.model_router.arbitration import (  # noqa: F401
    ArbitrationEngine,
    ArbitrationPolicy,
    ProviderSpec,
)
from dreamco_platform.model_router.router import DreamCoModelRouter  # noqa: F401

__all__ = [
    "OpenRouterAdapter",
    "OpenRouterRequest",
    "OpenRouterResponse",
    "ArbitrationEngine",
    "ArbitrationPolicy",
    "ProviderSpec",
    "DreamCoModelRouter",
]
