#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-}"
GITHUB_REPOSITORY="${GITHUB_REPOSITORY:-DreamCo-Technologies/Dreamcobots}"
POOL_ID="${POOL_ID:-dreamco-github-pool}"
PROVIDER_ID="${PROVIDER_ID:-dreamco-github-provider}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-dreamco-github-deployer}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Set PROJECT_ID first, for example: PROJECT_ID=my-dreamco-project ./deploy/google-cloud/workload-identity-github.sh"
  exit 1
fi

PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
DEPLOYER_EMAIL="$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com"

gcloud iam workload-identity-pools create "$POOL_ID" \
  --project="$PROJECT_ID" \
  --location=global \
  --display-name="DreamCo GitHub" \
  --quiet || true

gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_ID" \
  --project="$PROJECT_ID" \
  --location=global \
  --workload-identity-pool="$POOL_ID" \
  --display-name="DreamCo GitHub provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
  --attribute-condition="assertion.repository == '$GITHUB_REPOSITORY'" \
  --quiet || true

gcloud iam service-accounts add-iam-policy-binding "$DEPLOYER_EMAIL" \
  --project="$PROJECT_ID" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_ID/attribute.repository/$GITHUB_REPOSITORY" \
  --quiet

echo "Add these GitHub repository secrets:"
echo "GCP_PROJECT_ID=$PROJECT_ID"
echo "GCP_SERVICE_ACCOUNT=$DEPLOYER_EMAIL"
echo "GCP_WORKLOAD_IDENTITY_PROVIDER=projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_ID/providers/$PROVIDER_ID"
echo "GCP_REGION=us-central1"
