"""Routing engine for ragrelay.

Scores queries against workers and allocates retrieval attempts deterministically.
The scoring blend mirrors the Go ``relay`` command so the two components agree:

    affinity = (0.5 * cosine + 0.3 * topic_hit + 0.2 * latency_score) * weight

Attempt allocation is a deterministic largest-remainder distribution over the
top-ranked workers, bounded by per-worker capacity.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Tuple

from .model import Profiles, Query, Worker


def cosine(a: List[float], b: List[float]) -> float:
    n = min(len(a), len(b))
    dot = na = nb = 0.0
    for i in range(n):
        dot += a[i] * b[i]
        na += a[i] * a[i]
        nb += b[i] * b[i]
    if na == 0 or nb == 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def topic_overlap(query_topics: List[str], worker_topics: List[str]) -> float:
    if not query_topics:
        return 0.0
    wset = {t.lower() for t in worker_topics}
    hit = sum(1 for t in query_topics if t.lower() in wset)
    return hit / len(query_topics)


def latency_score(base_latency_ms: float, urgency: float) -> float:
    """Map base latency to a 0..1 preference (lower latency scores higher)."""

    if base_latency_ms <= 0:
        return 1.0
    k = 40.0 * (1.0 + urgency)
    return k / (k + base_latency_ms)


def score_query(query: Query, worker: Worker) -> float:
    """Compute the deterministic affinity score for a query/worker pair."""

    cos = cosine(query.vector, worker.vector)
    th = topic_overlap(query.topics, worker.topics)
    ls = latency_score(worker.base_latency_ms, query.urgency)
    return round((0.5 * cos + 0.3 * th + 0.2 * ls) * worker.weight, 6)


@dataclass(frozen=True)
class RouteDecision:
    """The allocation of attempts for a single query."""

    query_id: str
    allocation: List[Tuple[str, int]]  # (worker_id, attempts) in rank order
    scores: List[Tuple[str, float]] = field(default_factory=list)

    @property
    def primary(self) -> str:
        return self.allocation[0][0] if self.allocation else ""


def _largest_remainder(weights: List[float], total: int, caps: List[int]) -> List[int]:
    """Distribute ``total`` integer units across slots proportional to weights,
    honoring per-slot caps, using the largest-remainder method for determinism.
    """

    n = len(weights)
    if n == 0 or total <= 0:
        return [0] * n
    wsum = sum(weights)
    if wsum <= 0:
        # even split
        base = total // n
        alloc = [min(base, caps[i]) for i in range(n)]
    else:
        exact = [total * w / wsum for w in weights]
        alloc = [min(int(math.floor(e)), caps[i]) for i, e in enumerate(exact)]
        assigned = sum(alloc)
        remainder = total - assigned
        # rank slots by fractional part desc, then index asc for stability
        order = sorted(
            range(n),
            key=lambda i: (-(exact[i] - math.floor(exact[i])), i),
        )
        idx = 0
        guard = 0
        while remainder > 0 and guard < 10_000:
            i = order[idx % n]
            if alloc[i] < caps[i]:
                alloc[i] += 1
                remainder -= 1
            idx += 1
            guard += 1
    return alloc


def route(profiles: Profiles, query: Query, fanout: int = 3) -> RouteDecision:
    """Allocate a query's attempts across the top ``fanout`` workers.

    Workers are ranked by affinity (desc) then id (asc) for tie stability.
    Attempts are the query's ``attempts`` count, split proportional to score.
    """

    scored = [
