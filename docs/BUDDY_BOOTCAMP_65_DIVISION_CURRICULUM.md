# Buddy Bootcamp: 65-division learning curriculum

This curriculum gives every canonical MasterBot division a distinct student-model identity and a shared foundation across all 37 Hugging Face task families, then adds division-specific capability packs and pipeline-tag specializations.

## Coverage

- 65 division-specific curriculum lanes and independent model artifact namespaces.
- All 37 task families from the repository's refreshable Hugging Face task taxonomy.
- All 10 capability packs from the HF capability download map.
- 12 dataset discovery dimensions and 9 model discovery dimensions.
- 13 shared engineering modules covering ML foundations, data governance, instruction, reasoning, retrieval, agents/tools, multimodal, multilingual, safety/privacy, authorized reverse engineering, SFT/LoRA/distillation, evaluation, and MLOps/runtime.

## Training resource ecosystems

The curriculum is not limited to Hugging Face. The generated Bootcamp catalog also maps nine governed source families:

1. DreamCo-authored lessons, verified work, tests, and approved synthetic fixtures.
2. Official technical documentation and training frameworks.
3. Public dataset catalogs such as Hugging Face, Kaggle, OpenML, UCI, Zenodo, Data.gov, and public cloud dataset registries.
4. Research metadata and scholarly indexes.
5. Software repositories, releases, and package registries.
6. Government and standards-body data.
7. User-contributed data with purpose-specific opt-in.
8. Teacher-model outputs only when the provider and account terms explicitly allow training use.
9. Evaluation-only data, private holdouts, and red-team suites, which are never training inputs.

Each source is discovered and reviewed independently. The registry does not imply active connectors, downloads, licenses, or training permission. Source and file-level terms, provenance, privacy, quality, and intended commercial use remain required gates.

## DreamCo-originated teaching data

The first-party Bootcamp seed corpus is maintained at `data/dreamco_training/bootcamp/core_lessons.v1.jsonl`. Its original lesson drafts cover the 13 core modules and include stable IDs, rubrics, tags, and pinned train/validation/test assignments. The candidate builder materializes lane-specific copies for all 65 MasterBots with separate owner IDs and content hashes.

These are small draft candidates, not a complete training corpus. Ownership/assignment and training permission remain pending human review. The factory does not train models or copy private conversation transcripts, customer data, or third-party text.

## Buddy as teacher coordinator

Buddy is specified as the teacher coordinator: it plans curricula, selects only approved teacher routes, evaluates teacher quality, coordinates student training, and tracks evidence. This does not claim Buddy is already a trained teacher model. The best teacher candidate must be established through pinned revisions, license review, quality benchmarks, safety/privacy checks, latency/cost evaluation and independent selection.

Teacher-generated examples are untrusted. Training them requires documented output-use rights, provenance, quality filtering, deduplication, privacy screening and explicit approval. Paid provider calls require per-request approval.

## Division-specific students

Each division receives its own model name/version and weights, checkpoint, tokenizer, database, dataset, benchmark and runtime paths. Shared foundation modules and base-model weights may be reused when licensed and pinned; trained division artifacts remain isolated.

## Evidence boundary

The generated artifact is a curriculum and discovery plan, not proof of training. It does not download Hugging Face datasets/models, authorize licensing, run GPU jobs, certify models or deploy endpoints. Each division remains `SPECIFIED_NOT_TRAINED` until the training runner produces immutable weights/checkpoints/tokenizer hashes and independent benchmark evidence passes.
