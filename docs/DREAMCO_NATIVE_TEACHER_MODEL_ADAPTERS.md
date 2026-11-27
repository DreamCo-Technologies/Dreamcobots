# Native teacher-model adapters

This phase adds provider-native HTTPS request adapters for Anthropic Messages and Google Gemini GenerateContent. The existing OpenAI-compatible adapter remains separate because native APIs have different authentication, message-role, request, and response contracts.

## Routing contract
- The caller must pass model IDs from an owner-reviewed allowlist. Empty or mismatched allowlists block calls.
- Every billable request requires a non-empty approval reference.
- Credentials are read only from `ANTHROPIC_API_KEY` or `GEMINI_API_KEY`; arbitrary endpoints and URL-supplied API keys are not accepted.
- Requests have bounded message counts, content sizes, output-token limits, and timeouts.
- Evidence returns provider/model, approval reference, latency, and available token usage; it does not include credentials or raw provider payloads.
- No automatic paid fallback, model upgrade, distillation, or weight promotion is performed.

## Operational activation
Set provider credentials in the trusted runtime secret store, not repository files. Configure owner-reviewed model IDs in the model-routing control plane and pass that allowlist to the adapter. Run a separately approved live smoke test before recording provider connectivity as verified. CI uses mocked transports and does not spend provider credits.

## Limitations
This module does not yet implement Vertex AI service-account identity, AWS Bedrock IAM, Hugging Face Inference Endpoints, Ollama/local runtimes, rate-limit-aware queues, provider-specific safety filters, or production routing policy. Those require dedicated adapters and operational credentials/runtime configuration.
