# Social copy for the 2026-10-18 post

## LinkedIn

Five of the last six posts in this series got written the same ad-hoc way: open a terminal, read the week's commits, draft something, hope the voice still matches last week. This week I opened a draft PR that replaces that with an actual process.

[soc-incident-response-pipeline](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline) is a deterministic SOC triage tool — Splunk detects, VirusTotal and AbuseIPDB enrich, a transparent rubric scores, Jira gets ticketed. Severity is arithmetic, never a model's opinion. This week's change, open in PR #46, applies that same philosophy to how the project gets written about:

- A seven-role cycle: Scout, Researcher, Writer, Editor, Publisher, Community, Analyst
- A 14-day schedule with a GitHub Action that opens a tracking issue every other Monday, so the trigger lives in the repo instead of a chat session
- Seven gates an Editor has to clear before anything ships: fact-check, secrets/PII scan, public-repos-only, no invented numbers, a voice pass, a CTA, UTM-tagged links
- Publisher and Community are explicitly marked owner-approval-required — nothing posts or replies without me reading it first

It's still a draft, opened yesterday, 182 lines across 5 files, and nothing has run through it for real. CI caught one unrelated pre-existing bug along the way (a Docker build break on `npm install` that also fails on main) — logged, not papered over.

The honest part: this post was still written the old way. If the PR merges, the next one should look different.

Open to feedback on the PR itself, especially if you've tried to formalize a similar "repeatable, gated, human-approved" publishing loop. And if you're building SOC automation, detection engineering, or AI/security tooling and want a second pair of hands, that's exactly the kind of work I take on — my repo and contact info are linked below.

Repo: https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline
Full writeup: [MEDIUM_URL]

#SOC #SecurityAutomation #BuildInPublic

## X / Bluesky thread

1/ Five of the last six posts in this series were written the same ad-hoc way: read the week's commits, draft something, hope the voice still matches last week's post. This week's change fixes that — for real, not vibes. 🧵

2/ soc-incident-response-pipeline is a deterministic SOC triage pipeline: Splunk → VirusTotal/AbuseIPDB → a transparent rubric → Jira. Severity is arithmetic, not a model's guess. New PR applies the same discipline to the blog about it.

3/ PR #46 (still draft, opened yesterday): a 7-role cycle — Scout, Researcher, Writer, Editor, Publisher, Community, Analyst — on a 14-day schedule, triggered by a GitHub Action instead of "whoever remembers to run it."

4/ 7 gates before anything ships: fact-check, secrets/PII scan, public-repos-only, no invented numbers, a voice checklist, a CTA, UTM links. Publisher and Community need explicit owner approval — nothing auto-posts, nothing auto-replies.

5/ Honest bit: this very post was still written the old ad-hoc way. The PR is unmerged and nothing has run through the new cycle yet. CI also caught a real pre-existing Docker bug along the way — logged, not hidden.

6/ Repo's open for review, issues and comments welcome. If you build SOC/detection automation or AI security tooling and want to talk shop (or hire), I'm linked below.

https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline

#SOC #InfoSec #BuildInPublic
