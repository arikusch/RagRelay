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
