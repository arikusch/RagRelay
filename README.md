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
