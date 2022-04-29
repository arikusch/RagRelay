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

