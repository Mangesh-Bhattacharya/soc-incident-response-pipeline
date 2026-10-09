#!/usr/bin/env python3
"""CLI for running the SOC triage pipeline against a Splunk alert JSON file.

Examples:
    python cli.py --alert examples/sample_splunk_alert.json --dry-run
    python cli.py --alert examples/sample_splunk_alert.json --json
    python cli.py --calibrate examples/calibration_corpus.json
    REDACT_SALT=<secret> python cli.py --alert alert.json --dry-run --json --redact
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from socpipeline import process_alert
from socpipeline.calibration import evaluate, load_corpus
from socpipeline.redact import redact_result


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
    parser.add_argument(
        "--calibrate",
        metavar="CORPUS",
        help="Score a labelled corpus JSON file and print a confusion matrix instead of processing an alert",
    )
    parser.add_argument(
        "--redact",
        action="store_true",
        help="Pseudonymise users, hosts and private IPs in the output so it is safe to share "
        "(salt from REDACT_SALT, or random per run). Unknown alert fields are dropped.",
    )
    args = parser.parse_args()

    if args.calibrate:
        try:
            cases = load_corpus(args.calibrate)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"Cannot load corpus {args.calibrate}: {exc}", file=sys.stderr)
            return 2
        print(evaluate(cases).render())
        return 0

    try:
        alert = json.loads(Path(args.alert).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Alert file not found: {args.alert}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in {args.alert}: {exc}", file=sys.stderr)
        return 2

    result = process_alert(alert, dry_run=args.dry_run or args.redact)
    if args.redact:
        salt = os.environ.get("REDACT_SALT", "").encode()
        if not salt:
            salt = secrets.token_bytes(32)
            print("REDACT_SALT not set: tokens are random per run and will not match across runs", file=sys.stderr)
        result = redact_result(result, salt)
        alert = result["alert"]

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    score = result["score"]
    print(f"Rule:      {alert.get('rule_name', 'unknown')}")
    print(f"Host/User: {alert.get('host', 'unknown')} / {alert.get('user', 'unknown')}")
    print(f"Score:     {score['score']}/100  ({score['severity']})")
    for reason in score["reasons"]:
        print(f"  - {reason}")
    if score.get("enrichment_failed"):
        print("  ! Enrichment incomplete: treat the score as a lower bound, not a clean verdict", file=sys.stderr)

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
