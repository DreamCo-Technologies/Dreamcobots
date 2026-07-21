"""
reinforcement_tuner.py — Handles reinforcement reward optimisation.

Fine-tunes AI model hyper-parameters using a simple policy-gradient /
reward-shaping approach to continuously improve performance based on
signals produced by the sandbox lab.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class TuningStep:
    """Records one step of the reinforcement tuning loop."""

    step: int
    params: Dict[str, Any]
    reward: float
    cumulative_reward: float


class ReinforcementTuner:
    """
    Iteratively tunes model parameters using reward-based feedback.

    Parameters
    ----------
    learning_rate : float
        Step size applied to parameter updates.
    discount_factor : float
        Discount (gamma) for computing cumulative reward.
    max_steps : int
        Maximum number of tuning iterations.
    """

    def __init__(
        self,
        learning_rate: float = 0.01,
        discount_factor: float = 0.99,
        max_steps: int = 100,
    ):
        if not 0.0 < learning_rate <= 1.0:
            raise ValueError("learning_rate must be in (0, 1].")
        if not 0.0 <= discount_factor <= 1.0:
            raise ValueError("discount_factor must be between 0 and 1.")

        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.max_steps = max_steps
        self._history: List[TuningStep] = []
        self._cumulative_reward: float = 0.0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def tune(
        self,
        params: Dict[str, float],
        reward_fn: Callable[[Dict[str, float]], float],
        n_steps: Optional[int] = None,
    ) -> Dict[str, float]:
        """
        Run the tuning loop for up to *n_steps* steps.

        Parameters
        ----------
        params : dict[str, float]
            Initial parameter configuration.
        reward_fn : callable
            Receives a parameter dict and returns a float reward signal.
        n_steps : int | None
            Steps to run; defaults to ``self.max_steps``.

        Returns
        -------
        dict[str, float]
            Tuned parameter configuration.
        """
        current = dict(params)
        steps = n_steps if n_steps is not None else self.max_steps

        for i in range(steps):
            reward = reward_fn(current)
            self._cumulative_reward = (
                self.discount_factor * self._cumulative_reward + reward
            )
            self._history.append(
                TuningStep(
                    step=len(self._history),
                    params=dict(current),
                    reward=reward,
                    cumulative_reward=self._cumulative_reward,
                )
            )
            current = self._update_params(current, reward)

        return current

    def get_history(self) -> List[TuningStep]:
        """Return all recorded tuning steps."""
        return list(self._history)

    def best_params(self) -> Optional[Dict[str, Any]]:
        """Return the parameter configuration that yielded the highest reward."""
        if not self._history:
            return None
        best_step = max(self._history, key=lambda s: s.reward)
        return dict(best_step.params)

    def reset(self) -> None:
        """Reset the tuner state."""
        self._history = []
        self._cumulative_reward = 0.0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _update_params(
        self, params: Dict[str, float], reward: float
    ) -> Dict[str, float]:
        """Apply a simple gradient-free parameter perturbation proportional to reward."""
        updated: Dict[str, float] = {}
        for k, v in params.items():
            perturbation = self.learning_rate * reward * (1.0 if reward >= 0 else -1.0)
            updated[k] = v + perturbation
        return updated
