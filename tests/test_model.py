"""Model tests: defaults, fixture loading and validation."""

from __future__ import annotations

import json

import pytest

from ragrelay.model import Profiles, Query, Worker, load_profiles


def test_worker_defaults() -> None:
    w = Worker.from_dict({"id": "w1", "region": "eu-west"})
    assert w.id == "w1"
    assert w.region == "eu-west"
    assert w.weight == 1.0
    assert w.base_latency_ms == 50.0
    assert w.capacity == 8
    assert w.topics == []
    assert w.vector == []


def test_query_defaults() -> None:
    q = Query.from_dict({"id": "q1"})
    assert q.urgency == 0.0
    assert q.attempts == 3
    assert q.topics == []


def test_worker_missing_region_falls_back() -> None:
    w = Worker.from_dict({"id": "w1"})
    assert w.region == "unknown"


def test_profiles_requires_workers_and_queries() -> None:
    with pytest.raises(ValueError):
        Profiles.from_dict({"workers": [], "queries": [{"id": "q1"}]})
