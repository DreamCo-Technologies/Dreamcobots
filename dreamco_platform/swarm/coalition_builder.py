from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class CoalitionLifecycle(Enum):
    FORMING = 'forming'
    STORMING = 'storming'
    NORMING = 'norming'
    PERFORMING = 'performing'
    ADJOURNING = 'adjourning'


@dataclass
class Coalition:
    objective: str
    member_bots: List[str]
    coordination_protocol: str
    shared_context: Dict[str, str]
    lifecycle: CoalitionLifecycle = CoalitionLifecycle.FORMING


class CoalitionBuilder:
    def form(self, objective: str, available_bots: List[str]) -> Coalition:
        leader = available_bots[0] if available_bots else 'leader-bot'
        members = [leader] + available_bots[1:4]
        shared = {'leader': leader, 'validator': available_bots[-1] if available_bots else leader}
        return Coalition(objective, members, 'shared-blackboard', shared)

    def advance(self, coalition: Coalition) -> CoalitionLifecycle:
        order = list(CoalitionLifecycle)
        index = order.index(coalition.lifecycle)
        coalition.lifecycle = order[min(index + 1, len(order) - 1)]
        return coalition.lifecycle

def assign_roles(self, coalition: Coalition) -> Dict[str, str]:
    roles = {}
    if coalition.member_bots:
        roles[coalition.member_bots[0]] = 'leader'
    for bot in coalition.member_bots[1:-1]:
        roles[bot] = 'specialist'
    if len(coalition.member_bots) > 1:
        roles[coalition.member_bots[-1]] = 'validator'
    return roles


def lifecycle_summary(self, coalition: Coalition) -> str:
    return f'{coalition.objective}:{coalition.lifecycle.value}:{len(coalition.member_bots)}-members'


CoalitionBuilder.assign_roles = assign_roles
CoalitionBuilder.lifecycle_summary = lifecycle_summary

def is_active(self, coalition: Coalition) -> bool:
    return coalition.lifecycle != CoalitionLifecycle.ADJOURNING


CoalitionBuilder.is_active = is_active
