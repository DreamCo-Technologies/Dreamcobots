window.BUDDY_MEDIA_QUALITY_LAB = {
  "candidate_pipeline": [
    "validate active consent and artifact licenses",
    "hash the fixture, direction, source reference, engine version, and seed",
    "normalize text, pronunciation hints, framing, and performance direction",
    "render candidates locally with network access off",
    "trim silence or borders without changing identity",
    "normalize loudness, color space, and export metadata",
    "run deterministic and blinded human evaluators",
    "preserve only approved artifacts and useful aggregate evidence"
  ],
  "comparison_gate": {
    "confidence_level": 0.95,
    "minimum_fixtures": 30,
    "minimum_ratings_per_fixture": 3,
    "minimum_score_margin": 0.02,
    "minimum_wilson_lower_bound": 0.5,
    "requires_blind_review": true,
    "requires_identical_fixtures": true,
    "requires_randomized_order": true,
    "superiority_language_before_gate": false
  },
  "evidence_required_per_candidate": [
    "artifact SHA-256",
    "engine and installed model version",
    "signed fixture-set reference",
    "deterministic seed where supported",
    "evaluator and evaluator version",
    "fixture and repetition counts",
    "scorecard dimensions before rounding",
    "latency and peak resource use",
    "active rights and provenance references"
  ],
  "fixture_sets": [
    {
      "cases": [
        "clean narration",
        "natural conversation",
        "emotional range",
        "names, dates, currency, and difficult pronunciation",
        "long-form stability",
        "cross-language identity",
        "quiet and high-energy delivery",
        "noisy-reference robustness"
      ],
      "id": "voice-core-v1",
      "minimum_release_fixtures": 8,
      "modality": "voice"
    },
    {
      "cases": [
        "front portrait",
        "profile and three-quarter view",
        "full-body consistency",
        "lighting and color changes",
        "style variation",
        "legible in-scene text",
        "multi-scene identity consistency"
      ],
      "id": "image-core-v1",
      "minimum_release_fixtures": 7,
      "modality": "image"
    },
    {
      "cases": [
        "short conversational speech",
        "long-form identity stability",
        "fast phoneme sequence",
        "head and eye motion",
        "lighting transition",
        "emotional expression transition",
        "multilingual dubbing and lip sync"
      ],
      "id": "video-core-v1",
      "minimum_release_fixtures": 7,
      "modality": "video"
    }
  ],
  "hard_release_gates": [
    "active_consent",
    "adult_or_original_subject",
    "scoped_usage_rights",
    "installed_artifact_license",
    "provenance_manifest",
    "synthetic_media_label",
    "revocation_check",
    "owner_release_review"
  ],
  "quality_modes": {
    "balanced": {
      "candidate_count_per_engine": 3,
      "release_eligible": true,
      "repetitions_per_fixture": 2
    },
    "fast_preview": {
      "candidate_count_per_engine": 1,
      "release_eligible": false,
      "repetitions_per_fixture": 1
    },
    "highest_quality": {
      "candidate_count_per_engine": 6,
      "release_eligible": true,
      "repetitions_per_fixture": 3
    }
  },
  "retention": {
    "aggregate_metrics": "retain_while_useful",
    "failed_candidate_default": "delete_after_review_window",
    "raw_biometrics_in_score_report": false,
    "revocation_action": "block_export_and_schedule_owned_artifact_deletion",
    "winning_artifact_default": "owner_controlled_encrypted_storage"
  },
  "reviewed_on": "2026-07-31",
  "schema": "dreamco.buddy_media_quality_lab.v1",
  "scorecards": {
    "image": {
      "dimensions": {
        "anatomy_consistency": 0.1,
        "artifact_cleanliness": 0.12,
        "demographic_consistency": 0.05,
        "identity_similarity": 0.2,
        "latency_efficiency": 0.04,
        "prompt_adherence": 0.18,
        "style_control": 0.06,
        "text_legibility": 0.07,
        "visual_quality": 0.18
      },
      "regression_tolerance": 0.01,
      "release_threshold": 0.82
    },
    "video": {
      "dimensions": {
        "artifact_cleanliness": 0.08,
        "audio_quality": 0.1,
        "expression_control": 0.1,
        "identity_consistency": 0.18,
        "latency_efficiency": 0.04,
        "lip_sync": 0.16,
        "prompt_adherence": 0.06,
        "temporal_stability": 0.15,
        "visual_quality": 0.13
      },
      "regression_tolerance": 0.01,
      "release_threshold": 0.82
    },
    "voice": {
      "dimensions": {
        "artifact_cleanliness": 0.07,
        "expressiveness": 0.08,
        "identity_similarity": 0.2,
        "intelligibility": 0.18,
        "latency_efficiency": 0.04,
        "naturalness": 0.18,
        "pronunciation": 0.1,
        "prosody_control": 0.1,
        "stability": 0.05
      },
      "regression_tolerance": 0.01,
      "release_threshold": 0.82
    }
  },
  "strategy": [
    "generate multiple candidates across eligible local engines and deterministic seeds",
    "measure every candidate on identical signed fixtures",
    "reject candidates that fail consent, rights, provenance, labeling, or license gates",
    "select the strongest evidence-backed candidate instead of trusting one model",
    "prevent releases that regress below the last accepted local baseline",
    "use optional paid providers only as separately approved comparison references"
  ],
  "truth_boundary": "Buddy may target higher quality than any reference, but may claim an advantage only after a completed, blinded, repeatable comparison passes every evidence gate."
};
