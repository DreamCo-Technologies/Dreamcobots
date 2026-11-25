# Buddy Open-Source Multimodal Bootcamp

## Goal

Buddy Bootcamp is a continuously refreshed, evidence-based learning system for the 55 DreamCo domain divisions. It discovers upstream repositories, Hugging Face datasets/models/Spaces, technical documentation, and authorized video/audio/music material. It creates detailed independent study guides, lessons, projects, assessments, and training candidates. It does not claim that Buddy has mastered a topic simply because it indexed or summarized a source.

## Repositories first, not YouTube-first

The primary curriculum sources are versioned public repositories: source code, READMEs, documentation, examples, tests, notebooks, issue discussions where appropriate, release notes, and project architecture. YouTube is an optional media source, never the sole source of truth. The source catalog must retain repository URL, pinned commit or release, license identifier and evidence, discovery date, upstream attribution, division mapping, and a recheck date.

Buddy learns by *studying* upstream implementation and documentation, then building an independent exercise or compatible integration. It must not copy entire repositories into DreamCo or represent upstream code as original DreamCo work. License compatibility and security checks precede reuse.

## Hugging Face: all subjects, all artifact types

The discovery system searches the Hub's datasets, models, and Spaces separately. It uses task/subject terms and pagination, stores the Hub ID, card metadata, tags, license, revision, downloads/likes where available, and the source card URL. Each artifact gets its own summary and suitability review:
- Dataset guide: purpose, features, splits, sampling, data provenance, bias, privacy, license, preprocessing, recommended tasks, and evaluation plan.
- Model guide: intended use, architecture, task, inputs/outputs, inference, training disclosures, evaluation, limitations, license, hardware and safety.
- Space guide: demo purpose, user flow, model/dataset dependencies, code/dependencies, reproducibility, limitations and license.

"Every subject" means the subject taxonomy and discovery sweep must be broad and continually expanded from observed Hub tags. The Hub changes constantly; do not promise a fixed final count or claim every artifact was summarized unless inventory pagination and guide coverage prove it.

## Video, audio and music learning

A rights-gated local-media preparation tool is included at `tools/process_authorized_bootcamp_media.py`. It accepts media only from `data/authorized-media/`, requires an asset-specific SHA-256 match and separate study, derivative-summary and evaluation permissions, then uses local `ffprobe`/`ffmpeg` to extract audio and sparse video frames. It does not download media or model weights. The generated `asset-study-input.json` is input evidence for Buddy; it is not itself a transcript, summary, training run or mastery result. The media manifest is `config/buddy-authorized-media-rights.json`.

Buddy needs a multimodal ingestion capability, not just a URL catalog. For authorized or user-provided videos, the pipeline can extract audio, transcribe speech, sample frames, detect scenes, align timestamps, explain code or demonstrations, and create a detailed chapter-by-chapter guide. Sparse frame sampling is the default; dense processing is reserved for tasks that need temporal understanding.

For audio and music, Buddy can learn speech recognition, sound classification, audio signal processing, music information retrieval, tempo/meter, harmony/key estimation, structure, timbre/instrument analysis where supported, production/mixing concepts, and MIDI/score analysis. Music generation and audio models are separate capabilities and require their own model, data, compute, and evaluation plan. Copyrighted recordings are not automatically training data: use public-domain, permissively licensed, or user-owned assets with explicit permissions.

## Detailed guide standard

Every eligible source should receive a guide comparable in depth to the freeCodeCamp guide format:
1. Executive summary and detailed explanation.
2. Chapter/section map with timestamps or repository paths/line references.
3. Learning objectives and prerequisites.
4. Key concepts and terminology.
5. Architecture and code walkthroughs.
6. Reproducible worked examples.
7. Common mistakes, debugging, security and performance notes.
8. At least three original exercises and one capstone.
9. Knowledge checks with answer key.
10. Division mapping, citations, upstream version and license evidence.
11. Independent practice evidence, reviewer status and last-verified date.

If the source is metadata-only, Buddy may create a metadata record and a pending task, but must not invent a detailed summary.

## Machine-learning strategy stack

The system uses complementary strategies rather than assuming one training method can teach every skill:
- Retrieval-augmented learning for current, cited facts and source navigation.
- Supervised instruction tuning for carefully curated, licensed examples.
- Self-supervised learning for permitted raw corpora.
- Contrastive learning for text/image/audio/video/code alignment.
- LoRA/adapters for affordable domain specialization.
- Knowledge distillation to transfer validated capabilities from teacher models.
- Preference optimization for consented, high-quality preference pairs.
- Sandboxed reinforcement learning for tool use and agent behavior.
- Continual learning with replay, versioning, forgetting tests and rollback.
- Curriculum learning, prerequisite graphs and spaced repetition.
- Program synthesis and execution-based learning from independent implementations.
- Ensembles and model routing to select specialist models by measured performance.

No single strategy is assumed to be appropriate for all divisions. Each training run must state its hypothesis, dataset provenance, license, baseline, compute budget, evaluation split, expected gain, safety checks, and rollback plan.

## Weekly build loop

The weekly scheduled workflow should:
1. Discover new/changed repositories and Hugging Face artifacts.
2. Refresh versions and license metadata.
3. Deduplicate and run security/PII checks.
4. Queue rights review and source summarization.
5. Generate division-specific bootcamp lessons and projects.
6. Schedule five lessons per day per division as a target, subject to source eligibility and capacity.
7. Assess Buddy on eligible material, including weekly source/transcript coverage.
8. Build training candidates only from approved data.
9. Run regression, transfer, safety, latency and cost evaluations.
10. Publish a weekly report and next-week curriculum.

A successful discovery workflow is not proof that the model trained. A successful guide workflow is not proof of mastery. Reports must separate discovered, rights-cleared, summarized, studied, assessed, trained, and mastered counts.

## Operational limits

The scheduled workflow can discover and prepare work, but actual GPU training requires a configured runner/provider, secrets, quotas and a budget. It must fail closed when compute is unavailable rather than silently consuming paid resources. The repository can define and validate the training pipeline before an accelerator is connected.
