# GitHub Projects → Medium + LinkedIn Blogger Workflow

Cadence: **every 2 weeks, 2 posts** (one Medium article, one LinkedIn post derived from a different angle of the same or a second project). Optional Discord share.

Hard constraints (platform reality, not preference):

| Channel | Publish path | Comment monitoring |
|---|---|---|
| Medium | **Manual paste or "Import a story" from a URL.** Medium no longer issues API tokens. | Manual |
| LinkedIn | Zapier `LinkedInCLIAPI` (write-only) or manual | Manual. No read API |
| Discord | Zapier `DiscordCLIAPI` or webhook | Manual / bot |

Replies are **drafted by agents, approved and posted by the owner.** No unattended replies.

## Agents

| # | Agent | Input | Output | Gate |
|---|---|---|---|---|
| 1 | **Scout** | Public repos (`gh`/MCP), `queue.yml` | Ranked candidates; picks next project | Owner approves pick |
| 2 | **Researcher** | Repo README, commits, issues, CI, code | `briefs/<slug>.md` (facts only, see `brief-template.md`) | Every claim must cite a file/commit |
| 3 | **Writer** | Brief + `VOICE.md` | Medium draft + LinkedIn draft + Discord blurb | None |
| 4 | **Editor** | Drafts + brief + `VOICE.md` | Fact-check report, humanization pass, redacted drafts | Blocks on any failed check below |
| 5 | **Publisher** | Approved drafts | Publish steps per channel, UTM-tagged links | **Owner approval required** |
| 6 | **Community** | Comments pasted/forwarded by owner | Reply drafts + lead flags | **Owner approves every reply** |
| 7 | **Analyst** | Views/reactions/inbound DMs (owner supplies) | Update `queue.yml` scores, next-cycle notes | None |

## Cycle (14 days)

```
Day 0  Scout → pick project → Researcher → brief
Day 1  Writer → drafts → Editor → owner review
Day 2  Publish Medium (article). Owner approves.
Day 4  Publish LinkedIn (hook + link back to Medium + repo)
Day 5  Discord share (optional, community channels only)
Day 2–14  Community agent drafts replies within 24h of each comment batch
Day 14 Analyst closes cycle → next cycle issue opens (see .github/workflows/blog-cycle.yml)
```

## Gates (Editor must pass all before Publisher runs)

1. **Fact check:** every number, version, and capability traces to the brief; the brief traces to the repo.
2. **Secrets/PII scan:** no tokens, internal hostnames, employer/client names, private-repo names, real IPs. Screenshots reviewed manually.
3. **Public repos only.** Private repos are never named or described without explicit owner OK.
4. **No invented experience.** No fake clients, results, or metrics. Say "demo mode" when it's demo mode.
5. **Voice pass:** passes the checklist in `VOICE.md` (no filler openers, specific details, one opinion, honest limits).
6. **CTA present:** one clear "work with me" line + contact path (see below).
7. **Links:** repo link, plus `?utm_source=<channel>&utm_campaign=<slug>` on the portfolio/contact link.

## Client-conversion requirements (why previous posts brought no leads)

Each post must contain:

- **Problem-first framing** a buyer recognises ("analysts burn the first ten minutes of every alert on copy-paste lookups"), not tool-first.
- **One concrete outcome** (time saved, steps removed) that is true and sourced from the brief.
- **A decision you made and why** (e.g., deterministic scoring over an LLM) to signal judgment.
- **Who it's for + how to hire you** in the last 3 lines: scope (SOC automation, detection engineering, AI/LLM security), contact link, response time.
- **Repo hygiene before posting:** README top section, screenshot, one-command run, license, topics set.

## Community / comment policy

- Respond to every substantive comment within 24h (owner posts). Reply style in `VOICE.md`.
- Answer technical questions with specifics; link the code line or doc.
- **Lead flag:** comment/DM mentioning a team, budget, timeline, or "can you help with" → Community agent marks `LEAD` and drafts a short reply moving it to email/call. Owner handles from there.
- Criticism: acknowledge what's right, correct what's factually wrong, no defensiveness. Never argue publicly.
- Never claim to be the author typing live if asked directly; owner decides how to answer disclosure questions truthfully.
- Spam/abuse: ignore/report; no replies.

## Files

- `VOICE.md` voice rules and humanization checklist
- `brief-template.md` Researcher output format
- `queue.yml` project backlog + performance log
- `briefs/` generated briefs
- `.github/workflows/blog-cycle.yml` opens the biweekly cycle issue (durable trigger; replaces session-only cron)
