from issuepilot.triage import classify, extract_severity, triage_issue


def test_classifies_question_and_feature_request():
    assert classify("How do I reset a password?") == "question"
    assert classify("Please add export support") == "feature_request"
    assert classify("Checkout crashes") == "bug"


def test_extracts_severity():
    assert extract_severity("Production down for all users") == "critical"
    assert extract_severity("Checkout crashes") == "high"
    assert extract_severity("A minor typo") == "low"


def test_triage_extracts_cart_component_and_reproduction():
    report = triage_issue("X-1", "Cart subtotal", "- Add item\nExpected: 10\nActual: 0")
    assert report.component == "cart"
    assert report.reproduction_steps == ["Add item"]
    assert report.expected == "10"
    assert report.actual == "0"
