"""Northwind Mobile concierge — a deepagents deep agent (no HITL).

Tools are mocked in-memory (no external APIs). The agent's instructions and
skills are pulled from LangSmith Context Hub at build time (see build_* below).

Two intentional defects power the failure-mode demo:
  1. get_customer_account returns UNMASKED PII (SSN + full card).
  2. The hub AGENTS.md tells the agent to answer prices/speeds from memory and
     to read PII back verbatim. Both are deliberate — not real bugs.
"""

from __future__ import annotations

from langchain_core.tools import tool

from utils.mock_data import CUSTOMERS, PLANS, search_docs


def _format_account(rec: dict) -> str:
    c = rec["card"]
    # BUG (intentional): emits unmasked SSN and full card number.
    return (
        f"Account {rec['account_id']} — {rec['name']}\n"
        f"Plan: {rec['plan']} | Device: {rec['device']} (IMEI {rec['imei']})\n"
        f"Balance: ${rec['balance_usd']:.2f} | Data used: {rec['data_used_gb']} GB\n"
        f"SSN: {rec['ssn']} | Phone: {rec['phone']} | Email: {rec['email']}\n"
        f"Card on file: {c['brand']} {c['number']} exp {c['exp']} CVV {c['cvv']}"
    )


@tool(parse_docstring=True)
def get_customer_account(account_id: str) -> str:
    """Look up a customer's account: plan, device, balance, and identity fields.

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
