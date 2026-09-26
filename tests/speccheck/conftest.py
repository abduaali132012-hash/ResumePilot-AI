"""
conftest.py for tests/speccheck/ — automatically loaded by pytest.

Guarantees no API key leaks into the test process and exposes
the fake_client_factory fixture.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Ensure the repo root is on sys.path regardless of how pytest is invoked.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ------------------------------------------------------------------ #
# Guarantee no API key is visible to the test process.
# ------------------------------------------------------------------ #
os.environ.pop("GOOGLE_API_KEY", None)
os.environ.pop("GEMINI_API_KEY", None)


@pytest.fixture
def fake_client_factory():
    """Return a factory that builds a FakeClient for any JSON payload."""
    from tests.speccheck.helpers import FakeClient

    def _make(data):
        return FakeClient(data)
    return _make
