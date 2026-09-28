# GitHub Pages Universe Link Plan

Owner lane: Grok-Pages-Universe-Linker. Companion to `docs/PUBLIC_GITHUB_PAGES_MASTER_DASHBOARD.md`.

Rule: every major product mentioned anywhere on Pages must deep-link to a live page. No orphan mentions.

## 1. Publisher truth (checked 2026-09-28)

- Pages API: `build_type: legacy`, source `main` `/`. The live site is the whole repository rendered by legacy Jekyll.
- Result: the site root is the rendered `README.md`; the Buddy site is served under `/Dreamcobots/website/`.
- Two Actions publishers also exist and do **not** control the live site while the source is legacy:
  - `.github/workflows/pages.yml` (Jekyll `docs/` plus `website/` overlay, then deploy-pages)
  - `.github/workflows/deploy-buddy-pages.yml` (uploads `website/` as the artifact; recent runs failing)
- Owner action (settings only): pick ONE Actions publisher and switch Pages source to "GitHub Actions". Until then, the URL contract below holds.

## 2. URL base contract

- Public absolute form: `https://dreamco-technologies.github.io/Dreamcobots/website/<page>.html`.
- Inside `website/`, relative links (`models.html`) are correct.
- From `README.md` / Jekyll root, link as `website/<page>.html`.
- `sitemap.xml` must use the `/website/` form (the old root-level URLs returned 404).

## 3. P0 product deep links

| Product | Primary page | Secondary | Live (200) |
|---|---|---|---|
| Bootcamp | `website/own-bootcamp.html` | `hf-bootcamp.html`, `bootcamp-wrappers.html` | yes |
| Model picker | `website/models.html` | `open-model-lab.html` | yes |
| Packages | `website/hf-bootcamp.html` | `marketplace.html`, `hub.html` | yes |
| Fleet | `website/bots.html` | `divisions.html` | yes |
| Gates | `website/autonomy.html` | `test-center.html`, `build.html` | yes |
| HF lab | `website/learn-hf.html` | `hub.html`, `hf-hub.html` | yes |

Each P0 product appears in: `website/nav.js` visible bar (first 9 links), `README.md` "Buddy on GitHub Pages" list, and `website/sitemap.xml`.

## 4. Open gaps

- No dedicated package index page; `hf-bootcamp.html` is the closest real listing. A packages index (RP/LP/CP/DP) is owned by the package-market lane.
- No single "gates" page; `autonomy.html` is the closest. A gates desk should aggregate CI, cert, and live-revenue gates with evidence links.
- Publisher conflict (section 1) is owner-only.

## 5. Check before merge

- `node --check website/nav.js`
- every sitemap URL returns 200
- no secrets or tokens in any Pages file
