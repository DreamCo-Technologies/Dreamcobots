# Buddy Bootcamp: 65-division learning curriculum

This curriculum gives every canonical MasterBot division a distinct student-model identity and a shared foundation across all 37 Hugging Face task families, then adds division-specific capability packs and pipeline-tag specializations.

## Coverage

- 65 division-specific curriculum lanes and independent model artifact namespaces.
- All 37 task families from the repository's refreshable Hugging Face task taxonomy.
- All 10 capability packs from the HF capability download map.
- 12 dataset discovery dimensions and 9 model discovery dimensions.
- 13 shared engineering modules covering ML foundations, data governance, instruction, reasoning, retrieval, agents/tools, multimodal, multilingual, safety/privacy, authorized reverse engineering, SFT/LoRA/distillation, evaluation, and MLOps/runtime.

## Buddy as teacher coordinator

Buddy is specified as the teacher coordinator: it plans curricula, selects only approved teacher routes, evaluates teacher quality, coordinates student training, and tracks evidence. This does not claim Buddy is already a trained teacher model. The best teacher candidate must be established through pinned revisions, license review, quality benchmarks, safety/privacy checks, latency/cost evaluation and independent selection.

Teacher-generated examples are untrusted. Training them requires documented output-use rights, provenance, quality filtering, deduplication, privacy screening and explicit approval. Paid provider calls require per-request approval.

## Division-specific students

Each division receives its own model name/version and weights, checkpoint, tokenizer, database, dataset, benchmark and runtime paths. Shared foundation modules and base-model weights may be reused when licensed and pinned; trained division artifacts remain isolated.

## Evidence boundary

The generated artifact is a curriculum and discovery plan, not proof of training. It does not download Hugging Face datasets/models, authorize licensing, run GPU jobs, certify models or deploy endpoints. Each division remains `SPECIFIED_NOT_TRAINED` until the training runner produces immutable weights/checkpoints/tokenizer hashes and independent benchmark evidence passes.
