"""Simulation tests: aggregation, distributions and latency summary."""

from __future__ import annotations

import pytest

from ragrelay.model import Profiles, Query, Worker
from ragrelay.simulate import _percentile, simulate


def _profiles() -> Profiles:
    workers = [
        Worker(id="w1", region="r1", topics=["a"], vector=[1.0, 0.0],
               base_latency_ms=100.0, capacity=10),
        Worker(id="w2", region="r2", topics=["b"], vector=[0.0, 1.0],
               base_latency_ms=200.0, capacity=10),
    ]
    queries = [Query(id="q1", topics=["a"], vector=[1.0, 0.0], urgency=0.0, attempts=3)]
    return Profiles(workers=workers, queries=queries)


def test_simulate_totals_and_region_rollup() -> None:
    result = simulate(_profiles(), fanout=2)
    assert result.total_attempts == 3
    assert result.attempts_by_region == {"r1": 3}
    assert result.attempts_by_worker == {"w1": 3, "w2": 0}


def test_simulate_latency_model_includes_pressure_surcharge() -> None:
    result = simulate(_profiles(), fanout=2)
    # w1: 3 of 10 capacity -> surcharge = 100 * 0.3 * 0.5 = 15
    assert result.expected_latency_ms["w1"] == pytest.approx(115.0)
    assert result.mean_latency_ms == pytest.approx(115.0)
    assert result.p95_latency_ms == pytest.approx(115.0)


def test_route_distribution_sums_to_one() -> None:
    result = simulate(_profiles(), fanout=2)
    dist = result.route_distribution()
    assert sum(dist.values()) == pytest.approx(1.0)
    assert dist["w1"] == pytest.approx(1.0)


def test_route_distribution_empty_when_no_attempts() -> None:
    profiles = Profiles(
