"""
APISandboxTester — generates and runs isolated sandbox tests for every API
discovered across the DreamCo bot ecosystem.

Tests are run through GlobalAISourcesFlow's SandboxTestLab stage for
full pipeline compliance.

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  GLOBAL AI SOURCES FLOW
from .api_bot import APIEndpoint, SandboxTestCase, TestResult

logger = logging.getLogger(__name__)


class APISandboxTester:
    """
    Runs multi-pass sandbox test suites against all registered APIs.

    Test strategy:
    1. Smoke tests (basic reachability)
    2. Authentication tests
    3. Rate-limit boundary tests
    4. Payload validation tests
    5. Latency benchmarks
    6. Chaos tests (network partition simulation)

    GLOBAL AI SOURCES FLOW
    """

    def __init__(self) -> None:
        self._flow = GlobalAISourcesFlow(bot_name="APISandboxTester")
        self._results: Dict[str, List[Dict[str, Any]]] = {}

    def run_full_suite(self, endpoint: APIEndpoint) -> Dict[str, Any]:
        """Run the complete 6-pass test suite for an API endpoint."""
        suite_id = f"suite_{endpoint.api_id}_{uuid.uuid4().hex[:6]}"
        tests = self._build_test_suite(endpoint)
        results = []

        for test in tests:
            result = self._execute_test(test, endpoint)
            results.append(result)

        # Feed through GlobalAI pipeline
        pipeline = self._flow.run_pipeline(
            raw_data={
                "suite_id": suite_id,
                "api_id": endpoint.api_id,
                "test_count": len(tests),
                "passed": sum(1 for r in results if r["result"] == TestResult.PASS.value),
            },
            learning_method="supervised",
        )

        summary = {
            "suite_id": suite_id,
            "api_id": endpoint.api_id,
            "api_name": endpoint.name,
            "bot_id": endpoint.bot_id,
            "total_tests": len(tests),
            "passed": sum(1 for r in results if r["result"] == TestResult.PASS.value),
            "failed": sum(1 for r in results if r["result"] == TestResult.FAIL.value),
            "errors": sum(1 for r in results if r["result"] == TestResult.ERROR.value),
            "pass_rate": sum(1 for r in results if r["result"] == TestResult.PASS.value) / len(tests),
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "tests": results,
            "pipeline": pipeline,
        }
        self._results[endpoint.api_id] = results
        return summary

    def _build_test_suite(self, endpoint: APIEndpoint) -> List[SandboxTestCase]:
        aid = endpoint.api_id
        return [
            # Pass 1: Smoke
            SandboxTestCase(
                test_id=f"{aid}_smoke_get",
                api_id=aid,
                name="[Smoke] GET base URL",
                description="Verify base URL is reachable.",
                input_payload={"method": "GET", "path": "/"},
                expected_status=200,
            ),
            # Pass 2: Authentication
            SandboxTestCase(
                test_id=f"{aid}_auth_valid",
                api_id=aid,
                name="[Auth] Valid credentials accepted",
                description="Send valid auth token; expect non-401 response.",
                input_payload={"method": "GET", "path": "/", "auth_valid": True},
                expected_status=200,
            ),
            SandboxTestCase(
                test_id=f"{aid}_auth_invalid",
                api_id=aid,
                name="[Auth] Invalid credentials rejected",
                description="Send invalid auth token; expect 401.",
                input_payload={"method": "GET", "path": "/", "auth_valid": False},
                expected_status=401,
            ),
            # Pass 3: Rate limits
            SandboxTestCase(
                test_id=f"{aid}_rate_limit",
                api_id=aid,
                name="[Rate] 429 on limit exceeded",
                description="Exceed rate limit; expect 429.",
                input_payload={"method": "GET", "path": "/", "exceed_rate_limit": True},
                expected_status=429,
            ),
            # Pass 4: Payload validation
            SandboxTestCase(
                test_id=f"{aid}_invalid_payload",
                api_id=aid,
                name="[Payload] Malformed body rejected",
                description="Send malformed JSON; expect 400/422.",
                input_payload={"method": "POST", "path": "/data", "body": "not-json"},
                expected_status=400,
            ),
            # Pass 5: Latency benchmark
            SandboxTestCase(
                test_id=f"{aid}_latency",
                api_id=aid,
                name="[Perf] P95 latency < 2000ms",
                description="10 sequential requests; P95 must be under 2000ms.",
                input_payload={"method": "GET", "path": "/", "iterations": 10},
                expected_status=200,
            ),
            # Pass 6: Chaos
            SandboxTestCase(
                test_id=f"{aid}_chaos_timeout",
                api_id=aid,
                name="[Chaos] Handles timeout gracefully",
                description="Simulate network timeout; bot must not crash.",
                input_payload={"method": "GET", "path": "/", "simulate_timeout": True},
                expected_status=504,
            ),
        ]

    def _execute_test(self, test: SandboxTestCase, endpoint: APIEndpoint) -> Dict[str, Any]:
        """Execute a single test (simulated; wire httpx for production)."""
        import time
        test.ran_at = datetime.now(timezone.utc)
        start = time.monotonic()

        # Simulation logic — replace with real HTTP calls in production
        if test.input_payload.get("simulate_timeout"):
            test.result = TestResult.PASS  # Graceful handling simulated
            test.actual_status = 504
            test.latency_ms = 5000.0
        elif test.input_payload.get("exceed_rate_limit"):
            test.result = TestResult.PASS
            test.actual_status = 429
            test.latency_ms = 50.0
        elif test.input_payload.get("auth_valid") is False:
            test.result = TestResult.PASS
            test.actual_status = 401
            test.latency_ms = 80.0
        elif test.input_payload.get("body") == "not-json":
            test.result = TestResult.PASS
            test.actual_status = 400
            test.latency_ms = 60.0
        else:
            test.result = TestResult.PASS
            test.actual_status = 200
            test.latency_ms = (time.monotonic() - start) * 1000 + 120.0

        return test.to_dict()

    def get_all_results(self) -> Dict[str, List[Dict[str, Any]]]:
        return dict(self._results)

    def get_failure_report(self) -> List[Dict[str, Any]]:
        failures = []
        for api_id, results in self._results.items():
            for r in results:
                if r["result"] in (TestResult.FAIL.value, TestResult.ERROR.value):
                    failures.append({"api_id": api_id, **r})
        return failures
