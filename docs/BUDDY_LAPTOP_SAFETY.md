# Buddy Laptop Safety

Buddy is designed to run locally as a helpful command center, not as an unrestricted process.

## Laptop Protection

- Background mode sleeps at least 15 minutes between cycles.
- Each command is capped at 300 seconds.
- The runner refuses to start when free disk space is below 5 GB.
- The runner refuses to continue when the 1-minute system load is above 10.
- The runner refuses to continue when battery is below 15 percent.
- Logs and process IDs stay out of git.
- Token-like values are redacted before command output is saved.

## Apps, Signups, And Access

Buddy can prepare signup packets, setup checklists, test forms, and approval notes. It should not submit signups, accept terms, grant access, connect payments, buy domains, publish content, send messages, or deploy production without owner approval.

## Secret Keys

Buddy should never commit, print, email, or store raw secret values in generated files. Keep live values in macOS Keychain, environment variables, provider dashboards, or GitHub Actions secrets for CI-only use. Buddy can verify secret names, missing configuration, and code paths using masked status reports.

## Safe Operating Rule

Buddy can help with any app task by preparing the work, running local checks, and showing the approval packet. Live actions require a clear approval step first.
