from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping
import random

@dataclass
class SimulationWorld:
    agents: List[Dict[str, object]]
    environment_rules: Dict[str, object]
    time_step: int
    random_seed: int
    events: List[str] = field(default_factory=list)


class WorldBuilder:
    def create(self, config: Mapping[str, object]) -> SimulationWorld:
        seed = int(config.get('random_seed', 42))
        random.seed(seed)
        agents = list(config.get('agents', [])) or [
            {'id': 'trader-bot', 'role': 'trade', 'capital': 100},
            {'id': 'partner-bot', 'role': 'collaborate', 'capital': 80},
            {'id': 'rival-bot', 'role': 'compete', 'capital': 90},
        ]
        world = SimulationWorld(agents=agents, environment_rules=dict(config.get('environment_rules', {'tax': 0.05})), time_step=int(config.get('time_step', 1)), random_seed=seed)
        self._simulate(world, steps=int(config.get('steps', 5)))
        return world

    def _simulate(self, world: SimulationWorld, steps: int) -> None:
        for step in range(steps):
            for agent in world.agents:
                action = random.choice(['trade', 'compete', 'collaborate'])
                delta = random.randint(-5, 8)
                agent['capital'] = max(0, int(agent.get('capital', 0)) + delta)
                world.events.append(f'step={step} {agent["id"]} {action} delta={delta}')

    def emergent_behavior(self, world: SimulationWorld) -> List[str]:
        cooperative = sum('collaborate' in event for event in world.events)
        competitive = sum('compete' in event for event in world.events)
        behaviors = []
        if cooperative > competitive:
            behaviors.append('Cooperation-dominant ecosystem emerging.')
        if any('delta=8' in event for event in world.events):
            behaviors.append('Positive outlier growth loops detected.')
        return behaviors



def module_summary() -> dict:
    """Provide a compact runtime summary for orchestration tooling."""
    public_items = [name for name in globals() if not name.startswith('_')]
    return {
        'module': __name__,
        'public_items': sorted(public_items),
        'line_count': len(__doc__.splitlines()) if __doc__ else 0,
    }


def demo_payload() -> dict:
    """Return a deterministic payload useful for smoke-free integration wiring."""
    return {'module': __name__, 'status': 'ready'}
