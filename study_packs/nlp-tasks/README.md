# HF NLP Task Zoo drills (Buddy literacy)

Five core Hugging Face NLP tasks as small, runnable drills. Metadata + drills only: no weights downloaded, train_allowed false.

| Task | HF pipeline | Metric | Floor | Drills | Card |
| --- | --- | --- | --- | --- | --- |
| `classification` | `text-classification` | `accuracy` | 0.85 | 6 | [CARD](classification/CARD.md) |
| `ner` | `token-classification` | `entity_f1` | 0.8 | 5 | [CARD](ner/CARD.md) |
| `qa` | `question-answering` | `squad_em_f1` | 0.75 | 5 | [CARD](qa/CARD.md) |
| `summarization` | `summarization` | `rougeL_lite` | 0.35 | 3 | [CARD](summarization/CARD.md) |
| `translation` | `translation` | `chrf_lite` | 0.5 | 5 | [CARD](translation/CARD.md) |

- `drill_runner.py` scores a predictions JSONL against a task's drills (stdlib, no network).
- `drill_runner.py --selftest` scores gold-vs-gold and one known-wrong set per task to prove the scorer works. That is harness evidence, not model evidence.
- Related capability packs: `../pack.summarize`, `../pack.translate`.
