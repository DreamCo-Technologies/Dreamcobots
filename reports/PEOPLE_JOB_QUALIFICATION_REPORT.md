# People Search and Job Qualification Report

Give Buddy a governed people-search and job-qualification lookup system for recruiting, client discovery, contractor matching, partner research, and workforce planning.

## Summary

- Bot people lookup blueprints: 1248 / 1248
- Qualification lanes ready: 6
- Approval gates declared: 12
- Blocked uses declared: 8
- Privacy metadata fields: 9
- Human review required: True

## Qualification Lanes

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
- credit_or_insurance_decisions
- health_or_disability_inference
- minor_profiling
- doxxing_or_harassment
- mass_unsolicited_outreach