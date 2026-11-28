# DreamCo Media Foundry — Stage 10

Stage 10 is a local-first production planner for original music, voice, consistent
characters, animation, video, films, and YouTube workflows. Stage 08 remains
Repo Sentinel; Stage 09 remains Universal Watchtower.

## Model inventory and license truth

The registry distinguishes repository code licenses from exact checkpoint,
base-model, tokenizer, and dependency licenses. A repository MIT or Apache
license does not automatically prove that every downloaded weight or upstream
model is commercially usable.

Initial candidates:
- Chatterbox TTS — MIT repository; exact checkpoint/dependency review remains open.
- FLUX.2 Klein 4B — Apache-2.0 model card and official repository; exact revision,
  dependencies, inputs, and output terms still require release review.
- Wan 2.2 — Apache-2.0 repository/model card; exact task checkpoint and
  dependencies still require review.
- LongCat-Video — MIT repository; checkpoint license remains unverified.
- ACE-Step 1.5 — MIT repository; DiT/LM/base checkpoint and dependency review
  remains open.
- Whisper — MIT code and model weights; exact immutable revision and dependency review remain open.

Excluded from commercial workflows:
- F5-TTS: code is MIT, but official pretrained checkpoints are CC-BY-NC-4.0; do not use those weights for monetized or commercial outputs.
- FLUX.2 Klein 9B: FLUX Non-Commercial license.

No model is marked deployment-approved in the initial registry. The owner must
review the exact artifact revision, license text, dependency SBOM, commercial
permission, and output terms before approval.

## Pipeline

1. Brief and project type.
2. Asset/model rights preflight.
3. Script, treatment, and storyboard.
4. Character reference and keyframe generation.
5. Shot plan and continuity map.
6. Voice, music, and sound design.
7. Video/animation render through an explicitly configured adapter.
8. Edit timeline, captions, and platform versions.
9. Output hash and provenance quality gate.
10. Human release approval.

## Python usage

Import numbered stage folders through importlib because they are not valid
Python import syntax.

    import importlib
    director = importlib.import_module("stages.10_media_studio.director")
    packet = director.build_production_packet(
        {"title": "DreamCo Pilot", "objective": "Create an original channel trailer", "audience": "general"},
        [{"shot_id": "shot-001", "description": "Original DreamCo logo appears over a dark studio stage", "duration_seconds": 5}],
    )

The packet status is planned_not_rendered. A renderer must return actual files
and hashes before the quality gate can certify a render. The first release does
not download models, call paid APIs, upload assets, or publish media.
