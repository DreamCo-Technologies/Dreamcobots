# DreamCo model provider data governance

The OpenAI-compatible provider adapter now applies a data-classification ceiling before any network request.

- OpenAI adapter maximum: internal.
- OpenRouter adapter maximum: public until per-model and account-specific terms are reviewed.
- Confidential and restricted data are blocked by these hosted adapters.
- Provider output-training permission defaults to UNKNOWN. Inference results are not automatically added to training or distillation datasets.
- A request returns a correlation ID, provider/model identifiers, classification, token usage, latency, and an explicit training-use authorization boolean.
- Prompt and completion contents are not persisted by this adapter. Callers remain responsible for their own approved handling.
- Paid requests still require a per-request approval reference and credentials remain in environment secrets.
- Endpoints are fixed in code; caller-supplied base URLs are not accepted.

This contract does not verify provider terms, configure credentials, or prove live connectivity. A separate owner-reviewed provider terms record and live smoke test are required before a provider can be considered connected. Native Anthropic, Gemini, Bedrock, Hugging Face, and local runtime adapters remain separate implementations.
