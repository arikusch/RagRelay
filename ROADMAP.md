# Roadmap

## Completed

- [x] **Deterministic scoring engine** — cosine + topic-overlap + latency blend
  with stable ranking (`ragrelay/routing.py:score_query`, mirrored in
  `relay/main.go`).
- [x] **Largest-remainder attempt allocation** — capacity-bounded, drift-free
  splits across the top `fanout` workers (`ragrelay/routing.py:route`).
- [x] **Simulation aggregation** — route distribution, by-region rollup, mean and
