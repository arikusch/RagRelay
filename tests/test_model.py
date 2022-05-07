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
