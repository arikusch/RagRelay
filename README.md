# RagRelay

[![ci](https://github.com/jfrost4/RagRelay/actions/workflows/ci.yml/badge.svg)](https://github.com/jfrost4/RagRelay/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-blue)
![python](https://img.shields.io/badge/python-3.11%2B-blue)

RagRelay is a deterministic retrieval-routing simulator. It scores incoming
queries against a pool of worker (endpoint) profiles, splits each query's
retrieval attempts across its highest-affinity workers, reports the resulting
route distribution and expected latency, and writes content-addressed run
manifests so any simulation reproduces byte for byte.

RagRelay ships as a Python and Go pair. The Python package owns the routing
engine, the simulation aggregator, the manifest writer, and the CLI. The Go
command under `relay/` is a small, self-contained endpoint scorer that reads the
same fixture format and computes the same affinity math, giving you a native
cross-check against the Python run. Both halves use only their language's
standard library. No third-party packages, no network calls, no build-time
downloads.

![Transit-style routing map showing queries scored to endpoints across regions](docs/assets/route-map.svg)

## The problem it solves

When a retrieval-augmented workload fans out across a pool of unlike endpoints
(different regions, topic specializations, and latency envelopes), three
questions need answers before anything ships:

1. Where does each query land, and why does the scorer pick those endpoints?
2. How does load spread across the pool, and is one region carrying the rest?
3. What latency follows once capacity pressure builds?

RagRelay answers all three offline from a single JSON fixture. Because every
stage is a pure function of its inputs, the same fixture always yields the same
routing, the same distribution, and the same manifest `run_id`. That property
turns it into a regression oracle: change a worker weight or a query's urgency,
re-run, and diff the manifest.

The diagrams use a red-and-blue transit map as their visual language. Red lanes
carry the transactional topics (payments, ledger, audit); blue lanes carry the
semantic ones (search, embeddings, vector similarity). Endpoints are stations,
queries are trains, and the scorer is the interchange.

## Install and build

The two halves build independently.

```bash
# Python side: importable package and CLI, stdlib only
python -m pip install -e .          # optional; installs the `ragrelay` script
python -m ragrelay --help           # or run directly without installing

# Go side: the scorer/ranker binary
cd relay
go build ./...                      # produces the `relay` binary
```

Python 3.11+ and Go 1.24+ are the only prerequisites.

## Tests

The test suite is stdlib-only and runs from the repository root:

```bash
python -m pytest tests/ -o addopts=""     # requires pytest
```

It covers the scoring blend, the largest-remainder allocator, the simulation
aggregates, and manifest reproducibility. `make test` runs the same command.

## Quick start

```bash
# Summarize a run: distribution plus latency
python -m ragrelay simulate examples/profiles.json

# Inspect per-query attempt allocations
python -m ragrelay route examples/profiles.json

# Print the affinity matrix (query x worker)
python -m ragrelay score examples/profiles.json

# Write a reproducible manifest
python -m ragrelay manifest examples/profiles.json --out run.json

# Cross-check the ranking with the native Go scorer
relay/relay -in examples/profiles.json -top 2 -pretty
```

Running `simulate` against the bundled fixture prints a summary in this shape:

```
simulation summary (fanout=3)
====================================================
workers        : 5
queries        : 4
total attempts : 19

route distribution:
  w-azure        #####...................  21.1%
  w-cobalt       ####....................  15.8%
  w-crimson      ######..................  26.3%
  w-navy         ####....................  15.8%
  w-scarlet      #####...................  21.1%

attempts by region:
  ap-south       3
  eu-west        7
  us-east        9
```

## Fixture schema

A fixture is one JSON document with two arrays, `workers` and `queries`.

### Worker (endpoint profile)

| Field | Type | Meaning |
|-------|------|---------|
| `id` | string | Unique endpoint identifier (station name). |
| `region` | string | Deployment region, used for the by-region rollup. |
| `topics` | string[] | Topic labels this endpoint specializes in. |
| `weight` | float | Multiplier on the endpoint's final affinity. Default `1.0`. |
| `base_latency_ms` | float | Idle round-trip latency in milliseconds. Default `50.0`. |
| `capacity` | int | Maximum attempts the endpoint accepts in one run. Default `8`. |
| `vector` | float[] | Dense profile embedding, compared to the query vector. |

### Query (incoming request)

| Field | Type | Meaning |
|-------|------|---------|
| `id` | string | Unique query identifier (train name). |
| `topics` | string[] | Topic labels the query is about. |
| `vector` | float[] | Dense query embedding, compared to each worker vector. |
| `urgency` | float | 0..1; higher urgency sharpens the latency preference. |
| `attempts` | int | Retrieval attempts to allocate for this query. Default `3`. |

The bundled `examples/profiles.json` carries five workers across three regions
and four queries spanning payments, search, embeddings, and audit topics.

## The affinity score

The Python engine (`routing.py`) and the Go scorer compute the same blend:

```
affinity(query, worker) =
    ( 0.5 * cosine(query.vector, worker.vector)
    + 0.3 * topic_overlap(query.topics, worker.topics)
    + 0.2 * latency_score(worker.base_latency_ms, query.urgency)
    ) * worker.weight
```

- `cosine` is standard cosine similarity, returning 0 when either vector is zero.
- `topic_overlap` is the fraction of the query's topics present in the worker's
  topic set, matched case-insensitively.
- `latency_score` is `k / (k + base_latency_ms)` with `k = 40 * (1 + urgency)`,
  so a fast endpoint scores near 1 and rising urgency deepens the penalty on slow
  ones.

Ranking is stable: workers sort by affinity descending, ties broken on `id`
ascending. That stability is why the Python and Go outputs agree.

## Attempt allocation

Once workers are ranked, a query's `attempts` split across the top `fanout`
workers by a largest-remainder distribution proportional to affinity, bounded by
each worker's `capacity`:

1. Compute each top worker's exact proportional share of the attempts.
2. Floor each share, never exceeding capacity.
3. Hand out the leftover attempts one at a time to the largest fractional
   remainders, skipping any worker already at capacity.
4. Break remainder ties on index so the result stays fixed.

The top-ranked worker is guaranteed at least one attempt, so no query goes
unrouted. Largest-remainder avoids the drift of naive rounding and stays
reproducible.

## How a run flows

```
 fixture.json
     |
     v
 load_profiles ----> Profiles(workers, queries)
     |
     v
 score_query  ----> affinity per (query, worker)    <== same math in Go relay
     |
     v
 route        ----> RouteDecision(allocation per query)
     |
     v
 simulate     ----> SimulationResult(distribution, latency)
     |
     v
 build_manifest --> RunManifest(run_id = sha256(inputs)[:16])
```

Nothing reads the clock, the network, or a random source, so a given fixture
pins every downstream artifact.

![Attempt distribution bars with a latency sweep across endpoints](docs/assets/distribution.svg)

## Component layout

```
+-----------------------------------------------------------+
|                     ragrelay (Python)                     |
|  cli.py     route | score | simulate | manifest           |
|  routing.py score, rank, largest-remainder allocation     |
|  simulate.py aggregate distribution + latency             |
|  manifest.py sha256 run_id, canonical serialize           |
|  model.py    Worker / Query / Profiles + fixture loading  |
+-----------------------------------------------------------+
                         ^
                         |  shared fixture schema + scoring blend
                         v
+-----------------------------------------------------------+
|                     relay/ (Go, main package)             |
|  main.go   profiles JSON -> cosine + topic + latency      |
|            -> ranked endpoints JSON (affinity, rank, ...)  |
+-----------------------------------------------------------+
```

The two halves never call each other at runtime; the shared fixture schema and
scoring formula keep them in agreement. Reach for the Python side for
simulation, distribution, and manifests; reach for the Go binary when you want a
fast, dependency-free ranking to drop into another pipeline.

## Recipes

Compare two capacity plans:

```bash
python -m ragrelay manifest examples/profiles.json --out before.json
# edit a worker's capacity in a copy of the fixture, then:
python -m ragrelay manifest my-fixture.json --out after.json
diff before.json after.json
```

An identical plan yields an identical `run_id`; any change to a worker, query, or
the fanout flips it.

Widen fan-out and watch the tail:

```bash
python -m ragrelay simulate examples/profiles.json --fanout 2
python -m ragrelay simulate examples/profiles.json --fanout 5
```

A wider fan-out pushes attempts onto lower-affinity (often slower) endpoints,
which tends to raise p95 while smoothing the distribution.

Take the single winning endpoint per query from the Go scorer:

```bash
relay/relay -in examples/profiles.json -top 1
```

Feed a fixture over stdin:

```bash
cat examples/profiles.json | relay/relay -pretty
```

## Operations reference

### Python CLI

```
ragrelay route     <fixture> [--fanout N]                per-query allocations
ragrelay score     <fixture>                             affinity matrix
ragrelay simulate  <fixture> [--fanout N]                distribution + latency
ragrelay manifest  <fixture> [--fanout N] [--out PATH]   reproducible manifest
```

`--fanout N` (default `3`) sets how many top-ranked workers a query may spread
across. `--out PATH` (manifest only) writes JSON to a file instead of stdout. The
exit code is `0` on success and non-zero on a malformed fixture (missing
`workers` or `queries`, or unparseable JSON).

### Go scorer

```
relay -in PATH     read fixture from a file (default: stdin)
relay -top N       keep only the top N rows per query (0 = all)
relay -pretty      pretty-print the JSON output
```

Output is a JSON array of ranked rows, each carrying `query_id`, `worker_id`,
`region`, `affinity`, `cosine`, `topic_hit`, `latency_score`, `base_latency_ms`,
and `rank`.

### Manifest fields

| Field | Meaning |
|-------|---------|
| `run_id` | First 16 hex chars of SHA-256 over canonical inputs plus fanout. |
| `fanout` | Fan-out used for the run. |
| `worker_count` | Number of worker profiles. |
| `query_count` | Number of queries. |
| `total_attempts` | Sum of allocated attempts across all queries. |
| `route_distribution` | Fraction of total attempts per worker. |
| `attempts_by_region` | Attempt counts rolled up by region. |
| `mean_latency_ms` | Attempt-weighted mean expected latency. |
| `p95_latency_ms` | 95th percentile of per-attempt expected latency. |
| `allocations` | Per-query primary worker and full allocation breakdown. |

### Latency model

Expected latency for a worker is its base latency plus a load surcharge
(`simulate.py`):

```
pressure  = attempts_used / capacity          (clamped to 2.0)
surcharge = base_latency_ms * pressure * 0.5
expected  = base_latency_ms + surcharge
```

Per-attempt latencies expand across every allocated attempt, then the mean and
the 95th percentile are computed with linear interpolation.

## Project layout

```
ragrelay/
  ragrelay/            Python package
    __init__.py        public API + version
    __main__.py        python -m ragrelay entry point
    model.py           Worker / Query / Profiles + fixture loading
    routing.py         scoring, ranking, largest-remainder allocation
    simulate.py        distribution + latency aggregation
    manifest.py        content-addressed run manifests
    cli.py             argparse CLI (route/score/simulate/manifest)
  relay/               Go scorer/ranker
    go.mod
    main.go
  examples/
    profiles.json      the bundled transit-map fixture
  tests/               pytest suite for engine, simulation and manifests
  docs/
    routing.md         schema and scoring notes
    operations.md      CLI and manifest reference
    assets/
      route-map.svg     transit routing map
      distribution.svg  attempt distribution + latency
  Makefile
  pyproject.toml
```

## Determinism guarantees

- No randomness, wall-clock reads, or environment lookups anywhere in the
  routing, simulation, or manifest paths.
- Stable sort keys (`affinity` descending, `id` ascending) fix the ranking order.
- Largest-remainder allocation resolves leftovers by a fixed ordering.
- The manifest `run_id` is a pure function of the canonical JSON inputs plus
  fan-out.

Two runs with byte-identical fixtures and the same fan-out produce identical
output on any platform.

## License

Licensed under the MIT License. See [LICENSE](LICENSE).

<!-- draft note 315 -->
