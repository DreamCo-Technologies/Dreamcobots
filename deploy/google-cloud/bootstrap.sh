#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-}"
REGION="${REGION:-us-central1}"
REPOSITORY="${REPOSITORY:-dreamco}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-dreamco-github-deployer}"
SERVICE_NAME="${SERVICE_NAME:-dreamco-buddy}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Set PROJECT_ID first, for example: PROJECT_ID=my-dreamco-project ./deploy/google-cloud/bootstrap.sh"
  exit 1
fi

gcloud config set project "$PROJECT_ID"
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"

gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  iamcredentials.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  cloudscheduler.googleapis.com \
  pubsub.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com

gcloud artifacts repositories create "$REPOSITORY" \
  --repository-format=docker \
  --location="$REGION" \
  --description="DreamCo container images" \
  --quiet || true

gcloud iam service-accounts create "$SERVICE_ACCOUNT" \
  --display-name="DreamCo GitHub deployer" \
  --quiet || true

DEPLOYER_EMAIL="$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com"
BUILD_RUNTIME_EMAIL="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

for ROLE in \
  roles/run.admin \
  roles/artifactregistry.writer \
  roles/iam.serviceAccountUser \
  roles/secretmanager.secretAccessor \
  roles/logging.logWriter \
  roles/monitoring.metricWriter \
  roles/pubsub.editor \
  roles/cloudscheduler.admin \
  roles/datastore.user \
  roles/storage.admin; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$DEPLOYER_EMAIL" \
    --role="$ROLE" \
    --condition=None \
    --quiet
done

for ROLE in \
  roles/storage.objectViewer \
  roles/artifactregistry.writer \
  roles/logging.logWriter \
  roles/run.admin \
  roles/iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$BUILD_RUNTIME_EMAIL" \
    --role="$ROLE" \
    --condition=None \
    --quiet
done

for TOPIC in dreamco-bot-jobs dreamco-payment-events dreamco-approval-events; do
  gcloud pubsub topics create "$TOPIC" --quiet || true
done

for SECRET in \
  STRIPE_SECRET_KEY \
  STRIPE_WEBHOOK_SECRET \
  STRIPE_PUBLISHABLE_KEY \
  PAYMENT_ALERT_EMAILS \
  PAYMENT_EMAIL_PROVIDER \
  PAYMENT_EMAIL_FROM \
  PAYMENT_GITHUB_TOKEN \
  OPENAI_API_KEY \
  ANTHROPIC_API_KEY \
  GOOGLE_API_KEY \
  DATABASE_URL \
  SESSION_SECRET \
  BUDDY_ADMIN_EMAIL \
  WEBHOOK_SIGNING_SECRET; do
  printf "" | gcloud secrets create "$SECRET" --data-file=- --replication-policy=automatic --quiet || true
done

gcloud scheduler jobs create pubsub dreamco-hourly-readiness \
  --schedule="0 * * * *" \
  --topic=dreamco-bot-jobs \
  --message-body='{"task":"hourly_readiness","mode":"sandbox_first"}' \
  --location="$REGION" \
  --quiet || true

echo "Google Cloud project prepared."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Artifact Registry: $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY"
echo "Cloud Run service target: $SERVICE_NAME"
echo "Service account: $DEPLOYER_EMAIL"
echo "Next: configure GitHub Workload Identity Federation and set repository secrets."
