PYTHON ?= python3
.PHONY: test-all test-contracts test-stages compile build-sandbox
test-all: test-contracts test-stages compile
test-contracts:
	$(PYTHON) -m pytest -q tests/test_pipeline_contracts.py
test-stages:
	$(PYTHON) -m pytest -q tests/test_pipeline_stages.py tests/test_pipeline_sandbox.py
compile:
	$(PYTHON) -m compileall -q stages
build-sandbox:
	docker build --network=default -f stages/05_sandbox_verifier/Dockerfile -t dreamco-verifier:local .
