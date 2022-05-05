"""Model tests: defaults, fixture loading and validation."""

from __future__ import annotations

import json

import pytest

from ragrelay.model import Profiles, Query, Worker, load_profiles


