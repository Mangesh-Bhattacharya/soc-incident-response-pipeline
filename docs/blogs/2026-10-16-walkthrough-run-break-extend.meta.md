# Metadata for the 2026-10-16 walkthrough

**Title variants**
1. A SOC Triage Pipeline That Refuses to Fail Quietly: Run It in Five Minutes, Then Help Me Break It (primary)
2. Your Alert Pipeline Is Silently Dropping Evidence. Here Is One That Cannot
3. Fail Closed: Building a SOC Triage Pipeline You Can Audit, Run Anywhere, and Argue With

**Tags:** cybersecurity, soc, incident-response, automation, open-source

**Excerpt:** When an enrichment lookup fails, most pipelines score the alert as clean and drop it. This walkthrough shows a SOC pipeline that fails closed, how to run it on Windows, macOS or Linux with one command, how to fix the usual install problems, and where help is wanted.

**Images:** hero (alert queue and shield gate, same prompt as the previous post), architecture diagram, terminal screenshot of `python launch.py --doctor` with one failing check, dashboard on a phone.

**Publish by hand:** Medium no longer issues integration tokens. Paste the post into the editor, or publish it elsewhere first and use Medium's **Import a story**. `python scripts/publish_medium_draft.py <file> --dry-run` prints the cleaned Markdown.
