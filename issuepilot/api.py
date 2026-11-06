"""Optional tiny FastAPI surface for the deterministic triage function."""

from .triage import triage_issue

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ImportError as exc:  # Helpful error when the optional extra is absent.
    raise RuntimeError("Install the optional API dependencies with: pip install -e '.[api]'") from exc

app = FastAPI(title="IssuePilot Demo API")


class IssueInput(BaseModel):
    issue_id: str
    title: str
    description: str


@app.post("/triage")
def triage(payload: IssueInput):
    return triage_issue(payload.issue_id, payload.title, payload.description).to_dict()
