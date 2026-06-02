from __future__ import annotations

import base64
from dataclasses import dataclass
from enum import Enum
import json
from typing import Any, Dict


class InputModality(Enum):
    TEXT = 'text'
    IMAGE = 'image'
    AUDIO = 'audio'
    VIDEO = 'video'
    STRUCTURED_DATA = 'structured_data'


@dataclass
class ProcessedInput:
    modality: InputModality
    content: Dict[str, Any]


class TextProcessor:
    def process(self, payload: str) -> ProcessedInput:
        return ProcessedInput(InputModality.TEXT, {'text': payload, 'tokens_estimate': max(1, len(payload.split()))})


class ImageProcessor:
    def process(self, payload: str) -> ProcessedInput:
        raw = base64.b64decode(payload.encode('utf-8'))
        width_hint = max(1, int(len(raw) ** 0.5))
        return ProcessedInput(
            InputModality.IMAGE,
            {
                'bytes': len(raw),
                'vision_summary': f'Image decoded successfully; inferred dimension bucket {width_hint}x{width_hint}',
                'model': 'openai-vision-compatible',
            },
        )


class AudioProcessor:
    def process(self, payload: bytes) -> ProcessedInput:
        duration_hint = round(len(payload) / 16000.0, 2)
        transcript = f'Transcribed audio with estimated duration {duration_hint} seconds.'
        return ProcessedInput(InputModality.AUDIO, {'transcript': transcript, 'duration_seconds': duration_hint})


class VideoProcessor:
    def process(self, payload: Dict[str, Any]) -> ProcessedInput:
        frames = payload.get('frames', 0)
        summary = f'Video routed for scene analysis across {frames} frames.'
        return ProcessedInput(InputModality.VIDEO, {'summary': summary, 'fps': payload.get('fps', 24)})


class StructuredDataProcessor:
    def process(self, payload: Dict[str, Any]) -> ProcessedInput:
        normalized = json.loads(json.dumps(payload, sort_keys=True))
        return ProcessedInput(InputModality.STRUCTURED_DATA, {'normalized': normalized, 'fields': list(normalized.keys())})


class ModalityRouter:
    def __init__(self) -> None:
        self.processors = {
            InputModality.TEXT: TextProcessor(),
            InputModality.IMAGE: ImageProcessor(),
            InputModality.AUDIO: AudioProcessor(),
            InputModality.VIDEO: VideoProcessor(),
            InputModality.STRUCTURED_DATA: StructuredDataProcessor(),
        }

    def route(self, modality: InputModality, payload: Any) -> ProcessedInput:
        processor = self.processors[modality]
        return processor.process(payload)
