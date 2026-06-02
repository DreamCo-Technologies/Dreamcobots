from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class Platform(Enum):
    REPLIT = 'replit'
    GITHUB_ACTIONS = 'github_actions'
    DOCKER = 'docker'
    K8S = 'k8s'
    LAMBDA = 'lambda'


@dataclass
class DeploymentHandle:
    bot_id: str
    platform: Platform
    runtime_target: str
    injected_secrets: Dict[str, str]


class BotBridge:
    def __init__(self) -> None:
        self.deployments: Dict[str, DeploymentHandle] = {}

    def deploy(self, bot_id: str, platform: Platform, config: Dict[str, str]) -> DeploymentHandle:
        translated = self._translate(platform, config)
        secrets = self._inject_secrets(config.get('secrets', {}))
        handle = DeploymentHandle(bot_id, platform, translated, secrets)
        self.deployments[f'{bot_id}:{platform.value}'] = handle
        return handle

    def _translate(self, platform: Platform, config: Dict[str, str]) -> str:
        target = config.get('target', 'default')
        return f'{platform.value}:{target}'

    def _inject_secrets(self, secrets: Dict[str, str]) -> Dict[str, str]:
        return {key: f'injected::{value}' for key, value in secrets.items()}
