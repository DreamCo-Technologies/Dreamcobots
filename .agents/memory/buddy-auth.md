---
name: Buddy Bot auth authority
description: Buddy Bot (server/seed-buddy-bot.ts) is the empire's single authentication authority — all OAuth, JWT, secrets, MFA, SAML, CLI auth patterns live in his system prompt.
---
**Why:** Centralizing auth knowledge in one bot ensures consistent, secure patterns empire-wide. All other bots have BUDDY_BOT_PROTOCOL instructing them to route coding/auth to Buddy.

**How to apply:** When any auth pattern needs updating (new OAuth provider, new secrets manager, new CLI tool), update Buddy's system prompt in server/seed-buddy-bot.ts. The self-building skill library in his prompt includes 20 pre-built auth skill entries.

Auth domains Buddy covers:
- OAuth 2.0 all 5 flows (PKCE, client credentials, device, implicit, ROPC)
- 50+ OAuth provider scopes
- JWT (HS256, RS256, JWKS, refresh rotation)
- Password hashing (Argon2id, bcrypt, PBKDF2, timing-safe comparison)
- Secrets management (env vars, AWS SM, Vault, GCP SM, Azure KV, AES-256-GCM token encryption)
- CLI auth (AWS, gcloud, Azure, GitHub, Stripe, Vercel, Fly, Railway, Heroku, Docker, npm, SSH, GPG)
- MFA/TOTP/WebAuthn/Passkeys
- SAML 2.0/SSO via WorkOS/Clerk
- Session management (Redis-backed, __Host- prefix, CSRF via csrf-csrf)
- Webhook signature verification (Stripe, GitHub, generic HMAC)
- Auth security checklist (13 points) appended to every auth response
