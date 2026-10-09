# Your SOC Pipeline Should Fail Closed: Enrichment, Scoring, and Tickets You Can Audit

*Draft for Medium. Companion metadata, image prompts, and comment replies: [`2026-10-09-soc-incident-response-pipeline.meta.md`](2026-10-09-soc-incident-response-pipeline.meta.md).*

![Hero: an analyst's alert queue feeding a shield-shaped gate that routes alerts to a ticket or a log](hero.png)

## TL;DR

Picture a burst of forty alerts that share one source address. Your VirusTotal free-tier quota runs out on alert six. Alerts seven through forty get scored on no evidence, come back `0 / INFO`, and are silently dropped. Nobody was evaded; the pipeline just ran out of lookups. This week's change to [soc-incident-response-pipeline](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline) makes that case reach a human instead.

## What it is

A SOC analyst's first ten minutes on an alert are the same every time: paste the hash into VirusTotal, paste the source address into AbuseIPDB, decide if it is worth escalating, write the ticket. This project automates that first pass. Splunk detects, VirusTotal and AbuseIPDB enrich, a scoring rubric assigns a 0 to 100 severity, and only alerts at 40 or above get a Jira ticket with the evidence already attached.

It ships three interchangeable ways to run the same logic: a Python package and CLI, an importable n8n workflow, and a FastAPI backend with a React console, all behind one `docker compose up`.

**Key features**

- Transparent scoring: 6 points per malicious engine (capped at 60), AbuseIPDB confidence at 50 percent weight, +10 for a Tor exit node.
- Dry-run mode that never touches Jira.
- A hardened Docker stack: non-root, read-only filesystems, all capabilities dropped, bound to `127.0.0.1`.
- 33 tests with every external call mocked.

## Why it matters

Alert fatigue is a throughput problem, and the obvious fix is to suppress more. Suppression is only safe if you trust what is being dropped. Two things erode that trust: scoring you cannot explain after the fact, and controls that quietly degrade under load. The first is why severity here is arithmetic rather than a model. Alert payloads contain attacker-controlled strings (file paths, process names, command lines), and routing them into a model that decides whether a human ever sees the event gives an attacker a vote on their own escalation. The second is this week's subject.

## Install

Prerequisites: Docker, or Python 3.10+.

**Docker (one command)**

```bash
git clone https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline.git
cd soc-incident-response-pipeline
cp .env.example .env     # add API keys, or leave blank for demo mode
docker compose up --build
```

Open `http://localhost:8080`.

**Native**

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
python cli.py --alert examples/sample_splunk_alert.json --dry-run
pytest tests/ -v          # 33 passed
```

With no keys set, the run now reports `0/100 (INFO)` plus an "Enrichment incomplete" reason and a would-be `Medium` ticket. Before this change it reported a clean verdict.

## How it works

```
Splunk alert --> normalize --> VirusTotal (hash) --> AbuseIPDB (IP) --> score_alert --> ticket?
                                                                            |
                                              enrichment_errors --> force ticket, priority >= Medium
```

The interesting file is [`scoring.py`](../../src/socpipeline/scoring.py). The core of the fix:

```python
if vt_result and vt_result.error:
    enrichment_errors.append(f"VirusTotal: {vt_result.error}")
...
@property
def should_create_ticket(self) -> bool:
    return self.score >= TICKET_THRESHOLD_SCORE or self.enrichment_failed
```

The enrichment clients already separated "not found" (HTTP 404, `error=None`) from "lookup failed" (`error` set). The scorer just never read the distinction. Now a rate limit, timeout, or missing key is recorded, named in the ticket, and ticketed at `Medium` unless surviving evidence scores higher.

### This week's three commits

| Branch | Commit | Why it helps |
|---|---|---|
| `fix/enrichment-fail-closed` | `fix: fail closed when enrichment errors instead of scoring as clean` | Removes the quota-exhaustion suppression path. The trade is queue flooding in place of silent loss, which is the safer failure. |
| `feat/calibration-harness` | `feat: add calibration harness that scores a labelled corpus` | `python cli.py --calibrate corpus.json` prints a confusion matrix and counts **under-triaged** alerts, the metric that matters. Any scorer with `score_alert`'s signature can be evaluated, including a model-based one. |
| `feat/alert-redaction` | `feat: add allowlist-based alert redaction for safe sharing` | `--redact` pseudonymises users, hosts, private IPs, and profile paths with a salted HMAC and drops unknown fields, so alerts can go into a public issue or shared corpus. |

## Security considerations

**Threat model.** The adversary controls alert field contents and can generate alert volume. They cannot see your scoring weights but can infer them over time.

**Safe defaults**

- Dry-run in the API: the dashboard backend can never file a ticket.
- Secrets in environment variables only; `.env` is gitignored and dockerignored.
- Redaction is an allowlist, and an empty salt is rejected, because an unkeyed hash of a username is reversible by enumeration.

**Hardening to do yourself**

- The n8n webhook accepts unauthenticated POSTs by default. Put it behind a shared secret or IP allowlist before exposing it.
- Tighten the API's wide-open CORS policy outside a personal demo.
- Indicators go to VirusTotal and AbuseIPDB. For air-gapped environments, replace the clients with an internal TIP.

**Known residual risks.** The VirusTotal term still saturates at ten engines, scoring ignores event count, and there is no caching or backoff, so the quota burst now floods the queue. The README lists each one, and the calibration corpus encodes two as expected failures.

Found a vulnerability? Use the repository's private security advisory flow rather than a public issue, and redact the alert first.

## Use cases

1. **Quota exhaustion during a campaign.** A phishing wave hits many users from one infrastructure. Previously the tail of the wave scored clean; now it is ticketed with the failure named.
2. **Evaluating a model-based scorer.** Run both scorers over the same labelled corpus and compare under-triage counts rather than anecdotes.
3. **Asking for help.** Redact a misclassified alert and attach it to an issue.

## Contribute

Best next contributions, roughly by value: a real labelled corpus (the bundled eleven cases are synthetic), enrichment caching with backoff, ratio-based VirusTotal scoring, a behavioural axis, and surfacing `enrichment_failed` in the dashboard.

## FAQ

**Why not let a model score severity?** Reproducibility, auditability, and prompt injection through attacker-controlled fields. Models are reasonable for summarisation and hunting hypotheses, not for the escalation gate.

**Does a ticket for every failed lookup flood my queue?** During an outage, yes, by design. Caching and backoff are the real fix and are open for contribution.

**Is `--redact` enough to publish an alert?** It reduces exposure; it does not certify. Read the output before you post it.

---

Repo: https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline · Issues and PRs welcome.
