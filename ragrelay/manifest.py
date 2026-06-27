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
                "region": w.region,
                "topics": w.topics,
                "weight": w.weight,
                "base_latency_ms": w.base_latency_ms,
                "capacity": w.capacity,
                "vector": w.vector,
            }
            for w in profiles.workers
        ],
        "queries": [
            {
                "id": q.id,
                "topics": q.topics,
                "vector": q.vector,
                "urgency": q.urgency,
                "attempts": q.attempts,
            }
            for q in profiles.queries
        ],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def build_manifest(
    profiles: Profiles, result: SimulationResult, fanout: int
) -> RunManifest:
    """Assemble a run manifest from a simulation result."""

    allocations = [
        {
            "query_id": d.query_id,
            "primary": d.primary,
            "allocation": [{"worker_id": wid, "attempts": n} for wid, n in d.allocation],
        }
        for d in result.decisions
    ]
    return RunManifest(
        run_id=_digest(profiles, fanout),
        fanout=fanout,
        worker_count=len(profiles.workers),
        query_count=len(profiles.queries),
        total_attempts=result.total_attempts,
        route_distribution=result.route_distribution(),
        attempts_by_region=result.attempts_by_region,
        mean_latency_ms=result.mean_latency_ms,
        p95_latency_ms=result.p95_latency_ms,
        allocations=allocations,
    )
