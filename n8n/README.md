# n8n workflow: SOC Incident Triage Pipeline

[`soc_triage_workflow.json`](soc_triage_workflow.json) is a ready-to-import
n8n workflow that implements the same detect → enrich → score → ticket logic
as the Python package in [`src/socpipeline/`](../src/socpipeline/) — pick
whichever fits your stack; a no-code SOC can run this entirely in n8n.

## Nodes

| # | Node | What it does |
|---|------|---------------|
| 1 | **Splunk Alert Webhook** | `POST /webhook/splunk-alert` — receives the JSON body Splunk's Webhook alert action sends. |
| 2 | **Normalize Alert** (Code) | Flattens Splunk's `result`/`results` nesting into flat fields: `rule_name`, `host`, `user`, `src_ip`, `file_hash`, `_time`. |
| 3 | **VirusTotal Lookup** (HTTP Request) | `GET /api/v3/files/{file_hash}` against VirusTotal, using an `httpHeaderAuth` credential for the `x-apikey` header. "Never Error" is enabled so an unseen hash (404) doesn't halt the run. |
| 4 | **AbuseIPDB Lookup** (HTTP Request) | `GET /api/v2/check?ipAddress=...` against AbuseIPDB, using an `httpHeaderAuth` credential for the `Key` header. Reads `src_ip` from the **Normalize Alert** node directly, since this node's own `$json` at this point is the VirusTotal response. |
| 5 | **Score Alert** (Code) | Combines both enrichment results into a 0–100 risk score and a severity (`INFO`/`LOW`/`MEDIUM`/`HIGH`/`CRITICAL`), mirroring [`socpipeline/scoring.py`](../src/socpipeline/scoring.py) exactly so both implementations agree. |
| 6 | **Should Create Ticket?** (IF) | Branches on `should_create_ticket` (score ≥ 40). |
| 7 | **Build Jira Payload** (Code) | Builds the Jira REST API v3 issue body (ADF description, priority, labels) — true branch only. |
| 8 | **Create Jira Ticket** (HTTP Request) | `POST /rest/api/3/issue` against Jira Cloud, using an `httpBasicAuth` credential (email + API token). |
| 9 | **Below Threshold – Log Only** (No Op) | False branch — the run still shows up in n8n's execution log for audit purposes, just without a ticket. |

## Import

1. In n8n: **Workflows > Import from File**, select `soc_triage_workflow.json`.
2. Create three credentials (n8n **Credentials** tab) and attach them to the
   matching HTTP Request nodes:
   - **VirusTotal API Key** — Header Auth, name `x-apikey`, value your VT API key.
   - **AbuseIPDB API Key** — Header Auth, name `Key`, value your AbuseIPDB API key.
   - **Jira Cloud API** — Basic Auth, username = your Atlassian account email,
     password = your [Jira API token](https://id.atlassian.com/manage-profile/security/api-tokens).
3. Set the `JIRA_BASE_URL` and `JIRA_PROJECT_KEY` environment variables on
   your n8n instance (or hardcode them in the **Create Jira Ticket** /
   **Build Jira Payload** nodes if you don't control n8n's environment).
4. Activate the workflow and copy its production webhook URL into Splunk —
   see [`../splunk/alert_webhook_setup.md`](../splunk/alert_webhook_setup.md).

## Adjusting the scoring threshold

The ticket-creation cutoff (score ≥ 40) is hardcoded in the **Score Alert**
node's `should_create_ticket` field and in the **Should Create Ticket?** IF
condition. Change both together, and keep them in sync with
`TICKET_THRESHOLD_SCORE` in [`socpipeline/scoring.py`](../src/socpipeline/scoring.py)
if you're running both implementations side by side.
