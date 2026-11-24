# DreamCo First-Party Training Data License — Owner Template

> **Template only; not legal advice.** Complete and review this instrument before adding a dataset to DreamCo's authorized-training manifest. It applies only to material the licensor owns or is legally authorized to license. It does not override third-party terms, privacy rights, publicity rights, confidentiality duties, or applicable law.

## 1. Parties and covered material

- **Licensor / rights owner:** [Full legal name or entity]
- **Authorized project / licensee:** [DreamCo project owner or legally formed entity]
- **Effective date:** [YYYY-MM-DD]
- **Dataset ID and version:** [Stable ID]
- **Description and source:** [What the material is, who created it, and where it came from]
- **Content fingerprint:** [SHA-256 manifest or signed inventory reference]

## 2. Ownership representation

The Licensor represents that it owns the covered material or has written authority sufficient to grant every permission selected below. The Licensor will identify excluded material, third-party components, personal information, confidential information, and any other restrictions before ingestion.

## 3. Permissions — select and document each separately

For the covered material, the Licensor grants the Authorized Project the following permissions to the extent legally controlled by the Licensor:

- [ ] Internal storage, backup, and access by approved project personnel.
- [ ] Reformatting, cleaning, deduplication, filtering, annotation, and tokenization.
- [ ] Training and evaluating machine-learning models, including pretraining and fine-tuning.
- [ ] Creating and using derivative model architectures, adapters, checkpoints, and model weights.
- [ ] Commercial use of resulting models and model services.
- [ ] Redistribution or sublicensing of the original dataset (separate permission; not implied).
- [ ] Redistribution or sublicensing of derived datasets (separate permission; not implied).

The selected permissions, any limits, and the applicable division IDs must be reflected in the dataset manifest. An unchecked permission is not granted.

## 4. Resulting model assets

Subject to applicable law and third-party rights, the parties designate [model owner] as the owner/controller of model code, checkpoints, tokenizer assets, and model weights produced using the covered material. This clause does not transfer ownership of the source material, grant rights in excluded material, or guarantee that model outputs are non-infringing.

## 5. Attribution, exclusions, retention, and revocation

- **Required attribution:** [Text or “None”]
- **Excluded material:** [List or “None”]
- **Personal/confidential data review:** [Evidence reference]
- **Retention period and deletion procedure:** [Terms]
- **Revocation/termination terms:** [Terms and effect on already-created checkpoints]

## 6. Evidence and approval

- **Rights evidence reference:** [Signed agreement, deed, source record, or other evidence]
- **Licensor signature:** ____________________  **Date:** __________
- **Project owner approval:** ________________  **Date:** __________
- **Reviewed by:** __________________________  **Date:** __________

A manifest entry may be marked `APPROVED` only after the signed evidence is retained and every permission required for the intended training and model use is explicitly granted. Public availability, a repository URL, or an unverified license label is not sufficient evidence.
