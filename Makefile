SHELL := /bin/bash
PYTHON ?= python3

.PHONY: test lint validate

test:
	$(PYTHON) -m pytest -q

lint:
	@find tools -type f -print0 | while IFS= read -r -d '' f; do if head -n1 "$$f" | grep -q 'bash'; then bash -n "$$f"; fi; done
	@if command -v shellcheck >/dev/null 2>&1; then find tools -type f -print0 | while IFS= read -r -d '' f; do if head -n1 "$$f" | grep -q 'bash'; then shellcheck "$$f"; fi; done; else echo 'shellcheck not installed; syntax-only lint completed'; fi
	@$(PYTHON) -m compileall -q tools tests

validate: lint test
