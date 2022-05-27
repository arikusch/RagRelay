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
