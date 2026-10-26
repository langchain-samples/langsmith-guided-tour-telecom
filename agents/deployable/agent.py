"""Deployable graph for `langgraph dev` / LangSmith Deployments.

No checkpointer: the langgraph server injects thread persistence. Instructions
and skills are pulled from Context Hub at import (local fallback if unreachable).
"""

from agents.telecom_concierge import build_telecom_concierge

agent = build_telecom_concierge(pull_from_hub=True, with_checkpointer=False)
