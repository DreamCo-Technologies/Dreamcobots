# DreamCo Google Cloud Connection

This folder connects DreamCo to Google Cloud without committing secret values.

## Local Login

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

## Bootstrap Project

```bash
PROJECT_ID=YOUR_PROJECT_ID REGION=us-central1 ./deploy/google-cloud/bootstrap.sh
```

## Connect GitHub Without JSON Keys

```bash
PROJECT_ID=YOUR_PROJECT_ID ./deploy/google-cloud/workload-identity-github.sh
```

The script prints the exact GitHub repository secrets to add.

## GitHub Secrets

Add these repository secrets:

- `GCP_PROJECT_ID`
- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`
- `GCP_REGION`

Use Google Workload Identity Federation for GitHub. Do not upload a service
account JSON key to GitHub.

## Deploy Paths

- GitHub Actions: `.github/workflows/google-cloud-run-deploy.yml`
- Cloud Build: `cloudbuild.yaml`
- Cloud Run Dockerfile: `deploy/google-cloud/Dockerfile.control-tower`
- Service map: `deploy/google-cloud/service-map.json`
- Secret plan: `deploy/google-cloud/secret-manager.template.json`
