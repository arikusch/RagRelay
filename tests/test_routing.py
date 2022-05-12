"""Routing tests: the scoring blend, ranking and attempt allocation."""

from __future__ import annotations

import pytest

from ragrelay.model import Profiles, Query, Worker
from ragrelay.routing import cosine, latency_score, route, score_query, topic_overlap


