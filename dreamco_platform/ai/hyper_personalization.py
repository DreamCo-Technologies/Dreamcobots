from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class UserPersona:
    communication_style: str
    expertise_level: str
    goals: List[str]
    preferences: Dict[str, str]


@dataclass
class PersonalizedConfig:
    bot_id: str
    user_id: str
    system_prompt_delta: str
    on_device: bool


class HyperPersonalizer:
    def __init__(self) -> None:
        self.personas: Dict[str, UserPersona] = {}

    def adapt_bot(self, bot_id: str, user_id: str, on_device: bool = False) -> PersonalizedConfig:
        persona = self.personas[user_id]
        delta = f"Style={persona.communication_style}; expertise={persona.expertise_level}; goals={','.join(persona.goals)}"
        return PersonalizedConfig(bot_id, user_id, delta, on_device)

    def update_persona(self, user_id: str, signals: Dict[str, str]) -> UserPersona:
        persona = self.personas.get(user_id, UserPersona('balanced', 'intermediate', [], {}))
        if 'communication_style' in signals:
            persona.communication_style = signals['communication_style']
        if 'expertise_level' in signals:
            persona.expertise_level = signals['expertise_level']
        if 'goal' in signals:
            persona.goals.append(signals['goal'])
        persona.preferences.update({key: value for key, value in signals.items() if key.startswith('pref_')})
        self.personas[user_id] = persona
        return persona

def persona_snapshot(self, user_id: str) -> dict:
    persona = self.personas[user_id]
    return {
        'communication_style': persona.communication_style,
        'expertise_level': persona.expertise_level,
        'goal_count': len(persona.goals),
        'preferences': dict(persona.preferences),
    }


def on_device_persona(self, user_id: str) -> PersonalizedConfig:
    return self.adapt_bot('local-personalizer', user_id, on_device=True)


HyperPersonalizer.persona_snapshot = persona_snapshot
HyperPersonalizer.on_device_persona = on_device_persona

def has_persona(self, user_id: str) -> bool:
    return user_id in self.personas


HyperPersonalizer.has_persona = has_persona
