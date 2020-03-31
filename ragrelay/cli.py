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
        print(f"  {q.id:<14} -> {parts}")
    return 0


def _cmd_score(args) -> int:
    profiles = load_profiles(args.fixture)
    header = ["query"] + [w.id for w in profiles.workers]
    widths = [max(len(h), 8) for h in header]
    print("  ".join(h.ljust(widths[i]) for i, h in enumerate(header)))
    print("-" * (sum(widths) + 2 * len(widths)))
    for q in profiles.queries:
        row = [q.id]
        for w in profiles.workers:
            row.append(f"{score_query(q, w):.4f}")
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))
    return 0


def _bar(fraction: float, width: int = 24) -> str:
    filled = int(round(fraction * width))
    return "#" * filled + "." * (width - filled)


def _cmd_simulate(args) -> int:
    profiles = load_profiles(args.fixture)
    result = simulate(profiles, fanout=args.fanout)
    print(f"simulation summary (fanout={args.fanout})")
    print("=" * 52)
    print(f"workers        : {len(profiles.workers)}")
    print(f"queries        : {len(profiles.queries)}")
    print(f"total attempts : {result.total_attempts}")
    print(f"mean latency   : {result.mean_latency_ms} ms")
    print(f"p95 latency    : {result.p95_latency_ms} ms")
    print()
    print("route distribution:")
    dist = result.route_distribution()
    for wid, frac in dist.items():
        print(f"  {wid:<14} {_bar(frac)} {frac*100:5.1f}%")
    print()
    print("attempts by region:")
    for region, n in result.attempts_by_region.items():
        print(f"  {region:<14} {n}")
    return 0


def _cmd_manifest(args) -> int:
    profiles = load_profiles(args.fixture)
    result = simulate(profiles, fanout=args.fanout)
    manifest = build_manifest(profiles, result, fanout=args.fanout)
    text = manifest.to_json()
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"wrote manifest {manifest.run_id} -> {args.out}")
    else:
        print(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ragrelay",
        description="deterministic retrieval-routing simulator",
    )
    sub = p.add_subparsers(dest="command", required=True)

    def add_common(sp):
        sp.add_argument("fixture", help="path to a profiles JSON fixture")
        sp.add_argument(
            "--fanout", type=int, default=3, help="workers per query (default 3)"
        )

    sp = sub.add_parser("route", help="show per-query attempt allocations")
    add_common(sp)
    sp.set_defaults(func=_cmd_route)

    sp = sub.add_parser("score", help="print the affinity matrix")
    sp.add_argument("fixture", help="path to a profiles JSON fixture")
    sp.set_defaults(func=_cmd_score)

