# I Built a SOC Triage Pipeline in [N weeks]. Here Is Why, How It Works, and Every Command to Run It

<!-- hero.png: generate from the prompt in the .meta.md file, then upload to Medium -->

I was tired of reading about "AI-powered security automation" that could not answer one question: *what happens to the alerts it drops?*

So I built a pipeline that takes a Splunk alert, enriches it against VirusTotal and AbuseIPDB, scores it with arithmetic you can read in one file, and opens a Jira ticket only when the score earns one. Then I spent most of the effort on the part nobody demos: what the system does when it is wrong, rate limited, or misconfigured.

This post covers what it is, why I built it, how it works, how long it took, and every command to run it yourself. Code: [github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline).

## The problem

A SOC analyst's first ten minutes on an alert are always the same. Paste the hash into VirusTotal. Paste the source IP into AbuseIPDB. Decide whether it is worth escalating. Write the ticket. Four of those five steps are mechanical. Only the judgment is not.

Automating the four is easy. Automating them *safely* is the actual problem, because a triage pipeline that silently drops a real alert is worse than no pipeline.

## How it works

```
Splunk alert -> normalise -> VirusTotal (hash) -> AbuseIPDB (IP) -> score 0-100 -> ticket if >= 40
                                                                        |
                                              lookup errored? -> ticket anyway
```

| Layer | Tool | Role |
|---|---|---|
| Detect | Splunk | Scheduled searches fire a webhook |
| Orchestrate | Python or n8n | Two interchangeable implementations of the same logic |
| Enrich | VirusTotal, AbuseIPDB | Hash and IP reputation |
| Ticket | Jira | `Incident` issue with the evidence attached |
| See it | React + TypeScript console | Animates a real alert through every stage |

The scoring is the whole point, so here it is. From `scoring.py`:

```python
malicious_points = min(vt_result.malicious * 6, 60)
abuse_points = round(abuse_result.abuse_confidence_score * 0.5)
if abuse_result.is_tor:
    score += 10
```

Six points per malicious engine, capped at sixty. Half the abuse confidence score. Ten for a Tor exit node. Cap at 100.

## Four decisions I would defend in an interview

**1. Severity is arithmetic, not a model.** Alert fields (file paths, process names, command lines) are chosen by the attacker. Routing them into a model that decides whether a human sees the event gives the attacker a vote on their own escalation. Arithmetic is also reproducible and auditable. I use models for nothing in the escalation path.

**2. It fails closed.** The first version treated a rate-limited lookup exactly like a clean one: both returned "not found", both scored zero. A burst of correlated alerts could exhaust the free VirusTotal quota and every later alert would be suppressed. Now a lookup error is recorded, named in the ticket, and forces escalation at Medium priority.

```python
return self.score >= TICKET_THRESHOLD_SCORE or self.enrichment_failed
```

**3. It can be measured.** `python cli.py --calibrate` scores a labelled corpus and reports a confusion matrix plus the number that matters: alerts that should have reached an analyst and did not. I wrote two test cases the rubric deliberately fails, so the harness has something real to report.

**4. It documents its own flaws.** The VirusTotal term saturates at ten engines. There is no behavioural axis, so forty failed logins and one look the same. The README says so and lists them as contribution targets.

## Run it

```bash
git clone https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline.git
cd soc-incident-response-pipeline
python launch.py            # Windows: py launch.py
```

The launcher checks Python, Docker, Compose v2, port 8080 and your `.env`, starts the stack, waits until it is healthy, and opens `http://localhost:8080`. No API keys are needed to see the demo.

Without Docker:

```bash
pip install -r requirements-dev.txt
python cli.py --alert examples/sample_splunk_alert.json --dry-run
pytest tests/ -v            # 51 passed
python cli.py --calibrate examples/calibration_corpus.json
```

If something breaks: `python launch.py --doctor` prints the exact fix. Full guide: [`docs/TROUBLESHOOTING.md`](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline/blob/main/docs/TROUBLESHOOTING.md).

## How long it took

- **Git history:** first commit on 2026-09-13, current work on 2026-10-16. 27 commits on 4 separate days at the time of writing.
- **Calendar time:** [N weeks, fill in the real number].
- **Hours:** [roughly N hours, fill in the real number].
- **Size:** about 2,000 lines of Python including tests and tooling, about 1,000 lines of TypeScript, 51 tests, CI on Linux, Windows and macOS.

Beyond the pipeline logic, the repository shows work on Docker hardening (non-root containers, read-only filesystems, dropped capabilities, loopback-only port binding), a workaround for a Vite 8 / npm optional-dependency bug inside a minimal Debian image (documented in `dashboard/Dockerfile`), and failure-mode documentation. [Add your own account of the hardest part.]

## What I learned

- A control's behaviour under failure is the real specification.
- Honest limitations build more trust than a clean README.
- "Works on my machine" is a bug report. Hence the doctor command.
- Writing the CI that boots the real Docker stack caught more than any unit test.

## Work with me

The repo has labelled issues, a contributing guide and issue forms, and the most useful contribution is an alert the pipeline got wrong. Details in [`CONTRIBUTING.md`](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline/blob/main/CONTRIBUTING.md).

I am looking for [role type: e.g. security engineer / SOC automation / detection engineering] roles. If your team works on triage automation, detection engineering or SOAR, I would like to hear how you handle the fail-closed trade-off. **[Add: LinkedIn link, email, location or remote preference.]**
