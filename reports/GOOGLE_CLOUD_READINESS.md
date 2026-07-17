# Google Cloud Readiness

- gcloud installed: True
- gcloud authenticated: True
- gcloud project configured: True
- Deployment targets: 9
- Required APIs: 11
- GitHub secrets required: 4
- Deploy files ready: 8
- Cloud Run services mapped: 3
- Pub/Sub topics mapped: 3
- Secret Manager placeholders: 14
- Workload Identity recommended: True
- Production deploy approval required: True
- Free or low-cost AI routing: True
- Google Gemini secret ready: True
- Cloud Run min instances 0 recommended: True

## Deploy Files

- deploy/google-cloud/Dockerfile.control-tower: True
- cloudbuild.yaml: True
- .gcloudignore: True
- .github/workflows/google-cloud-run-deploy.yml: True
- deploy/google-cloud/service-map.json: True
- deploy/google-cloud/secret-manager.template.json: True
- deploy/google-cloud/bootstrap.sh: True
- deploy/google-cloud/workload-identity-github.sh: True

## Required APIs

- run.googleapis.com
- cloudbuild.googleapis.com
- artifactregistry.googleapis.com
- iamcredentials.googleapis.com
- secretmanager.googleapis.com
- logging.googleapis.com
- monitoring.googleapis.com
- cloudscheduler.googleapis.com
- pubsub.googleapis.com
- firestore.googleapis.com
- storage.googleapis.com

## GitHub Secrets

- GCP_PROJECT_ID
- GCP_WORKLOAD_IDENTITY_PROVIDER
- GCP_SERVICE_ACCOUNT
- GCP_REGION

## AI Cost Control

- Keep Cloud Run min instances at 0 unless real traffic requires warm instances.
- Set max instances low while cash is tight, then raise only after revenue or approval.
- Use Gemini free-tier or low-cost Flash-Lite style routes for sandbox drafts, summaries, and routing.
- Cache repeated report reads and model outputs before making more paid calls.
- Do not run paid always-on model loops without a budget cap and owner approval.
- Use local/static reports when they answer the question without an API call.

## Guardrails

- Never commit Google service account keys or Stripe secrets.
- Prefer Workload Identity Federation over downloaded JSON keys.
- Keep production deploys approval-gated until tests, rollback, billing alerts, and secret checks pass.
- Use Secret Manager for live credentials and GitHub Secrets only for deployment identity values.
- Separate sandbox, staging, and production projects before taking client payments.
- Enable budgets and alerts before running always-on workloads.
