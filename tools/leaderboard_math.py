"""Deterministic Glicko-2 and Pareto utilities for evidence-backed model comparisons.

Ratings require actual head-to-head outcomes. A leaderboard row without match
evidence is not assigned a fabricated win, loss, or rating update.
"""
from __future__ import annotations

import math
from typing import Any, Iterable

_SCALE = 173.7178
_PI = math.pi


def _finite(value: Any, name: str, *, minimum: float | None = None) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    if minimum is not None and number < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return number


def _g(phi: float) -> float:
    return 1.0 / math.sqrt(1.0 + 3.0 * phi * phi / (_PI * _PI))


def _expectation(mu: float, opponent_mu: float, opponent_phi: float) -> float:
    exponent = -_g(opponent_phi) * (mu - opponent_mu)
    if exponent >= 0:
        z = math.exp(-min(exponent, 745.0))
        return z / (1.0 + z)
    z = math.exp(max(exponent, -745.0))
    return 1.0 / (1.0 + z)


def update_glicko2(
    rating: float,
    rating_deviation: float,
    volatility: float,
    opponents: Iterable[dict[str, Any]],
    *,
    tau: float = 0.5,
    epsilon: float = 1e-6,
) -> dict[str, float | int]:
    """Update one rating period using opponent {rating, rd, score} records."""
    r = _finite(rating, "rating")
    rd = _finite(rating_deviation, "rating_deviation", minimum=0.0)
    sigma = _finite(volatility, "volatility", minimum=1e-9)
    tau = _finite(tau, "tau", minimum=1e-9)
    epsilon = _finite(epsilon, "epsilon", minimum=1e-12)
    if rd <= 0:
        raise ValueError("rating_deviation must be positive")
    if sigma >= 1:
        raise ValueError("volatility must be less than 1")

    games = []
    for index, opponent in enumerate(opponents):
        if not isinstance(opponent, dict):
            raise ValueError(f"opponent {index} must be an object")
        opp_rating = _finite(opponent.get("rating"), f"opponent[{index}].rating")
        opp_rd = _finite(opponent.get("rd"), f"opponent[{index}].rd", minimum=0.0)
        score = _finite(opponent.get("score"), f"opponent[{index}].score")
        if opp_rd <= 0 or score not in (0.0, 0.5, 1.0):
            raise ValueError("opponent rd must be positive and score must be 0, 0.5, or 1")
        games.append(((opp_rating - 1500.0) / _SCALE, opp_rd / _SCALE, score))

    if not games:
        return {"rating": r, "rd": rd, "volatility": sigma, "games": 0}

    mu = (r - 1500.0) / _SCALE
    phi = rd / _SCALE
    variance_sum = 0.0
    delta_sum = 0.0
    for opp_mu, opp_phi, score in games:
        g_value = _g(opp_phi)
        expected = _expectation(mu, opp_mu, opp_phi)
        variance_sum += g_value * g_value * expected * (1.0 - expected)
        delta_sum += g_value * (score - expected)
    if variance_sum <= 0:
        raise ValueError("rating period has no usable information")
    variance = 1.0 / variance_sum
    delta = variance * delta_sum

    a = math.log(sigma * sigma)
    phi_squared = phi * phi

    def objective(x: float) -> float:
        exp_x = math.exp(max(min(x, 700.0), -700.0))
        numerator = exp_x * (delta * delta - phi_squared - variance - exp_x)
        denominator = 2.0 * (phi_squared + variance + exp_x) ** 2
        return numerator / denominator - (x - a) / (tau * tau)

    A = a
    if delta * delta > phi_squared + variance:
        B = math.log(delta * delta - phi_squared - variance)
    else:
        k = 1
        while objective(a - k * tau) < 0 and k < 1000:
            k += 1
        B = a - k * tau
    fA, fB = objective(A), objective(B)
    for _ in range(100):
        if abs(B - A) <= epsilon:
            break
        C = A + (A - B) * fA / (fB - fA)
        fC = objective(C)
        if fC * fB < 0:
            A, fA = B, fB
        else:
            fA /= 2.0
        B, fB = C, fC
    else:
        raise RuntimeError("Glicko-2 volatility solver did not converge")

    new_sigma = math.exp(A / 2.0)
    phi_star = math.sqrt(phi_squared + new_sigma * new_sigma)
    new_phi = 1.0 / math.sqrt(1.0 / (phi_star * phi_star) + 1.0 / variance)
    new_mu = mu + new_phi * new_phi * delta_sum
    new_rating = 1500.0 + _SCALE * new_mu
    new_rd = _SCALE * new_phi
    return {
        "rating": round(new_rating, 4),
        "rd": round(new_rd, 4),
        "volatility": round(new_sigma, 8),
        "games": len(games),
    }


def pareto_frontier(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return non-dominated models; maximize accuracy, minimize latency/size."""
    rows = []
    seen = set()
    for index, row in enumerate(records):
        if not isinstance(row, dict):
            raise ValueError(f"record {index} must be an object")
        model_id = str(row.get("model_id", "")).strip()
        if not model_id or model_id in seen:
            raise ValueError("every model must have a unique non-empty model_id")
        seen.add(model_id)
        accuracy = _finite(row.get("accuracy"), f"{model_id}.accuracy", minimum=0.0)
        latency = _finite(row.get("latency_ms"), f"{model_id}.latency_ms", minimum=0.0)
        params = _finite(row.get("parameters_m"), f"{model_id}.parameters_m", minimum=0.0)
        if accuracy > 1.0 or latency <= 0 or params <= 0:
            raise ValueError("accuracy must be <= 1; latency and parameters must be positive")
        rows.append({**row, "model_id": model_id, "accuracy": accuracy,
                     "latency_ms": latency, "parameters_m": params,
                     "efficiency_index": round(accuracy / (params * math.log1p(latency)), 8)})

    frontier = []
    for candidate in rows:
        dominated = any(
            other is not candidate
            and other["accuracy"] >= candidate["accuracy"]
            and other["latency_ms"] <= candidate["latency_ms"]
            and other["parameters_m"] <= candidate["parameters_m"]
            and (
                other["accuracy"] > candidate["accuracy"]
                or other["latency_ms"] < candidate["latency_ms"]
                or other["parameters_m"] < candidate["parameters_m"]
            )
            for other in rows
        )
        if not dominated:
            frontier.append(candidate)
    return sorted(frontier, key=lambda row: (-row["efficiency_index"], row["model_id"]))
