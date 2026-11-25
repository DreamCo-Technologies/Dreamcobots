# Buddy Model Purpose, Ownership & Deployment Profiles

**Status:** product and governance specification; implementation, legal review, and enforcement tests remain to be completed.

## Product decision

Every model-building customer must choose and be able to change the intended model profile. The default choice is not forced to be commercial. Buddy supports personal/private models, commercial/business models, and models intended for both personal and commercial use, subject to the actual model, dataset, provider, jurisdiction, deployment, and use-case restrictions.

A "personal" label is not a universal legal exemption. A "commercial" label is not a universal permission set. Rules depend on the activity, data, model and base-model license, provider terms, deployment, affected people, industry, and applicable law. The interface must explain this rather than inventing a blanket personal-versus-commercial law.

## User-facing model profiles

### 1. Personal / private model
For an individual's private learning, experimentation, hobbies, personal productivity, accessibility, and personal projects.

Expected controls:
- Private-by-default workspace and user-controlled storage.
- Local/offline deployment where hardware and model support it.
- No sharing, publication, resale, hosted access for others, or commercial use unless the relevant licenses and terms allow it.
- Clear warnings for sensitive personal data, other people's data, regulated activities, and unsafe uses.
- User-configurable retention, export and deletion controls.
- Optional private fine-tuning only with eligible data and documented rights.
- Personal use does not override safety policies, privacy law, copyright, cybersecurity law, or third-party rights.

### 2. Commercial / business model
For business operations, customer-facing services, employee workflows, paid products, client work, and other commercial activity.

Expected controls:
- Commercial-use license and provider-terms checks for the base model, datasets, adapters, code and tools.
- Business tenant isolation, role-based access, audit trails and credential vaulting.
- Data-processing, retention, privacy and security configuration appropriate to the business.
- Human review and escalation for high-impact or regulated decisions.
- Sector-specific checks where applicable (for example health, finance, employment, education, insurance, legal services, or critical infrastructure).
- Security testing, reliability objectives, incident response, backup and recovery.
- Model card, provenance, versioning, evaluation, rollback and change management.
- Contractual and operational requirements before customer-facing or production deployment.

### 3. Dual-use / personal plus commercial
For a model the user intends to use privately and later publish, sell, license, host for customers, or deploy in a business.

Expected controls:
- Track personal and commercial datasets, weights, adapters, tools and dependencies separately.
- Require a commercial-rights review before commercial promotion or distribution.
- Re-run privacy, security, safety, performance and domain evaluations for the intended deployment.
- Preserve lineage and permissions for every included component.
- Do not assume a personal-use model can be commercially reclassified without checking all licenses and obligations.

### 4. Research / educational / evaluation
For coursework, reproducible experiments, benchmarks and non-production research.

Expected controls:
- Record research purpose, sources, terms, data rights and benchmark restrictions.
- Keep benchmark test data held out and prevent leakage.
- Clearly label prototypes and experimental checkpoints.
- Block production claims or deployment until production gates are met.

## Decision flow

1. Ask what the model is for and who will use it.
2. Ask whether it will be private, shared, sold, hosted, or used to provide paid services.
3. Identify jurisdiction(s), industry, deployment environment, and whether decisions affect other people.
4. Inspect base-model and provider license/terms, dataset rights, tool dependencies and redistribution conditions.
5. Classify data: public, licensed, confidential, personal, sensitive, regulated, or third-party.
6. Generate a plain-language permissions and restrictions report.
7. Select eligible models, datasets, training methods and deployment routes.
8. Run appropriate safety, privacy, security and capability evaluations.
9. Require expert/legal review where risk or uncertainty warrants it.
10. Reassess when purpose, model, data, provider, deployment or law changes.

## What the user must see before choosing

Show:
- What the selected profile permits and does not permit.
- Whether the base model can be used personally, commercially, modified, redistributed, hosted, or sublicensed.
- Dataset and teacher-model restrictions.
- Whether data may be sent to an external API or used for provider/model improvement.
- Hosting, compute, storage and expected usage-cost considerations.
- Required safeguards, approvals, evaluations and human oversight.
- Which questions remain unresolved and why.

Never display a green "commercially approved" or "legally cleared" state when license terms, jurisdiction, data rights or use-case requirements are unknown. Use statuses such as **eligible based on reviewed terms**, **restricted**, **review required**, and **blocked**. Provide source links and the date/version of the review.

## Model registry fields

Each model record should include:
- purpose_profile: personal | commercial | dual_use | research
- intended_users and intended_use
- jurisdictions and industry/domain
- base_model, exact revision, license identifier and source
- provider terms and API data-use/retention conditions
- dataset lineage, license, consent and data classification
- adapter/checkpoint hashes and training method
- redistribution, hosted-use, modification and sublicensing permissions
- safety/security/privacy evaluation results
- deployment target and tenant model
- cost profile and hardware requirements
- restrictions, unresolved questions, reviewer and review date
- approval state and rollback reference

## Enforcement requirements

- Purpose profiles are policy inputs, not cosmetic labels.
- Enforce restrictions at model selection, dataset ingestion, training, artifact export, API routing, sharing, sale, hosting and deployment.
- Prevent personal/private workspaces from silently becoming shared or commercial.
- Prevent commercial projects from using components whose terms prohibit the intended use.
- Block or quarantine unknown-rights data and components until reviewed.
- Do not make legal determinations from the profile alone; provide jurisdiction-aware explanations and refer complex cases to qualified counsel.
- Allow the user to export their model and lineage where licenses and technical constraints permit.
- Keep customer data isolated; never use it to train shared models without separate informed authorization and valid rights.

## Acceptance tests

1. A user can create a private personal model without enabling commercial distribution.
2. A user can create a commercial model and see commercial-use eligibility checks for every component.
3. A dual-use model cannot be sold or hosted until the commercial review gate passes.
4. A noncommercial base-model license blocks commercial use even if the user selects "commercial."
5. An unclear dataset license is marked review-required and excluded from training/export.
6. A personal project cannot expose private data to another tenant or an external teacher without permission.
7. Changing purpose from personal to commercial triggers re-evaluation and preserves provenance.
8. The UI explains that personal use does not exempt illegal, harmful, privacy-invasive or third-party-rights-violating activity.
9. High-impact or regulated use cases trigger the relevant additional safeguards and human review.
10. All status labels are backed by recorded evidence, reviewer, version and timestamp.

## Bootcamp module

Add a practical module titled **Choosing the Right Model: Personal, Commercial, Dual-Use and Research**. It must teach licenses versus law versus provider terms; personal data and consent; commercial redistribution and hosting; open weights versus open source; dataset and teacher-model rights; sector-specific obligations; deployment risk; and how to read model cards and licenses. Include scenarios, a decision exercise, answer key, and automated policy tests.

**No legal certification, commercial clearance, external spend, customer-data transfer, model sale, or production deployment is authorized by this specification.**
