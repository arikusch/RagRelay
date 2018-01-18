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
