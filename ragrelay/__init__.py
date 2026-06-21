"""RagRelay — a deterministic retrieval-routing simulator.

The package scores incoming queries against worker profiles, allocates
retrieval attempts across endpoints, summarizes route distribution and
latency, and writes reproducible run manifests.

Public API:
    load_profiles   -- parse a profiles fixture into dataclasses
    score_query     -- affinity score for one query against one worker
    route           -- allocate retrieval attempts for a query set
    simulate        -- run a full routing simulation
    RunManifest     -- serializable record of a simulation run
"""

from .model import Worker, Query, Profiles, load_profiles
from .routing import score_query, route, RouteDecision
from .simulate import simulate, SimulationResult
from .manifest import RunManifest

__version__ = "5.0.2"

__all__ = [
    "Worker",
    "Query",
    "Profiles",
    "load_profiles",
    "score_query",
    "route",
    "RouteDecision",
    "simulate",
    "SimulationResult",
    "RunManifest",
    "__version__",
]
