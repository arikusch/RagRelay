"""Routing tests: the scoring blend, ranking and attempt allocation."""

from __future__ import annotations

import pytest

from ragrelay.model import Profiles, Query, Worker
from ragrelay.routing import cosine, latency_score, route, score_query, topic_overlap


def test_cosine_orthogonal_and_identical() -> None:
    assert cosine([1.0, 0.0], [0.0, 1.0]) == 0.0
    assert cosine([1.0, 1.0], [1.0, 1.0]) == pytest.approx(1.0)


def test_cosine_zero_vector_is_zero() -> None:
    assert cosine([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_cosine_uses_overlapping_prefix() -> None:
    assert cosine([1.0, 1.0], [1.0, 1.0, 5.0]) == pytest.approx(1.0)


def test_topic_overlap_is_case_insensitive() -> None:
    assert topic_overlap(["Search", "rank"], ["search", "RANK"]) == 1.0
    assert topic_overlap(["search"], ["payments"]) == 0.0
    assert topic_overlap([], ["search"]) == 0.0


