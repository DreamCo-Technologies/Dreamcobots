# DreamCo Laptop + VR Architecture

## Roles

The M5 MacBook Air is the local engineering, testing, Buddy sandbox, and command-center workstation. GitHub is the source of truth. Cloud infrastructure is the persistent production runtime. Web/mobile/VR are client interfaces.

```text
                    Buddy / DreamCo Core
                            |
              +-------------+-------------+
              |             |             |
            Web           Mobile         VR
              |             |             |
              +-------------+-------------+
                            |
                    DreamCo Control Plane
                            |
             +--------------+--------------+
             |              |              |
           GitHub          Cloud        Mac Lab
          CI/CD          Production     Testing
```

## Mac responsibilities

- Clone and synchronize the canonical repository.
- Run local lint/build/unit/integration checks.
- Run `tools/dreamco_doctor.py` before development sessions.
- Reproduce GitHub Actions failures locally when possible.
- Run bounded Buddy experiments in a sandbox.
- Run model/benchmark experiments appropriate for the available hardware.
- Commit changes and push through normal Git workflows.

## Security boundary

Buddy must not receive unrestricted access to the host. Local automation should use explicit allowlists, sandboxed working directories, timeouts, least-privilege credentials, audit logs, and human approval for destructive or deployment operations.

## VR strategy

VR is a visualization and interaction surface, not the production compute layer. The first VR milestone should display live, authenticated DreamCo state: system health, divisions, bot/module status, Actions, benchmark jobs, alerts, and deployment status. Only after the core control plane is stable should VR support write operations.

## Production flow

`Mac -> local verification -> GitHub -> CI/certification -> cloud deployment -> live telemetry -> VR/mobile/web clients`

Hardware-dependent model results must record the machine profile and must not be generalized to other hardware without evidence.
