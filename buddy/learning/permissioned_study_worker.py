"""Permission-gated study execution; media and transcript access stay disabled."""
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class StudyAuthorization:
    source: str
    source_url: str
    scope: str
    allowed_actions: frozenset[str] = frozenset()

@dataclass(frozen=True)
class StudyContext:
    workspace: Path
    media_download_allowed: bool = False
    transcript_ingestion_allowed: bool = False
    model_training_allowed: bool = False
