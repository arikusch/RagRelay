"""Simulation layer for ragrelay.

Runs routing across every query in a profile set, then aggregates the route
distribution and expected latency. Latency is modeled deterministically from
each worker's base latency plus a load surcharge proportional to the fraction
of its capacity consumed in the run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .model import Profiles
from .routing import RouteDecision, route


@dataclass
class SimulationResult:
    """Aggregated output of a routing simulation."""

    decisions: List[RouteDecision]
    attempts_by_worker: Dict[str, int]
    attempts_by_region: Dict[str, int]
    total_attempts: int
    expected_latency_ms: Dict[str, float]  # per worker
    mean_latency_ms: float
    p95_latency_ms: float

    def route_distribution(self) -> Dict[str, float]:
        """Fraction of total attempts landing on each worker."""

        if self.total_attempts == 0:
            return {}
        return {
            wid: round(n / self.total_attempts, 4)
            for wid, n in sorted(self.attempts_by_worker.items())
        }

