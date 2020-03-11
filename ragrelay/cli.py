"""Command-line interface for ragrelay.

Subcommands:
    route     -- show per-query attempt allocations for a profiles fixture
    simulate  -- run a full simulation and print a route/latency summary
    manifest  -- emit a reproducible run manifest as JSON
    score     -- print the affinity matrix (query x worker)

All output is deterministic for a given fixture.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from .model import load_profiles
from .routing import route, score_query
from .simulate import simulate
from .manifest import build_manifest


def _cmd_route(args) -> int:
    profiles = load_profiles(args.fixture)
    print(f"route allocations (fanout={args.fanout})")
    print("=" * 52)
    for q in profiles.queries:
        d = route(profiles, q, fanout=args.fanout)
        parts = ", ".join(f"{wid}:{n}" for wid, n in d.allocation)
