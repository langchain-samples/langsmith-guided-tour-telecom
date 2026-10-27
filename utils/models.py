"""Centralized model init. Swap providers / endpoints here only.

Default: Anthropic Claude Sonnet 4.6 (vision-capable, needed for the multi-modal
example) using your own `ANTHROPIC_API_KEY`.

Optional: set `MODEL_BASE_URL` to route calls through your own gateway endpoint
(any OpenAI/Anthropic-compatible proxy). Leave it unset to call Anthropic directly.
Override the model with `MODEL_NAME`.

Loads `.env` from the repo root regardless of cwd so it works from notebooks
(cwd=modules/) and the langgraph server (cwd=root).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env", override=False)

from langchain.chat_models import init_chat_model  # noqa: E402

MODEL_NAME = os.environ.get("MODEL_NAME", "claude-sonnet-4-6")
_BASE_URL = os.environ.get("MODEL_BASE_URL")  # optional: your own gateway endpoint

if _BASE_URL:
    # Route through your own gateway/proxy.
    model = init_chat_model(
        model=MODEL_NAME,
        model_provider="anthropic",
        base_url=_BASE_URL,
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )
else:
    # Direct to Anthropic using ANTHROPIC_API_KEY.
    model = init_chat_model(f"anthropic:{MODEL_NAME}")


def anthropic_client_args() -> dict:
    """client_args for the raw Anthropic SDK (used by Strands / OTEL cells).

    Includes base_url only when MODEL_BASE_URL is set, so the same code works
    direct-to-Anthropic or through your own gateway.
    """
    args = {"api_key": os.environ["ANTHROPIC_API_KEY"]}
    if _BASE_URL:
        args["base_url"] = _BASE_URL
    return args
