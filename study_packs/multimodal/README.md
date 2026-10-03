# pack.multimodal: HF vision + ASR + TTS literacy

Cross-modal study pack for the Buddy AV trainer handoff. It complements
`pack.vision` and `pack.speech` (single-modality capability cards) with small,
pinned, CPU-runnable drills that exercise each Hugging Face `pipeline` task and
one real cross-modal loop (TTS audio transcribed back by ASR).

- train_allowed: false (study + eval only)
- min_native_pass_rate: 0.7
- automatic weight download: no (runner downloads pinned revisions only when run by hand)
- evidence: `evidence/latest.json` (plus timestamped `run_*.json`)

## Pinned models (verified against the Hub API on 2026-09-28)

| Task | Model | Revision | License | Commercial |
|---|---|---|---|---|
| zero-shot image classification | `openai/clip-vit-base-patch32` | `3d74acf9` | not declared on Hub | blocked until verified |
| image classification | `google/vit-base-patch16-224` | `3f49326e` | apache-2.0 | yes |
| text-to-speech | `facebook/mms-tts-eng` | `c71de0fe` | cc-by-nc-4.0 | **no** |
| speech recognition | `openai/whisper-tiny` | `169d4a43` | apache-2.0 | yes |
| audio classification | `MIT/ast-finetuned-speech-commands-v2` | `315b0b84` | bsd-3-clause | yes |

Full SHAs live in `sources.json`.

## Drills (`evals.json`)

1. `mm.clip_zero_shot_shapes`: CLIP picks the right caption for PIL-drawn shapes.
2. `mm.vit_imagenet_smoke`: ViT returns a valid top-5 (smoke only, no accuracy claim).
3. `mm.tts_generate`: MMS TTS produces a waveform; saved to `evidence/tts_sample.wav`.
4. `mm.asr_roundtrip`: Whisper transcribes the TTS clip; pass at WER <= 0.5.
5. `mm.audio_cls_smoke`: AST labels a TTS "yes"; top-1 match is informational.

Run: `python study_packs/multimodal/drill_runner.py` (needs `torch`, `transformers`, `pillow`, `soundfile`, `numpy`).

## Pipeline literacy notes

- Always pass `revision=` so runs are reproducible; `sources.json` is the single source of pins.
- Audio pipelines take `{"raw": float32 array, "sampling_rate": sr}`. Whisper and AST expect 16 kHz; MMS TTS emits 16 kHz, but resample anything else first.
- Zero-shot CLIP quality depends heavily on label phrasing ("a red circle" beats "circle").
- Whisper-tiny hallucinates on silence and very short clips; keep clips over about 1 s.
- TTS then ASR round-trips are a cheap, self-contained check but are optimistic (synthetic, clean audio). They are not a real-world ASR benchmark.

## Handoff to the Buddy AV trainer

`recipes/av_trainer_handoff.yaml` lists the gates. Only models with
`commercial_ok: true` may feed sellable CP/LP packages. MMS TTS is non-commercial,
and CLIP stays blocked until its license is verified.

## Latest run (2026-09-28, CPU, transformers 5.17.0, torch 2.14.0)

5 of 5 drills passed (`evidence/run_20260928T225217.json`). Observed results:
CLIP got all 3 shapes right; Whisper heard "The quick-brown fox jumps over the lazy die."
(WER 0.333); the MMS clip ran 3.94 s. Caveats: AST labeled the TTS "yes" as "visual"
(top-1 wrong, so synthetic single-word audio isn't a usable keyword-spotting check), and
ViT on a drawn circle is a smoke test only. The earlier run `run_20260928T225019.json`
records a real `transformers` 5.17 bug in the `text-to-speech` pipeline
(`BatchEncoding.to() got an unexpected keyword argument 'dtype'`); the drill now calls
`VitsModel` directly.
