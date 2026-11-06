"""Local demo workflow. Switch room messages are the collaboration handoff."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from .triage import triage_issue

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_demo(approve: bool = False) -> dict:
    sample = json.loads((DATA / "sample_issue.json").read_text(encoding="utf-8"))
    report = triage_issue(sample["issue_id"], sample["title"], sample["description"])
    save_json(DATA / "triage_result.json", report.to_dict())
    print("[IssuePilot-Triage] Structured report saved to data/triage_result.json")
    print(json.dumps(report.to_dict(), indent=2))

    print("\n[Switch room handoff] Post the triage report in the same room and mention IssuePilot-Repro.")
    print(f"  @IssuePilot-Repro investigate {report.issue_id}; do not edit source without explicit human approval.")

    command = [sys.executable, "-m", "pytest", "-q", "tests/test_cart.py::test_subtotal_includes_first_item"]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    investigation = {
        "issue_id": report.issue_id,
        "command": " ".join(command),
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "root_cause": "subtotal starts its loop at index 1, omitting the first price",
        "approval": {"approved": bool(approve), "recorded_at_utc": datetime.now(timezone.utc).isoformat() if approve else None},
    }
    print("\n[IssuePilot-Repro] Exact reproduction command output:")
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if not result.stdout and not result.stderr:
        print("(no output)")
    print(f"[IssuePilot-Repro] exit code: {result.returncode}")

    if approve:
        if result.returncode == 1 and "No module named pytest" in result.stderr:
            raise RuntimeError("pytest is unavailable; refusing to edit because the pre-fix reproduction did not run.")
        from .sample_app.cart import subtotal
        source = (ROOT / "issuepilot/sample_app/cart.py").read_text(encoding="utf-8")
        old = "for index in range(1, len(prices)):"
        if old not in source:
            raise RuntimeError("Expected seeded bug was not found; refusing an unexpected edit.")
        (ROOT / "issuepilot/sample_app/cart.py").write_text(source.replace(old, "for index in range(0, len(prices)):", 1), encoding="utf-8")
        fixed = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_cart.py"], cwd=ROOT, text=True, capture_output=True)
        if "No module named pytest" in fixed.stderr:
            raise RuntimeError("pytest became unavailable after the edit; install pytest and rerun the full test suite before claiming resolution.")
        investigation["fix"] = {"applied": True, "test_exit_code": fixed.returncode, "stdout": fixed.stdout, "stderr": fixed.stderr, "verified_value": subtotal([12.50, 3.25])}
        report.status = "resolved" if fixed.returncode == 0 else "fix_failed"
        report_data = report.to_dict()
        report_data["status"] = "resolution pending human review" if fixed.returncode == 0 else "fix_failed"
        save_json(DATA / "triage_result.json", report_data)
        print("\n[IssuePilot-Repro] Human approval recorded; fix applied and full cart tests rerun.")
        print(fixed.stdout, end="")
        if fixed.stderr:
            print(fixed.stderr, end="", file=sys.stderr)
        print(f"[IssuePilot-Repro] fix test exit code: {fixed.returncode}")
    else:
        investigation["fix"] = {"applied": False, "reason": "No human approval was supplied; source was left unchanged."}
        print("\n[Approval gate] No fix applied. To approve in the Switch room, follow the README, then rerun: python scripts/demo.py --approved")
    save_json(DATA / "investigation_result.json", investigation)
    return investigation
