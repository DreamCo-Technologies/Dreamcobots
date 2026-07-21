"""
DreamCo Python Bots — Base Bot

Defines the standardised ``BaseBot`` interface that every Python bot in the
new DreamCo OS must implement.  Bots are wired together via an event bus
rather than direct calls so the system remains loosely coupled.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from event_bus.base_bus import BaseEventBus


class BaseBot(abc.ABC):
    """
    Abstract base class for all DreamCo OS Python bots.

    Parameters
    ----------
    name : str
        Human-readable bot identifier used in logs and the bot registry.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    @abc.abstractmethod
    def run(self, event_bus: "BaseEventBus") -> None:
        """
        Execute the bot's core logic and emit events on *event_bus*.

        Parameters
        ----------
        event_bus : BaseEventBus
            Shared event bus for publishing results and subscribing to
            upstream events.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement run(event_bus)"
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}(name={self.name!r})"
