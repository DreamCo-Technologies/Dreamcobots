"""Local deterministic logo concepts with an auditable rights manifest."""

from __future__ import annotations

import hashlib
import html
import re
from dataclasses import dataclass
from pathlib import Path


class BrandingError(ValueError):
    """Raised when a logo brief cannot be rendered safely."""


@dataclass(frozen=True)
class LogoBrief:
    brand_name: str
    personality: tuple[str, ...]
    primary_color: str
    accent_color: str
    symbol: str = "monogram"

    def validate(self) -> None:
        if len(self.brand_name.strip()) < 2 or len(self.brand_name) > 60:
            raise BrandingError("Brand name must contain 2 to 60 characters.")
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", self.primary_color) or not re.fullmatch(
            r"#[0-9A-Fa-f]{6}", self.accent_color
        ):
            raise BrandingError("Logo colors must use six-digit hex values.")
        if self.symbol not in {"monogram", "spark", "shield", "signal", "portal"}:
            raise BrandingError("Choose a supported original symbol family.")


class BuddyLogoGenerator:
    """Generate editable SVG concepts without stock or third-party artwork."""

    def generate(self, brief: LogoBrief) -> dict[str, str]:
        brief.validate()
        clean_name = " ".join(brief.brand_name.split())
        initials = "".join(part[0] for part in clean_name.split()[:2]).upper()
        concept_id = hashlib.sha256(
            f"{clean_name}:{brief.personality}:{brief.primary_color}:{brief.accent_color}:{brief.symbol}".encode("utf-8")
        ).hexdigest()[:16]
        safe_name = html.escape(clean_name)
        safe_initials = html.escape(initials)
        mark = self._mark(brief.symbol, brief.accent_color)
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 200" role="img" '
            f'aria-labelledby="title-{concept_id}"><title id="title-{concept_id}">{safe_name} logo concept</title>'
            f'<rect width="640" height="200" fill="{brief.primary_color}"/>'
            f'{mark}<text x="100" y="119" fill="#ffffff" font-family="Arial, sans-serif" font-size="54" '
            f'font-weight="700">{safe_name}</text><text x="50" y="120" text-anchor="middle" fill="#ffffff" '
            f'font-family="Arial, sans-serif" font-size="24" font-weight="700">{safe_initials}</text></svg>'
        )
        return {
            "schema": "dreamco.logo_concept.v1",
            "concept_id": f"logo-{concept_id}",
            "svg": svg,
            "rights": "generated from geometric primitives and owner-provided text; clearance search still required",
            "third_party_assets": "none",
            "trademark_registered": "no",
        }

    def write(self, concept: dict[str, str], path: Path) -> Path:
        if concept.get("schema") != "dreamco.logo_concept.v1" or "<svg" not in concept.get("svg", ""):
            raise BrandingError("A valid generated logo concept is required.")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(concept["svg"], encoding="utf-8")
        return path

    @staticmethod
    def _mark(symbol: str, accent: str) -> str:
        marks = {
            "monogram": f'<circle cx="50" cy="100" r="36" fill="{accent}"/>',
            "spark": f'<path d="M50 55 L60 88 L92 100 L60 112 L50 145 L40 112 L8 100 L40 88 Z" fill="{accent}"/>',
            "shield": f'<path d="M50 55 L84 68 V98 C84 122 69 139 50 148 C31 139 16 122 16 98 V68 Z" fill="{accent}"/>',
            "signal": f'<path d="M16 130 Q50 75 84 130 M26 112 Q50 82 74 112 M39 101 Q50 90 61 101" fill="none" stroke="{accent}" stroke-width="9" stroke-linecap="round"/>',
            "portal": f'<circle cx="50" cy="100" r="36" fill="none" stroke="{accent}" stroke-width="11"/><circle cx="50" cy="100" r="12" fill="{accent}"/>',
        }
        return marks[symbol]
