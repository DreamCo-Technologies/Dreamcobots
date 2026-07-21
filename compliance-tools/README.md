# Compliance Tools

Regulatory compliance auditing and checking tools for the DreamCo ecosystem.

## Tools

### ComplianceChecker (`compliance_checker.py`)

A fully functional compliance checker that evaluates organizational and
technical controls against major regulatory frameworks.

**Supported Frameworks:**
- **GDPR** — General Data Protection Regulation (EU)
- **CCPA** — California Consumer Privacy Act (US-CA)
- **HIPAA** — Health Insurance Portability and Accountability Act (US)
- **SOC2** — Service Organization Control 2 (Global)
- **PCI DSS** — Payment Card Industry Data Security Standard (Global)
- **ADA** — Americans with Disabilities Act (US)
- **OSHA** — Occupational Safety and Health Administration (US)
- **ISO 27001** — Information Security Management (Global)

**Features:**
- Check compliance for any supported framework
- Multi-framework simultaneous evaluation
- Aggregate risk scoring across frameworks
- PII masking and pseudonymization utilities
- Email, SSN, phone validation helpers
- Full audit log of all compliance checks

**Usage:**
```python
from compliance_tools.compliance_checker import ComplianceChecker

checker = ComplianceChecker()

# List available frameworks
frameworks = checker.list_frameworks()

# Check GDPR compliance with your org profile
profile = {
    "data_minimization": True,
    "consent_mechanism": True,
    "privacy_policy": True,
    "right_to_erasure": False,
    "data_breach_notification": True,
}
report = checker.check_compliance("GDPR", profile)
print(f"Score: {report['score_pct']}%  |  Risk: {report['risk_level']}")

# Check multiple frameworks at once
reports = checker.check_multiple_frameworks(["GDPR", "CCPA", "HIPAA"], profile)

# Calculate aggregate risk
risk = checker.calculate_risk_score(reports)
print(f"Overall risk: {risk['overall_risk']}")

# Mask PII in text
masked = checker.mask_pii("Contact john@example.com or 555-867-5309")

# Pseudonymize a user ID
hashed = checker.hash_identifier("user@example.com")
```

**Run the sample report:**
```bash
python compliance-tools/compliance_checker.py
```
