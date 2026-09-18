# Contributing to RagRelay

Thanks for taking the time to contribute. RagRelay is deliberately small and
dependency-free, and contributions are held to that standard.

## Ground rules

- **Standard library only.** Both the Python package and the Go command must
  build and run with no third-party dependencies. A change that adds a runtime
  dependency will not be merged.
- **Deterministic by default.** No randomness, wall-clock reads, or environment
  lookups in the routing, simulation, or manifest paths. Two runs over the same
  fixture must produce identical output.
- **Offline.** No network calls at build time or run time.
- **Small, focused changes.** One topic per pull request.

## Getting started

```bash
git clone https://github.com/jfrost4/RagRelay.git
cd RagRelay

# Python side
python -m compileall ragrelay
python -m pytest tests/ -o addopts=""     # requires pytest
python -m ragrelay simulate examples/profiles.json

# Go side
cd relay && go build ./... && go vet ./...
```

## Before you open a pull request

1. Run the full test suite (`python -m pytest tests/ -o addopts=""`) and both
   toolchains (`go build ./... && go vet ./...` in `relay/`).
2. Keep the CLI contract stable: subcommand names, flag names, exit codes, and
   manifest fields are public API.
3. If behavior changes, update `CHANGELOG.md` under `[Unreleased]` and any
   affected docs.
4. Reference the fixture you tested with in the pull request description.

## Reporting bugs

Open an issue with the fixture that reproduces the problem (or a minimal
version of it), the exact command you ran, and the output you expected versus
what you saw.
