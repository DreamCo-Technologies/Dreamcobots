# Military Contract Bot

State-of-the-art military procurement intelligence bot for the Dreamcobots platform.

## Features

| Feature | FREE | PRO | ENTERPRISE |
|---|---|---|---|
| Basic DoD contract search | ✅ | ✅ | ✅ |
| Full search + filters | ❌ | ✅ | ✅ |
| Solicitation parser (MIL-SPEC, FAR/DFARS) | ❌ | ✅ | ✅ |
| CMMC / FAR compliance checker | ❌ | ✅ | ✅ |
| Export control screening (ITAR/EAR) | ❌ | ✅ | ✅ |
| Deadline alerts + saved searches | ❌ | ✅ | ✅ |
| AI bid analysis + win probability | ❌ | ✅ | ✅ |
| Proposal builder | ❌ | ✅ | ✅ |
| Security module (RBAC, AES-256, audit trail) | ❌ | ❌ | ✅ |
| Performance analytics API | ❌ | ❌ | ✅ |
| Competitor analysis | ❌ | ❌ | ✅ |
| Subcontract finder | ❌ | ❌ | ✅ |
| Manual override system | ❌ | ❌ | ✅ |
| REST API access | ❌ | ❌ | ✅ |

## Pricing

| Tier | Monthly |
|---|---|
| FREE | $0 |
| PRO | $199 |
| ENTERPRISE | $499 |

## Quick Start

```bash
# Run the bot directly
python bot.py

# Or import it in your code
from military_contract_bot import MilitaryContractBot, Tier

bot = MilitaryContractBot(tier=Tier.PRO)
results = bot.search_contracts(keyword="cybersecurity", agency="Department of the Navy")
for r in results:
    print(r["id"], r["title"], r["value"])
```

## Security

- **PBKDF2+SHA-256 key derivation with XOR-stream encryption** for sensitive data at rest
  and in transit (swap in the `cryptography` package for FIPS-validated AES-256-GCM in production)
- **Role-Based Access Control (RBAC)** — five levels: VIEWER → ANALYST → CONTRACTOR → OFFICER → ADMIN
- **Tamper-evident audit trail** using HMAC-SHA256-protected entries
- **ITAR / EAR export control screening** on all contract descriptions
- **Manual override system** with full logging for fail-safe operations

## Compliance

- CMMC Level 1/2/3 compliance checking
- FAR and DFARS clause validation
- Military specification (MIL-STD / MIL-HDBK) extraction
- SAM.gov / PIEE / FPDS-NG format compatibility
- NIST SP 800-171 control mapping

## Architecture

```
bots/military-contract-bot/
├── bot.py                    # Entry point
├── military_contract_bot.py  # Core bot class (MilitaryContractBot)
├── mil_security.py           # PBKDF2+XOR encryption, RBAC, audit trail
├── mil_compliance.py         # CMMC, FAR/DFARS, MIL-SPEC, ITAR/EAR
├── mil_analytics.py          # Performance metrics & monitoring
├── mil_api.py                # REST-style API handlers
├── config.json               # Deployment configuration
└── README.md
```

## Government System Integration

The bot is designed to interface with:

- **SAM.gov** — System for Award Management (contract search)
- **beta.SAM.gov** — Next-gen procurement data
- **PIEE** — Procurement Integrated Enterprise Environment
- **FPDS-NG** — Federal Procurement Data System Next Generation
- **DARPA BROAD** — DARPA broad agency announcements

## Usage

### Search contracts
```python
results = bot.search_contracts(
    keyword="autonomous",
    agency="DARPA",
    cmmc_level=3,
    min_value=10_000_000,
)
```

### Analyze an opportunity
```python
analysis = bot.analyze_opportunity("HR0011-24-R-0022")
print(analysis["analysis"]["win_probability_pct"])
print(analysis["analysis"]["recommended_action"])
```

### Run compliance check
```python
user = bot.create_user("alice", "officer", clearance_level=3)
result = bot.run_compliance_check(
    "W56HZV-24-R-0001",
    implemented_controls=["AC.1.001", "IA.1.076"],
    user=user,
)
print(result["cmmc_compliance"])
```

### Parse a solicitation
```python
parsed = bot.parse_solicitation_text(solicitation_text)
print(parsed["parsed"]["mil_specs"])
print(parsed["parsed"]["far_dfars_clauses"])
```

### Submit a proposal
```python
user = bot.create_user("contractor_alice", "contractor")
result = bot.submit_proposal(
    "FA8621-24-R-0055",
    {"technical_volume": "...", "price_volume": "..."},
    user=user,
)
```

### Performance analytics
```python
summary = bot.analytics.get_summary()
print(summary["win_rate_pct"])
print(summary["counters"])
```
