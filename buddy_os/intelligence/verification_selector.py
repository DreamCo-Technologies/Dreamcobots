"""Select the next verification strategy when planners disagree."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VerificationOption:
    option_id: str
    expected_information_gain: float
    cost: float = 1.0
    risk: float = 0.0
    available: bool = True

    def __post_init__(self) -> None:
        for name, value in (("expected_information_gain", self.expected_information_gain), ("risk", self.risk)):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.cost <= 0:
            raise ValueError("cost must be positive")


class VerificationSelector:
    @staticmethod
    def value(option: VerificationOption) -> float:
        return option.expected_information_gain * (1.0 - option.risk) / option.cost

    def choose(self, options: tuple[VerificationOption, ...] | list[VerificationOption]) -> VerificationOption | None:
        usable = [o for o in options if o.available]
        return max(usable, key=lambda o: (self.value(o), o.option_id), default=None)
