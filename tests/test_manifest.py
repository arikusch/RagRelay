"""Manifest tests: content addressing and serialization."""

from __future__ import annotations

import json

from ragrelay.manifest import build_manifest
from ragrelay.model import Profiles, Query, Worker
from ragrelay.simulate import simulate


def _profiles() -> Profiles:
    workers = [
        Worker(id="w1", region="r1", topics=["a"], vector=[1.0], capacity=5),
        Worker(id="w2", region="r2", topics=["b"], vector=[0.0], capacity=5),
    ]
    queries = [Query(id="q1", topics=["a"], vector=[1.0], attempts=3)]
    return Profiles(workers=workers, queries=queries)


def test_run_id_is_stable_for_same_inputs() -> None:
    profiles = _profiles()
    first = build_manifest(profiles, simulate(profiles, fanout=2), fanout=2)
    second = build_manifest(profiles, simulate(profiles, fanout=2), fanout=2)
    assert first.run_id == second.run_id
    assert len(first.run_id) == 16


def test_run_id_changes_with_fanout() -> None:
    profiles = _profiles()
    a = build_manifest(profiles, simulate(profiles, fanout=1), fanout=1)
    b = build_manifest(profiles, simulate(profiles, fanout=2), fanout=2)
    assert a.run_id != b.run_id


def test_run_id_changes_with_fixture() -> None:
    profiles = _profiles()
    other = Profiles(
        workers=profiles.workers,
        queries=[Query(id="q1", topics=["a"], vector=[1.0], attempts=4)],
    )
    a = build_manifest(profiles, simulate(profiles, fanout=2), fanout=2)
    b = build_manifest(other, simulate(other, fanout=2), fanout=2)
    assert a.run_id != b.run_id


def test_manifest_fields_and_json() -> None:
    profiles = _profiles()
    manifest = build_manifest(profiles, simulate(profiles, fanout=2), fanout=2)
    data = manifest.to_dict()
    assert data["fanout"] == 2
    assert data["worker_count"] == 2
    assert data["query_count"] == 1
    assert data["total_attempts"] == 3
    assert data["allocations"][0]["query_id"] == "q1"
    assert data["allocations"][0]["primary"] == "w1"

    text = manifest.to_json()
    parsed = json.loads(text)
    assert parsed == data
    assert text == json.dumps(data, indent=2, sort_keys=True)
