# Changelog

All notable changes to RagRelay are documented here. This project adheres to
semantic versioning.

## [5.0.2] - 2026-10-06

### Fixed
- `relay` scorer no longer reports a zero cosine when one vector is a prefix of
  the other; the shared prefix is scored as before.

## [4.0.0] - 2026-09-22

### Changed
- Manifest `run_id` is now computed over the canonical fixture plus fan-out and
  version string, so a scoring change invalidates cached manifests.
- CLI `manifest` output writes a trailing newline in both stdout and `--out`
  modes.

## [3.1.0] - 2026-08-25

### Added
- `--fanout` is honored by `route` and `simulate` for every fixture shape,
  including queries whose attempt counts exceed the summed capacity.
- README recipes for diffing two capacity plans via manifests.

## [2.3.0] - 2026-07-21

### Added
- Per-region attempt rollup in the simulation summary.
- Go scorer `-top` flag to limit ranked rows per query.

## [1.0.0] - 2026-06-09

### Added
- Stable CLI contract: `route`, `score`, `simulate`, `manifest` subcommands and
  the `--fanout` / `--out` flags.
- `RunManifest` with the documented field set, covered by tests.

### Changed
- Latency model applies a capacity-pressure surcharge and reports both mean and
  p95 (linear-interpolated percentile).

## [0.9.0] - 2025-11-25

### Added
- Cross-check workflow: run the Python engine and the Go scorer over the same
  fixture and compare rankings.

## [0.8.0] - 2024-12-03

### Added
- Capacity-bounded allocation: attempts never exceed a worker's `capacity`.

### Changed
- Remainder ties resolve on rank index so allocations stay byte-stable.

## [0.7.0] - 2023-11-14

### Added
