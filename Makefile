PYTHON ?= python3
.PHONY: test-all test-contracts test-stages test-ci-tools test-repair-stage compile build-sandbox test-sandbox-integration test-report
test-all: test-contracts test-stages test-ci-tools test-repair-stage compile
test-contracts:
	$(PYTHON) -m pytest -q tests/test_pipeline_contracts.py
test-stages:
	$(PYTHON) -m pytest -q tests/test_pipeline_stages.py tests/test_pipeline_sandbox.py tests/test_intake_parser_stage.py tests/test_sandbox_verifier_stage.py
test-ci-tools:
	$(PYTHON) -m pytest -q tests/test_repair_pr_guard.py tests/test_ci_failure_report.py tests/test_repair_hardening_regressions.py
test-repair-stage:
	$(PYTHON) -m pytest -q tests/test_repo_repair_stage.py
compile:
	$(PYTHON) -m compileall -q stages reverse_engineer
build-sandbox:
	docker build --network=default -f stages/05_sandbox_verifier/Dockerfile -t dreamco-verifier:local .
test-sandbox-integration:
	DREAMCO_RUN_ROOTLESS_DOCKER_TESTS=1 $(PYTHON) -m pytest -q tests/test_rootless_docker_integration.py
test-report:
	mkdir -p reports
	PYTEST_ADDOPTS="--json-report --json-report-file=reports/pytest-report.json" $(PYTHON) -m pytest -q tests
