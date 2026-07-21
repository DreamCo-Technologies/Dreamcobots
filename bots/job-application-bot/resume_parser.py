"""
resume_parser.py

Extracts text from PDF and DOCX resumes, then identifies skills and
qualifications via keyword matching.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import re
from pathlib import Path


def _extract_text_pdf(file_path: str) -> str:
    """Return the full text of a PDF resume using pdfminer.six."""
    try:
        from pdfminer.high_level import extract_text  # type: ignore
        return extract_text(file_path)
    except ImportError:
        raise ImportError(
            "pdfminer.six is required for PDF parsing. "
            "Install it with:  pip install pdfminer.six"
        )


def _extract_text_docx(file_path: str) -> str:
    """Return the full text of a DOCX resume using python-docx."""
    try:
        from docx import Document  # type: ignore
        doc = Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs)
    except ImportError:
        raise ImportError(
            "python-docx is required for DOCX parsing. "
            "Install it with:  pip install python-docx"
        )


def extract_text(file_path: str) -> str:
    """
    Extract raw text from a resume file.

    Supports .pdf and .docx formats.

    :param file_path: Absolute or relative path to the resume file.
    :returns: Extracted plain text.
    :raises ValueError: If the file format is not supported.
    :raises FileNotFoundError: If the file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_text_pdf(str(path))
    elif suffix == ".docx":
        return _extract_text_docx(str(path))
    else:
        raise ValueError(
            f"Unsupported resume format '{suffix}'. Supported formats: .pdf, .docx"
        )


def extract_skills(text: str, skill_keywords: list[str]) -> list[str]:
    """
    Return a list of skills found in *text* by matching against *skill_keywords*.

    Matching is case-insensitive and uses word-boundary checks to avoid
    partial-word false positives.

    :param text: Plain text extracted from a resume.
    :param skill_keywords: Skills to look for (e.g. ["Python", "SQL", "Git"]).
    :returns: Deduplicated list of matched skills (preserving original casing from
              *skill_keywords*).
    """
    found: list[str] = []
    for skill in skill_keywords:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)
    return found


class ResumeParser:
    """High-level facade that parses a resume file and reports qualifications."""

    def __init__(self, required_skills: list[str]):
        """
        :param required_skills: Skills considered required for a job application.
        """
        self.required_skills = required_skills
        self.resume_text: str = ""
        self.found_skills: list[str] = []

    def load(self, file_path: str) -> None:
        """
        Parse the resume at *file_path* and populate :attr:`found_skills`.

        :param file_path: Path to the resume (PDF or DOCX).
        """
        print(f"[ResumeParser] Parsing resume: {file_path}")
        self.resume_text = extract_text(file_path)
        self.found_skills = extract_skills(self.resume_text, self.required_skills)
        print(f"[ResumeParser] Skills found: {self.found_skills}")

    def is_qualified(self, min_skills: int = 1) -> bool:
        """
        Return True if the resume contains at least *min_skills* required skills.

        :param min_skills: Minimum number of required skills that must be present.
        """
        return len(self.found_skills) >= min_skills

    def qualification_summary(self) -> dict:
        """
        Return a dict with found skills, missing skills, and a qualified flag.
        """
        missing = [s for s in self.required_skills if s not in self.found_skills]
        return {
            "found_skills": self.found_skills,
            "missing_skills": missing,
            "qualified": self.is_qualified(),
        }
