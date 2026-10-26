import re

from utils.mock_data import CUSTOMERS, PLANS, KB_DOCS, search_docs


def test_five_customers_with_synthetic_pii():
    assert len(CUSTOMERS) == 5
    rec = CUSTOMERS["ACCT-1001"]
    # Synthetic SSN in the 552/553 test range, 555 phone, example.com email.
    assert re.match(r"55[23]-\d{2}-\d{4}", rec["ssn"])
    assert "555" in rec["phone"]
    assert rec["email"].endswith("example.com")
    assert rec["card"]["number"].startswith("4242")


def test_plans_present():
    assert "Unlimited Premium" in PLANS
    assert "price_usd" in PLANS["Unlimited Premium"]


def test_search_docs_substring_match_and_miss():
    hits = search_docs("roaming")
    assert any("roaming" in h.lower() for h in hits)
    # Deliberately sparse: no exact promo price doc, so this returns [].
    assert search_docs("zzz-nonexistent-topic") == []
