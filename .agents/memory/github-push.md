---
name: GitHub push method
description: Push through the configured repository remote and GitHub Desktop credential helper.
---
**Why:** GitHub Desktop keeps credentials outside commands, shell history, logs, and committed files.

**How to apply:**
1. Confirm the branch and remote with `git status -sb` and `git remote -v`.
2. Push the current branch with `git -c credential.helper=desktop push -u origin HEAD`.
3. Open a pull request and merge only after checks pass.

Never put a personal access token in a remote URL. Never force-push a shared branch unless the owner explicitly approves that exact operation.
