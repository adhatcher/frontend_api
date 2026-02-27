"""Tests for frontend_app Flask routes and behavior."""

from __future__ import annotations

import frontend_app
from requests import RequestException


class _FakeResponse:
    """Simple fake response object for mocked backend calls."""

    def __init__(self, payload: dict, raise_error: Exception | None = None):
        self._payload = payload
        self._raise_error = raise_error

    def raise_for_status(self):
        if self._raise_error:
            raise self._raise_error

    def json(self):
        return self._payload


def test_healthz_ok(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_home_renders_landing_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Phrase Pulse" in response.data


def test_get_phrase_success(client, monkeypatch):
    fake_payload = {"phrase": "Ship it.", "selection_time": 0.02}

    def _fake_get(url, timeout):  # noqa: ANN001
        assert isinstance(url, str)
        assert timeout == frontend_app.REQUEST_TIMEOUT_SECONDS
        return _FakeResponse(fake_payload)

    monkeypatch.setattr(frontend_app.session, "get", _fake_get)

    response = client.get("/get_phrase")
    assert response.status_code == 200
    assert b"Ship it." in response.data
    assert b"Selection Time" in response.data
    assert b"Frontend Time" in response.data


def test_get_phrase_backend_failure(client, monkeypatch):
    def _fake_get(_url, **_kwargs):  # noqa: ANN001
        return _FakeResponse({}, raise_error=RequestException("backend unavailable"))

    monkeypatch.setattr(frontend_app.session, "get", _fake_get)

    response = client.get("/get_phrase")
    assert response.status_code == 502
    assert b"Backend service unavailable. Please try again." in response.data


def test_metrics_endpoint_exposes_prometheus_payload(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"frontend_request_count" in response.data


def test_security_headers_applied(client):
    response = client.get("/healthz")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_resolve_base_dir_uses_current_dir_when_templates_exist(tmp_path):
    app_dir = tmp_path / "app"
    templates_dir = app_dir / "templates"
    templates_dir.mkdir(parents=True)

    resolved = frontend_app._resolve_base_dir(app_dir)
    assert resolved == app_dir


def test_resolve_base_dir_falls_back_to_parent_when_templates_absent(tmp_path):
    repo_root = tmp_path / "repo"
    src_dir = repo_root / "src"
    src_dir.mkdir(parents=True)
    (repo_root / "templates").mkdir(parents=True)

    resolved = frontend_app._resolve_base_dir(src_dir)
    assert resolved == repo_root
    assert (resolved / "templates").exists()
