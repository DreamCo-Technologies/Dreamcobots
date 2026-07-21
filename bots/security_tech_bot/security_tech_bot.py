"""
Dreamcobots Security Tech Bot — tier-aware vulnerability scanning and security analysis.

Usage
-----
    from security_tech_bot import SecurityTechBot
    from tiers import Tier

    bot = SecurityTechBot(tier=Tier.FREE)
    result = bot.scan_vulnerabilities("example.com")
    print(result)
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path

import importlib.util as _ilu
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_spec = _ilu.spec_from_file_location("_security_tiers", os.path.join(_THIS_DIR, "tiers.py"))
_security_tiers = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_security_tiers)
SECURITY_FEATURES = _security_tiers.SECURITY_FEATURES
SCAN_LIMITS = _security_tiers.SCAN_LIMITS
get_security_tier_info = _security_tiers.get_security_tier_info


class SecurityTechBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class SecurityTechBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class SecurityTechBot:
    """
    Tier-aware security vulnerability scanning and analysis bot.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling scan limits and feature availability.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._scan_count: int = 0

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def scan_vulnerabilities(self, target: str, scan_type: str = "basic") -> dict:
        """
        Scan a target for vulnerabilities.

        Parameters
        ----------
        target : str
            Target URL, IP, or system identifier.
        scan_type : str
            "basic" (all tiers) or "full" (PRO/ENTERPRISE only).

        Returns
        -------
        dict
        """
        self._check_request_limit()
        scan_limit = SCAN_LIMITS[self.tier.value]
        if scan_limit is not None and self._scan_count >= scan_limit:
            raise SecurityTechBotTierError(
                f"Scan limit of {scan_limit}/month reached on the {self.config.name} tier. "
                "Upgrade to run more scans."
            )
        if scan_type == "full" and self.tier == Tier.FREE:
            raise SecurityTechBotTierError(
                "Full vulnerability assessment requires PRO or ENTERPRISE tier."
            )
        self._request_count += 1
        self._scan_count += 1
        findings = [
            {
                "cve_id": "CVE-2024-MOCK1",
                "severity": "medium",
                "description": f"Mock vulnerability found in {target}",
                "remediation": "Apply latest security patches.",
            }
        ]
        if scan_type == "full":
            findings.append({
                "cve_id": "CVE-2024-MOCK2",
                "severity": "high",
                "description": f"Advanced vulnerability detected in {target}",
                "remediation": "Upgrade affected component to version 2.0+.",
            })
        return {
            "target": target,
            "scan_type": scan_type,
            "findings": findings,
            "total_findings": len(findings),
            "scans_used_this_month": self._scan_count,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def check_password_strength(self, password: str) -> dict:
        """
        Check the strength of a password.

        Parameters
        ----------
        password : str
            The password to evaluate.

        Returns
        -------
        dict
            Score (0-100), entropy, and recommendations.
        """
        self._check_request_limit()
        self._request_count += 1
        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        charset_size = (
            (26 if has_upper else 0)
            + (26 if has_lower else 0)
            + (10 if has_digit else 0)
            + (32 if has_special else 0)
        )
        entropy = round(length * math.log2(max(charset_size, 1)), 2)
        score = min(100, int((length / 20) * 40 + (entropy / 100) * 60))
        recommendations = []
        if length < 12:
            recommendations.append("Use at least 12 characters.")
        if not has_upper:
            recommendations.append("Add uppercase letters.")
        if not has_lower:
            recommendations.append("Add lowercase letters.")
        if not has_digit:
            recommendations.append("Add numbers.")
        if not has_special:
            recommendations.append("Add special characters (e.g., !@#$%).")
        if score >= 80:
            strength = "Strong"
        elif score >= 50:
            strength = "Moderate"
        else:
            strength = "Weak"
        return {
            "score": score,
            "strength": strength,
            "entropy_bits": entropy,
            "recommendations": recommendations,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def audit_dependencies(self, dependencies: list[dict]) -> dict:
        """
        Audit a list of dependencies for known CVEs.  Requires PRO or ENTERPRISE tier.

        Parameters
        ----------
        dependencies : list[dict]
            List of dicts with keys "name" and "version".

        Returns
        -------
        dict
        """
        self._check_request_limit()
        if self.tier == Tier.FREE:
            raise SecurityTechBotTierError(
                "Dependency auditing requires PRO or ENTERPRISE tier."
            )
        self._request_count += 1
        vulnerable = []
        for dep in dependencies:
            if dep.get("version", "").startswith("1."):
                vulnerable.append({
                    "name": dep["name"],
                    "version": dep["version"],
                    "cve_id": "CVE-2024-MOCK-DEP",
                    "severity": "high",
                    "fix_version": "2.0.0",
                })
        return {
            "total_checked": len(dependencies),
            "vulnerable": vulnerable,
            "clean": len(dependencies) - len(vulnerable),
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def generate_security_report(self, scan_results: list[dict]) -> dict:
        """
        Generate a comprehensive security report.  Requires ENTERPRISE tier.

        Parameters
        ----------
        scan_results : list[dict]
            List of scan result dicts from scan_vulnerabilities().

        Returns
        -------
        dict
        """
        self._check_request_limit()
        if self.tier != Tier.ENTERPRISE:
            raise SecurityTechBotTierError(
                "Security report generation is only available on the ENTERPRISE tier."
            )
        self._request_count += 1
        all_findings = []
        for result in scan_results:
            all_findings.extend(result.get("findings", []))
        severity_counts: dict[str, int] = {}
        for finding in all_findings:
            sev = finding.get("severity", "unknown")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        return {
            "report_id": f"SEC-RPT-{self._request_count:04d}",
            "total_scans": len(scan_results),
            "total_findings": len(all_findings),
            "severity_breakdown": severity_counts,
            "executive_summary": (
                f"[Mock] Analyzed {len(scan_results)} scan(s) with "
                f"{len(all_findings)} total finding(s)."
            ),
            "recommendations": [
                "Apply all critical and high-severity patches immediately.",
                "Schedule a follow-up scan in 30 days.",
                "Enable continuous monitoring for real-time alerts.",
            ],
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a description of the current tier."""
        info = get_security_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        scan_limit = (
            "Unlimited"
            if info["scan_limit"] is None
            else str(info["scan_limit"])
        )
        lines = [
            f"=== {info['name']} Security Tech Bot Tier ===",
            f"Price      : ${info['price_usd_monthly']:.2f}/month",
            f"Requests   : {limit}/month",
            f"Scan limit : {scan_limit}/month",
            f"Support    : {info['support_level']}",
            "",
            "Features:",
        ]
        for feat in info["security_features"]:
            lines.append(f"  ✓ {feat}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg
        current_feats = set(SECURITY_FEATURES[self.tier.value])
        new_feats = [f for f in SECURITY_FEATURES[next_cfg.tier.value] if f not in current_feats]
        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features:",
        ]
        for feat in new_feats:
            lines.append(f"  + {feat}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing SecurityTechBot or contact support."
        )
        output = "\n".join(lines)
        print(output)
        return output

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise SecurityTechBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))


if __name__ == "__main__":
    bot = SecurityTechBot(tier=Tier.FREE)
    bot.describe_tier()
    result = bot.scan_vulnerabilities("example.com")
    print(result)
