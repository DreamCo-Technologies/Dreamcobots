#!/usr/bin/env python3
"""Run generated bot smoke tests without requiring pytest."""

from __future__ import annotations

import importlib.util
import inspect
import json
import sys
import tempfile
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = ROOT / "tests" / "generated_bot_smoke"
REPORT_DIR = ROOT / "reports"


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_test_function(test_function) -> None:
    signature = inspect.signature(test_function)
    unsupported = [name for name in signature.parameters if name != "tmp_path"]
    if unsupported:
        raise TypeError(
            f"unsupported smoke test fixture(s): {', '.join(sorted(unsupported))}"
        )

    if "tmp_path" not in signature.parameters:
        test_function()
        return

    with tempfile.TemporaryDirectory(prefix="dreamco-smoke-") as tmp_dir:
        test_function(tmp_path=Path(tmp_dir))


def main() -> int:
    failures: list[dict[str, str]] = []
    tests = sorted(TEST_DIR.glob("test_*.py"))
    for path in tests:
        try:
            module = load_module(path)
            test_functions = [
                getattr(module, name)
                for name in dir(module)
                if name.startswith("test_") and callable(getattr(module, name))
            ]
            if not test_functions:
                raise AssertionError("no test functions found")
            for test_function in test_functions:
                run_test_function(test_function)
        except Exception as exc:  # pragma: no cover - reports external failures
            failures.append(
                {
                    "test": str(path.relative_to(ROOT)),
                    "error": str(exc),
                    "traceback": traceback.format_exc(limit=8),
                }
            )

    report = {
        "schema": "dreamco.generated_bot_smoke.v1",
        "tests_discovered": len(tests),
        "tests_passed": len(tests) - len(failures),
        "tests_failed": len(failures),
        "failures": failures,
    }
    REPORT_DIR.mkdir(exist_ok=True)
    (REPORT_DIR / "generated_bot_smoke_results.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({k: report[k] for k in report if k != "failures"}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
