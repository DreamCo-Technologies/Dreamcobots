# AI Data Package Library Report

Create governed AI data packages that DreamCo can sell or license for model training, fine-tuning, retrieval, benchmarking, evaluation, and agent simulation.

## Summary

- Bot package blueprints: 1248 / 1248
- Package types ready: 12
- Quality gates ready: 12
- Commercial models ready: 7
- Rights metadata fields: 14
- LangChain ready: True

## Package Types

### Instruction Tuning

Improve task following, customer support, and business workflow agents.

- Formats: jsonl, parquet
- Must include: instruction, input, output, metadata

### RAG Knowledge Base

Power retrieval systems with chunked, cited, metadata-rich documents.

- Formats: jsonl, markdown, parquet
- Must include: document_id, chunk, source, license, embedding_ready_metadata

### Eval Benchmark

Test models, agents, tools, safety, and domain performance.

- Formats: jsonl, csv
- Must include: prompt, expected_behavior, rubric, scoring_notes

### Agent Simulation

Train and test agents on multi-step business workflows.

- Formats: jsonl, yaml
- Must include: scenario, tools, steps, success_criteria, failure_modes

### Tool Calling

Train structured API, webhook, and workflow tool selection.

- Formats: jsonl
- Must include: user_request, tool_schema, tool_call, expected_result

### Domain Glossary

Teach models industry terminology, abbreviations, and structured definitions.

- Formats: csv, jsonl
- Must include: term, definition, domain, source, license

### Conversation Safety

Evaluate refusals, approvals, escalation, and safe handoff behavior.

- Formats: jsonl
- Must include: conversation, risk_label, ideal_response, approval_gate

### Synthetic Business Cases

Train models on sales, operations, finance, logistics, marketing, and startup scenarios.

- Formats: jsonl, parquet
- Must include: case, constraints, decision, rationale_summary, metadata

### Vision Labeling

Support image classification, OCR, layout, asset, and inspection datasets.

- Formats: jsonl, coco, csv
- Must include: asset_ref, label, annotation, rights, consent

### Audio and Voice Safe

Support consent-safe speech, pronunciation, narration, and transcription datasets.

- Formats: jsonl, wav_manifest
- Must include: audio_ref, transcript, speaker_consent, usage_rights

### Code Agent Tasks

Train and evaluate code agents on bugs, tests, refactors, and repo tasks.

- Formats: jsonl, patch
- Must include: repo_context, task, expected_patch, tests, license

### Contract Opportunity Data

Train business agents to find, classify, and prepare opportunity packets.

- Formats: jsonl, csv
- Must include: opportunity, requirements, deadline, fit_score, approval_needed

## Rights Rule

Only rights-cleared, source-backed, consent-safe packages may be sold or licensed.
