# DreamCo Dashboards

Central directory for all DreamCo dashboard implementations. Each sub-folder
contains documentation, hosting configuration, and entry points for its
specific dashboard.

---

## Dashboard Index

| Folder                                      | Dashboard                          | Stack          | Hosting Ready |
|---------------------------------------------|------------------------------------|----------------|--------------|
| [`dreamco_main/`](dreamco_main/)            | DreamCo Main Dashboard             | Flask (Python) | ✅ Heroku/Railway |
| [`web_control/`](web_control/)              | Web Control Dashboard              | Flask (Python) | ✅ Heroku/Railway |
| [`analytics/`](analytics/)                  | Analytics Dashboard Bot            | Python class   | API           |
| [`division_performance/`](division_performance/) | Division Performance Dashboard | Python class   | API           |
| [`big_bro_master/`](big_bro_master/)        | Big Bro AI Master Dashboard        | Python class   | API           |
| [`big_bro_interactive/`](big_bro_interactive/) | Big Bro AI Interactive Dashboard | Python class   | API           |
| [`crypto/`](crypto/)                        | Crypto Bot Dashboard               | Python class   | API           |
| [`owner/`](owner/)                          | Owner Dashboard (Bot Network)      | Python class   | API / Firebase |
| [`payments_reporting/`](payments_reporting/) | Payments Reporting Dashboard      | Python class   | API           |
| [`dreamops/`](dreamops/)                    | DreamOps Dashboard                 | Python class   | API           |
| [`global_learning/`](global_learning/)      | Global Learning Dashboards (×3)    | Python class   | API           |
| [`roku/`](roku/)                            | Roku TV KPI Dashboard              | Python class   | Roku ECP      |
| [`home_screen/`](home_screen/)              | Home Screen Dashboard              | Python class   | Mobile / Web  |

---

## Flask Dashboards — Go Live Today

The two Flask-based dashboards (`dreamco_main` and `web_control`) are
deployment-ready. They include a `Procfile` and `requirements.txt` for
one-command deployment to Heroku or Railway:

```bash
# DreamCo Main Dashboard (port 5001)
pip install -r dashboard/requirements.txt
python dashboard/app.py

# Web Control Dashboard (port 5050)
pip install -r dashboards/web_control/requirements.txt
python dashboards/web_control/run.py
```

---

## GitHub Pages

The static GitHub Pages site lives in [`docs/`](../docs/). It includes:

- [`docs/index.html`](../docs/index.html) — DreamCobots ecosystem overview
- [`docs/dashboards.html`](../docs/dashboards.html) — Dashboard portal

Enable GitHub Pages in **Repository Settings → Pages → Source: `main` / `docs/`**.

---

## Adding a New Dashboard

1. Create a sub-folder here with a descriptive name.
2. Add a `README.md` linking to the source file(s).
3. For Flask apps: add `requirements.txt` and `Procfile`.
4. For frontend dashboards: add the HTML/JS/CSS and update `docs/dashboards.html`.
