"""Centralized model init. Swap providers here only.

Default routes Claude Sonnet 4.6 (vision-capable, needed for the multi-modal
example) through the LangSmith LLM Gateway, authenticated with LANGSMITH_API_KEY
— so a single token covers tracing, Context Hub, and model calls. Loads `.env`
from the repo root regardless of cwd so it works from notebooks (cwd=modules/)
and the langgraph server (cwd=root).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env", override=False)

from langchain.chat_models import init_chat_model  # noqa: E402

# --- Default: Anthropic via the LangSmith LLM Gateway (single-token auth) ---
model = init_chat_model(
    model="claude-sonnet-4-6",
    model_provider="anthropic",
    base_url="https://gateway.smith.langchain.com/anthropic",
    api_key=os.environ["LANGSMITH_API_KEY"],
)

# --- Anthropic, direct (requires ANTHROPIC_API_KEY) ---
# model = init_chat_model("anthropic:claude-sonnet-4-6")
