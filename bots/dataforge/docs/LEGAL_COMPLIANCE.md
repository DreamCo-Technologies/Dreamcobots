# DataForge AI Legal & Compliance Guide

## Overview

DataForge AI systems are designed with privacy, consent, and data protection as core principles. All synthetic datasets are generated to be compliant with major data protection regulations.

## GDPR Compliance

The General Data Protection Regulation (GDPR) applies to all personal data of EU residents.

### Key Requirements Met
- **Consent**: All data collection requires explicit, recorded consent
- **Anonymization**: Real PII is never stored; only synthetic data is generated
- **Right to Erasure**: `GDPRComplianceChecker.check_right_to_erasure()` supports deletion requests
- **Data Minimization**: Only necessary data fields are generated

### Usage
```python
from bots.dataforge.compliance import GDPRComplianceChecker

checker = GDPRComplianceChecker()
result = checker.check_compliance({
    "consent": True,
    "anonymized": True,
    "license": "CC-BY-4.0",
    "data_subject_rights": True
})
```

## CCPA Compliance

The California Consumer Privacy Act applies to businesses collecting personal data from California residents.

### Key Requirements Met
- **Opt-Out**: Users can opt out of data selling via `CCPAComplianceChecker.validate_opt_out()`
- **Disclosure**: Data collection practices are documented
- **Access Rights**: Users can request their data

## HIPAA Compliance

For any healthcare-adjacent datasets, HIPAA Safe Harbor de-identification is applied.

### PHI Removal
The `HIPAAAnonymizer` removes:
- Social Security Numbers (SSNs)
- Dates of birth
- Phone numbers
- Email addresses
- Medical Record Numbers (MRNs)

```python
from bots.dataforge.compliance import HIPAAAnonymizer

anon = HIPAAAnonymizer()
clean_record = anon.safe_harbor_anonymize(record)
```

## Biometric Data Protection

DataForge AI complies with BIPA (Biometric Information Privacy Act) and similar laws.

- All facial expression datasets use **synthetic GAN-generated images** (no real people)
- Voice datasets use **synthetic audio metadata** only
- Biometric consent is tracked via `BiometricDataProtector`

## Synthetic Data Policy

**All DataForge AI datasets are 100% synthetic**. No real personal data is collected or used:

- Voice datasets: Generated metadata with random synthetic speaker IDs
- Facial datasets: Synthetic GAN labels with `real_person: false`
- Behavioral datasets: Template-based conversations with random IDs
- Emotion datasets: Simulated feature vectors

## Licensing

All published datasets use Creative Commons licenses:

| Use Case | License |
|----------|---------|
| Commercial | CC-BY-4.0 |
| Non-Commercial | CC-BY-NC-4.0 |
| Research Only | CC-BY-NC-ND-4.0 |

## Consent Management

```python
from bots.dataforge.licensing.consent_manager import ConsentManager

mgr = ConsentManager()
mgr.record_consent("user_123", "data_selling", granted=True)
mgr.check_consent("user_123", "data_selling")  # True
mgr.revoke_consent("user_123", "data_selling")
```
