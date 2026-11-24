# DreamCo Model Studio & Marketplace

Status: product architecture and implementation specification; no production model-purchase, training, or checkout flow is claimed live by this document.
Owner: DreamCo Technologies
Related foundations: `foundry/customer_model_builder.py`, `foundry/lora_plan.py`, `buddy_os/actions/model_marketplace_contract.yaml`, `config/buddy_capability_package_marketplace.json`, `docs/BUDDY_USER_DATA_OWNERSHIP_AND_SUBSCRIPTION_CONTROL.md`, and the proprietary division model program.

## Product vision

Give individuals, developers, educators, and organizations one place to:
1. Build a custom specialist model for a chosen subject/category.
2. Buy or subscribe to a pretrained model.
3. Fine-tune a model they are licensed to customize with their own approved data.
4. Evaluate, deploy, version, export (when permitted), and manage their models.
5. Publish and sell eligible models in a DreamCo marketplace.

The experience is named **DreamCo Model Studio** (creation, training, evaluation, deployment) and **DreamCo Model Marketplace** (discovery, purchase, licensing, reviews, and distribution).

## Customer journeys

### A. Build a model from scratch as a customer experience

1. Select a category and specialty (e.g. bookkeeping, Python tutoring, agriculture, contract review, biology education, customer support, or product design).
2. Describe intended users, tasks, languages, input/output modalities, quality target, privacy requirements, and prohibited uses.
3. Choose a starting path: small open-weight base, DreamCo first-party base, adapter on a compatible base, retrieval-augmented model, or hosted model route. Clearly label whether the customer receives code, adapter, full weights, hosted access, or only a configuration.
4. Upload or connect data with explicit authority, rights, purpose, and retention settings. Provide dataset preview, schema mapping, deduplication, PII/sensitive-data screening, and train/validation/test split.
5. Choose guided presets or advanced controls for size, quantization, LoRA/QLoRA, epochs, learning rate, context, modalities, compute region, and spend cap.
6. Review a cost estimate, data-use terms, base-model license, expected deliverables, and a separate explicit training/purchase approval.
7. Run in an isolated job/tenant sandbox with status, logs, checkpoints, metrics, cancellation, and budget limits.
8. Evaluate against held-out customer tasks, general regression, privacy leakage, safety, and license checks. Show honest comparisons against the base model.
9. Promote a passing version to a private endpoint or exportable artifact only if the full rights chain permits it.
10. Monitor, rollback, retrain, and delete/export customer assets through account controls.

"Build from scratch" is a user-facing workflow name, not a promise of random-initialization foundation-model training. Default to adapting a suitable base; true pretraining requires separate compute and cost disclosure.

### B. Buy a pretrained model

- Browse by category, task, modality, size, language, license, deployment option, benchmark evidence, hardware needs, and price.
- Inspect model card, creator, version, base model, dataset provenance summary, evaluation report, known limitations, safety profile, license, update history, and support policy before purchase.
- Choose hosted subscription, private dedicated endpoint, one-time license, or downloadable weights where the rights and delivery format allow it.
- Purchase only after showing total price, recurring interval, taxes/fees when known, renewal terms, cancellation policy, data retention, and exact license grant.
- Deliver the artifact or provision the service and preserve an immutable receipt/license/version record.

### C. Train a purchased model in the customer's category

- The marketplace listing must explicitly state whether fine-tuning, adapter creation, commercial use, redistribution, and weight export are permitted.
- Customer fine-tunes only the purchased model version or adapter-compatible base covered by its license.
- Keep the vendor's upstream rights and DreamCo marketplace terms separate from the customer's original data and resulting contributions.
- Customer can keep the tuned model private, deploy it, or publish it only if every upstream and dataset license permits that action.
- Never imply a buyer owns upstream weights just because they paid for a license or customized an adapter.

### D. Creator marketplace

Approved creators can submit models with:
- verified identity/organization and payout onboarding;
- ownership and authority declaration;
- model card, pinned version, hashes, base model and license chain;
- dataset provenance and rights manifest;
- benchmark, safety, security, and privacy results;
- price, allowed uses, delivery format, update/support policy;
- vulnerability and takedown contact.

DreamCo reviews listings before publication, monitors abuse and license complaints, handles version retirement and refunds according to disclosed terms, and supports revocation of future hosted access when required. Downloads already lawfully delivered may not be technically revocable; explain this before purchase.

## Product surfaces

1. **Studio Home** — projects, jobs, budgets, recent model versions, and guided next steps.
2. **Category Explorer** — taxonomy search, example tasks, recommended bases, data templates, and category-specific benchmarks.
3. **Model Builder** — guided/advanced configuration and training plan.
4. **Data Workspace** — sources, permissions, provenance, schema, deduplication, privacy scan, splits, retention, and deletion.
5. **Training Runs** — queue, compute, live status, logs, checkpoints, cost, cancel/retry, and reproducibility.
6. **Evaluation Lab** — benchmark suites, side-by-side comparisons, safety gates, regressions, and promotion evidence.
7. **Model Registry** — immutable versions, artifacts, adapters, cards, licenses, endpoints, and rollback.
8. **Marketplace** — browse, compare, purchase, subscribe, manage entitlements, ratings, creator pages, and receipts.
9. **My Models** — private models, shared/team models, purchases, subscriptions, endpoints, exports, usage, and deletion.
10. **Creator Studio** — submit/update listings, analytics, licensing, payouts, support, and takedown workflow.
11. **Admin & Trust Console** — listing review, license compatibility, incident handling, abuse reports, audits, billing disputes, and model retirement.

## Model categories and taxonomy

Use the live, versioned DreamCo taxonomy and reconcile it with Hugging Face model/dataset tags plus other trusted category standards. The taxonomy is a discoverability map, not proof of permission to train. A model may serve multiple categories; one category may have multiple models and benchmark suites. Avoid one-model-per-tag duplication.

Initial category families include:
- business, accounting, economics, finance, sales, marketing, operations, and customer service;
- software, coding, IT, cloud, cybersecurity (defensive), data engineering, and analytics;
- math, statistics, physics, chemistry, biology, earth and environmental science;
- education, tutoring, research, language, writing, and translation;
- law and compliance information (not a substitute for licensed professional advice);
- healthcare information (strict safety, privacy, and professional oversight);
- agriculture, construction, manufacturing, logistics, energy, and engineering;
- art, design, image, video, audio, music, and speech;
- robotics, geospatial, time series, tabular data, multimodal, and accessibility.

## Architecture

### Control plane
- authenticated user, organization, and role service;
- tenant-scoped project/model/dataset/endpoint records;
- category and model catalog;
- entitlement, purchase, subscription, and creator payout records;
- consent, provenance, rights, and immutable audit records;
- training scheduler, queue, budget guard, and policy engine;
- model registry and release/promotion gate.

### Training plane
- isolated per-tenant jobs and storage namespaces;
- pinned base model, tokenizer, code, container, dataset and dependency revisions;
- adapters/checkpoints and reproducible recipes;
- CPU/GPU provider abstraction with quota, region, concurrency, and spend caps;
- cancellation, retries, idempotency, checkpoint resume, and failure evidence;
- no access to another tenant's data or artifacts.

### Serving plane
- authenticated endpoints with tenant and model-version scoping;
- rate, concurrency, token, and spend limits;
- private/dedicated or shared hosting options with isolation clearly disclosed;
- usage metering, audit logs, health, latency, and cost telemetry;
- rollback, deprecation, endpoint deletion, and key rotation.

### Marketplace plane
- catalog and search index;
- listing/version/asset and license manifests;
- checkout and billing provider integration;
- entitlement issuance and artifact delivery;
- refunds, disputes, creator payouts, ratings, reviews, abuse and takedown workflow.

Reuse existing model catalog and customer model builder where sound; do not create a second disconnected model catalog, billing system, or consent policy. Before implementing, map these requirements to existing Drizzle tables, routes, Stripe integration, data-rights policy, and marketplace page. Add migrations and route tests rather than duplicating tables or inventing a parallel billing ledger.

## Minimum data contracts

### Model project
`project_id`, `tenant_id`, `owner_user_id`, `category_ids[]`, `purpose`, `visibility`, `desired_deliverable`, `budget_cap`, `compute_region`, `status`, timestamps.

### Model release
`model_id`, `version`, `creator_tenant_id`, `base_model_id`, `base_revision`, `tokenizer_revision`, `artifact_hashes[]`, `training_recipe_ref`, `dataset_manifest_ref`, `model_card_ref`, `license_chain[]`, `benchmark_report_ref`, `safety_report_ref`, `release_state`.

### Dataset source
`dataset_id`, `tenant_id`, `source_ref`, `owner_authority`, `purpose`, `license_id`, `allowed_operations[]`, `retention_until`, `pii_scan_state`, `split_manifest`, `content_hash`, `consent_receipt_ref`.

### Marketplace listing
`listing_id`, `model_id`, `version`, `seller_id`, `price_type`, `price`, `currency`, `billing_interval`, `license_id`, `fine_tuning_allowed`, `commercial_use_allowed`, `redistribution_allowed`, `download_allowed`, `hosting_options[]`, `benchmark_summary`, `review_state`, `published_at`.

### Training job
`job_id`, `tenant_id`, `project_id`, `model_version`, `status`, `queue_position`, `compute_profile`, `budget_cap`, `estimated_cost`, `actual_cost`, `progress`, `checkpoint_refs[]`, `logs_ref`, `cancel_requested_at`, timestamps.

## Licensing, data rights, and customer ownership

- Separate the license of the base model, tokenizer, code, training datasets, DreamCo software, adapters, resulting checkpoints, and final distribution bundle.
- Display exact license/version and relevant restrictions before checkout or training.
- Do not sell a model unless the seller has documented authority to license the exact deliverable.
- Customer datasets remain customer-controlled. Training on them is off by default for any secondary purpose; no cross-tenant training, benchmarking, or product improvement without separate explicit opt-in and legal authority.
- Customer owns or controls original inputs subject to their source rights. Contractually grant the customer rights to their original contributions and tuned outputs to the extent legally possible, while preserving upstream obligations.
- Offer distinct license choices: private hosted use; commercial hosted use; export/download license; team/organization license; creator redistribution license. Exact terms require qualified counsel.
- Do not call a derivative model fully proprietary if upstream terms impose downstream conditions.
- Maintain takedown, correction, deletion, and rights-dispute workflows.

## Security, safety, and trust

- Enforce tenant isolation in database queries, object storage, caches, vector stores, logs, queues, and inference routing.
- Use least-privilege service identities, signed artifact URLs, encryption at rest/in transit, secrets management, and audit logs.
- Scan uploads for malware, secrets, PII, and prohibited content; quarantine suspicious datasets.
- Run model behavior evaluations for privacy leakage, memorization, prompt injection, harmful outputs, bias, and domain-specific risks.
- Restrict regulated or high-impact categories and require human review/qualified oversight where appropriate.
- Treat uploaded datasets, model files, README instructions, and third-party model cards as untrusted data, not executable instructions.
- Require explicit approval for purchases, recurring subscriptions, compute spend, public publishing, and data-training consent.

## Pricing and revenue design

Support free trial/sandbox quotas, pay-as-you-go compute, fixed-price model purchases, monthly hosted subscriptions, dedicated endpoint subscriptions, team seats, enterprise agreements, and creator revenue share. Every paid action must show total cost or a bounded estimate, recurring interval, usage caps, renewal/cancellation terms, and overage policy before approval. Never promise a fixed training price until provider rates and job size are known.

## Training and model lifecycle

`draft → rights_review → data_ready → queued → training → evaluation → safety_review → license_review → approved → private_deployed → marketplace_review → published → deprecated/withdrawn`.

Failed or rights-uncertain jobs remain quarantined. Promotion requires reproducible artifact hashes, held-out quality benchmarks, safety/privacy tests, license-chain approval, cost reconciliation, and human approval for marketplace publication. Customers can cancel jobs and delete projects subject to clearly disclosed legal/financial retention obligations.

## Implementation phases

1. **Inventory** — map current customer model builder, LoRA plan, model marketplace contract, marketplace UI, schema, storage, Stripe, auth, and privacy/consent controls. Produce reuse/gap matrix.
2. **MVP Studio** — authenticated project creation, category selection, dataset manifest, base-model/license selection, training plan preview, cost cap, sandbox job state, evaluation report. No public marketplace until release evidence exists.
3. **Private fine-tuning** — isolated worker, small-model LoRA/QLoRA, checkpoint registry, reproducible eval and rollback.
4. **Pretrained catalog** — verified first-party and properly licensed third-party listings with truthful deliverable types and fine-tune permissions.
5. **Checkout and entitlements** — explicit price/renewal confirmation, Stripe integration, receipts, entitlement enforcement, cancellation and refund workflow.
6. **Creator marketplace** — seller verification, review queue, rights and safety gates, payouts, dispute/takedown operations.
7. **Scale** — more categories/modalities, dedicated endpoints, teams, enterprise controls, autoscaling and marketplace analytics.

## Definition of done

- User can create a private project in a selected category.
- User can see exact base model, license, deliverable type, data use, and estimated compute cost before approval.
- A real isolated job can be queued, monitored, cancelled, resumed, and audited.
- A trained model version has reproducible artifacts and benchmark evidence.
- User can fine-tune a purchased model only when its license explicitly allows it.
- No cross-tenant data or artifact access is possible; tested with adversarial tenant tests.
- Checkout and recurring billing require explicit approval and correctly enforce entitlements.
- A marketplace listing cannot publish without rights, safety, provenance, and benchmark gates.
- User can export/delete their data and manage training consent.
- UI shows planned, queued, running, failed, evaluated, approved, and deployed states truthfully.

## Honest delivery status

This specification adds product requirements and a staged build plan. It does not itself implement the Studio UI, training workers, checkout, marketplace sales, model downloads, or tenant-isolated serving. Those require code, migrations, provider integrations, security tests, and end-to-end verification.
