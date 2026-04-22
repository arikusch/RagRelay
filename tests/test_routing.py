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


def test_latency_score_prefers_fast_endpoints() -> None:
    fast = latency_score(10.0, 0.0)
    slow = latency_score(200.0, 0.0)
    assert fast > slow
    assert fast <= 1.0
    assert latency_score(0.0, 0.5) == 1.0


def test_urgency_sharpens_latency_penalty() -> None:
    calm = latency_score(200.0, 0.0)
    urgent = latency_score(200.0, 1.0)
    assert urgent > calm


def test_score_query_is_deterministic() -> None:
    q = Query(id="q", topics=["payments"], vector=[1.0, 0.0], urgency=0.5)
    w = Worker(id="w", region="r", topics=["payments"], vector=[1.0, 0.0])
    first = score_query(q, w)
    second = score_query(q, w)
    assert first == second
    assert first > 0.0


def test_score_query_applies_weight() -> None:
    q = Query(id="q", topics=["a"], vector=[1.0])
    light = Worker(id="w", region="r", topics=["a"], vector=[1.0], weight=1.0)
    heavy = Worker(id="w", region="r", topics=["a"], vector=[1.0], weight=2.0)
    assert score_query(q, heavy) == 2 * score_query(q, light)


def _profiles() -> Profiles:
    workers = [
        Worker(id="w-fast", region="us-east", topics=["payments"], vector=[1.0, 0.0],
               base_latency_ms=20.0, capacity=10),
        Worker(id="w-slow", region="ap-south", topics=["payments"], vector=[1.0, 0.0],
               base_latency_ms=200.0, capacity=10),
    ]
    queries = [Query(id="q1", topics=["payments"], vector=[1.0, 0.0], urgency=0.0, attempts=5)]
    return Profiles(workers=workers, queries=queries)


def test_route_ranks_best_worker_first() -> None:
    profiles = _profiles()
    decision = route(profiles, profiles.queries[0], fanout=2)
    assert decision.primary == "w-fast"
    assert sum(n for _, n in decision.allocation) == 5


def test_route_respects_capacity() -> None:
    workers = [
        Worker(id="w1", region="r", topics=["a"], vector=[1.0], capacity=2),
        Worker(id="w2", region="r", topics=["a"], vector=[1.0], capacity=2),
    ]
    profiles = Profiles(workers=workers, queries=[Query(id="q", topics=["a"], vector=[1.0], attempts=8)])
    decision = route(profiles, profiles.queries[0], fanout=2)
    for _, n in decision.allocation:
        assert n <= 2


def test_route_top_worker_always_gets_an_attempt() -> None:
    workers = [
        Worker(id="w1", region="r", topics=["a"], vector=[1.0], capacity=1),
        Worker(id="w2", region="r", topics=["a"], vector=[1.0], capacity=1),
    ]
    profiles = Profiles(workers=workers, queries=[Query(id="q", topics=["a"], vector=[1.0], attempts=1)])
    decision = route(profiles, profiles.queries[0], fanout=2)
    assert decision.allocation[0][0] == "w1"
    assert decision.allocation[0][1] >= 1


def test_route_is_stable_across_runs() -> None:
    profiles = _profiles()
    a = route(profiles, profiles.queries[0], fanout=2)
    b = route(profiles, profiles.queries[0], fanout=2)
    assert a.allocation == b.allocation
    assert a.scores == b.scores
