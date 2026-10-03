"""Encryption at rest for the private holdout files (answer key, authoring source).

Format: a small JSON envelope, AES-256-GCM with a key derived from a passphrase by scrypt (n=2**15, r=8, p=1) and a
fresh 128-bit salt and 96-bit GCM nonce per file. The file's role (e.g. "holdout_key") is bound in as associated data, so
an envelope cannot be swapped for another private file. GCM authenticates the ciphertext: a modified file fails to
decrypt instead of decrypting to something else.

The passphrase lives OUTSIDE /workspace and outside the repo, by default /home/box/.ecp-holdout/passphrase (directory
0700, file 0600), override with $DREAMCO_HOLDOUT_PASSPHRASE_FILE. Threat model (see evidence/holdout_kit/README.md):
this stops a casual read of the private folder from revealing the key. It does not stop an agent on the same box and
account that sets out to decrypt it, because that agent can read the passphrase file too.

CLI (builder only):
  python holdout_crypto.py init-passphrase          create the passphrase file if it does not exist
  python holdout_crypto.py encrypt <file> <role>    write <file>.enc, verify it decrypts, delete the plaintext
"""
import base64, json, os, pathlib, secrets, sys

FORMAT = "dreamco-holdout-aes256gcm-scrypt-v1"
SCRYPT_N, SCRYPT_R, SCRYPT_P = 2 ** 15, 8, 1
DEFAULT_PASSPHRASE_FILE = "/home/box/.ecp-holdout/passphrase"


def passphrase_path():
    return pathlib.Path(os.environ.get("DREAMCO_HOLDOUT_PASSPHRASE_FILE", DEFAULT_PASSPHRASE_FILE))


def init_passphrase(path=None):
    p = pathlib.Path(path or passphrase_path())
    if p.is_file():
        return p
    p.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(p.parent, 0o700)
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(secrets.token_urlsafe(32) + "\n")
    os.chmod(p, 0o600)
    return p


def read_passphrase(path=None):
    p = pathlib.Path(path or passphrase_path())
    if not p.is_file():
        raise SystemExit(f"holdout passphrase file not found: {p} (builder only; see holdout_crypto.py)")
    v = p.read_text().strip()
    if len(v) < 20:
        raise SystemExit(f"holdout passphrase in {p} is too short")
    return v.encode()


def _aes(passphrase, salt):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    return AESGCM(Scrypt(salt=salt, length=32, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P).derive(passphrase))


def encrypt_bytes(data, passphrase, role):
    salt, nonce = secrets.token_bytes(16), secrets.token_bytes(12)
    ct = _aes(passphrase, salt).encrypt(nonce, data, f"{FORMAT}:{role}".encode())
    env = {"format": FORMAT, "role": role, "kdf": {"name": "scrypt", "n": SCRYPT_N, "r": SCRYPT_R, "p": SCRYPT_P,
                                                  "salt": salt.hex()},
           "nonce": nonce.hex(), "ciphertext": base64.b64encode(ct).decode()}
    return (json.dumps(env, indent=1) + "\n").encode()


def decrypt_bytes(env_bytes, passphrase, role):
    from cryptography.exceptions import InvalidTag
    try:
        env = json.loads(env_bytes)
        assert env["format"] == FORMAT and env["role"] == role and env["kdf"]["name"] == "scrypt"
        k = env["kdf"]
        assert (k["n"], k["r"], k["p"]) == (SCRYPT_N, SCRYPT_R, SCRYPT_P)
        return _aes(passphrase, bytes.fromhex(k["salt"])).decrypt(bytes.fromhex(env["nonce"]), base64.b64decode(env["ciphertext"]), f"{FORMAT}:{role}".encode())
    except (InvalidTag, ValueError, KeyError, AssertionError, TypeError) as e:
        raise SystemExit(f"cannot decrypt the private {role} file (wrong passphrase, wrong file or modified ciphertext): "
                         f"{type(e).__name__}")


def write_encrypted(path, data, passphrase, role):
    """Write <path> (an .enc envelope) atomically with mode 0600 and check that it decrypts back to data."""
    path = pathlib.Path(path)
    tmp = path.with_name(path.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(encrypt_bytes(data, passphrase, role))
    if decrypt_bytes(tmp.read_bytes(), passphrase, role) != data:
        tmp.unlink()
        raise SystemExit(f"encryption round-trip failed for {path}")
    os.replace(tmp, path)
    os.chmod(path, 0o600)


def main(argv):
    if argv[:1] == ["init-passphrase"]:
        print("passphrase file:", init_passphrase())
    elif argv[:1] == ["encrypt"] and len(argv) == 3:
        src = pathlib.Path(argv[1])
        write_encrypted(src.with_name(src.name + ".enc"), src.read_bytes(), read_passphrase(), argv[2])
        src.unlink()
        print(f"encrypted {src.name} -> {src.name}.enc; plaintext deleted")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
