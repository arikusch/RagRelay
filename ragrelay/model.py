"""Data model for ragrelay.

Defines the worker and query dataclasses plus JSON fixture loading. Only the
standard library is used. Vectors are plain lists of floats.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Worker:
    """A retrieval endpoint profile."""

    id: str
    region: str
    topics: List[str] = field(default_factory=list)
    weight: float = 1.0
    base_latency_ms: float = 50.0
    capacity: int = 8
    vector: List[float] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "Worker":
        return cls(
            id=str(d["id"]),
            region=str(d.get("region", "unknown")),
            topics=[str(t) for t in d.get("topics", [])],
            weight=float(d.get("weight", 1.0)),
            base_latency_ms=float(d.get("base_latency_ms", 50.0)),
            capacity=int(d.get("capacity", 8)),
            vector=[float(x) for x in d.get("vector", [])],
        )


@dataclass(frozen=True)
class Query:
    """An incoming retrieval request."""

    id: str
    topics: List[str] = field(default_factory=list)
    vector: List[float] = field(default_factory=list)
    urgency: float = 0.0
    attempts: int = 3

    @classmethod
    def from_dict(cls, d: dict) -> "Query":
        return cls(
            id=str(d["id"]),
            topics=[str(t) for t in d.get("topics", [])],
            vector=[float(x) for x in d.get("vector", [])],
            urgency=float(d.get("urgency", 0.0)),
            attempts=int(d.get("attempts", 3)),
        )


@dataclass(frozen=True)
class Profiles:
    """A parsed fixture: the set of workers and queries."""

    workers: List[Worker]
    queries: List[Query]

    @classmethod
    def from_dict(cls, d: dict) -> "Profiles":
        workers = [Worker.from_dict(w) for w in d.get("workers", [])]
        queries = [Query.from_dict(q) for q in d.get("queries", [])]
        if not workers:
            raise ValueError("profiles must contain at least one worker")
        if not queries:
            raise ValueError("profiles must contain at least one query")
        return cls(workers=workers, queries=queries)


def load_profiles(path: str | Path) -> Profiles:
    """Load a profiles fixture from a JSON file."""

    raw = Path(path).read_text(encoding="utf-8")
    return Profiles.from_dict(json.loads(raw))


def load_profiles_str(text: str) -> Profiles:
    """Load profiles from a JSON string."""

