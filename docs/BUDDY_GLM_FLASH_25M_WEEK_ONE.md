# Buddy 25M+ parameter experiment: one-week milestone

## Scope
A 25M+ parameter model cannot reproduce GLM-5.3-Flash's broad capabilities by copying a few responses. GLM-5.3-Flash has approximately 320B total / 18B active parameters. This experiment is a **small original Buddy model**, not a compressed copy of GLM's weights or architecture.

## Day-by-day acceptance criteria
1. Review GLM-5.3-Flash's official model card and MIT license, and separately confirm the inference provider's output-training terms. **Do not assume model-weight licensing automatically permits API output distillation.**
2. Gather a locally stored, provenance-recorded, rights-cleared dataset; remove private data and benchmark holdouts. No automatic external scraping.
3. Install PyTorch locally on the user's Mac, verify MPS availability and memory headroom.
4. Run a bounded original-model experiment: `python -m buddy.certification.train_original_25m --licensed-data /path/to/approved.txt --output-dir /path/out --steps 100`. Start with fewer steps if memory constrained.
5. Evaluate on untouched holdouts. Report loss, independent task metrics, hardware, runtime, and reproducible checkpoint hashes.
6. If provider terms permit teacher-output training, add separately reviewed GLM-generated examples with provenance and compare distilled-vs-undistilled students. Otherwise use independently licensed instruction data.
7. Publish evidence of completed experiments and blockers; never declare model GLM-equivalent or production-ready without independent proof.

## Safety and limitations
- The committed trainer does **not** invoke GLM or perform distillation. It is a byte-level transformer training baseline with >25M parameters, and may be slow on a 24GB Mac.
- No pretrained weights, model downloads, external inference, cloud compute, or API costs are initiated by this repository code.
- Keep training data and checkpoints outside Git unless explicitly approved and scrubbed; model weights can be large and sensitive.
- A one-week checkpoint is an engineering goal, not a guaranteed outcome or frontier-quality model.
