from agents.telecom_concierge import (
    get_customer_account, get_data_usage, check_network_status, search_support_docs,
)


def _invoke(tool, **kwargs):
    # LangChain @tool objects are invoked via .invoke(dict)
    return tool.invoke(kwargs)


def test_account_lookup_leaks_pii_by_design():
    out = _invoke(get_customer_account, account_id="ACCT-1001")
    # Intentional bug: unmasked SSN + full card appear in the tool output.
    assert "552-19-4488" in out
    assert "4242 4242 4242 4242" in out


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
