# DreamCo Actions Control Plane

The GitHub Actions page is the operational entry point for DreamCo's daily production checks.

## Authoritative workflow

`DreamCo Control Plane` is the canonical workflow for the production scan. It supports scheduled daily execution plus manual dispatch.

## Manual actions

| Action | Purpose | Default resource policy |
|---|---|---|
| Daily scan | Repository and production evidence scan | Free/local |
| Benchmark inventory | Discover benchmark/evaluation evidence | Free/local |
| Capability audit | Inspect Capability Genome evidence | Free/local |
| Learning audit | Inspect learning/reasoning/distillation evidence | Free/local |
| Resource audit | Inspect resource/cost signals | Free/local |
| Integration audit | Inspect Actions/control-plane contracts | Free/local |
| Full production audit | Run the broad control-plane checks | Free/local |

## Daily contract

Every scheduled run must:

1. check out the repository
2. run the deterministic repository scan
3. emit machine-readable JSON
4. emit a human-readable Markdown report
5. upload the report as an artifact
6. verify the control-plane contracts
7. publish a GitHub Actions run summary

## Production safety

The control plane does not authorize paid compute, modify model weights, merge pull requests, or publish unverified benchmark claims by default. Those operations require separate workflows/permissions and explicit evidence gates.

## Scaling

The workflow is intentionally independent of fixed bot/model counts. New models, modules, benchmarks, labs, and capabilities can be discovered by extending the underlying registries and scanners without changing the control-plane contract.

## Next integration gates

- connect benchmark runners to the `benchmark-inventory` action
- connect Capability Genome updates to `capability-audit`
- connect Buddy teacher evaluation to `learning-audit`
- add resource measurements to `resource-audit`
- publish the daily report to GitHub Pages
- add regression and deployment health checks
