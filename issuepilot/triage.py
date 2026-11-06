"""Deterministic starter triage; no model calls or hidden service required."""

import re
from .models import IssueReport

KIND_TERMS = {
    "question": ("how do", "how can", "why does", "question", "help"),
    "feature_request": ("feature", "please add", "would be nice", "support for", "request"),
}


def classify(text: str) -> str:
    normalized = text.lower()
    for kind, terms in KIND_TERMS.items():
        if any(term in normalized for term in terms):
            return kind
    return "bug"


def extract_severity(text: str) -> str:
    normalized = text.lower()
    if any(word in normalized for word in ("data loss", "security", "all users", "production down")):
        return "critical"
    if any(word in normalized for word in ("crash", "blocked", "cannot", "can't", "fails")):
        return "high"
    if "slow" in normalized or "intermittent" in normalized:
        return "medium"
    if "minor" in normalized or "typo" in normalized:
        return "low"
    return "unknown"


def triage_issue(issue_id: str, title: str, description: str) -> IssueReport:
    """Create a structured report using simple, inspectable keyword rules."""
    text = f"{title}\n{description}"
    component = "cart" if re.search(r"\b(cart|subtotal|price|checkout)\b", text, re.I) else "unknown"
    steps = [line.strip(" -*\t") for line in description.splitlines() if line.strip().startswith(("-", "*"))]
    expected = ""
    actual = ""
    for line in description.splitlines():
        lower = line.lower()
        if lower.startswith("expected:"):
            expected = line.split(":", 1)[1].strip()
        elif lower.startswith("actual:"):
            actual = line.split(":", 1)[1].strip()
    if not steps:
        steps = ["Reproduction steps were not supplied; ask the reporter to provide them."]
    return IssueReport(issue_id, title, description, classify(text), extract_severity(text), component, steps, expected, actual)
