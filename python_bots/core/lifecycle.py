from enum import Enum


class BotLifecycleState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    QUARANTINED = "quarantined"
    STOPPED = "stopped"
    FAILED = "failed"
