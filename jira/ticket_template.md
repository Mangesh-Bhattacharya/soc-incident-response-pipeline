# Jira incident ticket template

Both the n8n workflow and the Python pipeline generate tickets in this shape.
Reproduced here so a SOC analyst (or whoever configures the Jira project) can
see the field mapping without reading code.

| Field | Source | Example |
|---|---|---|
| **Project** | `JIRA_PROJECT_KEY` env var | `SOC` |
| **Issue type** | Hardcoded | `Incident` |
| **Summary** | `[{severity}] {rule_name} — {host}` | `[CRITICAL] Suspicious File Write — WKS-FIN-0231` |
| **Priority** | Mapped from severity (see below) | `Highest` |
| **Labels** | Hardcoded | `soc-automation` |
| **Description** | Built from the alert + enrichment reasons, see below | — |

## Severity → Jira priority mapping

| Severity | Score range | Jira priority |
|---|---|---|
| CRITICAL | 80–100 | Highest |
| HIGH | 60–79 | High |
| MEDIUM | 40–59 | Medium |
| LOW | 1–39 | Low *(ticket not created — logged only)* |
| INFO | 0 | Lowest *(ticket not created — logged only)* |

Only `MEDIUM` and above create a ticket (`TICKET_THRESHOLD_SCORE = 40` in
[`scoring.py`](../src/socpipeline/scoring.py)) — `LOW`/`INFO` alerts are still
scored and logged for audit trail, just without paging an analyst.

## Example description body

```
Detected by rule: Suspicious File Write
Host: WKS-FIN-0231   User: j.alvarez
Risk score: 88/100 (CRITICAL)
VirusTotal: 58/74 engines flagged 275a021b...51fd0 as malicious
AbuseIPDB: 185.220.101.45 has a 92% abuse confidence score across 341 reports
AbuseIPDB: 185.220.101.45 is a known Tor exit node
Raw alert time: 2026-09-12T03:41:07Z
```

## Suggested Jira automation on top

Once tickets land in the `SOC` project, a couple of Jira automation rules
pair well with this pipeline (configured in Jira itself, not in this repo):

- Auto-assign `Highest`/`High` priority incidents to the on-call SOC analyst
  (via a Jira Automation rule keyed on priority + label `soc-automation`).
- Auto-transition an incident to "Stale" if unassigned 30 minutes after
  creation, to catch on-call paging failures.
