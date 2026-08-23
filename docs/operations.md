# Operations reference

## Python CLI

```
ragrelay route     <fixture> [--fanout N]
ragrelay score     <fixture>
ragrelay simulate  <fixture> [--fanout N]
ragrelay manifest  <fixture> [--fanout N] [--out PATH]
```

Run without installing via `python -m ragrelay <subcommand> ...`.

- `--fanout N` (default 3): top-ranked workers a query may spread attempts over.
- `--out PATH` (manifest only): write JSON to a file instead of stdout.

A malformed fixture (bad JSON, or missing `workers`/`queries`) exits non-zero
with a message on stderr.

## Go scorer

```
relay -in PATH     read fixture from a file (default stdin)
relay -top N       keep only the top N rows per query (0 = all)
relay -pretty      pretty-print JSON output
```

Output is a JSON array of ranked rows: `query_id`, `worker_id`, `region`,
`affinity`, `cosine`, `topic_hit`, `latency_score`, `base_latency_ms`, `rank`.

## Manifest

`manifest` produces a JSON document keyed by:

| Field                | Meaning                                                  |
|----------------------|----------------------------------------------------------|
| `run_id`             | SHA-256(canonical inputs + fanout)[:16].                 |
| `fanout`             | Fan-out used.                                            |
| `worker_count`       | Number of workers.                                       |
| `query_count`        | Number of queries.                                       |
| `total_attempts`     | Total attempts allocated.                                |
| `route_distribution` | Fraction of attempts per worker.                         |
| `attempts_by_region` | Attempt counts by region.                                |
| `mean_latency_ms`    | Attempt-weighted mean expected latency.                  |
| `p95_latency_ms`     | 95th percentile of per-attempt expected latency.         |
| `allocations`        | Per-query primary + full breakdown.                      |

Identical inputs and fan-out yield an identical `run_id`, which makes manifests
usable as regression fixtures: commit one, and diff future runs against it.

## Make targets

```
make build      # compile Python + Go
make demo       # simulate + native ranking against the bundled fixture
make simulate   # distribution + latency summary
make manifest   # emit a run manifest
make clean      # remove build artifacts
```
