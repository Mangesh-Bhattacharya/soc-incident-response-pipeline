---
name: soc-triage
description: Triage a Splunk SOC alert through the soc-incident-response-pipeline — enrich a file hash with VirusTotal and a source IP with AbuseIPDB, apply the deterministic 0-100 scoring rubric, and decide whether it clears the Jira ticket threshold. Also runs the calibration harness against a labelled alert corpus and redacts an alert for safe sharing. Use whenever the user pastes a Splunk/SIEM alert JSON and asks "is this worth escalating", "score this alert", "would this page an analyst", "run this through the pipeline", or asks to calibrate/tune the scoring rubric or redact an alert before posting it.
---

# SOC Triage (soc-incident-response-pipeline)

Wraps `cli.py` from [soc-incident-response-pipeline](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline) so Claude can run the same deterministic triage a SOC analyst's first ten minutes would do: extract indicators, look up hash reputation (VirusTotal) and IP reputation (AbuseIPDB), score 0-100 with `src/socpipeline/scoring.py`, and decide whether the alert clears the ticket threshold (score >= 40, or any enrichment lookup failure — see "fail closed" below).

**This skill does not decide severity itself.** It runs the repo's own scorer and reports exactly what it returns — that determinism is the project's whole point (see the repo README, "Why the scoring layer is deterministic"). Do not override or second-guess the score with a model judgment; if it looks wrong, that is useful signal to add the case to the calibration corpus, not to talk the user out of the number.

## Setup (once per environment)

```bash
cd soc-incident-response-pipeline
pip install -r requirements-dev.txt
cp .env.example .env   # fill VT_API_KEY / ABUSEIPDB_API_KEY, or leave blank for --dry-run
```

With no API keys set, every run returns `0/100 (INFO)` with reason "Enrichment incomplete" and a would-be Medium ticket — that is a missing-key enrichment failure, not a clean verdict (fail-closed by design).

## Triage one alert

1. Get the alert JSON from the user (pasted, uploaded, or an attached file path). It must look like a Splunk webhook payload — see `examples/sample_splunk_alert.json` for the shape expected by `cli.py`.
2. Write it to a temp file if it was pasted inline, then run:
   ```bash
   python cli.py --alert <path-to-alert.json> --dry-run --json
   ```
   Drop `--dry-run` only if the user has real `JIRA_*` env vars set and explicitly wants a ticket filed — confirm with them first, since this is a live side effect (Explicit permission required: "Sending any message / creating content on the user's behalf").
3. Report back in this order, matching the repo's own vocabulary: **score / 100**, **severity** (CRITICAL/HIGH/MEDIUM/LOW/INFO), **ticket decision** (created/would-create vs. logged only), and the **reason line** — especially call out `enrichment_errors` if present, since a failed lookup (rate limit, timeout, missing key) forces a ticket at Medium+ regardless of score, per the fail-closed design.
4. If VT or AbuseIPDB keys are missing and the user wants a realistic demo instead of an enrichment-failure result, point them at the bundled EICAR sample: `python cli.py --alert examples/sample_splunk_alert.json --dry-run` — it uses the EICAR test hash (universally flagged, harmless) and a known Tor exit node, so with live keys it reliably scores CRITICAL.

## Calibrate the scoring rubric

```bash
python cli.py --calibrate examples/calibration_corpus.json
```

Prints a confusion matrix plus **under-triaged** (should have reached an analyst, didn't — the number that matters) and **over-triaged** counts. If the user supplies their own labelled corpus (same shape as `examples/calibration_corpus.json`), run the harness against that file instead of the bundled synthetic one — it encodes the maintainer's opinion, not ground truth.

## Redact an alert before sharing

```bash
REDACT_SALT=$(openssl rand -hex 32) python cli.py --alert <alert.json> --json --redact
```

Pseudonymizes users/hostnames/private IPs/profile-directory paths with a keyed HMAC (same salt → same token, not reversible without it); drops command lines, URLs, and registry values outright since those routinely carry credentials; keeps public IPs and file hashes since those are the actual indicators. `--redact` implies `--dry-run`. Tell the user to eyeball the output before posting — this reduces exposure, it does not certify the alert as safe to publish.

## Explain the scoring model when asked

- VirusTotal: 6 pts per engine flagging **malicious** (capped at 60), 2 pts per **suspicious** (capped at 10).
- AbuseIPDB: 0-100 abuse confidence score at 50% weight, +10 flat for a known Tor exit node.
- Combined, capped at 100 → 80-100 CRITICAL, 60-79 HIGH, 40-59 MEDIUM (all three ticket), 1-39 LOW, 0 INFO (both log-only).
- Any enrichment lookup error (not a clean "not found") forces a ticket at Medium+ regardless of score — see `README.md#known-limitations` for the full rationale and the open scoring gaps (VT saturates at 10 engines; no behavioral/event-count axis yet).

## Boundaries

- Never add containment actions (host isolation, account disable, firewall changes) — this project is deliberately enrich/score/ticket only, nothing further.
- Never run with real `JIRA_*` credentials without the user's explicit go-ahead for that specific run.
- Don't fabricate VirusTotal/AbuseIPDB results if keys are absent — report the enrichment failure plainly, as the pipeline itself does.
