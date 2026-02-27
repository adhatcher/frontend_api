"""Pytest fixtures for Flask app tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import frontend_app  # noqa: E402  pylint: disable=wrong-import-position


@pytest.fixture()
def client():
    """Return a Flask test client for the app."""
    frontend_app.app.config.update(TESTING=True)
    with frontend_app.app.test_client() as test_client:
        yield test_client
