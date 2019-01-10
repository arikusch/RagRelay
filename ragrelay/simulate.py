"""Simulation layer for ragrelay.

Runs routing across every query in a profile set, then aggregates the route
distribution and expected latency. Latency is modeled deterministically from
each worker's base latency plus a load surcharge proportional to the fraction
of its capacity consumed in the run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .model import Profiles
from .routing import RouteDecision, route


