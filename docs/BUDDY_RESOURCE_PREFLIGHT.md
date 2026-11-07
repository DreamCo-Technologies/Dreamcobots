# Buddy resource preflight for models, chatbots, and GitHub projects

The common intake covers `chatbot`, `ai_model`, `agent`, `tool`, `mcp_server`, and `workflow` resources from any provider. Provider-specific authentication and runtime APIs remain behind an explicitly configured adapter; the intake itself stores the source, optional immutable revision, license/terms claims, intended actions, and unresolved checks. It does not connect, load model weights, grant permissions, or declare a resource trusted.

## Review an AI resource

```sh
python3 tools/buddy_resource_preflight.py ai open-model-v1 ai_model "Example Provider" https://provider.example/models/open-model-v1 --revision abc1234 --license Apache-2.0 --terms-url https://provider.example/terms --intended-action "answer study questions"
```

Use this for hosted or local models, API models, chatbots, agent frameworks, MCP servers, and workflow packages. The report shows checks for publisher identity, source revision, license and terms, permissions, privacy, dependencies, behavior, cost, and approval. Provider credentials should be connected only through a user-controlled secret store after review.

For a user-approved behavior check, a provider adapter can call `run_ai_adapter_smoke_tests`. The adapter contract requires a timeout, tools disabled, and a disposable isolated test context. It sends synthetic probes for a basic response, untrusted prompt injection, and a tool boundary. It stores only pass/fail, latency, and tool-call counts. These are smoke checks, not a complete benchmark or a safety certification. Never run arbitrary downloaded adapter code or use production credentials and user data in the suite.

## Review a GitHub project before cloning

```sh
python3 tools/buddy_resource_preflight.py github https://github.com/OWNER/REPOSITORY --select src/agent --output review.json
```

The reviewer resolves the chosen branch/tag to a full commit SHA, inspects the repository tree, and fetches a bounded set of small text files such as README/license files, dependency manifests, setup files, Docker configuration, and GitHub Actions workflows. It scans reviewed text for common unsafe install/execution patterns, lifecycle scripts, insecure CI permissions, possible embedded secrets, remote model code, and prompt injection indicators. It flags executable files, secrets-file paths, symlinks/submodules, and very large files. It never clones or executes the repository during preflight.

Select a whole folder or individual files. A folder selection expands to the files under that exact path, with a 100-file cap. Review the resulting commit, license, warnings, and selected file list before deciding whether to copy it.

## Copy selected open-source components

```sh
python3 tools/buddy_resource_preflight.py clone-selected review.json ./my-dreamco-module \
  --confirm-authorization --confirm-license-review \
  --customize workflow --customize privacy \
  --differentiator "Describe an original DreamCo behavior that serves my intended users."
```

The copy command rechecks the exact reviewed commit before transferring selected files. It requires an identified repository license, explicit user authorization, a separate license/notice review, two DreamCo customization areas, and an original differentiator. It automatically carries root license/notice files, verifies GitHub blob hashes, refuses credential-like content, limits the copy to 20 MB, never overwrites an existing target, and publishes the staged result only after checks pass. It adds `dreamco-source-provenance.json` and `DREAMCO_CUSTOMIZATION_PLAN.md`. The copied component is still the source project until users implement and test the customizations. No package install, build script, model loading, or code execution is performed.

An unknown or missing license blocks the copy flow. A license identifier is not legal advice and does not grant permission for every commercial, training, redistribution, or derivative use. Users must review the applicable license, notices, trademarks, data rights, provider terms, dependencies, and any other restrictions for their specific use. For a restrictive license, obtain the needed review before reuse.

## Trust boundary

These reports reveal selected classes of problems; they cannot prove that a model, chatbot, repository, dependency, or dataset is safe. Static pattern checks have false positives and false negatives. They do not replace malware scanning, dependency vulnerability review, privacy review, license analysis, task-specific tests, or isolated execution. A green result is not a trust certification or production authorization. Model and bot behavior must be tested through an approved adapter on synthetic or consented fixtures, then compared with task-specific benchmarks and regressions.
