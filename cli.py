#!/usr/bin/env python3
"""CLI for running the SOC triage pipeline against a Splunk alert JSON file.

Examples:
    python cli.py --alert examples/sample_splunk_alert.json --dry-run
    python cli.py --alert examples/sample_splunk_alert.json --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from socpipeline import process_alert


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect -> Enrich -> Ticket SOC triage pipeline")
    parser.add_argument(
        "--alert",
        default="examples/sample_splunk_alert.json",
        help="Path to a Splunk alert JSON payload (default: examples/sample_splunk_alert.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run enrichment and scoring for real, but skip creating a Jira ticket",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output")
    args = parser.parse_args()

    try:
        alert = json.loads(Path(args.alert).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Alert file not found: {args.alert}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in {args.alert}: {exc}", file=sys.stderr)
        return 2

    result = process_alert(alert, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    score = result["score"]
    print(f"Rule:      {alert.get('rule_name', 'unknown')}")
    print(f"Host/User: {alert.get('host', 'unknown')} / {alert.get('user', 'unknown')}")
    print(f"Score:     {score['score']}/100  ({score['severity']})")
    for reason in score["reasons"]:
        print(f"  - {reason}")

    ticket = result["ticket"]
    if ticket.get("created"):
        print(f"Jira ticket created: {ticket['issue_key']} ({ticket['issue_url']})")
    elif ticket.get("dry_run"):
        print(f"[dry-run] Would create Jira ticket: {ticket['would_create']['summary']}")
    else:
        print(f"No Jira ticket created: {ticket.get('reason') or ticket.get('error')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
