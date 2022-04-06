"""Manifest tests: content addressing and serialization."""

from __future__ import annotations

import json

from ragrelay.manifest import build_manifest
from ragrelay.model import Profiles, Query, Worker
from ragrelay.simulate import simulate


def _profiles() -> Profiles:
    workers = [
