"""Tests for security remediation agent pagination behavior."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "security_remediation_agent.py"
SPEC = importlib.util.spec_from_file_location("security_remediation_agent", SCRIPT_PATH)
assert SPEC and SPEC.loader
AGENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AGENT)


def test_extract_next_link_url_returns_none_without_next() -> None:
    link_header = '<https://api.github.com/repos/a/b/dependabot/alerts?after=abc>; rel="prev"'
    assert AGENT._extract_next_link_url(link_header) is None


def test_extract_next_link_url_finds_next() -> None:
    link_header = (
        '<https://api.github.com/repos/a/b/dependabot/alerts?before=xyz>; rel="prev", '
        '<https://api.github.com/repos/a/b/dependabot/alerts?after=abc>; rel="next"'
    )
    assert (
        AGENT._extract_next_link_url(link_header)
        == "https://api.github.com/repos/a/b/dependabot/alerts?after=abc"
    )


def test_fetch_open_alerts_uses_link_header_pagination(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_api_get_json_with_headers(repo, token, path, params=None, url=None):
        calls.append({"repo": repo, "token": token, "path": path, "params": params, "url": url})
        if len(calls) == 1:
            return (
                [{"number": 1}, {"number": 2}],
                {
                    "Link": (
                        '<https://api.github.com/repos/adhatcher/frontend_api/dependabot/alerts?after=cursor-1>; '
                        'rel="next"'
                    )
                },
            )
        return ([{"number": 3}], {})

    monkeypatch.setattr(AGENT, "_api_get_json_with_headers", fake_api_get_json_with_headers)

    alerts = AGENT._fetch_open_alerts("adhatcher/frontend_api", "test-token")

    assert alerts == [{"number": 1}, {"number": 2}, {"number": 3}]
    assert calls[0]["params"] == {"state": "open", "per_page": 100}
    assert calls[0]["url"] is None
    assert calls[1]["params"] is None
    assert calls[1]["url"] == "https://api.github.com/repos/adhatcher/frontend_api/dependabot/alerts?after=cursor-1"
