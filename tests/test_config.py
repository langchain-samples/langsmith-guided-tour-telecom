from utils.config import project_for, PROJECT_BASE, _slugify


def test_slugify_basic():
    assert _slugify("Christine A") == "christine-a"
    assert _slugify("  Bob!! ") == "bob"
    assert _slugify("") == "anon"


def test_project_for_appends_slug():
    assert project_for("Christine A") == f"{PROJECT_BASE}-christine-a"


def test_project_for_defaults_to_anon_when_blank(monkeypatch):
    monkeypatch.delenv("USER", raising=False)
    assert project_for("") == f"{PROJECT_BASE}-anon"
