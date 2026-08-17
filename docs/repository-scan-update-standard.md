# Repository Scan Update Standard

After an authorized repository scan, Buddy should publish an evidence-backed update comment or workflow summary.

## Required distinctions

- **Found:** an observation supported by scan evidence.
- **Proposed:** a recommended improvement that has not been implemented.
- **Changed:** a change exists in a commit or pull request.
- **Verified:** the change passed the relevant test or benchmark with evidence.
- **Blocked:** work cannot continue because a dependency, permission, environment, or human decision is required.
- **Unknown:** insufficient evidence.

## Update sequence

`scan → findings → evidence → proposed improvements → approved changes → tests → benchmark → regression → update comment`

Code changes remain subject to repository authorization and configured approval gates.
