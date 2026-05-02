"""CLI smoke tests against the bundled fixture."""

from __future__ import annotations

import json
from pathlib import Path

from ragrelay import __version__
from ragrelay.cli import main

FIXTURE = str(Path(__file__).resolve().parents[1] / "examples" / "profiles.json")


def test_version_is_set() -> None:
    assert __version__ == "5.0.2"


def test_cli_score(capsys) -> None:
    assert main(["score", FIXTURE]) == 0
    out = capsys.readouterr().out
    assert "query" in out
    assert "w-crimson" in out


def test_cli_route(capsys) -> None:
    assert main(["route", FIXTURE]) == 0
    out = capsys.readouterr().out
    assert "route allocations (fanout=3)" in out
    assert "q-invoice" in out


def test_cli_simulate(capsys) -> None:
    assert main(["simulate", FIXTURE]) == 0
    out = capsys.readouterr().out
    assert "total attempts : 19" in out
    assert "attempts by region:" in out


def test_cli_manifest_stdout(capsys) -> None:
    assert main(["manifest", FIXTURE]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload["run_id"]) == 16
    assert payload["worker_count"] == 5
    assert payload["query_count"] == 4


def test_cli_manifest_out(tmp_path, capsys) -> None:
    out_path = tmp_path / "run.json"
    assert main(["manifest", FIXTURE, "--out", str(out_path)]) == 0
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["total_attempts"] == 19
