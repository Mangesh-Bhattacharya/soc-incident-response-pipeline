# Social copy for the 2026-10-10 post

Replace `[MEDIUM_URL]` after publishing. Attach `images/hero.png`.

## LinkedIn

I put a SOC triage pipeline inside Claude, and deliberately kept the model out of the verdict.

Paste a Splunk alert and ask "is this worth escalating?" The soc-triage skill runs the repo's own CLI and reports what the deterministic scorer returns: score, severity, ticket decision, reason line.

Why arithmetic instead of a model: alert payloads contain strings an attacker chose. Routing them into whatever decides whether a human sees the event gives the attacker a vote on their own escalation.

What is in the repo:
- VirusTotal and AbuseIPDB enrichment, a 0 to 100 rubric, Jira ticketing
- Fail-closed behaviour: a rate-limited lookup opens a ticket instead of scoring as clean
- A calibration harness with a confusion matrix and an under-triage count
- Alert redaction so you can share a misclassified alert safely
- Python, n8n, and a React console behind one docker compose up
- 33 tests, all mocked

It has known gaps and I list them in the post. I am looking for collaborators, especially anyone with a real labelled alert corpus, and for SOC and detection engineering teams who want to tell me where the scoring is wrong.

Post: [MEDIUM_URL]
Repo: https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline

#cybersecurity #soc #incidentresponse #detectionengineering #automation

## X / Bluesky thread

1/ I turned my SOC triage pipeline into a Claude skill. Paste a Splunk alert, get a score from the real scorer, not a model's opinion. [hero.png]

2/ The skill runs `cli.py --dry-run --json` and reports score, severity, ticket decision, and reason. It never overrides the number with a model judgment.

3/ Why: alert fields like file paths and command lines are attacker-controlled. A model that decides escalation hands them a vote on whether anyone looks.

4/ Failure behaviour matters more than the happy path. A 429 or timeout is not a clean verdict, so it opens a ticket at Medium or higher instead of silently scoring 0. [architecture.png]

5/ You can measure the scorer: `--calibrate` prints a confusion matrix and counts under-triaged alerts. Mine: 9 of 11 exact, 0 under-triaged, on a synthetic corpus. [calibration-matrix.png]

6/ Known gaps are in the README: VirusTotal term saturates at 10 engines, no behavioural axis, no caching. Each is a good first PR.

7/ Post: [MEDIUM_URL] Repo: https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline
If you have an alert that scored LOW and should have been CRITICAL, I want to see it (redacted).
