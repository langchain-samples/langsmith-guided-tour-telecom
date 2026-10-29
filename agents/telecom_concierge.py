"""Northwind Mobile concierge — a deepagents deep agent (no HITL).

Tools are mocked in-memory (no external APIs). The agent's instructions and
skills are pulled from LangSmith Context Hub at build time (see build_* below).

One intentional defect powers the failure-mode demo: the hub AGENTS.md tells
the agent to answer prices/speeds from memory. It is deliberate — not a real bug.
get_customer_account masks identity/payment fields and never returns the CVV.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from deepagents import create_deep_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

from utils.context_hub import pull_agent_instructions, pull_skills_to_disk
from utils.mock_data import CUSTOMERS, PLANS, search_docs
from utils.models import model


def _last4(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())[-4:]


def _mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}"


def _format_account(rec: dict) -> str:
    c = rec["card"]
    return (
        f"Account {rec['account_id']} — {rec['name']}\n"
        f"Plan: {rec['plan']} | Device: {rec['device']} (IMEI {rec['imei']})\n"
        f"Balance: ${rec['balance_usd']:.2f} | Data used: {rec['data_used_gb']} GB\n"
        f"SSN: ***-**-{_last4(rec['ssn'])} | Phone: ***-***-{_last4(rec['phone'])} "
        f"| Email: {_mask_email(rec['email'])}\n"
        f"Card on file: {c['brand']} ending {_last4(c['number'])} exp {c['exp']}"
    )


@tool(parse_docstring=True)
def get_customer_account(account_id: str) -> str:
    """Look up a customer's account: plan, device, balance, and masked identity/payment fields.

    Args:
        account_id: Account identifier, e.g. 'ACCT-1001'.
    """
    rec = CUSTOMERS.get(account_id.strip().upper())
    if rec is None:
        return f"No account found for '{account_id}'. Known: {', '.join(CUSTOMERS)}"
    return _format_account(rec)


@tool(parse_docstring=True)
def get_data_usage(account_id: str) -> str:
    """Return current billing-cycle data usage for an account.

    Args:
        account_id: Account identifier, e.g. 'ACCT-1001'.
    """
    rec = CUSTOMERS.get(account_id.strip().upper())
    if rec is None:
        return f"No account found for '{account_id}'."
    cap = "unlimited" if rec["data_cap_gb"] is None else f"{rec['data_cap_gb']} GB"
    return f"{rec['account_id']} used {rec['data_used_gb']} GB this cycle (cap: {cap})."


@tool(parse_docstring=True)
def check_network_status(zip_code: str) -> str:
    """Check network / outage status for a 5-digit US ZIP code.

    Args:
        zip_code: A 5-digit US ZIP code, e.g. '94105'.
    """
    z = zip_code.strip()
    if not (z.isdigit() and len(z) == 5):
        return f"'{zip_code}' is not a valid 5-digit ZIP code."
    # Deterministic mock: ZIPs ending in 0 have a partial outage.
    if z.endswith("0"):
        return f"ZIP {z}: PARTIAL OUTAGE — degraded 5G, voice unaffected. ETA 2h."
    return f"ZIP {z}: all systems normal. 5G and voice fully operational."


@tool(parse_docstring=True)
def search_support_docs(query: str) -> str:
    """Search Northwind Mobile support docs for policies, fees, and plan info.

    Args:
        query: What to look up, e.g. 'international roaming'.
    """
    hits = search_docs(query)
    if not hits:
        return "I couldn't find anything in the support docs for that query."
    return "\n\n".join(hits)


# Local fallbacks used when Context Hub is unreachable (keeps the notebook runnable offline).
_LOCAL_SKILLS_DIR = str(Path(__file__).resolve().parent / "deployable" / "skills")
_SEED_AGENTS_MD = (Path(__file__).resolve().parent / "deployable" / "AGENTS.md").read_text()

network_diagnostics_subagent = {
    "name": "network-diagnostics",
    "description": "Delegate deep device/network troubleshooting. Give one issue at a time.",
    "system_prompt": (
        f"You are a Northwind Mobile network diagnostics specialist. "
        f"Today is {datetime.now().strftime('%Y-%m-%d')}.\n"
        "Walk through likely causes of a connectivity issue (coverage, device settings, "
        "SIM/eSIM, outage) and give concrete steps. Use check_network_status when a ZIP is known."
    ),
    "tools": [check_network_status, search_support_docs],
}


def build_telecom_concierge(pull_from_hub: bool = True, with_checkpointer: bool = True,
                            system_prompt: str | None = None):
    """Build a fresh Northwind Mobile concierge deep agent (no HITL).

    system_prompt   -> if given, use it directly (used for A/B prompt variants); skills stay local.
    pull_from_hub=True -> otherwise pull instructions + skills from LangSmith Context Hub
                          (falls back to local seed files if the hub is unreachable).
    with_checkpointer=True -> include MemorySaver (notebook multi-turn). The deployable
                          build passes False; the langgraph server injects persistence.
    """
    if system_prompt is not None:
        prompt = system_prompt
        skills_dir = _LOCAL_SKILLS_DIR
    elif pull_from_hub:
        prompt = pull_agent_instructions(fallback=_SEED_AGENTS_MD)
        try:
            skills_dir = pull_skills_to_disk()
        except Exception:
            skills_dir = _LOCAL_SKILLS_DIR
    else:
        prompt = _SEED_AGENTS_MD
        skills_dir = _LOCAL_SKILLS_DIR

    kwargs = dict(
        model=model,
        tools=[get_customer_account, get_data_usage, check_network_status, search_support_docs],
        system_prompt=prompt,
        subagents=[network_diagnostics_subagent],
        skills=[skills_dir],
    )
    if with_checkpointer:
        kwargs["checkpointer"] = MemorySaver()
    return create_deep_agent(**kwargs)
