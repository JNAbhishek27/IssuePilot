"""Typed data structures shared by triage and investigation code."""

from dataclasses import asdict, dataclass
from typing import Literal

IssueKind = Literal["bug", "question", "feature_request"]
Severity = Literal["low", "medium", "high", "critical", "unknown"]


@dataclass
class IssueReport:
    issue_id: str
    title: str
    description: str
    kind: IssueKind
    severity: Severity
    component: str
    reproduction_steps: list[str]
    expected: str
    actual: str
    status: str = "triaged"

    def to_dict(self) -> dict:
        return asdict(self)
