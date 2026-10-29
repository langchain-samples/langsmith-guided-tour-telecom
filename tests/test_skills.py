import logging
from pathlib import Path

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from pydantic import Field

import agents.telecom_concierge as concierge
from agents.telecom_concierge import (
    _LOCAL_SKILLS_DIR,
    SKILLS_ROUTE,
    build_skills_backend,
)

EXPECTED_SKILLS = {"bill-explainer", "plan-comparison", "outage-triage"}


class _ScriptedModel(GenericFakeChatModel):
    """Fake chat model that replays scripted replies and records every prompt it receives."""

    prompts: list = Field(default_factory=list)

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.prompts.append(messages)
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)


def _run(monkeypatch, replies, prompt="hi"):
    fake = _ScriptedModel(messages=iter(replies))
    monkeypatch.setattr(concierge, "model", fake)
    agent = concierge.build_telecom_concierge(pull_from_hub=False, with_checkpointer=False)
    result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    return fake, result


def _system_prompt(fake) -> str:
    return fake.prompts[0][0].text


def _write_skill(root: Path, name: str, content: str) -> None:
    (root / name).mkdir(parents=True)
    (root / name / "SKILL.md").write_text(content)


def test_local_skills_appear_in_agent_prompt(monkeypatch):
    fake, _ = _run(monkeypatch, [AIMessage(content="ok")])
    system = _system_prompt(fake)
    assert "No skills available yet" not in system
    for name in EXPECTED_SKILLS:
        assert f"**{name}**" in system
        assert f"/skills/{name}/SKILL.md" in system
    assert "Explain why a customer's bill changed" in system
    assert "Compare Northwind Mobile plans" in system
    assert "no service / slow data" in system


def test_only_skills_with_frontmatter_are_discovered(monkeypatch, tmp_path):
    _write_skill(tmp_path, "good-skill", "---\nname: good-skill\ndescription: Does a good thing.\n---\n\n# good\n")
    _write_skill(tmp_path, "bare-skill", "# bare-skill\n\n## Purpose\nNo frontmatter here.\n")
    monkeypatch.setattr(concierge, "_LOCAL_SKILLS_DIR", str(tmp_path))
    fake, _ = _run(monkeypatch, [AIMessage(content="ok")])
    system = _system_prompt(fake)
    assert "**good-skill**" in system
    assert "bare-skill" not in system


def test_skills_route_reads_disk_and_other_paths_stay_in_state(monkeypatch):
    replies = [
        AIMessage(content="", tool_calls=[
            {"name": "read_file", "args": {"file_path": "/skills/bill-explainer/SKILL.md"}, "id": "c1"},
            {"name": "write_file", "args": {"file_path": "/notes.txt", "content": "scratch"}, "id": "c2"},
            {"name": "read_file", "args": {"file_path": "/pyproject.toml"}, "id": "c3"},
        ]),
        AIMessage(content="done"),
    ]
    _, result = _run(monkeypatch, replies)
    tool_out = {m.tool_call_id: m.content for m in result["messages"] if m.type == "tool"}
    assert "get_customer_account" in tool_out["c1"]
    assert "[project]" not in tool_out["c3"]
    assert "/notes.txt" in result["files"]
    assert not (Path(_LOCAL_SKILLS_DIR) / "notes.txt").exists()


def test_skills_route_rejects_path_traversal():
    backend = build_skills_backend(_LOCAL_SKILLS_DIR)
    with pytest.raises(ValueError):
        backend.read(f"{SKILLS_ROUTE}../AGENTS.md")


def test_empty_skill_discovery_warns(tmp_path, caplog):
    _write_skill(tmp_path, "bare-skill", "# bare-skill\n")
    with caplog.at_level(logging.WARNING, logger=concierge.__name__):
        build_skills_backend(str(tmp_path))
    assert any("No skills discovered" in r.getMessage() for r in caplog.records)


def test_successful_skill_discovery_does_not_warn(caplog):
    with caplog.at_level(logging.WARNING, logger=concierge.__name__):
        build_skills_backend(_LOCAL_SKILLS_DIR)
    assert not any("No skills discovered" in r.getMessage() for r in caplog.records)
