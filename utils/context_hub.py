"""Push/pull the concierge's skills and instructions to/from LangSmith Context Hub.

Repo handles are prefixed to avoid collisions in a shared workspace:
  skills -> "telecom-concierge-<skill>",  agent -> "telecom-concierge-agent".
"""

from __future__ import annotations

from pathlib import Path

from langsmith import Client
from langsmith.schemas import FileEntry

_ROOT = Path(__file__).resolve().parent.parent
_SKILLS_SRC = _ROOT / "agents" / "deployable" / "skills"
_AGENTS_MD = _ROOT / "agents" / "deployable" / "AGENTS.md"

HUB_PREFIX = "telecom-concierge"
SKILL_NAMES = ["bill-explainer", "plan-comparison", "outage-triage"]
AGENT_REPO = f"{HUB_PREFIX}-agent"


def _skill_repo(name: str) -> str:
    return f"{HUB_PREFIX}-{name}"


def push_skills(client: Client | None = None) -> list[str]:
    """Push each local SKILL.md to Context Hub. Idempotent (new commit each run)."""
    client = client or Client()
    urls = []
    for name in SKILL_NAMES:
        content = (_SKILLS_SRC / name / "SKILL.md").read_text()
        urls.append(client.push_skill(
            _skill_repo(name),
            files={"SKILL.md": FileEntry(content=content)},
            description=f"Northwind Mobile concierge {name} skill",
            tags=[HUB_PREFIX],
        ))
    return urls


def push_agent_instructions(client: Client | None = None) -> str:
    """Push the (intentionally buggy) AGENTS.md to Context Hub."""
    client = client or Client()
    content = _AGENTS_MD.read_text()
    return client.push_agent(
        AGENT_REPO,
        files={"AGENTS.md": FileEntry(content=content)},
        description="Northwind Mobile concierge instructions (intentionally buggy, for demo)",
        tags=[HUB_PREFIX],
    )


def pull_skills_to_disk(dest: str = ".context/skills", client: Client | None = None) -> str:
    """Pull each skill from Context Hub and materialize SKILL.md under `dest`.

    Returns the dest directory to pass as `skills=[dest]` to create_deep_agent.
    """
    client = client or Client()
    dest_path = _ROOT / dest
    for name in SKILL_NAMES:
        skill = client.pull_skill(_skill_repo(name))
        content = skill.files["SKILL.md"].content
        d = dest_path / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(content)
    return str(dest_path)


def pull_agent_instructions(fallback: str = "", client: Client | None = None) -> str:
    """Pull AGENTS.md content from Context Hub; return `fallback` if unavailable."""
    client = client or Client()
    try:
        agent = client.pull_agent(AGENT_REPO)
        content = agent.files["AGENTS.md"].content
        if content:
            return content
    except Exception:
        pass
    return fallback


# --------------------------------------------------------------------------- #
# A/B prompt variants (Module 3) — each variant is its own Context Hub agent repo.
# --------------------------------------------------------------------------- #

def _variant_repo(name: str) -> str:
    return f"{HUB_PREFIX}-agent-{name}"


def push_agent_variant(name: str, content: str, client: Client | None = None) -> str:
    """Push one A/B prompt variant to Context Hub as `telecom-concierge-agent-<name>`."""
    client = client or Client()
    return client.push_agent(
        _variant_repo(name),
        files={"AGENTS.md": FileEntry(content=content)},
        description=f"Northwind Mobile concierge — A/B prompt variant: {name}",
        tags=[HUB_PREFIX, "ab-test"],
    )


def pull_agent_variant(name: str, fallback: str = "", client: Client | None = None) -> str:
    """Pull an A/B prompt variant's AGENTS.md content from Context Hub."""
    client = client or Client()
    try:
        agent = client.pull_agent(_variant_repo(name))
        content = agent.files["AGENTS.md"].content
        if content:
            return content
    except Exception:
        pass
    return fallback
