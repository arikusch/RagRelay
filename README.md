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
