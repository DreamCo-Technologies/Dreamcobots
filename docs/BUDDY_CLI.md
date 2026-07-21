# Buddy CLI

Buddy can be installed as a laptop command:

```bash
python3 tools/install_buddy_cli.py
```

After install:

```bash
buddy status
buddy setup
buddy test
buddy once
buddy full
buddy start
buddy stop
buddy dashboard
buddy open-test-kit
buddy song-test
buddy open-song-test
buddy open-website
```

The CLI is free/local-first by default. It can scan, test, generate reports, open local files, start the local dashboard, and run guarded background maintenance. Live signups, secrets, money, deploys, outreach, account access, publishing, and destructive actions still require approval.

For media testing, `buddy song-test` creates a local song packet and `buddy open-song-test` opens a browser page where you can select your own image and voice sample locally. The browser test previews your files without uploading or cloning them.
