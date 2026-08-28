# Mergeable PR Rebuild Process

DreamCo does not force-merge conflicted or obsolete pull requests.

For a PR that cannot safely merge:

1. Inspect the PR metadata and changed files.
2. Identify unique capabilities worth retaining.
3. Start a clean branch from current `main`.
4. Reapply only compatible, required changes.
5. Run the control-plane and regression gates.
6. Create a replacement PR.
7. Keep the original PR available as historical evidence until the replacement is validated.

This process prevents large conflicted PR backlogs from becoming production dependencies and keeps `main` as the source of truth.
