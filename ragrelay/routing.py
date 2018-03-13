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

