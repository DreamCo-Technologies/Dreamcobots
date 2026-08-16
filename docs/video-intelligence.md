# Buddy Video Intelligence

Buddy should process long videos efficiently by using a progressive analysis strategy instead of sending every frame to a model.

## Pipeline

`metadata → adaptive sampling → scene detection → shot clustering → keyframes → audio → optional speech/OCR/object/action analysis → timeline index → retrieval → reasoning → verification`

## Efficiency principles

- Start with metadata and a low-cost coarse pass.
- Increase frame density around scene changes and relevant events.
- Deduplicate near-identical frames.
- Run OCR, object tracking, and speech analysis only when useful.
- Cache intermediate artifacts so retries don't restart the whole video.
- Escalate resolution only when evidence requires it.
- Store timestamps with observations so claims can be checked.
- Preserve uncertainty instead of filling gaps with guesses.

## Benchmarking

Measure temporal localization, action recognition, scene retrieval, OCR, speech, object tracking, domain accuracy, hallucination rate, and processing efficiency.

The video system feeds Buddy's world-model and simulation work: observations can become original benchmark scenarios, environmental rules, animation requirements, and regression tests.

Use authorized sources and minimum necessary retention. Free/local/open tooling is the default; paid video models require explicit approval.
