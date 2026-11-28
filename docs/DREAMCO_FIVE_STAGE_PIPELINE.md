# DreamCo Five-Stage Clean-Room Pipeline

## Local setup

    python -m pip install -r requirements-reverse-engineer.txt
    make test-all

## Stage contracts and CLI

Every stage reads one JSON contract and writes one JSON contract. Contract schemas are under \`contracts/\`.

1. Policy gate:
   \`python -m stages.01_policy_gate --input raw_upload.json --output artifact_manifest.json\`
2. Deterministic parser:
   \`python -m stages.02_intake_parser --input artifact_manifest.json --output parsed_facts.json\`
3. Abstract specification:
   \`python -m stages.03_spec_and_onet --input parsed_facts.json --output functional_spec.json\`
   Add \`--onet-db /path/to/authorized-onet.sqlite --task-description "owner-authored task description"\` to query a local read-only SQLite table named \`onet_tasks(soc_code, task_id, task)\`.
4. Mock clean-room generation:
   \`python -m stages.04_clean_room_gen --input functional_spec.json --output course_module.json --mock\`
5. Sandbox verification:
   Build the trusted verifier image with \`make build-sandbox\`, run a rootless Docker daemon, then:
   \`python -m stages.05_sandbox_verifier --input course_module.json --output eval_report.json --reference /path/to/owner-authorized-reference.txt\`

## Stage boundaries

- Stage 1 requires explicit authorization, applies heuristic secret/PII redaction, checks a 5 MiB text limit and bounded ZIP metadata, and rejects unsupported/restricted URL targets. Redaction is not a guarantee; manually review high-risk material.
- Stage 2 uses Python AST, JSON, OpenAPI JSON, HAR and CSV parsing only. It does not import or execute uploaded source. Unsupported formats fail closed.
- Stage 3 replaces function and field identifiers with abstract operation labels. O*NET matching is optional and uses an owner-provisioned SQLite catalog; lexical matching is triage, not an official job classification. A human must confirm the match.
- Stage 4 currently supports deterministic mock generation only. No external model is called. Add a model adapter only after license, model provenance, data retention and structured-output controls are independently reviewed.
- Stage 5 requires an owner-authorized comparison reference and a rootless Docker daemon. The container is network-disabled, read-only, non-root, capability-dropped, PID/memory/CPU bounded and limited to 10 seconds. Similarity is a heuristic, not legal proof of originality.
- Training export is opt-in through \`DREAMCO_TRAINING_EXPORT_PATH\` and rejects records unless tests pass, policy passes and similarity is below 0.25. Exported records contain abstract specifications, generated code and evaluation metadata only; hidden chain-of-thought, raw uploads and secrets are not collected.

## Not yet production-complete

There is no production FastAPI service, managed O*NET data distribution, live LLM adapter, remote training bucket integration, complete multi-language parser coverage, Docker runtime integration test in hosted CI, or legal originality guarantee. These are deliberately not represented as shipped capabilities. Use a rootless Docker host and run a separate integration test before enabling production jobs.
