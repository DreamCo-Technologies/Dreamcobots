# Dependency Intelligence Report

## Summary

- Project nodes: 16
- package.json manifests: 7
- requirements manifests: 10
- Duplicate dependencies: 13
- Version conflicts: 13
- Likely unused entries: 13

## Top Critical Infrastructure Packages

- `express` (score: 10)
- `requests` (score: 10)
- `stripe` (score: 10)
- `flask` (score: 9)
- `dotenv` (score: 8)
- `openai` (score: 8)
- `selenium` (score: 8)
- `fastapi` (score: 6)
- `httpx` (score: 6)
- `pytest` (score: 6)

## Version Conflicts

- `@octokit/rest` → ^20.0.2, ^20.1.1
- `dotenv` → ^16.3.1, ^17.4.1
- `express` → ^4.17.1, ^4.18.2
- `flask` → flask>=2.0.0, flask>=3.0.0, flask>=3.1.3
- `flask-cors` → flask-cors>=4.0.0, flask-cors>=6.0.2
- `jinja2` → jinja2>=3.1.0, jinja2>=3.1.6
- `openai` → openai>=1.0.0, openai>=2.37.0
- `python-dotenv` → python-dotenv>=1.0.0, python-dotenv>=1.2.2
- `requests` → requests>=2.28.0, requests>=2.34.2
- `schedule` → schedule>=1.2.0, schedule>=1.2.2
- `selenium` → selenium>=4.0.0, selenium>=4.10.0, selenium>=4.44.0
- `stripe` → ^14.0.0, ^14.21.0, stripe>=15.1.0, stripe>=5.0.0, stripe>=7.0.0
- `webdriver-manager` → webdriver-manager>=4.0.0, webdriver-manager>=4.1.1

## Likely Unused Dependencies

- `dreamco/package.json`: cheerio, json2csv, node-fetch, nodemon, uuid
- `dreamco-control-tower/frontend/package.json`: autoprefixer, postcss, react, react-dom, recharts, tailwindcss
- `dreamco-control-tower/package.json`: express
- `package.json`: eslint, jest, prettier, supertest
- `bots/211-resource-eligibility-bot/requirements.txt`: python-dotenv, requests
- `bots/ai-side-hustle-bots/requirements.txt`: openai, python-dotenv, requests
- `bots/government-contract-grant-bot/requirements.txt`: jinja2, python-dotenv, requests, schedule
- `bots/job-application-bot/requirements.txt`: pdfminer-six, python-docx, webdriver-manager
- `bots/selenium-job-application-bot/requirements.txt`: python-dotenv, requests
- `dashboard/requirements.txt`: flask-cors
- `dashboards/web_control/requirements.txt`: flask, flask-cors
- `requirements.txt`: flask-cors, httpx, jinja2, openai, pytest-benchmark, pytest-cov, python-dotenv, schedule
- `stripe/python/requirements.txt`: python-dotenv
