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

