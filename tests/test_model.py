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
    with pytest.raises(ValueError):
        Profiles.from_dict({"workers": [{"id": "w1"}], "queries": []})


def test_load_profiles_roundtrip(tmp_path) -> None:
    fixture = {
        "workers": [{"id": "w1", "region": "r1", "topics": ["a"], "vector": [1.0]}],
        "queries": [{"id": "q1", "topics": ["a"], "vector": [1.0], "attempts": 2}],
    }
    path = tmp_path / "fixture.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")

    profiles = load_profiles(path)
    assert len(profiles.workers) == 1
    assert len(profiles.queries) == 1
    assert profiles.workers[0].id == "w1"
    assert profiles.queries[0].attempts == 2
