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
