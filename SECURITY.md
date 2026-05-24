# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x.x   | ✅ Yes — actively maintained |
| 1.x.x   | ❌ No — please upgrade to v2 |

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

### How to Report

1. **Email:** security@dreamco.ai (or open a [private security advisory](https://github.com/DreamCo-Technologies/Dreamcobots/security/advisories/new))
2. **PGP key:** Available at https://dreamco.ai/.well-known/security.txt
3. **Response time:** We aim to acknowledge reports within **24 hours** and resolve within **7 days** for critical issues.

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fix (optional)

## Our Commitment

- We will acknowledge your report within 24 hours
- We will provide regular updates on our progress
- We will credit you in the changelog (unless you prefer anonymity)
- We will not take legal action against good-faith researchers

## Zero CVE Policy

DreamCo OS maintains a **zero open CVE policy**:

- `pip-audit` runs on every CI push and blocks merges on any known CVE
- Dependabot is configured to auto-create PRs for security updates
- All dependencies are pinned to exact versions
- `CODEOWNERS` ensures security-critical files require review

## Known Security Measures

- All API keys loaded from environment variables — no hardcoded secrets
- PII detection layer scans data before any memory storage
- Capability whitelist: bots declare permitted tools; violations raise `PermissionError`
- Sandbox execution: tool calls wrapped in async timeout + policy enforcement
- Append-only governance audit log for all security-relevant events
- Prompt injection detection in bots that process external input

## Disclosure Policy

We follow **Coordinated Vulnerability Disclosure (CVD)**:

1. Reporter submits vulnerability privately
2. DreamCo investigates and develops a fix
3. Fix released as a patch version
4. CVE number requested if applicable
5. Public disclosure after patch release (typically 30 days)

---

*Last updated: May 2026*
