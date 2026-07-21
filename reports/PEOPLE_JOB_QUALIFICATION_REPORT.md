# People Search and Job Qualification Report

Give Buddy a governed genealogy, people-search, background-check intake, phone-number history, and job-qualification lookup system for recruiting, client discovery, contractor matching, partner research, ancestry reporting, and workforce planning.

## Summary

- Bot people lookup blueprints: 1248 / 1248
- Qualification lanes ready: 10
- Approval gates declared: 16
- Blocked uses declared: 13
- Privacy metadata fields: 9
- Genealogy reports ready: True
- Background-check intake ready: True
- Phone-number recovery ready: True
- Human review required: True

## Qualification Lanes

### Genealogy Report

Build family-history packets from self-provided documents and public archival sources with source citations, confidence notes, and unknowns clearly marked.

- Outputs: family_tree_outline, ancestor_timeline, source_citations, confidence_notes, research_gaps

### Consent-Based People Search

Prepare a public-source or user-authorized lookup packet for reconnecting, vendor due diligence, partnership research, or contact hygiene without private-data scraping.

- Outputs: identity_match_candidates, public_source_links, confidence_score, permission_basis, human_review_packet

### Background Check Intake

Collect the checklist, consent status, permissible purpose, and provider handoff data needed before any lawful background check can run.

- Outputs: consent_checklist, permissible_purpose_notes, provider_handoff_packet, blocked_until_compliant_provider

### Phone Number Recovery

Help a user document old numbers, account ownership, carrier contacts, and lawful reuse steps without accessing private subscriber data or tracking people.

- Outputs: old_number_timeline, carrier_contact_plan, account_ownership_checklist, reuse_feasibility_notes, privacy_risk_notes

### Candidate Resume Match

Compare self-provided resumes or application materials against a job description using role requirements and evidence notes.

- Outputs: skills_match, experience_evidence, gap_notes, interview_questions, human_review_packet

### Contractor and Vendor Match

Research public contractor/vendor profiles, portfolios, capabilities, reviews, and fit for a project.

- Outputs: vendor_shortlist, capability_match, risk_notes, approval_packet

### Sales People Research

Prepare compliant lead or stakeholder research from public and approved sources for owner-reviewed outreach.

- Outputs: stakeholder_map, public_profile_summary, relevance_reason, outreach_draft

### Employee Role Fit

Prepare role-fit notes, training needs, onboarding plans, and interview prompts without making automated hiring decisions.

- Outputs: role_fit_notes, training_plan, interview_prompts, human_decision_notes

### License and Certification Checklist

Prepare a checklist for licenses, certifications, permits, and evidence that a human must verify against allowed sources.

- Outputs: license_checklist, source_links, verification_status, review_notes

### Relocation Workforce Match

Research local talent pools, workforce availability, training programs, and hiring channels for business relocation or expansion.

- Outputs: talent_market_notes, hiring_channel_map, training_programs, location_fit_score

## Blocked Uses

- automated_hiring_or_rejection
- protected_class_scoring
- background_screening_without_compliant_provider
- people_search_without_permission_basis
- phone_number_tracking_or_live_location_lookup
- carrier_record_access_without_account_owner_authorization
- genealogy_outreach_without_review
- using_public_records_to_harass_or_pressure_people
- credit_or_insurance_decisions
- health_or_disability_inference
- minor_profiling
- doxxing_or_harassment
- mass_unsolicited_outreach