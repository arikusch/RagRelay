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
