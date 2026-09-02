from customer_service_agent.knowledge.cleaner import clean_text, is_boilerplate


def test_clean_text_normalizes_whitespace() -> None:
    assert clean_text("Step 1\n\n  Click  here") == "Step 1 Click here"
    assert clean_text("  leading and trailing  ") == "leading and trailing"


def test_is_boilerplate_detects_phrases_case_insensitive() -> None:
    assert is_boilerplate("Was this page helpful? Yes") is True
    assert is_boilerplate("LAST UPDATED: March 2026") is True
    assert is_boilerplate("Learn how to refund an order") is False
