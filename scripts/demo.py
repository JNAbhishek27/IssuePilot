#!/usr/bin/env python3
"""Run IssuePilot's local reproduction and optional approved-fix demo."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from issuepilot.workflow import run_demo

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--approved", action="store_true", help="record the human approval and apply the demo fix")
args = parser.parse_args()
run_demo(approve=args.approved)
