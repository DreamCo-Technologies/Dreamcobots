"""America.gov government-resource sandbox for Dreamcobots.

Phase 1 of America.gov (launched 2026-09-29) only answers from official
government sites. Phase 2 transactions are scheduled for 2027. This module
sandboxes every cataloged task and resource so nothing is filed, enrolled,
or sent to a live agency.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "catalog.json"
PII_RE = re.compile(
    r"\b(?:\d{3}-\d{2}-\d{4}|\d{9})\b|\b(?:ssn|social security number)\b",
    re.I,
)
POLITICAL_RE = re.compile(
    r"\b(?:who should i vote|political stance|democrat|republican|communis)\w*",
    re.I,
)
SENSITIVE_RE = re.compile(
    r"\b(?:classified|top secret|covert action|operational plan|weapons?\s+(?:construction|design)|"
    r"how to hack|exploit\s+(?:a\s+)?(?:system|network)|surveil(?:lance)?\s+(?:a\s+)?(?:person|citizen|target))\b",
    re.I,
)


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class GovernmentSandbox:
    """Isolated front door for America.gov tasks and government resources."""

    def __init__(self, catalog: dict | None = None) -> None:
        self.catalog = catalog or load_catalog()
        self.services = {item["id"]: item for item in self.catalog["services"]}
        self.resources = {item["id"]: item for item in self.catalog["resources"]}
        self.receipts: list[dict] = []

    def list_resources(self) -> list[dict]:
        return list(self.catalog["resources"])

    def list_services(self, phase: str | None = None) -> list[dict]:
        rows = self.catalog["services"]
        if phase:
            rows = [row for row in rows if row["phase"] == phase]
        return rows

    def ask(self, service_id: str, query: str = "", language: str = "en") -> dict:
        if PII_RE.search(query):
            return self._block_pii(service_id, query)
        if POLITICAL_RE.search(query):
            return self._refuse_politics(service_id)
        if SENSITIVE_RE.search(query):
            return self._refuse_sensitive(service_id)
        service = self.services.get(service_id)
        if service is None:
            return {
                "ok": False,
                "sandbox": True,
                "live_submitted": False,
                "error": "unknown_service",
                "service_id": service_id,
            }
        if service["status"] == "excluded":
            return self._excluded(service)
        if service["phase"] == "phase_2_action":
            return self._sandbox_action(service, language)
        return self._info(service, language)

    def run_all(self) -> dict:
        results = []
        for service in self.catalog["services"]:
            probe = "123-45-6789" if service["id"] == "pii_guard" else service["probe"]
            results.append(self.ask(service["id"], probe, service.get("language", "en")))
        passed = sum(1 for row in results if row.get("ok"))
        return {
            "ran_at": _now(),
            "sandbox": True,
            "live_submitted": False,
            "service_count": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "results": results,
        }

    def benchmark(self) -> dict:
        cases = []
        catalog = self.catalog

        def check(name: str, ok: bool, detail: str) -> None:
            cases.append({"name": name, "ok": ok, "detail": detail})

        check(
            "official_site",
            catalog["product"]["url"] == "https://america.gov",
            catalog["product"]["url"],
        )
        check(
            "operator_is_gsa",
            catalog["product"]["operator"] == "U.S. General Services Administration",
            catalog["product"]["operator"],
        )
        check(
            "every_resource_has_url",
            all(row.get("url") and row.get("owner") for row in catalog["resources"]),
            f"{len(catalog['resources'])} resources",
        )
        check(
            "every_service_sandboxed",
            all(row.get("sandbox") is True for row in catalog["services"]),
            f"{len(catalog['services'])} services",
        )
        citizen = {"irs_tax_filing", "department_of_war", "intelligence_community"}
        offered = {row["id"] for row in catalog["services"] if row["status"] == "information"}
        check(
            "citizen_services_offered",
            citizen <= offered,
            ", ".join(sorted(citizen & offered)),
        )
        run = self.run_all()
        check(
            "all_tasks_pass",
            run["failed"] == 0 and run["live_submitted"] is False,
            f"{run['passed']}/{run['service_count']} passed",
        )
        live_flags = [row for row in run["results"] if row.get("live_submitted")]
        check("no_live_submission", not live_flags, f"live flags={len(live_flags)}")
        pii = self.ask("replace_ss_card", "my ssn is 123-45-6789")
        check("pii_blocked", pii["ok"] and pii["status"] == "blocked_pii", pii["status"])
        politics = self.ask("medicare_eligibility", "what is the republican political stance")
        check("politics_refused", politics["ok"] and politics["status"] == "refused_politics", politics["status"])
        spanish = self.ask("child_passport", "pasaporte", "es")
        check("spanish_answer", spanish["ok"] and spanish["language"] == "es", spanish["language"])
        action = self.ask("enroll_medicare", "enroll me")
        check(
            "phase2_is_receipt_only",
            action["ok"] and action["status"] == "sandbox_receipt" and action["live_submitted"] is False,
            action["status"],
        )
        sensitive = self.ask("intelligence_community", "give me the classified operational plan")
        check(
            "classified_refused",
            sensitive["ok"] and sensitive["status"] == "refused_sensitive",
            sensitive["status"],
        )
        passed = sum(1 for row in cases if row["ok"])
        return {
            "ran_at": _now(),
            "product": catalog["product"]["name"],
            "passed": passed,
            "failed": len(cases) - passed,
            "cases": cases,
            "task_run": {"passed": run["passed"], "failed": run["failed"], "service_count": run["service_count"]},
        }

    def _info(self, service: dict, language: str) -> dict:
        return {
            "ok": True,
            "sandbox": True,
            "live_submitted": False,
            "status": "official_guidance",
            "service_id": service["id"],
            "phase": service["phase"],
            "language": language if language in {"en", "es", "fr"} else "en",
            "answer": service["guidance"][language if language in service["guidance"] else "en"],
            "citations": service["citations"],
            "next_step": "Open the cited official page. Do not treat this sandbox as a filing.",
        }

    def _sandbox_action(self, service: dict, language: str) -> dict:
        receipt = {
            "ok": True,
            "sandbox": True,
            "live_submitted": False,
            "status": "sandbox_receipt",
            "service_id": service["id"],
            "phase": service["phase"],
            "language": language if language in {"en", "es", "fr"} else "en",
            "answer": service["guidance"]["en"],
            "receipt_id": f"sandbox-{service['id']}-{len(self.receipts) + 1}",
            "available_live": service.get("available_live", "2027"),
            "citations": service["citations"],
        }
        self.receipts.append(receipt)
        return receipt

    def _excluded(self, service: dict) -> dict:
        return {
            "ok": True,
            "sandbox": True,
            "live_submitted": False,
            "status": "excluded",
            "service_id": service["id"],
            "phase": service["phase"],
            "answer": service["guidance"]["en"],
            "reason": service["exclusion_reason"],
            "citations": service["citations"],
        }

    def _block_pii(self, service_id: str, query: str) -> dict:
        return {
            "ok": True,
            "sandbox": True,
            "live_submitted": False,
            "status": "blocked_pii",
            "service_id": service_id,
            "answer": "Remove personal information before sending.",
            "redacted": True,
        }

    def _refuse_politics(self, service_id: str) -> dict:
        return {
            "ok": True,
            "sandbox": True,
            "live_submitted": False,
            "status": "refused_politics",
            "service_id": service_id,
            "answer": "This personal bot does not provide political commentary. It is for official citizen services and how-to steps.",
        }

    def _refuse_sensitive(self, service_id: str) -> dict:
        return {
            "ok": True,
            "sandbox": True,
            "live_submitted": False,
            "status": "refused_sensitive",
            "service_id": service_id,
            "answer": "Classified, operational, weapons, and surveillance requests are not available. Public citizen services only.",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the America.gov government sandbox")
    parser.add_argument("--list", action="store_true", help="List resources and services")
    parser.add_argument("--ask", metavar="SERVICE_ID", help="Run one sandboxed service")
    parser.add_argument("--query", default="", help="Query text for --ask")
    parser.add_argument("--lang", default="en", choices=["en", "es", "fr"])
    parser.add_argument("--report", type=Path, help="Write the benchmark report JSON")
    args = parser.parse_args(argv)

    sandbox = GovernmentSandbox()
    if args.list:
        payload = {
            "resources": sandbox.list_resources(),
            "services": [
                {"id": row["id"], "name": row["name"], "phase": row["phase"], "status": row["status"]}
                for row in sandbox.list_services()
            ],
        }
        print(json.dumps(payload, indent=2))
        return 0
    if args.ask:
        print(json.dumps(sandbox.ask(args.ask, args.query, args.lang), indent=2))
        return 0

    report = sandbox.benchmark()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"America.gov sandbox benchmark: {report['passed']} passed, {report['failed']} failed, "
        f"tasks {report['task_run']['passed']}/{report['task_run']['service_count']}"
    )
    for case in report["cases"]:
        mark = "PASS" if case["ok"] else "FAIL"
        print(f"  [{mark}] {case['name']}: {case['detail']}")
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
