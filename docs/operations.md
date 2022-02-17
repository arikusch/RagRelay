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

