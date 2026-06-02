from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from typing import Dict, Iterable, List


@dataclass
class BotDNA:
    capability_vector: List[float]
    behavior_hash: str
    revenue_signature: float


class DNASequencer:
    def sequence(self, bot_id: str, capabilities: Iterable[str], revenue: float) -> BotDNA:
        capabilities = list(capabilities)
        digest = hashlib.sha256((bot_id + '|'.join(capabilities)).encode('utf-8')).digest()
        vector = [(digest[index % len(digest)] / 255.0) for index in range(512)]
        behavior_hash = hashlib.sha256(f'{bot_id}:{capabilities}'.encode('utf-8')).hexdigest()
        return BotDNA(vector, behavior_hash, round(revenue, 2))

    def similarity(self, left: BotDNA, right: BotDNA) -> float:
        dot = sum(a * b for a, b in zip(left.capability_vector, right.capability_vector))
        left_norm = math.sqrt(sum(a * a for a in left.capability_vector))
        right_norm = math.sqrt(sum(b * b for b in right.capability_vector))
        return round(dot / max(left_norm * right_norm, 1e-9), 4)

    def mutation(self, before: BotDNA, after: BotDNA) -> Dict[str, float]:
        changed = sum(1 for a, b in zip(before.capability_vector, after.capability_vector) if abs(a - b) > 0.05)
        return {'vector_shift': round(changed / 512, 4), 'revenue_delta': round(after.revenue_signature - before.revenue_signature, 2)}
