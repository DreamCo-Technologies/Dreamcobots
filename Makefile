PYTHON ?= python3
.PHONY: test-all test-contracts test-stages compile
test-all: test-contracts test-stages compile
test-contracts:
	$(PYTHON) -m pytest -q tests/test_pipeline_contracts.py
test-stages:
	$(PYTHON) -m pytest -q tests/test_pipeline_stages.py
compile:
	$(PYTHON) -m compileall -q stages
