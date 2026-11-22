# Metadata for the 2026-11-22 post

## Inputs used

| Field | Value |
|---|---|
| Repo / branch | `Mangesh-Bhattacharya/soc-incident-response-pipeline` / `main` (HEAD `d4df8bf`, unchanged since 2026-10-16) |
| Audience | Security engineers and maintainers of small open-source security tools, people deciding whether their own Dependabot setup is doing anything real |
| Tone | Technical, direct |
| Length | About 1,200 words |
| Focus | Not a weekly feature update -- `main` had zero human commits in the last 7 days, only Dependabot activity. A close read of the dependency-update machinery itself (Dependabot config, the CI gate it has to clear, the monthly scheduled run), using this week's real PR activity as the evidence |
| Real numbers used | `ruff check .` -> `All checks passed!`; `pytest tests/ -v` -> `33 passed, 1 warning in 0.95s` (run against current `main` in a fresh venv); PR activity pulled via the GitHub API: 10 Dependabot PRs touching `main` in the last 7 days, 4 of the 5 opened 2026-11-15 (`#74` ruff, `#75` fastapi, `#76` framer-motion, `#77` oxlint) closed and superseded on 2026-11-22 by `#80`, `#82`, `#83`, `#81` respectively proposing newer versions of the same dependency; `#78` (`@vitejs/plugin-react`) still open, not superseded; `#79` (docker base image bump in `/api`) opened fresh on 2026-11-22 |
| Activity survey | `git log --since="7 days ago"` on `main`: 0 commits. `list_pull_requests` (state=all, sorted by updated) over the last 7 days: every PR touching `main` was Dependabot-authored (10 total), confirmed non-substantive per the usual filter (version bumps, no logic changes). Checked PR #36 (long-running draft, last touched 2026-10-16) and PR #72 (prior week's own "no activity" post, 2026-11-08, covering the calibration harness -- different angle, no overlap with this post). Other candidate repos: this session's GitHub access is scoped only to `soc-incident-response-pipeline` and has no `add_repo`/`list_repos` tool available to broaden it (confirmed by direct tool search and a subagent check, and by a denied `get_file_contents` call against `Active-Directory-Red-Team-Lab`). Anonymous `git clone` over HTTPS was attempted for all four other candidates as a fallback: `Active-Directory-Red-Team-Lab`, `jobpilot`, and `LinkedIn-Auto-Blogger` all refused with "could not read Username" (private or inaccessible); `compliant-data-collector` cloned successfully (public) but its last commit is 2025-12-15, far outside the 7-day window. `soc-incident-response-pipeline` was the only repo both actionable and in scope, matching last week's survey exactly. |

## Title variants

1. The Week Nothing Shipped: What a Dependency-Update Pipeline Actually Does When It Works (primary)
2. Ten Dependabot PRs, Zero Human Commits: Auditing the Machinery That Keeps a SOC Pipeline Patched
3. Superseded, Not Stale: What a Week of Dependency Bumps Taught Me About My Own CI Gate

**Tags:** cybersecurity, devsecops, python, ci-cd, open-source

**Excerpt:** No human commit landed on this SOC triage pipeline in seven days -- just ten Dependabot PRs, four of them replaced by a newer version before anyone merged them. A look at the gate every one of those PRs has to clear, and the scheduled run that checks for drift even when nobody pushes anything at all.

## Images (rendered, committed under `docs/blogs/images/`)

| File | Placement | Caption | Alt text |
|---|---|---|---|
| `2026-11-22-hero.png` | Below the title, before TL;DR | The week nothing shipped: zero human commits, ten automated dependency PRs, 33 tests still passing. | Dark hero graphic headlined "The week nothing shipped (on purpose)," three stat chips (33/33 tests pass, 10 dependabot PRs, 4 superseded today), a shield-and-checkmark icon captioned "ruff: all checks passed," and four ecosystem chips: pip, npm, docker, actions. |
| `2026-11-22-ci-gate-flow.png` | In "How it works", after the ecosystem list | Same gate for a bot PR as a human one: Dependabot's five ecosystems feeding the CI gate, with the scheduled monthly run and its auto-filed issue shown as a separate path. | Flow diagram: four Dependabot source boxes (pip, npm, docker x2, github-actions, the last greyed out as unused this week) feeding an "opens a PR" node, then four parallel CI check boxes (lint, test matrix, dashboard build, docker boot+curl), converging on an "all green?" decision that branches to "mergeable" (teal) or "stays open, flagged" (red); below, a separate panel shows the monthly `schedule:` trigger with a dashed red line to an "auto-files a scheduled-ci-failure issue" box, labeled "on failure only." |
| `2026-11-22-supersede-timeline.png` | In "Why it matters", after the paragraph describing the supersession | Last week's PRs, superseded before anyone merged them: Dependabot's own weekly re-scan closed 4 of 5, each replaced by a PR for a newer version of the same dependency. | Five rows pairing a 2026-11-15 PR (left, dark) with its 2026-11-22 replacement (right, teal) via a dashed red "closed" arrow, for ruff, fastapi, framer-motion, and oxlint; a fifth row (amber outline) shows `@vitejs/plugin-react`'s PR still open with no replacement; a separate blue-outlined box on the right notes the new `#79` docker base image PR. |
| `2026-11-22-terminal.png` | In "Install", after the command block | The gate itself, run just now against main: real ruff and pytest output, 33 passed in under a second. | Dark terminal-style card showing real `ruff check .` and `pytest tests/ -v` output against current `main`: "All checks passed!" in teal, abbreviated per-file test dot output, and "33 passed, 1 warning in 0.95s" in teal, with a note that the one warning is an unrelated `httpx`/`starlette` deprecation notice. |

Source for all four: `docs/blogs/images/src/2026-11-22-cards.html`, rendered with `scripts/render_blog_graphics_2026-11-22.py` (Playwright + the preinstalled Chromium at `/opt/pw-browsers/chromium`, via `CHROMIUM_PATH`). Namespaced to this post's date so it doesn't collide with the 2026-10-11 or 2026-11-08 posts' own `cards.html`/renderer pairs, per the convention those posts established. Each image was reviewed with an image read before committing; two layout issues were caught and fixed that way: the "10 dependabot PRs" hero chip clipped its own text (widened the chip), the "docker (/api, /dashboard)" source box in the flow diagram overflowed its border (wrapped to two lines), and the `@vitejs/plugin-react` row in the timeline ran into its own "still open" caption (widened the box, nudged the caption right).

## Where to post

| Channel | Notes |
|---|---|
| LinkedIn | Lead with the concrete hook (ten PRs, four superseded same-day) rather than the "nothing shipped" framing -- that reads as an editorial aside once someone's already reading, not the reason to click. |
| X / Bluesky | Use the thread in the companion `-social.md` file; open on the supersession detail, it is the most specific, least-generic claim in the post. |
| Hacker News (Show HN) | Title as "Show HN: What my Dependabot setup actually does when nothing else changes". This is the fifth post about this repo in about six weeks -- check [HN's Show HN guidelines](https://news.ycombinator.com/showhn.html) and weigh whether a DevOps/CI-process angle clears the bar better than another "look at my project" post would. |
| r/devops, r/cybersecurity | Check each subreddit's self-promotion rules before posting. r/devops in particular is a better fit for this post's actual subject (dependency automation, CI gating) than the usual SOC-pipeline angle; lead with that, not the repo pitch. |
| r/netsec | Lower priority this time -- this post is about CI/dependency process, not a security technique, so it's a weaker fit than prior posts from this repo. Skip unless reframed around the supply-chain-hygiene angle specifically. |
| Claude / Anthropic developer community | Not applicable this week -- no Claude-skill content in this post. |

## Reader comment reply templates

**"Isn't this just... Dependabot doing its job? Why does this need a blog post?"**
> Fair, and that's really the point -- the interesting part isn't that Dependabot opened PRs, it's that I could point at the exact CI gate (ruff, 33 tests across three Python versions, a dashboard build, and a real docker-compose boot-and-curl) that every one of those PRs has to clear before merging, the same as a human's PR would. A lot of projects have a dependabot.yml that nobody's checked actually blocks a bad merge. This was me checking mine.

**"What happens when you actually hit the open-pull-requests-limit: 10 cap?"**
> Honestly, I don't know yet -- it hasn't happened on this repo. Per-ecosystem it's currently sitting well under 10 after this week's batch. I flagged it in Known limitations because it's a real ceiling, not because I've seen it bite. If you've hit it on your own repo, I'd like to hear what Dependabot actually does at that point.

**"A week with zero commits doesn't sound like a very active project."**
> It's an accurate read of this specific week, and I'd rather say that plainly than pad out a fake feature update. The repo's had three real shipped changes in the five weeks before this one (fail-closed enrichment, a calibration harness, the Claude Code skill) -- this week's post is about the part of the project that keeps running even during a quiet week, which is also worth knowing works.

## Publishing

No Medium API token is configured in this repository, so this is a draft file only. Paste it into Medium's editor, or import it from a gist. `scripts/publish_medium_draft.py` exists on PR #36 (still open, draft-only even once merged -- hard-codes `publishStatus: "draft"`), but that PR has not merged, so this post does not depend on it.
