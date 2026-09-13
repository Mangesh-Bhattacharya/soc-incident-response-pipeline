# SOC Incident Response & Threat Enrichment Pipeline 🛡️

[![CI](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)

An automated SOC triage pipeline that takes a raw Splunk detection, enriches
its indicators against threat-intel APIs, scores the result, and — only when
it's actually worth an analyst's time — opens a Jira incident with the
evidence already attached.

**Detect → Enrich → Score → Ticket.**

```
Splunk  ──webhook──▶  n8n  ──▶  VirusTotal (file hash)
                        │  ──▶  AbuseIPDB  (source IP)
                        │
                        ▼
                  risk score + severity
                        │
                 score ≥ 40? ──▶  Jira incident ticket
```

See [`docs/architecture.md`](docs/architecture.md) for the full diagram and
design notes.

## Why This Exists

A SOC analyst's first 10 minutes on every alert look the same: copy the file
hash into VirusTotal, copy the source IP into AbuseIPDB, decide if it's worth
escalating, then manually type up a Jira ticket if it is. That's mechanical
work an alert pipeline should do before a human ever sees it — not because
analysts can't do it, but because doing it by hand doesn't scale past a
handful of alerts a day, and it's exactly the kind of repetitive, well-defined
task automation is good at. This project automates that first pass so
analysts spend their time on judgment calls, not data entry.

## Components

| Layer | Tool | Role |
|---|---|---|
| **Detect** | Splunk | Scheduled SPL searches flag suspicious activity (brute-force auth, malware file writes, C2 beaconing, watchlisted IPs) and fire a webhook alert action. |
| **Orchestrate** | n8n | Receives the webhook, calls both enrichment APIs, scores the alert, and branches to ticket-creation or log-only. |
| **Enrich (files)** | VirusTotal | Reputation lookup for file hashes — how many AV engines flag it malicious. |
| **Enrich (network)** | AbuseIPDB | Reputation lookup for source IPs — abuse confidence score, Tor exit node status. |
| **Ticket** | Jira | Auto-creates a prioritized `Incident` issue, with the enrichment evidence already in the description, for anything that crosses the scoring threshold. |

This repo ships **two equivalent implementations** of the same logic — pick
whichever fits your stack:

- **[`n8n/soc_triage_workflow.json`](n8n/soc_triage_workflow.json)** — an
  importable, no-code n8n workflow.
- **[`src/socpipeline/`](src/socpipeline/)** — a plain Python package with the
  identical detect → enrich → score → ticket logic, runnable via
  [`cli.py`](cli.py) or importable into your own service.

...plus a **[`dashboard/`](dashboard/)** — an animated React + TypeScript
console that visualizes either one running. Click a queued alert and watch it
move through the pipeline: nodes lighting up, a risk gauge counting up,
enrichment cards animating in, and a Jira ticket (or "logged only") outcome
at the end. Demo mode needs no backend at all — every number is precomputed
with the same scoring rubric as `scoring.py` — or point it at the optional
[`api/`](api/main.py) FastAPI wrapper to animate the real pipeline's output
instead.

## Quick start

### Option A: Docker (recommended — works the same on Linux, macOS, Windows)

```bash
cp .env.example .env      # fill in VT_API_KEY / ABUSEIPDB_API_KEY / JIRA_* — or leave blank for demo mode
docker compose up --build
```

Open **http://localhost:8080** — the animated dashboard, wired live to the
real Python pipeline behind an nginx reverse proxy, no Python/Node.js
install needed on the host. Bound to `127.0.0.1` by default, so this doesn't
need a firewall exception on any OS; see [`docs/docker.md`](docs/docker.md)
for the full security rationale and how to opt into LAN access.

### Option B: Python pipeline

```bash
pip install -r requirements-dev.txt
cp .env.example .env   # fill in VT_API_KEY, ABUSEIPDB_API_KEY, JIRA_* — or leave blank for --dry-run

python cli.py --alert examples/sample_splunk_alert.json --dry-run
```

The bundled sample alert uses the [EICAR test file hash](https://en.wikipedia.org/wiki/EICAR_test_file)
(universally flagged malicious by every AV engine on VirusTotal, but
harmless) and a known Tor exit-node IP range, so a real run against live
VirusTotal/AbuseIPDB keys reliably scores `CRITICAL` and shows the full
ticket-creation path without needing an actual malware sample.

Run the test suite (fully mocked — no API keys or network access required):

```bash
pytest tests/ -v
```

### Option C: n8n workflow

1. Import [`n8n/soc_triage_workflow.json`](n8n/soc_triage_workflow.json) into n8n.
2. Wire up the VirusTotal / AbuseIPDB / Jira credentials.
3. Point a Splunk alert's Webhook action at the workflow's production URL.

Full steps: [`n8n/README.md`](n8n/README.md) and
[`splunk/alert_webhook_setup.md`](splunk/alert_webhook_setup.md).

## Scoring model

Transparent and tunable rather than a black box — see
[`scoring.py`](src/socpipeline/scoring.py):

- VirusTotal: +6 points per engine flagging **malicious** (capped at 60), +2
  per **suspicious** (capped at 10).
- AbuseIPDB: its 0–100 abuse-confidence score, weighted 50%; +10 flat if the
  IP is a known Tor exit node.
- Combined score (capped at 100) maps to a severity:

  | Score | Severity | Jira priority | Ticket created? |
  |---|---|---|---|
  | 80–100 | CRITICAL | Highest | ✅ |
  | 60–79 | HIGH | High | ✅ |
  | 40–59 | MEDIUM | Medium | ✅ |
  | 1–39 | LOW | Low | ❌ (logged only) |
  | 0 | INFO | Lowest | ❌ (logged only) |

Field-level mapping into the actual Jira ticket:
[`jira/ticket_template.md`](jira/ticket_template.md).

## Repository structure

```
docker-compose.yml   One-command Docker deployment (dashboard + API, reverse-proxied)
splunk/              SPL detection searches + Splunk webhook alert action setup
n8n/                 Importable n8n workflow (the no-code path)
src/socpipeline/     Python package (the code path): VT + AbuseIPDB clients,
                     scoring, Jira ticket creation, pipeline orchestration
api/                 FastAPI wrapper around socpipeline (used by the dashboard/Docker setup)
dashboard/           React + TypeScript animated console, and its own Dockerfile
jira/                Ticket field mapping / template reference
examples/            Sample Splunk alert payload used by the CLI, tests, and docs
tests/               Pytest suite — every external API call is mocked
docs/                Architecture diagram, design notes, and the Docker security writeup
cli.py               Run the Python pipeline against an alert JSON file
```

## Security notes

- API keys live in environment variables (`.env`, gitignored) or n8n
  credentials — never hardcoded, never committed. `.env.example` documents
  every variable the pipeline reads, and `.dockerignore` keeps `.env` out of
  the Docker build context as a second line of defense.
- The Docker deployment runs both containers as non-root with read-only root
  filesystems, all Linux capabilities dropped, and the API container
  unreachable from outside the compose network — see
  [`docs/docker.md`](docs/docker.md) for the full rationale, including why
  the default setup needs no firewall exception on Linux, macOS, or Windows.
- The n8n webhook accepts unauthenticated POSTs by default — see the "Restrict
  who can reach the webhook" section in
  [`splunk/alert_webhook_setup.md`](splunk/alert_webhook_setup.md) before
  exposing it beyond a lab environment.
- The sample alert's file hash is the well-known EICAR test signature, not
  live malware — safe to commit and safe to submit to VirusTotal.

## License

[MIT](LICENSE)
