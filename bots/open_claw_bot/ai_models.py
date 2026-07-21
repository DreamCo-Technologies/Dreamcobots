"""
Open Claw Bot — AI Models

Provides AI/ML model definitions and a lightweight inference dispatcher
for strategy generation and decision-making.

Supported model families:
  - Trend Predictor  — LSTM-based time-series forecasting
  - Risk Classifier  — decision-tree risk assessment
  - Signal Generator — rule-based + ML signal fusion
  - Ensemble Ranker  — gradient-boosted strategy ranking
  - NLP Advisor      — natural-language strategy recommendation

GLOBAL AI SOURCES FLOW: participates via open_claw_bot.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class ModelFamily(Enum):
    TREND_PREDICTOR = "trend_predictor"
    RISK_CLASSIFIER = "risk_classifier"
    SIGNAL_GENERATOR = "signal_generator"
    ENSEMBLE_RANKER = "ensemble_ranker"
    NLP_ADVISOR = "nlp_advisor"


class ModelStatus(Enum):
    IDLE = "idle"
    TRAINING = "training"
    READY = "ready"
    DEPRECATED = "deprecated"


@dataclass
class AIModel:
    """Represents a registered AI/ML model."""

    model_id: str
    name: str
    family: ModelFamily
    version: str = "1.0.0"
    accuracy: float = 0.0          # 0.0 – 1.0
    parameters: dict = field(default_factory=dict)
    status: ModelStatus = ModelStatus.IDLE
    tags: list = field(default_factory=list)

    def is_ready(self) -> bool:
        return self.status == ModelStatus.READY

    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "family": self.family.value,
            "version": self.version,
            "accuracy": self.accuracy,
            "status": self.status.value,
            "tags": self.tags,
        }


@dataclass
class InferenceResult:
    """Output from a model inference call."""

    model_id: str
    input_summary: dict
    prediction: dict
    confidence: float
    explanation: str = ""

    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "explanation": self.explanation,
        }


# ---------------------------------------------------------------------------
# Default model catalogue
# ---------------------------------------------------------------------------

DEFAULT_MODELS: list[dict] = [
    {
        "name": "TrendPredictor v1",
        "family": ModelFamily.TREND_PREDICTOR,
        "version": "1.0.0",
        "accuracy": 0.76,
        "tags": ["time-series", "lstm", "forecasting"],
    },
    {
        "name": "RiskClassifier v1",
        "family": ModelFamily.RISK_CLASSIFIER,
        "version": "1.0.0",
        "accuracy": 0.82,
        "tags": ["classification", "risk", "decision-tree"],
    },
    {
        "name": "SignalGenerator v1",
        "family": ModelFamily.SIGNAL_GENERATOR,
        "version": "1.0.0",
        "accuracy": 0.71,
        "tags": ["signal", "rule-based", "ml-fusion"],
    },
    {
        "name": "EnsembleRanker v1",
        "family": ModelFamily.ENSEMBLE_RANKER,
        "version": "1.0.0",
        "accuracy": 0.85,
        "tags": ["ensemble", "gradient-boost", "ranking"],
    },
    {
        "name": "NLPAdvisor v1",
        "family": ModelFamily.NLP_ADVISOR,
        "version": "1.0.0",
        "accuracy": 0.68,
        "tags": ["nlp", "strategy-recommendation", "language-model"],
    },
]


class AIModelHub:
    """
    Registry and inference dispatcher for Open Claw AI/ML models.

    All models are simulated; in production these would call real
    ML model endpoints (TensorRT, ONNX, or cloud APIs).
    """

    def __init__(self, load_defaults: bool = True) -> None:
        self._models: dict[str, AIModel] = {}
        self._counter: int = 0
        if load_defaults:
            self._load_default_models()

    # ------------------------------------------------------------------
    # Model management
    # ------------------------------------------------------------------

    def register_model(
        self,
        name: str,
        family: ModelFamily,
        version: str = "1.0.0",
        accuracy: float = 0.0,
        parameters: Optional[dict] = None,
        tags: Optional[list] = None,
        auto_ready: bool = True,
    ) -> AIModel:
        """Register a new AI model."""
        self._counter += 1
        model_id = f"model_{self._counter:04d}"
        model = AIModel(
            model_id=model_id,
            name=name,
            family=family,
            version=version,
            accuracy=accuracy,
            parameters=dict(parameters or {}),
            status=ModelStatus.READY if auto_ready else ModelStatus.IDLE,
            tags=list(tags or []),
        )
        self._models[model_id] = model
        return model

    def get_model(self, model_id: str) -> AIModel:
        return self._get(model_id)

    def list_models(
        self,
        family: Optional[ModelFamily] = None,
        ready_only: bool = False,
    ) -> list[AIModel]:
        models = list(self._models.values())
        if family is not None:
            models = [m for m in models if m.family == family]
        if ready_only:
            models = [m for m in models if m.is_ready()]
        return models

    def deprecate_model(self, model_id: str) -> AIModel:
        model = self._get(model_id)
        model.status = ModelStatus.DEPRECATED
        return model

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict_trend(
        self,
        data_series: list[float],
        model_id: Optional[str] = None,
    ) -> InferenceResult:
        """Predict the next-period trend direction from a data series."""
        model = self._pick_model(ModelFamily.TREND_PREDICTOR, model_id)
        if len(data_series) < 2:
            direction = "neutral"
            magnitude = 0.0
        else:
            delta = data_series[-1] - data_series[0]
            direction = "up" if delta > 0 else ("down" if delta < 0 else "neutral")
            magnitude = round(abs(delta) / max(abs(data_series[0]), 1e-9) * 100, 2)

        return InferenceResult(
            model_id=model.model_id,
            input_summary={"series_length": len(data_series)},
            prediction={"direction": direction, "magnitude_pct": magnitude},
            confidence=model.accuracy,
            explanation=f"Trend {direction} by {magnitude}% based on {len(data_series)} data points.",
        )

    def classify_risk(
        self,
        features: dict,
        model_id: Optional[str] = None,
    ) -> InferenceResult:
        """Classify the risk level of a given feature set."""
        model = self._pick_model(ModelFamily.RISK_CLASSIFIER, model_id)
        volatility = float(features.get("volatility", 0.2))
        leverage = float(features.get("leverage", 1.0))
        exposure = float(features.get("exposure_pct", 10.0))

        score = (volatility * 0.4) + (min(leverage / 10, 1.0) * 0.4) + (exposure / 100 * 0.2)
        if score < 0.25:
            risk = "low"
        elif score < 0.5:
            risk = "medium"
        elif score < 0.75:
            risk = "high"
        else:
            risk = "extreme"

        return InferenceResult(
            model_id=model.model_id,
            input_summary=features,
            prediction={"risk_level": risk, "risk_score": round(score, 4)},
            confidence=model.accuracy,
            explanation=f"Risk classified as '{risk}' (score={score:.4f}).",
        )

    def generate_signals(
        self,
        market_data: dict,
        model_id: Optional[str] = None,
    ) -> InferenceResult:
        """Generate entry/exit signals from market data."""
        model = self._pick_model(ModelFamily.SIGNAL_GENERATOR, model_id)
        price = float(market_data.get("price", 100.0))
        moving_avg = float(market_data.get("moving_avg", 100.0))
        rsi = float(market_data.get("rsi", 50.0))

        if price > moving_avg and rsi < 70:
            signal = "buy"
        elif price < moving_avg and rsi > 30:
            signal = "sell"
        else:
            signal = "hold"

        return InferenceResult(
            model_id=model.model_id,
            input_summary=market_data,
            prediction={"signal": signal},
            confidence=model.accuracy,
            explanation=f"Signal '{signal}' based on price vs MA and RSI={rsi}.",
        )

    def rank_strategies_ml(
        self,
        strategy_scores: list[dict],
        model_id: Optional[str] = None,
    ) -> InferenceResult:
        """Use the ensemble ranker to re-order strategies by ML score."""
        model = self._pick_model(ModelFamily.ENSEMBLE_RANKER, model_id)
        ranked = sorted(
            strategy_scores,
            key=lambda s: s.get("confidence_score", 0) * s.get("expected_roi_pct", 0),
            reverse=True,
        )
        return InferenceResult(
            model_id=model.model_id,
            input_summary={"count": len(strategy_scores)},
            prediction={"ranked_strategies": ranked},
            confidence=model.accuracy,
            explanation=f"Ranked {len(ranked)} strategies by confidence × ROI.",
        )

    def advise_nlp(
        self,
        query: str,
        model_id: Optional[str] = None,
    ) -> InferenceResult:
        """Return an NLP-based strategy recommendation for a natural-language query."""
        model = self._pick_model(ModelFamily.NLP_ADVISOR, model_id)
        query_lower = query.lower()

        if any(k in query_lower for k in ("safe", "conservative", "low risk")):
            recommendation = "conservative"
        elif any(k in query_lower for k in ("fast", "aggressive", "high return")):
            recommendation = "aggressive"
        elif any(k in query_lower for k in ("balance", "moderate", "medium")):
            recommendation = "balanced"
        elif "scalp" in query_lower or "quick" in query_lower:
            recommendation = "scalping"
        elif "long" in query_lower or "hold" in query_lower:
            recommendation = "long_term"
        else:
            recommendation = "balanced"

        return InferenceResult(
            model_id=model.model_id,
            input_summary={"query": query},
            prediction={"recommended_strategy_type": recommendation},
            confidence=model.accuracy,
            explanation=f"NLP analysis suggests a '{recommendation}' strategy for your query.",
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _pick_model(
        self, family: ModelFamily, model_id: Optional[str]
    ) -> AIModel:
        if model_id is not None:
            model = self._get(model_id)
            if not model.is_ready():
                raise RuntimeError(f"Model '{model_id}' is not in READY state.")
            return model
        candidates = [m for m in self._models.values() if m.family == family and m.is_ready()]
        if not candidates:
            raise RuntimeError(f"No ready model found for family '{family.value}'.")
        return max(candidates, key=lambda m: m.accuracy)

    def _get(self, model_id: str) -> AIModel:
        if model_id not in self._models:
            raise KeyError(f"Model '{model_id}' not found.")
        return self._models[model_id]

    def _load_default_models(self) -> None:
        for spec in DEFAULT_MODELS:
            self.register_model(
                name=spec["name"],
                family=spec["family"],
                version=spec["version"],
                accuracy=spec["accuracy"],
                tags=spec["tags"],
                auto_ready=True,
            )
