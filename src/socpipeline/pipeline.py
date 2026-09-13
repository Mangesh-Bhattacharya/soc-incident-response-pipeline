"""End-to-end orchestration: Splunk alert -> enrichment -> scoring -> Jira ticket.

This is the Python equivalent of the n8n workflow in `n8n/soc_triage_workflow.json`
— use whichever fits your stack. Both consume the same alert JSON shape (see
`examples/sample_splunk_alert.json`) and apply the same scoring rules.
"""
from __future__ import annotations

from .abuseipdb import check_ip
from .jira_client import create_incident_ticket
from .scoring import JIRA_PRIORITY, score_alert
from .virustotal import check_file_hash


def process_alert(alert: dict, dry_run: bool = False) -> dict:
    """Run the full detect -> enrich -> score -> ticket pipeline for one alert.

    `alert` is expected to carry the fields Splunk's webhook alert action sends
    (see `splunk/alert_webhook_setup.md`): `rule_name`, `host`, `user`, `src_ip`
    and/or `file_hash` are read if present; anything else is passed through.

    With `dry_run=True`, enrichment and scoring still run for real, but no Jira
    ticket is created — the ticket that *would* be filed is returned instead so
    you can inspect the pipeline's output without live Jira credentials.
    """
    result: dict = {"alert": alert, "enrichment": {}}

    vt_result = None
    if file_hash := alert.get("file_hash"):
        vt_result = check_file_hash(file_hash)
        result["enrichment"]["virustotal"] = vt_result.to_dict()

    abuse_result = None
    if src_ip := alert.get("src_ip"):
        abuse_result = check_ip(src_ip)
        result["enrichment"]["abuseipdb"] = abuse_result.to_dict()

    score = score_alert(vt_result, abuse_result)
    result["score"] = score.to_dict()

    if not score.should_create_ticket:
        result["ticket"] = {"created": False, "reason": "Below ticket-creation threshold"}
        return result

    summary = f"[{score.severity.value}] {alert.get('rule_name', 'SOC Alert')} — {alert.get('host', 'unknown host')}"
    description_lines = [
        f"Detected by rule: {alert.get('rule_name', 'unknown')}",
        f"Host: {alert.get('host', 'unknown')}   User: {alert.get('user', 'unknown')}",
        f"Risk score: {score.score}/100 ({score.severity.value})",
        *score.reasons,
        f"Raw alert time: {alert.get('_time', 'unknown')}",
    ]
    priority = JIRA_PRIORITY[score.severity.value]

    if dry_run:
        result["ticket"] = {
            "created": False,
            "dry_run": True,
            "would_create": {"summary": summary, "description": description_lines, "priority": priority},
        }
        return result

    ticket = create_incident_ticket(summary=summary, description_lines=description_lines, priority=priority)
    result["ticket"] = ticket.to_dict()
    return result
