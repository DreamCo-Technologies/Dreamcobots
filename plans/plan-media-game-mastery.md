# plan-media-game-mastery — audit and plan

Status: **not production ready.** No trained weights. No sellable media or game package exists yet.
Audited against `main` at `dbb1a46` on 2026-09-28. Evidence only: each row points at a file that exists at that commit.

## What the repo already says about this plan

The repo has no file called `plan-media-game-mastery`, and it has no `plans/` naming convention. This file starts one.
These files already describe the goal:

| File | What it says |
|---|---|
| `docs/media-to-game-mastery.md` | Books, movies, video, websites, and games feed one learning graph. The loop is observe → infer rules → act → measure → adapt → build an original variant → benchmark. Protected works are used for concepts only. |
| `config/buddy_media_game_mastery_matrix.json` | Lists skills per media type, the game-builder targets, quality dimensions, a `copyright_rule`, and a `benchmark_rule`. No code reads this file. |
| `docs/MEDIA_GAME_CAPABILITY_ROADMAP.md` | Four phases: media basics, production pipelines, digital actors, and a game lab. `buddy/frontier/plan_status.py` marks it as "document", not a runner. |
| `config/buddy-training-data-provenance-policy.json` | Ownership classes, 17 required metadata fields per asset, and marketplace rules. No code loads it; only generated repo maps mention it. |

Machine-readable status: the repo tracks one frontier plan in `buddy/frontier/plan_status.py`, which writes `website/data/plan-status.json`. There is no status file per plan, so this audit adds none. When this plan has a runner, add a row to `DOCUMENTS` there, and update the asserts that count documents.

## Scope

Media/game mastery programs and packages. Buddy learns from web pages, books, movies, video, games, and user uploads. Every input must first pass a provenance, license, and consent gate. The outputs are:
1. Study or benchmark tasks built from those inputs.
2. Original simulations and games.
3. Packages that can be sold, but only when every input's rights allow it.

Out of scope until evidence exists: trained model weights, and any "production_ready" label.

## Gap table

| Goal | State | Real path(s) | Notes |
|---|---|---|---|
| Game lab: build plan from a brief | implemented (planner only) | `dreamco_platform/games/harness.py` (`BuddyGameLab.build_plan`), `tests/test_buddy_game_lab.py` | It returns a plan dict. It does not generate any game code or assets. |
| Game playing / playtest in a sandbox | implemented (harness) | `harness.py` `play_test`, `GameRuntimeAdapter` | It refuses adapters unless `owner_authorized` and `sandboxed` are both set. The only adapter is a test stub (`TinyGame`). No real game is connected. |
| Subject → simulation → game | stub | `harness.py` `convert_simulation_to_game` | It validates the brief and returns a design. Nothing can be played. |
| Game builder targets (2D/3D/browser/XR…) | missing | only listed in `config/buddy_media_game_mastery_matrix.json` | No engine integration. |
| Movies / video understanding | stub | `tools/video_scan_fast.py`, `tools/video_scan_manifest.py`, `tools/video_evidence_validator.py`, `config/buddy_video_*.json` | Builds a file inventory and checks claim schema. No model does scene, action, or timeline understanding. |
| Video → package | stub | `tools/video_package_compiler.py` | Sets `status: compiled_seed`. It does not check license or rights before packaging. |
| Books ingestion | missing | (`tools/dreamco_file_converter.py` converts files but has no rights metadata) | No book reader, no page/section pointers, no rule for public-domain proof. |
| Web ingestion | stub | `tools/buddy_source_selector.py` | Only ranks sources. It fetches nothing. `rights_ok` and `authorized` **default to `True`**, so an unchecked source passes. Its docstring says robots/terms checks belong to adapters, and no adapter exists. |
| User uploads: consent | implemented, but only for voice/image cloning | `buddy/media/consent.py` (`ConsentRegistry.require`, bound to file hash, scoped, revocable), `buddy/media/core.py` | Training and package ingest do not use it. It has no "train" or "sell" scopes. |
| Output provenance (what DreamCo generated) | implemented | `buddy/media/provenance.py` (watermark, sidecar `.provenance.json`, append-only ledger) | This covers outputs only, not the sources that went in. |
| Input provenance record per source | missing | policy only: `config/buddy-training-data-provenance-policy.json` | No schema or validator in the repo enforces the 17 `required_metadata` fields. |
| License check before training or packaging | missing | none | `connectors.py` lists model licenses as text only. Nothing enforces them. |
| Mastery promotion (source → variant → transfer → regression) | missing | rule text only in the matrix `benchmark_rule` | No runner. |
| Trained weights | missing | none | Do not claim any. |

## Provenance-gate requirements (must exist before any ingest)

1. **Rights record for every source**, using the 17 `required_metadata` fields in `config/buddy-training-data-provenance-policy.json` (source, license, license_url, collection_date, commercial_redistribution_allowed, attribution_required, provenance_hash, review_status, …). If any field is missing, the class is `unknown_do_not_publish`, and the asset is quarantined.
2. **No copyrighted movie, video, game, or book content goes in without a license.** The default class is `third_party_reference_only`. That allows summaries, citations, and original derived tasks only. Frames, clips, transcripts, maps, assets, and code stay out of sellable output.
3. **Web**: record robots.txt and terms status, the URL, the retrieval date, and a content hash. Unknown rights fail closed, which means changing the `rights_ok` / `authorized` defaults to `False`.
4. **Books**: record page or section pointers. Public domain needs a written basis (edition and date).
5. **Games**: play only through `GameRuntimeAdapter` with `owner_authorized=True` and `sandboxed=True`. Use either DreamCo-owned games or games whose license allows automated play.
6. **User uploads**: a consent record bound to the file hash, using the `buddy/media/consent.py` pattern. It adds scopes `train` and `sell`, an ownership attestation, and revocation. A revoked asset is removed from future package builds.
7. **Packages** take the most restrictive class of all their inputs. The package compiler refuses to build if any input is not cleared.

## P0 next steps

1. Add `schemas/source_provenance_record.schema.json` and a validator (`tools/validate_source_provenance.py`) that loads the policy's `required_metadata`. Add tests.
2. Make `tools/buddy_source_selector.py` fail closed: `rights_ok=False` and `authorized=False` by default. Add a test.
3. Make `tools/video_package_compiler.py` require a cleared provenance record for each `source`. Otherwise it refuses and exits non-zero.
4. Extend `buddy/media/consent.py` scopes to `train` and `sell`. Call `ConsentRegistry.require(...)` in every upload ingest path.
5. Connect one real DreamCo-owned game (for example a small grid game) through `GameRuntimeAdapter`. Save playtest evidence under `evidence/` before claiming game-playing capability.
6. Keep this plan's status at `planned / partially coded`. Change it only when the above has tests passing in CI.
