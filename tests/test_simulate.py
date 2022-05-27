"""Simulation tests: aggregation, distributions and latency summary."""

from __future__ import annotations

import pytest

from ragrelay.model import Profiles, Query, Worker
from ragrelay.simulate import _percentile, simulate


def _profiles() -> Profiles:
    workers = [
