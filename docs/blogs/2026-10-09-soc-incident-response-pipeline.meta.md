# Metadata for the 2026-10-09 post

## Inputs used

| Field | Value |
|---|---|
| Repo / branch | `Mangesh-Bhattacharya/soc-incident-response-pipeline` / `main` |
| Audience | Security engineers, SOC automation builders |
| Tone | Technical, direct |
| Length | About 1,100 words |
| Focus | Enrichment failure now fails closed; calibration harness; alert redaction |

## Title variants

1. Your SOC Pipeline Should Fail Closed: Enrichment, Scoring, and Tickets You Can Audit (primary)
2. When Your API Quota Runs Out, Does Your SOC Pipeline Drop Alerts?
3. Deterministic Triage: A SOC Pipeline With Scoring You Can Defend in an Audit

**Tags:** cybersecurity, soc, automation, incident-response, python

**Excerpt:** A rate-limited enrichment lookup used to score as a clean verdict, silently suppressing alerts. This post covers the fail-closed fix, a calibration harness for measuring any scorer, and a redaction tool for sharing alerts safely.

## Images (generate, save as `docs/blogs/*.png`, then upload to Medium)

| File | Prompt | Caption | Alt text |
|---|---|---|---|
| `hero.png` | Clean flat vector illustration: a queue of alert cards flowing into a shield-shaped gate, two outputs (ticket, log), blue/teal palette, high contrast, wide Medium header ratio, empty space at left for title text. | An alert queue passes through a scoring gate that routes to a ticket or a log. | Alert cards flowing through a shield-shaped gate into either a ticket or a log. |
| `architecture.png` | Block diagram, three colours, transparent PNG: Splunk alert, normalize, VirusTotal, AbuseIPDB, score, decision diamond to Jira or log, with a red dashed arrow from "lookup error" straight to Jira. Clear labels. | Enrichment errors now bypass the score threshold and go straight to a ticket. | Pipeline diagram where a lookup-error path skips scoring and reaches the ticket step. |
| existing `docs/dashboard-preview.png` | n/a | The console animating a CRITICAL alert end to end. | Dashboard showing an alert scored 100 of 100 with a Jira ticket created. |

**Demo GIF (under 15 s):** run `cli.py --dry-run` with no keys, show the old "clean" result in a split pane versus the new "Enrichment incomplete" ticket, then run `--calibrate` and end on the confusion matrix.

## Reader comment replies (review before posting)

**Bug report**
> Thanks for the detail. Can you run it with the exact alert JSON, redacted first via `python cli.py --alert your.json --redact --json`, and paste the `enrichment` and `score` blocks here? That shows whether the failure is in a lookup or in scoring. I'll open an issue with a failing test once I can reproduce it.

**Feature request**
> Good suggestion. A [feature] fits the roadmap next to caching and backoff. I've noted it in the contribution list with the module it would touch. If you want to take it, `scoring.py` and `tests/test_scoring.py` are the places to start, and the calibration corpus lets you show the effect with numbers.

**Praise / question about models**
> Appreciated. On the model question: I'd happily use one for summarising an alert for the analyst. I wouldn't let it decide whether a human sees the alert, because the inputs include strings an attacker chose. The calibration harness is there so that comparison can be measured rather than argued.

## Publishing

No Medium integration token is configured in this repository, so this is a draft file only. Paste it into Medium's editor or import it from a gist; Medium's own API for new posts is no longer issued to new applications, so check current availability before building automation on it.

## Draft-only publishing script

```bash
python scripts/publish_medium_draft.py docs/blogs/<post>.md --dry-run       # inspect, no network
MEDIUM_TOKEN=... python scripts/publish_medium_draft.py docs/blogs/<post>.md  # creates a DRAFT only
```

The token is read from the environment only and the script hard-codes `publishStatus: "draft"`, so a human always presses publish. Relative repo links are rewritten to GitHub URLs. Images are not uploaded; add them in the Medium editor.
