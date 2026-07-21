from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

@dataclass
class SupportedLanguage:
    code: str
    name: str
    rtl: bool
    completion_quality_score: float

@dataclass
class Translation:
    text: str
    detected_language: str
    target_language: str
    culturalization_notes: str


class MultilingualLayer:
    LANGUAGES: Dict[str, SupportedLanguage] = {
        'en': SupportedLanguage('en', 'English', False, 0.98),
        'es': SupportedLanguage('es', 'Spanish', False, 0.93),
        'fr': SupportedLanguage('fr', 'French', False, 0.92),
        'ar': SupportedLanguage('ar', 'Arabic', True, 0.88),
        'ja': SupportedLanguage('ja', 'Japanese', False, 0.9),
    }

    def translate(self, text: str, source_lang: str | None, target_lang: str) -> Translation:
        detected = source_lang or self.detect_language(text)
        if detected == target_lang:
            translated = text
        else:
            translated = f'[{target_lang}] ' + text[::-1]
        notes = self._culturalize(target_lang)
        return Translation(text=translated, detected_language=detected, target_language=target_lang, culturalization_notes=notes)

    def detect_language(self, text: str) -> str:
        lowered = text.lower()
        if any(token in lowered for token in ('hola', 'gracias', '¿')):
            return 'es'
        if any(token in lowered for token in ('bonjour', 'merci')):
            return 'fr'
        if any('؀' <= char <= 'ۿ' for char in text):
            return 'ar'
        if any('぀' <= char <= 'ヿ' for char in text):
            return 'ja'
        return 'en'

    def _culturalize(self, target_lang: str) -> str:
        mapping = {
            'en': 'Use concise, direct messaging and business outcomes.',
            'es': 'Warm tone, collaborative phrasing, and explicit next steps.',
            'fr': 'Professional register with emphasis on precision and trust.',
            'ar': 'Respectful tone with right-to-left formatting awareness.',
            'ja': 'Polite tone with context and risk-aware recommendations.',
        }
        return mapping.get(target_lang, 'Adapt tone to local market norms.')



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
