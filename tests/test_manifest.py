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


