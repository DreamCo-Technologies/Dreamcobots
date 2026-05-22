# DreamCobots — Replit Guide

This guide explains how to run, configure, and extend the DreamCobots project
inside a [Replit](https://replit.com) environment.

---

## Quick-Start on Replit

1. **Fork / import the repository**
   - Open Replit and choose **Create Repl → Import from GitHub**.
   - Paste `https://github.com/DreamCo-Technologies/Dreamcobots` and click **Import**.

2. **Install dependencies**

   Replit automatically installs packages listed in `requirements.txt`.
   If that file is absent, open the *Shell* tab and run:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your bot**

   Copy or edit `bots/config.json` and fill in any required API keys:

   ```json
   {
     "api_key": "YOUR_API_KEY_HERE",
     "bot_name": "GovernmentContractGrantBot",
     "log_level": "INFO"
   }
   ```

   > **Never commit real API keys.** Use Replit *Secrets* (the 🔒 tab in the
   > sidebar) to store sensitive values and load them via `os.environ`.

4. **Run a bot**

   In the *Shell* tab:

   ```bash
   python bots/government-contract-grant-bot/government_contract_grant_bot.py
   ```

   Or set the **Run** button command in `.replit` to the script you want.

5. **Run the debug utility**

   ```bash
   python debug.py
   ```

   This prints an environment summary, validates the bot interface, and runs a
   10-iteration stress test.

---

## Project Layout

```
Dreamcobots/
├── bots/
│   ├── config.json                          # Bot configuration (API keys, settings)
│   ├── README.md                            # Bot directory documentation
│   └── government-contract-grant-bot/
│       └── government_contract_grant_bot.py # Government Contract & Grant Bot
├── examples/
│   ├── README.md                            # Use-case examples
│   └── stress_test.py                       # Stress / load tests
├── debug.py                                 # Debugging & diagnostic utility
├── replit.md                                # This file
└── README.md                                # Main project documentation
```

---

## Replit-Specific Tips

| Tip | Detail |
|-----|--------|
| **Secrets** | Store `API_KEY` and other credentials in Replit Secrets, not in source files. |
| **Always-On** | Enable *Always On* (Hacker plan+) if bots need to run 24/7. |
| **Scheduled runs** | Use [Replit Deployments](https://docs.replit.com/hosting/deployments/about-deployments) or an external cron service to trigger bots on a schedule. |
| **Packages** | Add new Python packages with `pip install <pkg>` in the Shell; Replit persists the environment between sessions. |
| **`.replit` file** | Create a `.replit` file in the repo root to customise the Run button: `run = "python debug.py"` |

---

## If Replit says an admin blocked DreamCo access

If Replit cannot access `DreamCo-Technologies/Dreamcobots` because an admin
restriction is enabled:

1. Ask a **DreamCo-Technologies org admin** to approve Replit's GitHub
   authorization/app access for the organization repository.
2. Confirm your GitHub account has at least **Read** access to the repository.
3. Reconnect GitHub from Replit Version Control after approval.
4. If approval is delayed, use a temporary fallback:
   - Fork `DreamCo-Technologies/Dreamcobots` to your personal GitHub account.
   - Import the fork into Replit.
   - Open pull requests from the fork back to `DreamCo-Technologies/Dreamcobots`.

---

## Running the DreamSite Launcher

The `DreamSite_Launcher` script bootstraps the full DreamCo site stack.
After importing the repository on Replit:

```bash
python bots/dreamsite_launcher.py
```

If you have the launcher ZIP from the issue attachments, extract it into the
`bots/` directory before running.

---

## Contributing

1. Create a feature branch: `git checkout -b my-feature`
2. Make your changes and run `python debug.py` to validate.
3. Open a pull request against `main`.
