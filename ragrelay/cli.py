"""Command-line interface for ragrelay.

Subcommands:
    route     -- show per-query attempt allocations for a profiles fixture
    simulate  -- run a full simulation and print a route/latency summary
    manifest  -- emit a reproducible run manifest as JSON
    score     -- print the affinity matrix (query x worker)

All output is deterministic for a given fixture.
"""

from __future__ import annotations

