"""CLI smoke tests against the bundled fixture."""

from __future__ import annotations

import json
from pathlib import Path

from ragrelay import __version__
from ragrelay.cli import main

FIXTURE = str(Path(__file__).resolve().parents[1] / "examples" / "profiles.json")
