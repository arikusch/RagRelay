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


def _percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = pct / 100.0 * (len(ordered) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(ordered) - 1)
    frac = rank - lo
    return ordered[lo] + (ordered[hi] - ordered[lo]) * frac


def simulate(profiles: Profiles, fanout: int = 3) -> SimulationResult:
    """Run routing for every query and aggregate the results."""

    worker_by_id = {w.id: w for w in profiles.workers}
    decisions: List[RouteDecision] = []
    attempts_by_worker: Dict[str, int] = {w.id: 0 for w in profiles.workers}
    attempts_by_region: Dict[str, int] = {}

    for q in profiles.queries:
        decision = route(profiles, q, fanout=fanout)
        decisions.append(decision)
        for wid, n in decision.allocation:
            attempts_by_worker[wid] = attempts_by_worker.get(wid, 0) + n
            region = worker_by_id[wid].region
            attempts_by_region[region] = attempts_by_region.get(region, 0) + n

    total = sum(attempts_by_worker.values())

    # Deterministic latency model: base + surcharge for capacity pressure.
    expected: Dict[str, float] = {}
    per_attempt_latencies: List[float] = []
    for w in profiles.workers:
        used = attempts_by_worker.get(w.id, 0)
        pressure = used / w.capacity if w.capacity > 0 else 1.0
        surcharge = w.base_latency_ms * min(pressure, 2.0) * 0.5
        lat = round(w.base_latency_ms + surcharge, 3)
        expected[w.id] = lat
        per_attempt_latencies.extend([lat] * used)

    mean_lat = (
        round(sum(per_attempt_latencies) / len(per_attempt_latencies), 3)
        if per_attempt_latencies
        else 0.0
    )
    p95 = round(_percentile(per_attempt_latencies, 95.0), 3)

    return SimulationResult(
        decisions=decisions,
        attempts_by_worker={k: v for k, v in sorted(attempts_by_worker.items())},
        attempts_by_region={k: v for k, v in sorted(attempts_by_region.items())},
        total_attempts=total,
        expected_latency_ms=expected,
        mean_latency_ms=mean_lat,
        p95_latency_ms=p95,
