# Buddy Frontier Benchmark and Continuous Study Program

## Scope
Coding, research, and multi-step tool execution are separate evaluation domains. The six authored starter tasks test basic coding/research/workflow *reasoning*, **not** real tool invocation, source retrieval, patch application, or frontier mastery. Expand with sandboxed execution, real research citations, and multi-tool stateful tasks before making those claims.

## Model family adapters
- GPT: official OpenAI API; native provider adapter is pending, or a verified compatible gateway.
- Claude: official Anthropic API; native Messages adapter pending, or a verified compatible gateway.
- Gemini: official Google Gemini API; native adapter pending, or a verified compatible gateway.
- DeepSeek: configured compatible chat completions endpoint, with approved credentials.
- Qwen: configured compatible gateway or approved local inference server.
- Other open-weight: local OpenAI-compatible inference service with explicit loopback opt-in.

No API keys are committed. Never assume any model name, endpoint, pricing, or compatibility is valid without verification. Configured adapters must use owner-approved accounts and budgets. The generic adapter sends prompts to external providers, so only non-sensitive, authorized tasks are permitted.

## Run a bounded live comparison
Set BUDDY_BENCHMARK_PROVIDERS_JSON to an array of adapter definitions with keys name, model, base_url, api_key_env (and optionally allow_local_http). Put API keys in corresponding environment variables. Set BUDDY_LIVE_BENCHMARK_APPROVED=yes, then run:

    python -m buddy.certification.run_live_benchmarks --approved --max-tasks 6

The runner never runs on scheduled CI. Review data rights, spend and provider terms before execution. This starter runner records exact-match results, task hashes and receipts, but does not certify independent frontier performance. No real provider calls have been verified in this PR.

## Capability-specific scorecard
For each domain record task completion, accuracy, reasoning quality, tool success, reliability, latency, safety and cost. Define independent scorer and rubric for each metric, repeat trials, pin versions and environment, preserve holdout isolation, and record uncertainty. Do not infer cost or safety from exact-match score. Tool-execution tasks must use a sandboxed tool interface and independently validate state changes. Research tasks must require source provenance, retrieval and factual checking.

## Continuous study loop
Use daily CI for static discovery, gap reports, regression tests and training proposals; use hourly **bounded** study queue refreshes only if cost and GitHub Actions quotas permit. Study queue: failure -> skill taxonomy -> official documentation/licensed datasets -> practice exercises -> heldout benchmark -> gap report -> supervised repair/training -> independent retest. Favor official Python/MDN/GitHub docs for coding, authorized source methodology and citation checks for research, and tool contract/sandbox guides for tool use. Store exact source URL, license, version, retrieval timestamp and evidence. Respect robots, license and terms.

Do not train on holdout solutions. Do not run endless model calls or launch GPU jobs without budgets and explicit approvals. A schedule is not guaranteed 24/7 uptime. Human approval remains mandatory for spending, training on new data, credential access, code merges, deployments and external mutations.
