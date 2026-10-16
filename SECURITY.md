# Security policy

Report vulnerabilities privately through **GitHub Security Advisories** (Security tab → Report a vulnerability) rather than in a public issue. Include the affected file, steps to reproduce, and impact. You will get an acknowledgement within a week.

Do not include real alerts, API keys or customer data. Redact first: `python cli.py --alert alert.json --json --redact`.

In scope: the Python package, the API, the dashboard, the Docker configuration and the CI workflows. Out of scope: findings that need an attacker who already controls your Splunk, n8n or Jira instance, and the limitations already listed under "Known limitations" in the README.
