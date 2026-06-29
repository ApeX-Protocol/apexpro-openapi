# Single source of truth for what "tests pass" means in this repo.
# CI and the local pre-push hook both call `make test` — keeping the
# definitions here means they cannot drift apart.

PYTHON ?= python3
PIP    ?= $(PYTHON) -m pip
PYTEST ?= $(PYTHON) -m pytest

# Default target shown by `make` with no args.
.DEFAULT_GOAL := help

.PHONY: help setup install install-hooks test test-offline ci clean

help: ## Show this help.
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make <target>\n\nTargets:\n"} \
	      /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' \
	      $(MAKEFILE_LIST)

setup: install install-hooks ## One-shot setup for a fresh checkout.
	@echo ""
	@echo "Setup complete. Try: make test"

install: ## Install the SDK in editable mode plus demo + test extras.
	$(PIP) install -e ".[demos,tests]"

install-hooks: ## Wire git to use the hooks shipped in .githooks/.
	@if [ ! -d .git ]; then \
	  echo "Not a git checkout — skipping hook install."; \
	  exit 0; \
	fi
	git config core.hooksPath .githooks
	@echo "git hooks now live in .githooks/"

test: test-offline ## Run the full offline test gate (default for CI + pre-push).

test-offline: ## Offline tests only — no network, no API keys required.
	$(PYTEST) tests/test_demos_smoke.py tests/test_sdk_regressions.py -q

ci: test ## Alias used by CI workflows.

clean: ## Remove build artefacts and Python caches.
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
