"""
Fraud Detection module for the Dreamcobots Mining Bot.

Provides:
  - Honeypot detection: flags smart-contract addresses with suspicious
    transfer patterns.
  - Contract verification: validates that a contract address is checksummed,
    non-empty, and has not been flagged in the known-scam registry.
  - Scam pool detection: checks pool URLs against a list of known-bad domains.

All checks are performed locally (no external API calls), using simulated
heuristics suitable for demonstration and unit-testing.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


class FraudDetectionDisabledError(Exception):
    """Raised when fraud-detection features are not available on this tier."""


@dataclass
class FraudCheckResult:
    """Outcome of a single fraud/scam check."""

    passed: bool
    check_type: str          # "honeypot" | "contract" | "pool"
    target: str              # address, URL, or contract being checked
    risk_level: str          # "none" | "low" | "medium" | "high"
    details: str = ""
    flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "passed": self.passed,
            "check_type": self.check_type,
            "target": self.target,
            "risk_level": self.risk_level,
            "details": self.details,
            "flags": self.flags,
        }


# ---------------------------------------------------------------------------
# Built-in known-bad registries (simulated)
# ---------------------------------------------------------------------------

_KNOWN_SCAM_CONTRACTS: Set[str] = {
    "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
    "0x000000000000000000000000000000000000dEaD",
    "0xscam1111111111111111111111111111111111111",
}

_KNOWN_BAD_POOL_DOMAINS: Set[str] = {
    "fakeminingpool.com",
    "scampool.io",
    "honeypotpool.net",
    "fraudpool.org",
}


def _is_valid_eth_address(address: str) -> bool:
    """Basic Ethereum address format check (0x + 40 hex chars)."""
    if not address.startswith("0x"):
        return False
    hex_part = address[2:]
    if len(hex_part) != 40:
        return False
    try:
        int(hex_part, 16)
    except ValueError:
        return False
    return True


def _has_honeypot_pattern(address: str) -> bool:
    """
    Heuristic: addresses ending in a long run of repeating hex digits are
    suspicious (common pattern in toy honeypots).
    """
    hex_part = address[2:].lower() if address.startswith("0x") else address.lower()
    # Flag if last 8+ chars are identical
    if len(hex_part) >= 8 and len(set(hex_part[-8:])) == 1:
        return True
    return False


class FraudDetector:
    """
    Runs fraud-detection checks for mining-related addresses and pool URLs.

    Parameters
    ----------
    enabled : bool
        Whether fraud detection is available on this tier.
    custom_scam_contracts : list[str]
        Additional contract addresses to treat as known scams.
    custom_bad_domains : list[str]
        Additional pool domains to treat as known-bad.
    """

    def __init__(
        self,
        enabled: bool = False,
        custom_scam_contracts: Optional[List[str]] = None,
        custom_bad_domains: Optional[List[str]] = None,
    ):
        self.enabled = enabled
        self._scam_contracts: Set[str] = set(_KNOWN_SCAM_CONTRACTS)
        if custom_scam_contracts:
            self._scam_contracts.update(
                addr.lower() for addr in custom_scam_contracts
            )
        self._bad_domains: Set[str] = set(_KNOWN_BAD_POOL_DOMAINS)
        if custom_bad_domains:
            self._bad_domains.update(d.lower() for d in custom_bad_domains)

    def _require_enabled(self) -> None:
        if not self.enabled:
            raise FraudDetectionDisabledError(
                "Fraud detection requires PRO or ENTERPRISE tier."
            )

    # ------------------------------------------------------------------
    # Public checks
    # ------------------------------------------------------------------

    def check_contract(self, address: str) -> FraudCheckResult:
        """
        Verify that *address* is a legitimate contract address.

        Checks performed:
          1. Valid Ethereum address format.
          2. Not in the known-scam registry.
          3. No honeypot address pattern.
        """
        self._require_enabled()
        flags: List[str] = []

        if not _is_valid_eth_address(address):
            flags.append("invalid_address_format")

        if address.lower() in self._scam_contracts:
            flags.append("known_scam_contract")

        if _has_honeypot_pattern(address):
            flags.append("honeypot_address_pattern")

        if not flags:
            return FraudCheckResult(
                passed=True,
                check_type="contract",
                target=address,
                risk_level="none",
                details="Contract address passed all verification checks.",
            )

        risk_level = "high" if "known_scam_contract" in flags else "medium"
        return FraudCheckResult(
            passed=False,
            check_type="contract",
            target=address,
            risk_level=risk_level,
            details=f"Contract flagged with issues: {', '.join(flags)}.",
            flags=flags,
        )

    def check_honeypot(self, address: str) -> FraudCheckResult:
        """
        Check whether *address* exhibits honeypot characteristics.
        """
        self._require_enabled()
        flags: List[str] = []

        if address.lower() in self._scam_contracts:
            flags.append("known_scam_contract")

        if _has_honeypot_pattern(address):
            flags.append("honeypot_address_pattern")

        if not flags:
            return FraudCheckResult(
                passed=True,
                check_type="honeypot",
                target=address,
                risk_level="none",
                details="No honeypot indicators detected.",
            )

        return FraudCheckResult(
            passed=False,
            check_type="honeypot",
            target=address,
            risk_level="high",
            details=f"Honeypot indicators found: {', '.join(flags)}.",
            flags=flags,
        )

    def check_pool(self, pool_url: str) -> FraudCheckResult:
        """
        Check whether *pool_url* is associated with a known-scam domain.
        """
        self._require_enabled()
        flags: List[str] = []

        # Extract domain from URL (simple heuristic)
        domain = pool_url.lower()
        for prefix in ("https://", "http://", "stratum+tcp://", "stratum+ssl://"):
            if domain.startswith(prefix):
                domain = domain[len(prefix):]
                break
        domain = domain.split("/")[0].split(":")[0]

        if domain in self._bad_domains:
            flags.append("known_scam_domain")

        if not flags:
            return FraudCheckResult(
                passed=True,
                check_type="pool",
                target=pool_url,
                risk_level="none",
                details="Pool URL not found in the known-scam registry.",
            )

        return FraudCheckResult(
            passed=False,
            check_type="pool",
            target=pool_url,
            risk_level="high",
            details=f"Pool domain '{domain}' is in the known-scam registry.",
            flags=flags,
        )

    def run_all_checks(
        self,
        contract_address: Optional[str] = None,
        pool_url: Optional[str] = None,
    ) -> List[FraudCheckResult]:
        """
        Run all applicable fraud checks and return results.

        Parameters
        ----------
        contract_address : str, optional
            Contract address to check (contract + honeypot checks).
        pool_url : str, optional
            Pool URL to validate against the scam registry.
        """
        self._require_enabled()
        results: List[FraudCheckResult] = []

        if contract_address:
            results.append(self.check_contract(contract_address))
            results.append(self.check_honeypot(contract_address))

        if pool_url:
            results.append(self.check_pool(pool_url))

        return results
