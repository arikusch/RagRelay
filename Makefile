# RagRelay Makefile — compile, test and demo targets

PY ?= python
FIXTURE ?= examples/profiles.json

.PHONY: all build build-py build-go test demo route simulate manifest score clean

all: build

build: build-py build-go ## Compile both halves

build-py: ## Byte-compile the Python package
	$(PY) -m compileall ragrelay

build-go: ## Build the Go scorer/ranker
	cd relay && go build ./... && go vet ./...

test: ## Run the Python test suite
	$(PY) -m pytest tests/ -o addopts=""

demo: build ## Run a full demo against the bundled fixture
	$(PY) -m ragrelay simulate $(FIXTURE)
	@echo ---
	cd relay && go run . -in ../$(FIXTURE) -top 2 -pretty

route: ## Show per-query attempt allocations
	$(PY) -m ragrelay route $(FIXTURE)

simulate: ## Print distribution + latency summary
	$(PY) -m ragrelay simulate $(FIXTURE)

