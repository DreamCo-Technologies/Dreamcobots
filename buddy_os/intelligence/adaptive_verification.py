"""Turn planner disagreement into an explicit verification recommendation."""
from __future__ import annotations

from dataclasses import dataclass
from .planner_arbitration import Arbitration
from .verification_selector import VerificationOption, VerificationSelector


@dataclass(frozen=True)
class VerificationRequest:
    reason: str
    options: tuple[VerificationOption, ...]
    selected_option_id: str | None


class AdaptiveVerification:
    def __init__(self, selector: VerificationSelector | None = None) -> None:
        self.selector = selector or VerificationSelector()

    def build_request(self, arbitration: Arbitration, options: tuple[VerificationOption, ...] | list[VerificationOption]) -> VerificationRequest:
        usable = tuple(options)
        selected = self.selector.choose(usable) if arbitration.requires_verification else None
        reason = "planner disagreement" if arbitration.requires_verification else "no disagreement detected"
        return VerificationRequest(reason, usable, selected.option_id if selected else None)
