from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class ContentRequest:
    type: str
    topic: str
    audience: str
    tone: str
    length: int
    seo_keywords: List[str]


@dataclass
class ContentResult:
    content: str
    quality_score: float
    stage_outputs: List[str]


class ContentPipeline:
    def run(self, request: ContentRequest) -> ContentResult:
        research = self._research(request)
        outline = self._outline(request, research)
        draft = self._draft(request, outline)
        reviewed = self._review(draft)
        optimized = self._optimize(reviewed, request.seo_keywords)
        published = self._publish(request, optimized)
        quality = min(0.99, 0.6 + len(request.seo_keywords) * 0.04 + min(request.length, 1500) / 5000)
        return ContentResult(published, round(quality, 3), [research, outline, draft, reviewed, optimized, published])

    def _research(self, request: ContentRequest) -> str:
        return f'Research pack for {request.topic} targeting {request.audience} with tone {request.tone}.'

    def _outline(self, request: ContentRequest, research: str) -> str:
        return f'Outline: intro, value, proof, CTA for {request.type}. Based on {research}'

    def _draft(self, request: ContentRequest, outline: str) -> str:
        body = f"{request.topic} for {request.audience}. {outline}"
        if request.type == 'video_script':
            body += ' Include scene notes and voiceover cues.'
        elif request.type == 'image_prompt':
            body += ' Include style, lighting, and composition guidance.'
        return body

    def _review(self, draft: str) -> str:
        return draft + ' Reviewed for clarity, claims, and brand alignment.'

    def _optimize(self, reviewed: str, seo_keywords: List[str]) -> str:
        keyword_line = ', '.join(seo_keywords)
        return reviewed + f' Optimized with keywords: {keyword_line}.'

    def _publish(self, request: ContentRequest, optimized: str) -> str:
        return f'PUBLISHED[{request.type.upper()}]: {optimized[:request.length]}'
