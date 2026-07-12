# DreamCobots — DreamCo Guide

This guide explains how to run, configure, and extend the DreamCobots project
inside a [DreamCo](https://dreamco.local) environment.

---

## Quick-Start on DreamCo

1. **Fork / import the repository**
   - Open DreamCo and choose **Create Repl → Import from GitHub**.
   - Paste `https://github.com/ireanjordan24/Dreamcobots` and click **Import**.

2. **Install dependencies**

   DreamCo automatically installs packages listed in `requirements.txt`.
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

   > **Never commit real API keys.** Use DreamCo *Secrets* (the 🔒 tab in the
   > sidebar) to store sensitive values and load them via `os.environ`.

4. **Run a bot**

   In the *Shell* tab:

   ```bash
   python bots/government-contract-grant-bot/government_contract_grant_bot.py
   ```

   Or set the **Run** button command in `.dreamco` to the script you want.

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
├── dreamco.md                                # This file
└── README.md                                # Main project documentation
```

---

## DreamCo-Specific Tips

| Tip | Detail |
|-----|--------|
| **Secrets** | Store `API_KEY` and other credentials in DreamCo Secrets, not in source files. |
| **Always-On** | Enable *Always On* (Hacker plan+) if bots need to run 24/7. |
| **Scheduled runs** | Use [DreamCo Deployments](https://docs.dreamco.local/hosting/deployments/about-deployments) or an external cron service to trigger bots on a schedule. |
| **Packages** | Add new Python packages with `pip install <pkg>` in the Shell; DreamCo persists the environment between sessions. |
| **`.dreamco` file** | Create a `.dreamco` file in the repo root to customise the Run button: `run = "python debug.py"` |

---

## Running the DreamSite Launcher

The `DreamSite_Launcher` script bootstraps the full DreamCo site stack.
After importing the repository on DreamCo:

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
