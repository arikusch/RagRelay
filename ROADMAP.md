# Roadmap

## Completed

- [x] **Deterministic scoring engine** — cosine + topic-overlap + latency blend
  with stable ranking (`ragrelay/routing.py:score_query`, mirrored in
  `relay/main.go`).
- [x] **Largest-remainder attempt allocation** — capacity-bounded, drift-free
  splits across the top `fanout` workers (`ragrelay/routing.py:route`).
- [x] **Simulation aggregation** — route distribution, by-region rollup, mean and
  p95 latency (`ragrelay/simulate.py:simulate`).
- [x] **Content-addressed run manifests** — reproducible `run_id` from a
  SHA-256 digest of canonical inputs (`ragrelay/manifest.py:build_manifest`).

## Planned

- [ ] Multi-round simulation with attempt retries on simulated failures.
- [ ] Pluggable scoring blends selectable from the CLI.
- [ ] Sticky-session routing that pins a query family to a region.
- [ ] Manifest diffing subcommand with a human-readable delta report.
- [ ] Optional CSV export of the affinity matrix.
