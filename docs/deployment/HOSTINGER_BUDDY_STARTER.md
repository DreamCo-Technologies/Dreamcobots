# Hostinger Buddy Starter Branch

Use the `buddy` branch as the first Hostinger deployment branch for the DreamCo Control Tower frontend.

## Repository Settings

- Repository: `DreamCo-Technologies/Dreamcobots`
- Branch: `buddy`
- App root: `dreamco-control-tower/frontend`
- Build command: `npm ci && npm run build`
- Publish directory: `dreamco-control-tower/frontend/dist`
- Hostinger target directory: `public_html`
- Start page: Buddy command center, through `VITE_START_TAB=command-center`
- Health check: `/hostinger-health.html`

## Hostinger Git Deployment Path

1. In Hostinger hPanel, open the website, then open the Git or deployment area.
2. Connect the GitHub repository `DreamCo-Technologies/Dreamcobots`.
3. Select the `buddy` branch.
4. Set the deploy target to `public_html`.
5. Build from `dreamco-control-tower/frontend`.
6. Use Node 20 and run `npm ci && npm run build`.
7. Publish the generated `dreamco-control-tower/frontend/dist` contents.

## Environment

Set this build environment value when Hostinger allows build variables:

```bash
VITE_START_TAB=command-center
```

If Hostinger only pulls files and does not run builds, build locally or in GitHub Actions, then upload the `dist` folder contents into `public_html`.

## Security Rules

- Keep all Hostinger credentials in Hostinger or GitHub repository secrets.
- Never commit FTP passwords, SSH keys, API tokens, or database credentials.
- Keep backend API credentials separate from the static frontend deployment.
- Use the included `.htaccess` file so browser refreshes route back to the app.

## Optional GitHub Secrets For Upload Workflows

If you choose an FTP/SFTP workflow later, create secrets with names like:

- `HOSTINGER_HOST`
- `HOSTINGER_USERNAME`
- `HOSTINGER_PASSWORD`
- `HOSTINGER_TARGET_DIR`

The `buddy` branch is intentionally ready for Hostinger without storing those values in the repository.
