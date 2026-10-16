# Metadata for the 2026-10-10 post

## Inputs used

| Field | Value |
|---|---|
| Repo / branch | `Mangesh-Bhattacharya/soc-incident-response-pipeline` / `claude/skill-plugin` (PR #37) |
| Audience | Security engineers, SOC automation builders, people building Claude skills and plugins |
| Tone | Technical, direct |
| Length | About 1,300 words |
| Focus | Claude Code plugin and `soc-triage` skill wrapping a deterministic triage pipeline |

## Title variants

1. I Put a SOC Triage Pipeline Inside Claude, and Kept the Model Out of the Verdict (primary)
2. A Claude Skill That Triages Splunk Alerts Without Letting the Model Pick the Severity
3. Deterministic SOC Triage as a Claude Plugin: Enrich, Score, Ticket

**Tags (5):** cybersecurity, soc, claude, automation, incident-response

**Subtitle:** A Claude plugin that runs a deterministic enrich, score, ticket pipeline on pasted Splunk alerts, with a calibration harness and alert redaction.

**Excerpt:** Paste a Splunk alert into Claude and it runs the real scorer instead of guessing. The model handles the conversation; arithmetic you can audit handles the verdict.

## Images (rendered, committed in `docs/blogs/images/`)

| File | Placement | Caption | Alt text |
|---|---|---|---|
| `hero.png` | Top (set as Medium cover image) | Triage inside Claude. Severity stays math. | Alert cards passing through a shield labelled 40 into a Jira ticket or a log. |
| `architecture.png` | What it is | Enrichment errors bypass the score threshold and go straight to a ticket. | Pipeline from Splunk through VirusTotal and AbuseIPDB to a score, with a red dashed fail-closed path to the ticket decision. |
| `scoring-rubric.png` | Why it matters | The whole rubric: bands, weights, and the failed-lookup override. | Severity bands from INFO to CRITICAL with a ticket threshold at 40 and three rule cards. |
| `claude-skill-flow.png` | How it works | The skill runs the repo's own CLI and reports its output. | Four steps from pasted alert to Claude's report via cli.py dry-run. |
| `calibration-matrix.png` | Calibration | Eleven synthetic cases: 9 exact, 0 under-triaged, 1 over-triaged. | Five by five confusion matrix with a diagonal of correct classifications and two off-diagonal misses. |
| `dashboard-preview.png` (existing, `docs/`) | Optional, near Install | The console animating a CRITICAL alert end to end. | Dashboard showing an alert scored 100 of 100 with a Jira ticket created. |

Source for the graphics: `docs/blogs/images/src/cards.html`, regenerate with `python scripts/render_blog_graphics.py` (needs Playwright and Chromium; set `CHROMIUM_PATH` to reuse an installed browser). All numbers in `calibration-matrix.png` come from the real `--calibrate` output on 2026-10-10.

## Where to post it (distribution plan)

Post to Medium first, then link from each of these with a one-line hook and the repo link. Do not paste the same text everywhere.

| Channel | Angle |
|---|---|
| LinkedIn | Collaborator callout plus the "no model in the verdict" argument. Copy in `-social.md`. |
| X / Bluesky thread | Hero image, then the fail-closed result and the calibration matrix. |
| Hacker News (Show HN) | Lead with the repo, not the post. Title it plainly and be present in the thread for the first hours. |
| r/blueteamsec, r/cybersecurity, r/netsec | Check each subreddit's self-promotion rules first. The calibration and redaction tools are the reusable parts. |
| Claude Code and Claude skills communities | The plugin layout and the "skill runs the real CLI, never overrides it" boundary. |
| Splunk and n8n community forums | The `splunk/detections.spl` searches and the importable n8n workflow. |
| Direct outreach | Two or three SOC automation engineers or detection engineers, asking for one redacted alert that mis-scores. |

## Reader comment replies (review before posting)

**Bug report**
> Thanks for the detail. Can you run it with the exact alert JSON, redacted first via `python cli.py --alert your.json --redact --json`, and paste the `enrichment` and `score` blocks here? That shows whether the failure is in a lookup or in scoring. I'll open an issue with a failing test once I can reproduce it.

**Feature request**
> Good suggestion. It fits next to caching and backoff on the contribution list. `scoring.py` and `tests/test_scoring.py` are the places to start, and the calibration corpus lets you show the effect with numbers rather than anecdotes.

**Why not a model for severity?**
> I'd happily use one to summarise an alert for the analyst. I wouldn't let it decide whether a human sees the alert, because the inputs include strings an attacker chose. The calibration harness exists so the comparison can be measured: `evaluate()` takes any scorer with `score_alert`'s signature.

**Is the skill real time?**
> It runs when you invoke it, on an alert you paste. The always-on path is Splunk's webhook into n8n or the FastAPI service. The skill is for the analyst's second screen, not the ingestion pipeline.

## Publishing

No Medium integration token is configured, so Medium publishing is a manual paste-in: copy the post into the editor, upload the five PNGs from `docs/blogs/images/`, set `hero.png` as the cover, add the five tags above. PR #36 adds a draft-only publishing script if a token ever becomes available.
