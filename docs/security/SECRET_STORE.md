# Host-only secret store security

The Python secret store uses AES-256-GCM authenticated encryption with a per-file random salt and nonce. A host-provided master secret is stretched with scrypt. Secret files are created outside the repository with owner-only permissions. Writes are exclusive: an existing secret name is never silently overwritten.

## Host setup

Generate a high-entropy key on the host and keep it in a local secret manager or protected environment configuration:

```bash
openssl rand -hex 32
```

Set the resulting value as `OWNER_SECRET_KEY`. Install the `cryptography` Python package in the environment that uses the secret store. Never commit the key or place it in browser storage, logs, source files, or repository configuration.

## API

- `store(name, value, folder)` encrypts and creates a new file.
- `load(name, folder)` authenticates and decrypts a stored file.
- Invalid names, repository paths, weak keys, insecure file permissions, tampering, and unsupported legacy formats fail closed.
- Replacing a secret requires a deliberate operator-managed rotation procedure; the API refuses implicit overwrite.

## Compatibility and rollout

This changes the file format to `DCOG2`. Existing files created by the prior custom XOR/HMAC construction are not automatically migrated or trusted. Back them up securely, rotate the master key, and re-enter credentials through the approved host secret manager before production use.

This module is not by itself a complete production vault. Production deployment still requires platform key management, access controls, rotation/revocation, audit logging, backup/recovery, and security review.
