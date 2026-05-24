# DreamCo OS — Developer Makefile
# Usage: make <target>

.PHONY: help install install-dev lint format test test-unit test-integration \
        test-e2e coverage audit run docker docker-prod k8s-apply clean

PYTHON := python3
PIP := pip
PYTEST := $(PYTHON) -m pytest
COVERAGE := $(PYTHON) -m pytest --cov=python_bots --cov=dreamco_sdk --cov-report=term-missing

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Installation ─────────────────────────────────────────────────────────────
install:  ## Install production dependencies
	$(PIP) install -r requirements.txt

install-dev:  ## Install all dependencies including dev tools
	$(PIP) install -r requirements.txt pip-audit flake8 black isort

# ─── Code Quality ──────────────────────────────────────────────────────────────
lint:  ## Run flake8 linter
	flake8 python_bots/ dreamco_sdk/ dreamco_mcp_server.py --max-line-length=120 --ignore=E501,W503 || true

format:  ## Auto-format with black + isort
	black python_bots/ dreamco_sdk/ dreamco_mcp_server.py bots/coding/ --line-length=100
	isort python_bots/ dreamco_sdk/ dreamco_mcp_server.py bots/coding/

# ─── Testing ───────────────────────────────────────────────────────────────────
test:  ## Run all tests
	$(PYTEST) tests/ -q --tb=short

test-unit:  ## Run unit tests only
	$(PYTEST) tests/unit/ -v --tb=short

test-integration:  ## Run integration tests only
	$(PYTEST) tests/integration/ -v --tb=short

test-e2e:  ## Run end-to-end tests only
	$(PYTEST) tests/e2e/ -v --tb=short

coverage:  ## Run tests with coverage report
	$(COVERAGE) --cov-report=html tests/
	@echo "Coverage report: htmlcov/index.html"

# ─── Security ──────────────────────────────────────────────────────────────────
audit:  ## Run pip-audit security scan
	pip-audit --requirement requirements.txt

framework-check:  ## Validate bot framework compliance
	$(PYTHON) tools/check_bot_framework.py

# ─── Run ───────────────────────────────────────────────────────────────────────
run:  ## Start the DreamCo OS orchestrator API (requires uvicorn)
	uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

run-mcp:  ## Start the MCP server on stdio
	$(PYTHON) dreamco_mcp_server.py

demo:  ## Run all demo scenarios
	$(PYTHON) demo/demo_1_basic_bot.py
	$(PYTHON) demo/demo_2_orchestrated_bots.py
	$(PYTHON) demo/demo_3_mcp_interop.py

# ─── Docker ────────────────────────────────────────────────────────────────────
docker:  ## Build Docker image (development)
	docker build -t dreamco-os:dev .

docker-run:  ## Run Docker compose (development)
	docker compose up --build

docker-prod:  ## Run Docker compose (production)
	docker compose -f docker-compose.prod.yml up -d

docker-down:  ## Stop all Docker services
	docker compose down
	docker compose -f docker-compose.prod.yml down

# ─── Kubernetes ────────────────────────────────────────────────────────────────
k8s-apply:  ## Apply Kubernetes manifests
	kubectl apply -f k8s/

k8s-status:  ## Check Kubernetes deployment status
	kubectl get pods,services,hpa -n dreamco

k8s-logs:  ## Tail DreamCo OS logs from Kubernetes
	kubectl logs -f -l app=dreamco-os -n dreamco

# ─── Cleanup ───────────────────────────────────────────────────────────────────
clean:  ## Remove build artifacts, caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage coverage.xml dist build *.egg-info
	rm -f .dreamco_state.db dreamco_audit.jsonl

# ─── Registry ──────────────────────────────────────────────────────────────────
compile-registry:  ## Compile bot registry from category files
	$(PYTHON) tools/compile_bot_registry.py

check-registry:  ## Validate bot registry (dry run)
	$(PYTHON) tools/compile_bot_registry.py --check
