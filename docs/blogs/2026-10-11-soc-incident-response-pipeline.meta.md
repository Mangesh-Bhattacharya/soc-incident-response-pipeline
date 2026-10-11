# Metadata for the 2026-10-11 post

## Inputs used

| Field | Value |
|---|---|
| Repo / branch | `Mangesh-Bhattacharya/soc-incident-response-pipeline` / `main`, plus open PRs [#36](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline/pull/36) and [#37](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline/pull/37) |
| Audience | Security engineers, SOC automation builders, people evaluating Claude skills for security work |
| Tone | Technical, direct |
| Length | About 1,290 words |
| Focus | Weekly roundup: the merged fail-closed/calibration/redaction fix, plus two open PRs (Medium publishing script, Claude Code plugin + skill) |
| Real numbers used | `pytest tests/ -v` → 33 passed (main); publish script's own suite → 4 passed; `cli.py --calibrate examples/calibration_corpus.json` → 9/11 exact, 0 under-triaged, 1 over-triaged; `cli.py --dry-run` output; `git show --stat` insertion/file counts per PR |

## Title variants

1. This Week in soc-incident-response-pipeline: Fail-Closed Scoring, a Publish Script, and a Claude Skill (primary)
2. Three Shippable Changes, One Deterministic SOC Pipeline: This Week's Update
3. From Quota Exhaustion to a Claude Skill: A Week of Hardening a SOC Triage Pipeline

**Tags:** cybersecurity, soc, automation, claude, incident-response

**Excerpt:** A weekly update on a deterministic SOC triage pipeline: a merged fail-closed fix that stops a rate limit from silently dropping alerts, plus two open PRs — a draft-only Medium publishing script and a Claude Code skill that runs the same scorer from inside a chat.

## Images (rendered, committed under `docs/blogs/images/`)

| File | Placement | Caption | Alt text |
|---|---|---|---|
| `hero.png` | Below the title, before TL;DR | Three changes, one week: fail-closed merged, a publish script and a Claude skill open for review. | Dark hero graphic listing three project changes this week with a shield-and-checkmark icon and four tool chips: Splunk, Jira, Claude, Medium. |
| `weekly-timeline.png` | In "How it works", above the PR table | Timeline of this week's three PRs: one merged, two open for review, each with its real insertion and test counts. | Horizontal timeline with three nodes dated Oct 9, Oct 9, and Oct 10, each showing a PR number, title, and real insertion/test counts. |
| `calibration-matrix.png` | In "How it works", after the code snippet | Confusion matrix from the calibration harness: 9 of 11 exact, 0 under-triaged, 1 over-triaged. | 5x5 confusion matrix over INFO/LOW/MEDIUM/HIGH/CRITICAL with two off-diagonal misses highlighted, next to three stat tiles. |
| `test-stats.png` | In "How it works", last image | Test counts: 33 passing in the pipeline suite, 4 in the new publishing script's suite, 37 total. | Three stat tiles showing 33, 4, and 37 passing tests across two test suites, both fully mocked. |

Source for all four: `docs/blogs/images/src/cards.html`, rendered with `scripts/render_blog_graphics.py` (Playwright + the preinstalled Chromium at `/opt/pw-browsers/chromium`, set via `CHROMIUM_PATH`). Each was screenshotted at its own SVG element id and re-viewed with an image read before committing; one overflow in the hero's status chips was caught that way and fixed before the final render.

## Where to post

| Channel | Notes |
|---|---|
| LinkedIn | Full post text works as-is; lead with the TL;DR scenario. Post the hero image as the preview card. |
| X / Bluesky | Use the thread in the companion `-social.md` file; first post is the hook, not the full TL;DR. |
| Hacker News (Show HN) | Title as "Show HN: Deterministic SOC triage pipeline, now with a Claude skill (fail-closed scoring)". Check [HN's self-promotion / Show HN guidelines](https://news.ycombinator.com/showhn.html) before posting; this is the third post about the same repo in roughly a month, so consider whether this specific post clears the bar for a new Show HN versus a comment on a prior thread if one is still active. |
| r/cybersecurity, r/blueteamsec, r/netsec | Check each subreddit's self-promotion rules (several require a minimum account age/karma or cap self-promo frequency) before posting; r/netsec in particular is strict about pure self-promotion. Lead with the fail-closed bug, not the Claude skill, since that subreddit skews more skeptical of AI-adjacent tooling. |
| Claude / Anthropic developer community (Discord, forums) | The Claude Code plugin + skill angle (PR #37) is the most relevant hook here; link directly to that PR rather than the merged main branch, since the skill is not merged yet. |
| n8n community forum | Relevant since the pipeline ships an importable n8n workflow; this post's content is tangential to n8n specifically, so only post if a thread about alert-driven automation is already active rather than starting a new one just for this. |

## Reader comment reply templates

**"Is the Claude skill safe to point at real alerts?"**
> Good question to ask before trying it. The skill (PR #37, not yet merged) runs the exact same `cli.py` code path the CLI does and reports the score back verbatim — it's explicitly instructed not to override or second-guess the number. The risk isn't the skill deciding wrong, it's `--dry-run` being left off by accident if you want a real Jira ticket filed; the skill's own instructions call that out as something to confirm with the user first.

**"Why not just publish straight to Medium instead of a draft-only script?"**
> Because I don't trust any script, mine included, enough to let it press publish unattended. `publishStatus: "draft"` is hard-coded in the request body in PR #36, not a flag you can flip, so the worst case is an extra draft sitting in my Medium account, not a bad post going live.

**"When will #36 / #37 merge?"**
> Both are open for review right now, links are in the post. If you read either and have feedback, a comment on the PR is the fastest way to move it along — I'd rather merge something a second pair of eyes looked at than merge on my own schedule.

## Publishing

No Medium integration token is configured in this repository, so this is a draft file only. Paste it into Medium's editor or import it from a gist, or run `python scripts/publish_medium_draft.py docs/blogs/2026-10-11-soc-incident-response-pipeline.md --dry-run` once PR #36 merges to see it prepared for the API. Medium's own API for new integration tokens is no longer issued to new applications, so check current availability before relying on it.
