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
