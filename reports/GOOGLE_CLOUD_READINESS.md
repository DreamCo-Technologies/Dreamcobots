# Google Cloud Readiness

- gcloud installed: True
- Deployment targets: 9
- Required APIs: 11
- GitHub secrets required: 4
- Workload Identity recommended: True
- Production deploy approval required: True

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

## Guardrails

- Never commit Google service account keys or Stripe secrets.
- Prefer Workload Identity Federation over downloaded JSON keys.
- Keep production deploys approval-gated until tests, rollback, billing alerts, and secret checks pass.
- Use Secret Manager for live credentials and GitHub Secrets only for deployment identity values.
- Separate sandbox, staging, and production projects before taking client payments.
- Enable budgets and alerts before running always-on workloads.
