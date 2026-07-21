from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import hashlib
import json
from typing import List


@dataclass
class AuditBlock:
    index: int
    timestamp: str
    event_hash: str
    previous_hash: str
    nonce: int
    authority: str
    block_hash: str = field(init=False)

    def __post_init__(self) -> None:
        payload = f'{self.index}|{self.timestamp}|{self.event_hash}|{self.previous_hash}|{self.nonce}|{self.authority}'
        self.block_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()


class AuditChain:
    def __init__(self, authority: str = 'dreamco-auditor') -> None:
        self.authority = authority
        self.blocks: List[AuditBlock] = [self._genesis()]

    def _genesis(self) -> AuditBlock:
        return AuditBlock(0, datetime.utcnow().isoformat(), hashlib.sha256(b'genesis').hexdigest(), '0' * 64, 0, self.authority)

    def append_event(self, event: str) -> AuditBlock:
        previous = self.blocks[-1]
        event_hash = hashlib.sha256(event.encode('utf-8')).hexdigest()
        nonce = len(self.blocks)
        block = AuditBlock(len(self.blocks), datetime.utcnow().isoformat(), event_hash, previous.block_hash, nonce, self.authority)
        self.blocks.append(block)
        return block

    def verify_integrity(self) -> bool:
        for index in range(1, len(self.blocks)):
            current = self.blocks[index]
            previous = self.blocks[index - 1]
            if current.previous_hash != previous.block_hash:
                return False
            if current.authority != self.authority:
                return False
            if AuditBlock(current.index, current.timestamp, current.event_hash, current.previous_hash, current.nonce, current.authority).block_hash != current.block_hash:
                return False
        return True

    def get_history(self) -> List[dict]:
        return [asdict(block) for block in self.blocks]

    def export_json(self) -> str:
        return json.dumps(self.get_history(), indent=2)

def latest_block(self) -> dict:
    return asdict(self.blocks[-1])


def authority_chain_id(self) -> str:
    return hashlib.sha256(f'{self.authority}:{len(self.blocks)}'.encode('utf-8')).hexdigest()


AuditChain.latest_block = latest_block
AuditChain.authority_chain_id = authority_chain_id
