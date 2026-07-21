from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Mapping
import base64
import hashlib
import hmac
import json

@dataclass
class FederatedInstance:
    url: str
    public_key: str
    capabilities: List[str]
    trust_level: float

@dataclass
class FederatedSession:
    instance: FederatedInstance
    jwt_token: str
    attestation: Dict[str, str]
    expires_at: datetime

    def delegate_task(self, capability: str, payload: Mapping[str, object]) -> Dict[str, object]:
        allowed = capability in self.instance.capabilities and self.expires_at > datetime.utcnow()
        status = 'accepted' if allowed else 'rejected'
        return {
            'status': status,
            'target': self.instance.url,
            'capability': capability,
            'payload': dict(payload),
            'attestation': self.attestation,
        }


class FederationBridge:
    """Offline-capable federation bridge with JWT-style capability attestation."""

    def __init__(self, issuer: str = 'dreamco-empire') -> None:
        self.issuer = issuer

    def connect(self, instance: FederatedInstance) -> FederatedSession:
        issued_at = datetime.utcnow()
        expires_at = issued_at + timedelta(hours=1)
        attestation = self._capability_attestation(instance)
        token = self._mint_jwt(instance, issued_at, expires_at, attestation)
        return FederatedSession(instance=instance, jwt_token=token, attestation=attestation, expires_at=expires_at)

    def _capability_attestation(self, instance: FederatedInstance) -> Dict[str, str]:
        material = '|'.join(sorted(instance.capabilities)) + f'|{instance.trust_level:.2f}'
        digest = hashlib.sha256(material.encode()).hexdigest()
        return {'capability_hash': digest, 'trust_band': self._trust_band(instance.trust_level)}

    def _mint_jwt(self, instance: FederatedInstance, issued_at: datetime, expires_at: datetime, attestation: Dict[str, str]) -> str:
        header = self._b64({'alg': 'HS256', 'typ': 'JWT'})
        payload = self._b64({
            'iss': self.issuer,
            'aud': instance.url,
            'iat': int(issued_at.timestamp()),
            'exp': int(expires_at.timestamp()),
            'caps': instance.capabilities,
            'trust': instance.trust_level,
            'att': attestation,
        })
        signing_key = instance.public_key.encode()
        signature = hmac.new(signing_key, f'{header}.{payload}'.encode(), hashlib.sha256).digest()
        return f'{header}.{payload}.{base64.urlsafe_b64encode(signature).decode().rstrip("=")}'

    @staticmethod
    def _trust_band(level: float) -> str:
        if level >= 0.85:
            return 'high'
        if level >= 0.60:
            return 'medium'
        return 'low'

    @staticmethod
    def _b64(obj: Mapping[str, object]) -> str:
        raw = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip('=')
