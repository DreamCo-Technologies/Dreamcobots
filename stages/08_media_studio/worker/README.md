# Media Foundry planning worker

This is a provider-neutral CPU control-plane service. It accepts a production request, validates it with the shared Media Director, and stores a plan under the configured spool directory.

## Endpoints

- `GET /healthz`: liveness only; does not disclose configuration.
- `GET /readyz`: readiness requires a configured bearer token and writable spool directory.
- `POST /v1/jobs/plan`: validates and persists a plan. Requires `Authorization: Bearer <token>` and a JSON body matching `../shot-list.example.json`.

A successful plan response is marked `planned_not_rendered`. This worker does not render media, load weights, download models, run shell commands, or provision GPU resources. Render adapters belong in separately isolated execution workers and must use the asset and checkpoint gates.

## Run locally

```bash
export DREAMCO_WORKER_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export DREAMCO_MEDIA_SPOOL="./.media-spool"
python stages/08_media_studio/worker/server.py
```

The default bind address is loopback (`127.0.0.1`). Set `DREAMCO_WORKER_HOST=0.0.0.0` only behind a trusted network boundary and TLS-terminating reverse proxy. Keep the bearer token in a secret manager; never commit it.

## Container

The adjacent Dockerfile runs as a non-root user, has no model weights, and exposes port 8080. Supply `DREAMCO_WORKER_TOKEN` at runtime. Mount a persistent writable volume at `/var/lib/dreamco-media`.


## Isolated GPU execution contract

`execution_contract.py` defines the boundary for future GPU/provider workers:

- worker capability declarations and bounded CPU, RAM, GPU, and timeout requests
- plan-file containment and SHA-256 verification before execution
- an explicit job lifecycle with terminal states that cannot be reopened
- output manifests restricted to allowlisted media types, regular files, and verified byte size/hash
- symlink and path traversal rejection

This is an interface and validator, not a GPU executor. A provider implementation must run in a separate isolated process/container, invoke the canonical Media Director rights/consent and model-license gates before generation, and return artifact metadata for verification. It must not accept a user-supplied shell command or arbitrary host path. No GPU is provisioned by this repository change.
