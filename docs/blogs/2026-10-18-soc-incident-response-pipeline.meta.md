# Metadata for the 2026-10-18 post

## Inputs used

| Field | Value |
|---|---|
| Repo / branch | `Mangesh-Bhattacharya/soc-incident-response-pipeline` / `main`, plus open draft PR [#46](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline/pull/46) (`claude/intelligent-hopper-qipw9c`) |
| Audience | Security engineers, SOC automation builders, people curious how to run a repeatable "write about my own project" pipeline |
| Tone | Technical, direct, self-aware about the irony of the subject |
| Length | About 1,270 words |
| Focus | This week's one substantive change: a draft PR that formalizes a seven-agent workflow for writing these weekly posts |
| Real numbers used | `git log --since="7 days ago"` on `main` (3 commits, none new code); `pytest tests/ -v` → 33 passed, unchanged; PR #46 stats via GitHub API → 182 additions, 5 files, 1 commit, opened 2026-10-17; PR #46 CI run (id 38990596838) jobs via GitHub Actions API → lint, dashboard, test(3.10/3.11/3.12) passed, docker failed, notify-on-scheduled-failure skipped (6 of 7 green); owner's own PR comment confirming the `docker` failure reproduces identically on `main` at `d4df8bf`; full content of `blog-agent/WORKFLOW.md`, `VOICE.md`, `queue.yml`, `.github/workflows/blog-cycle.yml` as committed on the PR branch |

## Title variants

1. This Week in soc-incident-response-pipeline: Turning the Weekly Blog Into a Seven-Agent Workflow (primary)
2. I Built the Pipeline That's Supposed to Write These Posts — It's Still a Draft PR
3. Scout, Researcher, Writer, Editor: Formalizing How This Project Gets Blogged About

**Tags:** cybersecurity, automation, claude, soc, devtools

**Excerpt:** This week's SOC pipeline update isn't about the scorer — it's a draft PR that turns the ad-hoc process behind this very blog series into a defined seven-role, fourteen-day cycle with owner-approval gates on anything that publishes or replies.

## Images (rendered, committed under `docs/blogs/images/`)

| File | Placement | Caption | Alt text |
|---|---|---|---|
| `2026-10-18-hero.png` | Below the title, before TL;DR | Seven roles, one fourteen-day cycle: a draft PR formalizes how this blog gets written. | Dark hero graphic with the headline "Seven roles, one cycle. The blog gets automated too.", three status chips (Open PR #46, 182 lines/5 files, 2 of 7 roles need owner OK), and seven small role nodes arranged in a ring. |
| `2026-10-18-workflow-cycle.png` | In "How it works", above the PR table | The 14-day cycle: seven roles from Scout to Analyst, with two owner-approval gates. | Horizontal timeline with five stage boxes (Day 0 Scout+Researcher, Day 1 Writer+Editor, Day 2 Publisher, Day 4-5 Community, Day 14 Analyst) color-coded teal/blue/red, plus a list of the seven publish gates below. |
| `2026-10-18-ci-results.png` | In "How it works", after the PR table | Six of seven CI jobs green on PR #46's own commit; the one red job already fails on main. | Grid of seven CI job chips (lint, dashboard build, test matrix, notify-skipped, docker-failed) plus three stat tiles: 6 of 7 green, 33 pytest passed, and "pre-existing" labeling the red job. |
| `2026-10-18-queue.png` | In "How it works", last image | Four projects queued for future posts, zero cycles completed so far. | Four stacked rows listing queued repo names and their angle ideas from queue.yml, with a note that none has moved past status: queued. |

Source for all four: `docs/blogs/images/src/2026-10-18-cards.html`, rendered with `scripts/render_blog_graphics_2026-10-18.py` (Playwright + the preinstalled Chromium at `/opt/pw-browsers/chromium`, set via `CHROMIUM_PATH`). Each was screenshotted at its own SVG element id and re-viewed with an image read before committing; the first hero render had "Researcher" and "Writer" labels clipped at the card's right edge, fixed by pulling the role-ring cluster left and re-rendering.

## Where to post

| Channel | Notes |
|---|---|
| LinkedIn | Full post text works as-is; lead with the TL;DR's "five of the last six posts were written ad-hoc" line, it's the most concrete hook. Post the hero image as the preview card. |
| X / Bluesky | Use the thread in the companion `-social.md` file; first post is the hook, not the full TL;DR. |
| Hacker News (Show HN) | This one is borderline: it's a workflow/process post about the project's own blogging, not a new technical capability in the pipeline itself. Check [HN's Show HN guidelines](https://news.ycombinator.com/showhn.html) before posting; consider skipping Show HN this week and saving it for when the blog-agent cycle actually produces its first automated post, which is a stronger HN story than the draft PR alone. |
| r/cybersecurity, r/blueteamsec, r/netsec | Check each subreddit's self-promotion rules (minimum account age/karma, frequency caps) before posting. This post is meta (about the blogging process, not detection logic), so it's a weaker fit for r/netsec specifically — consider leading with the core project's fail-closed/calibration work instead if cross-posting there, and saving this post for LinkedIn/personal channels. |
| Claude / Anthropic developer community (Discord, forums) | Strong fit: this post is literally about a Claude-authored agent workflow with explicit owner-approval gates. Link PR #46 directly, and be upfront that it's unmerged and unproven. |
| n8n community forum | Not a good fit this week; this post has nothing to do with the n8n workflow. Skip. |

## Reader comment reply templates

**"Has this actually written a post yet, or is this post itself proof it works?"**
> Fair catch, and the post says it directly: no, this one was still written the old ad-hoc way, one agent reading recent commits in a single pass. PR #46 is unmerged and nothing has gone through the Scout-to-Analyst cycle for real yet. If it merges, the next cycle's post is the one that should look different — happy to link back here when that happens.

**"Why does Publisher still need a human if you trust the Scout/Researcher/Analyst steps unattended?"**
> Because the failure modes aren't symmetric. If Scout picks the wrong project or Researcher's brief has a small error, the cost is a wasted draft. If Publisher posts something factually wrong or off-voice in my name, or Community sends a bad reply to someone, that's out in public and hard to take back. WORKFLOW.md marks exactly those two steps "owner approval required," twice, on purpose.

**"What's the actual docker CI failure about, is it something I should worry about if I clone this?"**
> It's a `dashboard` Docker image build breaking on `npm install` — a Rolldown native-binding issue, not something this PR introduced. It reproduces identically on `main` right now, so if you `docker compose up --build` today you may hit it too. It's logged as a known gap in the PR's comments; no fix is in yet.

## Publishing

No Medium integration token is configured in this repository, so this is a draft file only — Medium stopped issuing new integration tokens to new applications, which `blog-agent/WORKFLOW.md` itself documents as a hard constraint. Paste this post into Medium's editor or import it from a gist/GitHub URL. The repo's draft-only publishing script (from PR #36) is still unmerged as of this post, so it was not used here.
