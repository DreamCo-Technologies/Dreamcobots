PYTHON ?= python3
.PHONY: test-all test-contracts test-stages compile build-sandbox test-sandbox-integration
test-all: test-contracts test-stages compile
test-contracts:
	$(PYTHON) -m pytest -q tests/test_pipeline_contracts.py
test-stages:
	$(PYTHON) -m pytest -q tests/test_pipeline_stages.py tests/test_pipeline_sandbox.py
compile:
	$(PYTHON) -m compileall -q stages reverse_engineer
build-sandbox:
	docker build --network=default -f stages/05_sandbox_verifier/Dockerfile -t dreamco-verifier:local .
test-sandbox-integration:
	DREAMCO_RUN_ROOTLESS_DOCKER_TESTS=1 $(PYTHON) -m pytest -q tests/test_rootless_docker_integration.py
