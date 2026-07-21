# Buddy Authentication Mega Architecture

Buddy's authentication framework is designed to support multi-layer security requirements for a universal AI operating system. This detailed documentation serves as a guide to understanding the various authentication mechanisms integrated into Buddy’s architecture and how they are implemented.

---

## Master List of Authentication Types for Buddy

### 1. Password Authentication
- **Use Case**: Username/password login, backup access, offline desktop modes.
- **Technologies**: bcrypt, Argon2, PBKDF2.
- **Usage in Buddy**:
  - Email signup/login.
  - Admin login.
  - Universal compatibility and legacy support.

### 2. OAuth 2.0 Authentication (Social Login)
- **Providers Supported**:
  - Google, Microsoft, Apple, GitHub, Discord, Meta, Amazon.
- **Use Case**: Social login, connect third-party APIs, access cloud data.
- **Key Setup**:
  - OAuth consent flow with redirection.

### 3. OpenID Connect (OIDC)
- **Use Case**: Enterprise Single Sign-On (SSO), identity federation, user profile syncing.
- **Why Important**: Modern SaaS integration standard.
- **Example Scenarios**:
  - Persistent identity across Buddy apps.

### 4. SAML Authentication
- **Use Case**: Enterprise SSO for corporations, universities, and governments.
- **Providers Supported**:
  - Okta, Microsoft, Ping Identity, OneLogin.
- **Buddy Use Cases**:
  - Enterprise dashboards, internal systems.

### 5. JWT Authentication
- **Use Case**: Stateless sessions for users, APIs, and AI agents.
- **Flow**:
  1. User logins to Auth Server.
  2. JWT issued.
  3. Services verify JWT.
- **Advantages**:
  - Fast, stateless, microservices friendly.

### 6. API Key Authentication
- **Use Case**: Machine-to-machine access, developers, CLI tools.
- **Features**:
  - Key rotation, expiration, rate limits, scoped permissions.

### 7. Passkeys / WebAuthn (FIDO2)
- **Use Case**: Passwordless login, biometric access.
- **Examples**: YubiKey, Face ID, Touch ID.

### 8. Multi-Factor Authentication (MFA)
- **Factors**: Something you know, have, and are.
- **Uses**: Admin security, financial transactions, high-trust systems.

---

## Recommended Architecture

### Core Auth Layers

| Layer            | Technology         |
|------------------|--------------------|
| **User Login**   | OIDC + OAuth 2.1  |
| **Enterprise SSO** | SAML + SCIM       |
| **Passwordless** | Passkeys/WebAuthn |
| **APIs**         | OAuth + API Keys  |
| **AI Agents**    | MCP OAuth         |

### Deployment Phases

#### Phase 1:
- JWT auth, OAuth login, RBAC, API keys.

#### Phase 2:
- Passkeys, MFA, AI-agent auth.

#### Phase 3:
- Zero trust, ABAC, device trust.

---

## API Endpoints

### Authentication Endpoints
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `POST /auth/refresh`
- `POST /auth/magic-link`
- `POST /auth/mfa/verify`

### OAuth
- `GET /oauth/google`
- `GET /oauth/github`
- `GET /oauth/apple`

### AI Agent Auth
- `POST /agents/register`
- `POST /agents/token`
- `POST /agents/authorize`

---

## Database Schema

### Users Table
- `id`, `email`, `username`, `password_hash`, `auth_provider`, `status`.

### Sessions Table
- `id`, `user_id`, `jwt_id`, `device_id`, `ip_address`, `expires_at`.

### API Keys Table
- `id`, `user_id`, `key_hash`, `scopes`, `rate_limit`, `expires_at`.

---

This documentation ensures a clear understanding of the technologies and flows powering Buddy's multi-layered authentication architecture.
