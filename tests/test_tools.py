from agents.telecom_concierge import (
    get_customer_account, get_data_usage, check_network_status, search_support_docs,
)
from utils.mock_data import CUSTOMERS


def _invoke(tool, **kwargs):
    # LangChain @tool objects are invoked via .invoke(dict)
    return tool.invoke(kwargs)


def test_account_lookup_masks_identity_and_payment_fields():
    out = _invoke(get_customer_account, account_id="ACCT-1001")
    assert "SSN: ***-**-4488" in out
    assert "552-19-4488" not in out
    assert "Visa ending 4242 exp 08/29" in out
    assert "4242 4242 4242 4242" not in out
    assert "Phone: ***-***-0142" in out
    assert "555-0142" not in out
    assert "Email: a***@example.com" in out
    assert "alex.rivera" not in out


def test_account_lookup_never_returns_cvv_or_full_identifiers():
    for account_id, rec in CUSTOMERS.items():
        out = _invoke(get_customer_account, account_id=account_id)
        assert "CVV" not in out.upper()
        assert f" {rec['card']['cvv']}" not in out
        assert rec["card"]["number"] not in out
        assert rec["ssn"] not in out


def test_account_lookup_unknown():
    out = _invoke(get_customer_account, account_id="ACCT-9999")
    assert "No account" in out


def test_data_usage():
    out = _invoke(get_data_usage, account_id="ACCT-1002")
    assert "18.9" in out


def test_network_status_bad_zip():
    out = _invoke(check_network_status, zip_code="not-a-zip")
    assert "5-digit" in out.lower()


def test_support_docs_hit_and_miss():
    assert "roaming" in _invoke(search_support_docs, query="international roaming").lower()
    assert "couldn't find" in _invoke(search_support_docs, query="zzz-nothing").lower()
