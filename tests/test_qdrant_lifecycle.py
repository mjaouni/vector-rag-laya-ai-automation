"""Regression tests for Qdrant explicit shutdown, without loading ML models."""
from functools import lru_cache
import sys
import pytest
import cli
from service import retrieval


def test_close_qdrant_only_closes_opened_cache(monkeypatch):
    class FakeClient:
        closes = 0
        def close(self):
            self.closes += 1

    fake = FakeClient()
    @lru_cache(maxsize=1)
    def fake_qdrant():
        return fake

    monkeypatch.setattr(retrieval, "qdrant", fake_qdrant)
    retrieval.close_qdrant()  # No client yet. Do not open one just to close it.
    assert fake_qdrant.cache_info().currsize == 0

    fake_qdrant()
    retrieval.close_qdrant()
    assert fake.closes == 1
    assert fake_qdrant.cache_info().currsize == 0
    retrieval.close_qdrant()
    assert fake.closes == 1


def test_cli_closes_cache_after_success(monkeypatch, capsys):
    events = []
    monkeypatch.setattr(cli, "seed", lambda: events.append("seed") or {"documents": 7})
    monkeypatch.setattr(cli, "close_qdrant", lambda: events.append("close"))
    monkeypatch.setattr(sys, "argv", ["cli.py", "seed"])
    cli.main()
    assert events == ["seed", "close"]
    assert "documents" in capsys.readouterr().out


def test_cli_closes_cache_after_failure(monkeypatch):
    events = []
    def fail():
        events.append("seed")
        raise ValueError("model error")
    monkeypatch.setattr(cli, "seed", fail)
    monkeypatch.setattr(cli, "close_qdrant", lambda: events.append("close"))
    monkeypatch.setattr(sys, "argv", ["cli.py", "seed"])
    with pytest.raises(ValueError, match="model error"):
        cli.main()
    assert events == ["seed", "close"]
