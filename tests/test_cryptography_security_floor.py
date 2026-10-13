"""Regression checks for the tools dependency security floor and holdout primitives.

No network, keys, secrets, or production holdout data are accessed.
"""
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_cryptography_dependency_excludes_known_vulnerable_versions():
    requirements = (ROOT / "requirements-tools.txt").read_text().splitlines()
    declarations = [line.strip() for line in requirements
                    if line.strip().lower().startswith("cryptography")
                    and not line.lstrip().startswith("#")]
    assert len(declarations) == 1, "Exactly one unambiguous cryptography requirement is needed"
    match = re.fullmatch(r"cryptography\s*>=\s*(\d+)\.(\d+)\.(\d+)\s*,\s*<\s*(\d+)", declarations[0])
    assert match, "Use an explicit lower security floor and bounded major-version upper limit"
    minimum = tuple(map(int, match.groups()[:3]))
    excluded_major = int(match.group(4))
    assert minimum >= (49, 0, 0), "GHSA-jwv3-5hgf-82ww requires cryptography >=49.0.0"
    assert minimum[0] < excluded_major <= 50, "Review major-version upgrades separately"


def test_holdout_crypto_primitives_round_trip_and_authenticate():
    pytest.importorskip("cryptography")
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

    key = Scrypt(salt=b"local-test-salt-16", length=32, n=2**14, r=8, p=1).derive(b"sandbox-passphrase")
    cipher = AESGCM(key)
    nonce = b"testnonce123"
    associated_data = b"dreamco-holdout:test"
    encrypted = cipher.encrypt(nonce, b"non-secret sandbox fixture", associated_data)
    assert cipher.decrypt(nonce, encrypted, associated_data) == b"non-secret sandbox fixture"
    with pytest.raises(InvalidTag):
        cipher.decrypt(nonce, encrypted, b"wrong-role")
