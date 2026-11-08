# Metadata for the 2026-11-08 post

## Inputs used

| Field | Value |
|---|---|
| Repo / branch | `Mangesh-Bhattacharya/soc-incident-response-pipeline` / `main` (HEAD `d4df8bf`, unchanged since 2026-10-16) |
| Audience | Security engineers, SOC automation builders, people evaluating whether a deterministic scorer is trustworthy enough to rely on |
| Tone | Technical, direct |
| Length | About 1,320 words |
| Focus | Not a weekly update — main carried zero substantive commits in the last 7 days (only dependency bumps). A deep dive on the calibration harness and scoring rubric, a part of the project not yet covered by its own post |
| Real numbers used | `pytest tests/ -v` → 33 passed; `cli.py --calibrate examples/calibration_corpus.json` → 9/11 exact, 0 under-triaged, 1 over-triaged, same confusion matrix as the 2026-10-11 post (rubric is unchanged); `cli.py --dry-run --redact` → real pseudonymised terminal output (`host-95b87abdca`, `user-c6ca890125`); `cli.py --help` → verified `--calibrate` and `--redact` flag names and descriptions before writing about them |
| Activity survey | `git log --since="7 days ago"` on `main`: 0 commits besides none (last real merge was PR #45/#37/#35, all 2026-10-16). Checked `git log --all` across every non-dependabot branch: nothing newer than 2026-10-18 (an unmerged draft PR #46 adding a `blog-agent/` authoring workflow, still open/draft, not touched this run). Other candidate repos (`Active-Directory-Red-Team-Lab`, `jobpilot`, `LinkedIn-Auto-Blogger`) were not reachable with this session's GitHub credentials (likely private); `compliant-data-collector` was reachable read-only (public, anonymous clone) and its last commit is 2025-12-15, far outside the 7-day window, with no write access available to open a PR there this run |

## Title variants

1. Grading the Scorer: How I Check a Deterministic SOC Rubric Isn't Quietly Wrong (primary)
2. Why I Built a Confusion Matrix for a Rule-Based Alert Scorer
3. 9 of 11: What a Calibration Harness Actually Tells You About a SOC Triage Rubric

**Tags:** cybersecurity, soc, automation, python, incident-response

**Excerpt:** No new commits this week, so instead of forcing an update this is a deep dive into the part of a deterministic SOC triage pipeline that proves the rubric works: a calibration harness scoring eleven labelled alerts, with real output showing exactly where and why it's wrong.

## Images (rendered, committed under `docs/blogs/images/`)

| File | Placement | Caption | Alt text |
|---|---|---|---|
| `2026-11-08-hero.png` | Below the title, before TL;DR | Grading the scorer, not just trusting it: no new commits this week, so this is the harness that checks the rubric, with real 9/11 calibration numbers. | Dark hero graphic with the headline "Grading the scorer, not just trusting it," three stat chips (9/11 exact, 0 under-triaged, 1 over-triaged), a shield-and-checkmark icon, and four tool chips: Splunk, Jira, VirusTotal, AbuseIPDB. |
| `2026-11-08-scoring-flow.png` | In "How it works", above the calibration output | score_alert() in scoring.py: VirusTotal and AbuseIPDB formulas summing into four severity bands, with the fail-closed path to a forced Medium ticket on enrichment error highlighted in red. | Flow diagram: two input boxes (VirusTotal formula, AbuseIPDB formula) feeding a capped sum, branching into four severity-band boxes and a ticket-decision box, with a dashed red branch down to an "enrichment errored, fails closed" box. |
| `2026-11-08-calibration-matrix.png` | In "How it works", after the confusion matrix text block | Confusion matrix from the calibration harness: 9 of 11 exact, 0 under-triaged, 1 over-triaged, with the two misclassified cases named. | 5x5 confusion matrix over INFO/LOW/MEDIUM/HIGH/CRITICAL with two off-diagonal cells highlighted amber, next to three stat tiles (9 of 11, 0 under-triaged, 1 over-triaged) and the misclassified case name. |
| `2026-11-08-redaction-demo.png` | In "How it works", last image | Real terminal output from a live run just now: REDACT_SALT warning, pseudonymised host-95b87abdca and user-c6ca890125 tokens, a 0/100 INFO score that still tickets because the lookups failed rather than cleared. | Dark terminal-style card showing real `cli.py --dry-run --redact` output: a REDACT_SALT warning, pseudonymised host/user tokens in blue, a 0/100 INFO score, two red enrichment-failure lines, and a teal dry-run ticket line. |

Source for all four: `docs/blogs/images/src/2026-11-08-cards.html`, rendered with `scripts/render_blog_graphics_2026-11-08.py` (Playwright + the preinstalled Chromium at `/opt/pw-browsers/chromium`, set via `CHROMIUM_PATH`). Namespaced to this post's date so it doesn't collide with the 2026-10-11 post's own `cards.html`/renderer pair (same convention that post established). Each image was screenshotted at its own SVG element id and re-viewed with an image read before committing; one caption/box overlap at the bottom of the scoring-flow card was caught that way (text ran into the red fail-closed box) and fixed by growing the card and moving the caption down before the final render.

## Where to post

| Channel | Notes |
|---|---|
| LinkedIn | Full post text works as a condensed version; lead with the TL;DR's concrete VirusTotal-saturation scenario, not the "no commits this week" framing — that's an editorial note for readers who click through, not a hook. |
| X / Bluesky | Use the thread in the companion `-social.md` file; first post is the hook (the 10-vs-70-engines framing), not the full TL;DR. |
| Hacker News (Show HN) | Title as "Show HN: I built a confusion matrix to grade my rule-based SOC scorer". This is the fourth post about this repo in a month — check [HN's Show HN guidelines](https://news.ycombinator.com/showhn.html) and consider whether this specific technical angle (model evaluation methodology applied to a non-ML system) clears the bar better than a repeat "look at my project" post. |
| r/cybersecurity, r/blueteamsec, r/netsec | Check each subreddit's self-promotion rules before posting. Lead with the calibration/confusion-matrix methodology, not the repo pitch — r/netsec in particular responds better to "here's how I measured X" than to project announcements. |
| r/MachineLearning or r/MLOps (optional) | The angle — evaluating a non-ML classifier the same way you'd evaluate a model, with a confusion matrix and under/over-triage error costs — may land with an ML-evaluation audience even though the scorer itself has no model in it. Only post if comfortable with likely "this isn't ML" pushback; frame it that way upfront. |
| Claude / Anthropic developer community | Lower priority this time — this post isn't about the Claude skill (covered in a prior post); skip unless a thread specifically about evaluating deterministic vs. model-based classifiers is active. |

## Reader comment reply templates

**"Why not just use the VirusTotal ratio instead of absolute engine count? Seems like an easy fix."**
> Agreed, and it's the next item on the known-limitations list — `total_engines()` is already computed on the result object, the scoring function just isn't using it yet. I'd rather land it with a labelled case or two proving it actually fixes `packer-false-positive` without breaking anything else in the corpus than change the formula on intuition alone. If you want to take a pass at it, the contributing list in the README has it as item 3.

**"Eleven cases isn't a real calibration set. Doesn't that make the 9/11 number kind of meaningless?"**
> Fair, and the README says the same thing in those words — it's the maintainer's opinion encoded as test cases, not ground truth from real alert volume. What it's actually useful for is catching regressions and making tradeoffs explicit (the two misses here are documented gaps, not surprises). A real labelled corpus from someone running this against production alerts is the single highest-value contribution this project can take; `cli.py --calibrate` works against anything shaped like the bundled example.

**"Isn't 'no behavioural axis' a pretty big gap for a SOC tool? A brute-force burst should score higher than one failed login."**
> Yes — that's exactly what `brute-force-burst-tor` in the corpus is there to demonstrate: forty failed logins from a Tor exit node scores identically to one, because event count never reaches the scorer. It's labelled HIGH by the maintainer but comes back MEDIUM today. It's on the known-limitations list and the contributing list (item 4) rather than silently accepted, but it hasn't been fixed yet — want to be the one who sends that PR?

## Publishing

No Medium integration token is configured in this repository, so this is a draft file only. Paste it into Medium's editor, or import it from a gist. `scripts/publish_medium_draft.py` exists on PR #36 (still open, draft-only even if merged — hard-codes `publishStatus: "draft"`) but that PR has not merged, so this post does not depend on it.
