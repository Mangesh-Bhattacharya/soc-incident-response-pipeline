# Metadata: "How I built it" post

**Fill in before posting:** the `[N weeks]` in the title and body, the real hours, your role target and contact line. The post only states facts that come from the repository (commit dates, line counts, test count). Do not add numbers you cannot show.

**Title variants**
1. I Built a SOC Triage Pipeline in [N weeks]. Here Is Why, How It Works, and Every Command to Run It (primary)
2. The Part of Security Automation Nobody Demos: What Happens When the Pipeline Is Wrong
3. Fail Closed: Four Design Decisions Behind My SOC Incident Response Pipeline

**Tags:** cybersecurity, soc, incident-response, python, automation

**Excerpt:** A walkthrough of a SOC triage pipeline that scores alerts with auditable arithmetic and fails closed when enrichment breaks: why I built it, how it works, how long it took, and every command to run it.

**LinkedIn post (paste with the Medium link)**
> I built a SOC triage pipeline that does one thing differently: when an enrichment lookup fails, it escalates instead of silently dropping the alert. Scoring is auditable arithmetic (no model in the escalation path, because alert fields are attacker-controlled). Runs on Windows, macOS and Linux with one command. Walkthrough, code and the design trade-offs are in the post. I am looking for [role] roles and would like to hear how your team handles fail-closed triage. [link]

**Resume bullets (edit to match what you can defend)**
- Built an open source SOC alert triage pipeline (Python, FastAPI, React/TypeScript, Docker) integrating Splunk, VirusTotal, AbuseIPDB and Jira.
- Designed the scoring layer as deterministic and auditable, and made enrichment failures fail closed so quota exhaustion cannot suppress alerts.
- Added a calibration harness reporting under-triage rates against labelled alerts, and CI across Linux, Windows and macOS with a full Docker stack boot test.

**Publish by hand:** paste into medium.com/new-story. Medium issues no integration tokens, so there is no supported automated path.
