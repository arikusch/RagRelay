# Routing internals

This document details the scoring and allocation math used by both the Python
engine and the Go scorer.

## Fixture format

A fixture is a JSON object with `workers` and `queries` arrays. See the field
tables in the top-level README for the full schema. The bundled example lives at
`examples/profiles.json` and models a red/blue transit map: transactional lanes
(payments, ledger, audit) and semantic lanes (search, embeddings, vector).

## Affinity blend

```
affinity = (0.5*cosine + 0.3*topic_hit + 0.2*latency_score) * weight
```

### Cosine similarity

Standard dot-product over L2 norms. When either vector is all zeros the result
is defined as `0.0` to avoid division by zero. Only the overlapping prefix of
the two vectors is compared, so vectors of differing length degrade gracefully.

### Topic overlap

Case-insensitive fraction of the query's topics that are present in the worker's
topic set. A query with no topics contributes `0.0`.

### Latency score

```
k = 40 * (1 + urgency)
latency_score = k / (k + base_latency_ms)
```

Higher urgency raises `k`, which flattens the curve so that urgent queries care
more strongly about picking a fast endpoint. An endpoint with zero base latency
scores `1.0`.

## Ranking

Workers are sorted by affinity descending, ties broken by `id` ascending. This
total order is identical in Python (`sort` with a key of `(-affinity, id)`) and
Go (`sort.SliceStable` with the same comparison), which is why the two
components never disagree.

## Attempt allocation

`route()` takes a query's `attempts` and splits them across the top `fanout`
workers with a largest-remainder method:

1. `exact_i = attempts * weight_i / sum(weights)`
2. `alloc_i = min(floor(exact_i), capacity_i)`
3. Distribute the remaining units to the largest fractional remainders, skipping
   capped workers, breaking ties by index.
4. The top worker is guaranteed at least one attempt.

The result is exact (allocations sum to `attempts` unless capacity forbids it)
and fully deterministic.
