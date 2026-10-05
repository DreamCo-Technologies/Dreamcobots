# Consent, provenance, and license gates

Every ingested asset gets a provenance record (`config/buddy_multimodal_provenance_record.schema.json`), using the ownership classes already defined in `config/buddy-training-data-provenance-policy.json`. A lesson inherits the most restrictive class of all its inputs. A package inherits the most restrictive class of all its lessons.

## Decision per ownership class
| ownership_class | Train/study | Sellable package |
|---|---|---|
| dreamco_owned, dreamco_commissioned_with_assignment, synthetic_generated_by_dreamco | yes | yes |
| licensed_for_use | yes | only if commercial_redistribution_allowed is true |
| open_license_with_conditions | yes | only if commercial_redistribution_allowed is true; attribution and share-alike carried |
| public_domain_or_publicly_reusable | yes | yes, with attribution kept |
| user_contributed_with_permission | only with a consent record in scope "train" | only with consent scope "sell" plus ownership attestation |
| third_party_reference_only | summaries, citations, original benchmark variants only | never (original derived tasks are re-classed dreamco_owned only after human review) |
| unknown_do_not_publish | quarantine | never |

## Per source
- **Web**: robots and terms checked and recorded; URL, retrieval date, content hash. Default class third_party_reference_only unless license stated.
- **Books**: default third_party_reference_only. Page/section pointers required. Public domain needs a recorded basis (e.g. edition + date).
- **Movies and video**: default third_party_reference_only. Timestamps required. No frames, clips, or transcripts in sellable output without license.
- **User uploads**: explicit consent record (bound to file hash, like `buddy/media/consent.py`), scope list ("train", "sell"), ownership attestation text, revocable; revoke removes the asset from future package builds.
- Missing any required field means the asset is treated as unknown_do_not_publish.
