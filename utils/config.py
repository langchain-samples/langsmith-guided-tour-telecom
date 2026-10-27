"""Single source of truth for project naming and the active agent.

Each workshop attendee gets their own LangSmith project so traces don't collide:
`project_for("Jane Doe")` -> "telecom-concierge-jane-doe".
"""

import os
import re
from pathlib import Path

PROJECT_BASE = "telecom-concierge"

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (name or "").strip().lower()).strip("-")
    return slug or "anon"


def project_for(username: str | None = None) -> str:
    """Return the per-user LangSmith project name."""
    username = username if (username and username.strip()) else os.environ.get("USER", "")
    return f"{PROJECT_BASE}-{_slugify(username)}"


def load_active_agent():
    """Return a freshly built telecom concierge agent (notebook/seeding use)."""
    from agents.telecom_concierge import build_telecom_concierge
    return build_telecom_concierge()


def persist_project(project_name: str, env_path: Path | None = None) -> None:
    """Upsert LANGSMITH_PROJECT in `.env`.

    The notebook sets the project in its own process via os.environ, but
    `langgraph dev` is a separate process that reads `.env`. Writing the project
    here makes the dev server trace into the same project. Other lines are
    preserved; (re)start `langgraph dev` after calling this to pick up the change.
    """
    env_path = env_path or _ENV_PATH
    lines = env_path.read_text().splitlines() if env_path.exists() else []
    out, found = [], False
    for ln in lines:
        if ln.startswith("LANGSMITH_PROJECT="):
            out.append(f"LANGSMITH_PROJECT={project_name}")
            found = True
        else:
            out.append(ln)
    if not found:
        out.append(f"LANGSMITH_PROJECT={project_name}")
    env_path.write_text("\n".join(out) + "\n")
