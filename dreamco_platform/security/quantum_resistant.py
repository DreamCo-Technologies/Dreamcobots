from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import os
from typing import Dict


@dataclass
class VersionedKey:
    version: int
    public_key: bytes
    private_key: bytes
    classical_key: bytes


class QuantumResistantEncryptor:
    def __init__(self) -> None:
        self.key_store: Dict[int, VersionedKey] = {}
        self.current_version = 0

    def key_generate(self) -> VersionedKey:
        self.current_version += 1
        seed = os.urandom(32)
        public_key = hashlib.sha256(seed + b'pub').digest()
        private_key = hashlib.sha256(seed + b'priv').digest()
        classical_key = hashlib.sha256(seed + b'rsa').digest()
        versioned = VersionedKey(self.current_version, public_key, private_key, classical_key)
        self.key_store[versioned.version] = versioned
        return versioned

    def encrypt(self, plaintext: str, version: int | None = None, hybrid: bool = True) -> dict:
        key = self._get_key(version)
        shared_secret = hashlib.sha256(key.public_key + key.classical_key).digest() if hybrid else key.public_key
        ciphertext = self._xor_stream(plaintext.encode('utf-8'), shared_secret)
        capsule = hashlib.sha256(key.public_key + b'kyber').hexdigest()
        return {'version': key.version, 'hybrid': hybrid, 'capsule': capsule, 'ciphertext': ciphertext.hex()}

    def decrypt(self, payload: dict) -> str:
        key = self._get_key(payload['version'])
        shared_secret = hashlib.sha256(key.public_key + key.classical_key).digest() if payload.get('hybrid', True) else key.public_key
        raw = bytes.fromhex(payload['ciphertext'])
        return self._xor_stream(raw, shared_secret).decode('utf-8')

    def rotate_keys(self) -> VersionedKey:
        return self.key_generate()

    def _xor_stream(self, data: bytes, secret: bytes) -> bytes:
        stream = hashlib.sha512(secret).digest()
        return bytes(byte ^ stream[index % len(stream)] for index, byte in enumerate(data))

    def _get_key(self, version: int | None) -> VersionedKey:
        if version is None:
            if not self.key_store:
                return self.key_generate()
            version = self.current_version
        return self.key_store[version]
