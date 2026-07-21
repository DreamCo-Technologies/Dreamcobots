# DreamCo Sandbox No-Hallucination Testing

DreamCo bots must prove work with evidence. A bot should not say every bot is running, every bug is gone, or a system is production ready unless a named command/report proves that exact claim.

## Required behavior

- Run sandbox-safe checks before claiming completion.
- Name the command that produced the evidence.
- Link or write a report under `reports/` when possible.
- Separate completed fixes from open risks.
- Say `not verified` when a live service, secret, paid API, deployment, or external client action was not actually tested.
- Keep write, money, deploy, and web-client actions behind explicit permission and audit logs.

## Main command

```bash
npm run sandbox:no-hallucinations
```

Strict mode fails on unsupported absolute success claims:

```bash
npm run sandbox:no-hallucinations:strict
```

## What the audit checks

- Required DreamCo evidence files exist.
- Actions, Agents, and Issues UI evidence exists.
- JSON files parse.
- JavaScript files pass `node --check`.
- Python files pass `python3 -m py_compile` when Python is available.
- Unsupported absolute success language is reported, including claims like `all bots running`, `no bugs`, `fully debugged`, `guaranteed`, `bulletproof`, and `production ready`.

## Reporting rule

Use this format in bot outputs:

```text
Status: completed | partial | blocked | not verified
Evidence: npm run sandbox:no-hallucinations, reports/sandbox-hallucination-audit.md
Completed: concrete fixes that landed
Open: remaining known issues or untested areas
Next test: the next command or workflow to run
```

This keeps DreamCo honest: strong claims only when the repository produced strong evidence.
