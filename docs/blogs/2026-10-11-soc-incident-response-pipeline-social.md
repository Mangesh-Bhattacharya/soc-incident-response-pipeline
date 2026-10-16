# Social copy for the 2026-10-11 post

## LinkedIn

A quota exhaustion bug used to turn a burst of alerts into forty silent false negatives. This week I closed that path on soc-incident-response-pipeline, a deterministic SOC triage pipeline (Splunk detects, VirusTotal + AbuseIPDB enrich, a transparent 0-100 rubric scores, Jira tickets the result).

What shipped and what's open for review:

- Merged: enrichment failures (rate limit, timeout, missing key) now force a ticket instead of scoring as clean. A calibration harness and an allowlist-based redaction tool shipped alongside it.
- Open for review: a draft-only Medium publishing script — the request body hard-codes draft status, there's no flag that turns it into an auto-publisher.
- Merged (as of 2026-10-16): a Claude Code plugin and skill that runs the exact same deterministic scorer from inside a Claude chat. It's instructed not to override the score, ever — if a verdict looks wrong, that's a signal to add the case to the calibration corpus, not to let a model talk its way around the number.

Real numbers, not a changelog: 33 tests passing in the core pipeline, 4 more in the new publishing script's suite, and a calibration run against eleven labelled cases scoring 9/11 exact with zero under-triaged alerts.

Full writeup: [MEDIUM_URL]

Looking for a second pair of eyes on either open PR, or a real labelled alert corpus to replace the synthetic one in the repo — both are open contributions with a clear path to merge.

Repo: https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline

#cybersecurity #SOC #incidentresponse #python #AIsecurity #blueteam

## X / Bluesky thread

1/ A VirusTotal rate limit used to silently turn a burst of alerts into clean "nothing to see here" verdicts. This week I fixed that in soc-incident-response-pipeline — and shipped two more things alongside it. Thread:

2/ The fix: enrichment failures (429, timeout, missing key) now force a Jira ticket at Medium+ instead of scoring 0/INFO. Trade is a flooded queue instead of silent loss during an outage — the safer failure. Merged, with a calibration harness and a redaction tool in the same PR.

3/ Also shipped this week:
- A script (open for review) that drafts this project's own Medium posts. publishStatus is hard-coded to "draft" — no flag flips it to auto-publish.
- A Claude Code skill (merged 10/16) that runs the same scorer from inside a chat. It cannot override the score; a wrong-looking number is a cue to fix the calibration corpus, not argue with the model.

4/ Numbers, not vibes: 33 tests passing in the core suite, 4 in the new publishing script's suite, 9/11 exact on the calibration corpus with 0 under-triaged alerts. Every external API call is mocked.

5/ Severity is still ~40 lines of arithmetic, not a model guess — alert fields are attacker-controlled, and routing them into a model that decides escalation gives an attacker a vote on whether anyone sees the alert. Everything this week extends that rule, doesn't bend it.

6/ Looking for collaborators: a real labelled alert corpus (the bundled one is synthetic), review on either open PR, or a second ticketing backend (ServiceNow/TheHive) alongside the existing Jira client.

Repo: https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline
Full post: [MEDIUM_URL]

#cybersecurity #SOC #DFIR #opensource #Claude
