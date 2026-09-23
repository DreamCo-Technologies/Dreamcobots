"""Small public router. No tokens, no writes, no spending."""
from __future__ import annotations

import json
from pathlib import Path

import gradio as gr

HERE = Path(__file__).resolve().parent


def load_skills() -> list[dict]:
    skills: list[dict] = []
    for path in sorted(HERE.glob("skills_*.json")):
        skills.extend(json.loads(path.read_text(encoding="utf-8")).get("skills") or [])
    by_id = {s["id"]: s for s in skills if s.get("id")}
    return [by_id[k] for k in sorted(by_id)]


SKILLS = load_skills()


def answer(text: str) -> str:
    said = (text or "").lower().strip()
    if not said:
        return "Type something like: i'm new, save my work, or what's broken."
    best = None
    best_score = 0
    for skill in SKILLS:
        score = 0
        title = str(skill.get("title") or "").lower()
        if title and title in said:
            score += 5
        for trig in skill.get("triggers") or []:
            trig = str(trig).lower()
            if trig and trig in said:
                score += 3 if len(trig) > 3 else 2
        if score > best_score:
            best, best_score = skill, score
    if not best:
        return "I don't have a written reply for that. Try: i'm new, save my work, what's broken, or plain words please."
    steps = "\n".join(f"- {step}" for step in best.get("steps") or [])
    return f"{best['reply']}\n\n{steps}\n\nThis did not change GitHub or Hugging Face."


demo = gr.Interface(
    fn=answer,
    inputs=gr.Textbox(label="Say it in plain words", lines=2),
    outputs=gr.Textbox(label="Buddy says"),
    title="DreamCo beginner router",
    description=f"{len(SKILLS)} written replies. Not a ranked model.",
)
if __name__ == "__main__":
    demo.launch()
