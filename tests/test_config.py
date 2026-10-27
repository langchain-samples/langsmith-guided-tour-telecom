from pathlib import Path

from utils.config import project_for, PROJECT_BASE, _slugify, persist_project


def test_slugify_basic():
    assert _slugify("Christine A") == "christine-a"
    assert _slugify("  Bob!! ") == "bob"
    assert _slugify("") == "anon"


def test_project_for_appends_slug():
    assert project_for("Christine A") == f"{PROJECT_BASE}-christine-a"


def test_project_for_defaults_to_anon_when_blank(monkeypatch):
    monkeypatch.delenv("USER", raising=False)
    assert project_for("") == f"{PROJECT_BASE}-anon"


def test_persist_project_upserts(tmp_path):
    env = tmp_path / ".env"
    env.write_text("LANGSMITH_API_KEY=abc\nLANGSMITH_PROJECT=old\nMODEL_NAME=x\n")
    persist_project("telecom-concierge-jane", env_path=env)
    body = env.read_text()
    assert "LANGSMITH_PROJECT=telecom-concierge-jane" in body
    assert "LANGSMITH_PROJECT=old" not in body
    assert "LANGSMITH_API_KEY=abc" in body  # other lines preserved
    assert "MODEL_NAME=x" in body


def test_persist_project_appends_when_missing(tmp_path):
    env = tmp_path / ".env"
    env.write_text("LANGSMITH_API_KEY=abc\n")
    persist_project("telecom-concierge-bob", env_path=env)
    assert "LANGSMITH_PROJECT=telecom-concierge-bob" in env.read_text()
