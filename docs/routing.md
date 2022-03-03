# Routing internals

This document details the scoring and allocation math used by both the Python
engine and the Go scorer.

## Fixture format

A fixture is a JSON object with `workers` and `queries` arrays. See the field
tables in the top-level README for the full schema. The bundled example lives at
`examples/profiles.json` and models a red/blue transit map: transactional lanes
(payments, ledger, audit) and semantic lanes (search, embeddings, vector).

## Affinity blend
