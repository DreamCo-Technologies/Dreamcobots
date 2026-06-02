from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class GovernanceProposal:
    proposal_id: str
    action: str
    payload: dict
    proposer: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    committed: bool = False


class ConsensusLog:
    def __init__(self) -> None:
        self.entries: List[dict] = []

    def append(self, proposal: GovernanceProposal, votes: Dict[str, bool]) -> None:
        self.entries.append({'proposal_id': proposal.proposal_id, 'action': proposal.action, 'votes': votes, 'timestamp': datetime.utcnow().isoformat()})


class ConsensusNode:
    VALID_ACTIONS = {'add_bot', 'remove_bot', 'change_policy', 'update_pricing'}

    def __init__(self, node_id: str, active_nodes: List[str], log: ConsensusLog | None = None) -> None:
        self.node_id = node_id
        self.active_nodes = active_nodes
        self.log = log or ConsensusLog()
        self.committed: List[GovernanceProposal] = []

    def propose(self, proposal_id: str, action: str, payload: dict) -> GovernanceProposal:
        if action not in self.VALID_ACTIONS:
            raise ValueError(f'Unsupported governance action: {action}')
        return GovernanceProposal(proposal_id=proposal_id, action=action, payload=payload, proposer=self.node_id)

    def vote(self, proposal: GovernanceProposal, ballots: Dict[str, bool]) -> bool:
        granted = sum(1 for approved in ballots.values() if approved)
        approved = granted >= self.quorum()
        if approved:
            self.commit(proposal, ballots)
        return approved

    def commit(self, proposal: GovernanceProposal, ballots: Dict[str, bool]) -> None:
        proposal.committed = True
        self.committed.append(proposal)
        self.log.append(proposal, ballots)

    def quorum(self) -> int:
        return len(self.active_nodes) // 2 + 1
