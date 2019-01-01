"""Run manifests for ragrelay.

A manifest is a reproducible, serializable record of a simulation run: the
inputs digest, the route distribution, latency summary, and per-query
allocations. Manifests are content-addressed by a SHA-256 digest of their
canonical inputs so identical runs produce identical run IDs.
"""

from __future__ import annotations

