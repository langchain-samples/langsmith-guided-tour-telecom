"""Single source of truth for project naming and the active agent.

Each workshop attendee gets their own LangSmith project so traces don't collide:
`project_for("Jane Doe")` -> "telecom-concierge-jane-doe".
"""

import os
import re

PROJECT_BASE = "telecom-concierge"


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
