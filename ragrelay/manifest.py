"""Run manifests for ragrelay.

A manifest is a reproducible, serializable record of a simulation run: the
inputs digest, the route distribution, latency summary, and per-query
allocations. Manifests are content-addressed by a SHA-256 digest of their
canonical inputs so identical runs produce identical run IDs.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .model import Profiles
from .simulate import SimulationResult


@dataclass
class RunManifest:
    """Serializable record of one simulation run."""

    run_id: str
    fanout: int
    worker_count: int
    query_count: int
    total_attempts: int
    route_distribution: Dict[str, float]
    attempts_by_region: Dict[str, int]
    mean_latency_ms: float
    p95_latency_ms: float
    allocations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "fanout": self.fanout,
            "worker_count": self.worker_count,
            "query_count": self.query_count,
            "total_attempts": self.total_attempts,
            "route_distribution": self.route_distribution,
            "attempts_by_region": self.attempts_by_region,
            "mean_latency_ms": self.mean_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "allocations": self.allocations,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _digest(profiles: Profiles, fanout: int) -> str:
    payload = {
        "fanout": fanout,
        "workers": [
            {
                "id": w.id,
