# A SOC Triage Pipeline That Refuses to Fail Quietly: Run It in Five Minutes, Then Help Me Break It

<!-- hero.png: generate from the prompt in the .meta.md file, then upload to Medium -->

Most triage automation is judged on what it escalates. I think it should be judged on what it drops.

Imagine your enrichment quota runs out in the middle of a phishing wave. Every alert after that gets scored on no evidence, comes back `0 / INFO`, and vanishes. Nobody beat your detection. The pipeline just ran out of lookups, and nothing told you.

I built [soc-incident-response-pipeline](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline) to behave differently, and this post is a walkthrough: how to run it on any OS in a few minutes, how to fix the things that usually go wrong, and where I want your help.

## What makes it different

Plenty of projects wire Splunk to VirusTotal to Jira. Four decisions here are unusual, and each one is argued in the README rather than asserted.

1. **Severity is arithmetic, not a model.** Alert fields (file paths, process names, command lines) are chosen by the attacker. Feed them to a model that decides whether a human ever sees the event, and you have given the attacker a vote on their own escalation. Six points per malicious engine, capped at sixty, is also an answer that survives an audit.
2. **It fails closed.** A rate limit, timeout or missing key is not a clean verdict. The alert is ticketed with the failed source named.
3. **You can measure it.** `python cli.py --calibrate` scores a labelled corpus and reports a confusion matrix plus the number that matters: alerts that should have reached an analyst and did not.
4. **It lists its own flaws.** The VirusTotal term saturates at ten engines. There is no behavioural axis, so forty failed logins and one score the same. Two of the bundled test cases fail on purpose to prove the harness reports them.

If that sounds like a project you would argue with, good. That is the point.

## Run it

You need Docker, or nothing at all if you only want the dashboard demo.

```bash
git clone https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline.git
cd soc-incident-response-pipeline
python launch.py          # Windows: py launch.py
```

The launcher checks Python, Docker, Compose v2, port 8080 and your `.env`, creates the `.env` if it is missing (blank keys mean demo mode), starts the stack, waits until both containers report healthy, and opens `http://localhost:8080`. If Docker is not available it falls back to the demo dashboard through Node.

No API keys are needed to see it work. The dashboard animates five scenarios from CRITICAL to INFO through the exact scoring code the backend uses.

## When it does not work

Run this first, on any OS:

```bash
python launch.py --doctor
```

It prints the exact fix for each problem. The common ones:

| You see | Cause | Fix |
|---|---|---|
| `Cannot connect to the Docker daemon` | Docker is not running | Start Docker Desktop, or `sudo systemctl start docker` |
| `permission denied ... docker.sock` | Linux user not in the docker group | `sudo usermod -aG docker $USER`, then log out and in |
| `'compose' is not a docker command` | Compose v1 only | Update Docker Desktop, or install `docker-compose-plugin` |
| `env file .env not found` | Missing `.env` | `python launch.py --fix` |
| `port is already allocated` | Something owns 8080 | `lsof -i :8080` (or `netstat -ano \| findstr :8080`), or change the left side of the port mapping |
| `502 Bad Gateway` on the dashboard | API container unhealthy | `docker compose logs api` |
| `0/100 (INFO)` plus "Enrichment incomplete" | No API keys set | Expected in demo mode. Add keys to `.env` |
| `python -m venv` gives you no pip (Windows) | Broken venv | `py -m pip install --user -r requirements-dev.txt` |

The full guide, including Python-only and WSL cases, is in [`docs/TROUBLESHOOTING.md`](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline/blob/main/docs/TROUBLESHOOTING.md). Still stuck? Open an issue and paste `python launch.py --doctor --json`. It contains no secrets, usernames, paths or hostnames. Once I enable it, a bot reads new issues against the docs and replies with a first answer, clearly labelled as AI-generated, and I follow up on anything it cannot solve.

## On your phone

By default the dashboard listens on `127.0.0.1` only, so nothing else on your network can reach it. To open it from a phone on the same Wi-Fi, change `"127.0.0.1:8080:8080"` to `"8080:8080"` in `docker-compose.yml`, allow port 8080 in your OS firewall, and browse to `http://<your-computer-ip>:8080`. Use **Add to Home screen** to pin it. The dashboard ships a web app manifest and icons for that.

Two honest caveats. There is no authentication, so keep it on a trusted network and never expose it to the internet. And full offline installation as an app needs HTTPS, which this setup does not provide.

## What I cannot promise

The launcher's checks are unit-tested against simulated failures (no Docker, daemon down, permission denied, Compose v1, busy port, missing `.env`), and CI runs the test suite on Linux, Windows and macOS. I have not run it on every Docker setup in existence, and I will not claim it works identically everywhere. When it does not, I want the report. That is what the doctor output is for.

## Help me break it

This is the part I care about most. Forking gets you a copy. Collaborating gets everyone a better triage decision. The most valuable things you can send, no coding required:

- **An alert it got wrong.** Scored LOW and should have been CRITICAL, or the reverse. Redact it with `--redact` and use the "Misjudged alert" issue form.
- **Labelled cases** for the calibration corpus. Right now it is eleven synthetic cases that encode my opinion. Yours will not.
- **A `--doctor` report from your OS,** especially if it was wrong.

If you want to build: ratio-based VirusTotal scoring, a behavioural axis carrying event count through from Splunk, enrichment caching with backoff, a ServiceNow or TheHive backend, or rendering the new `enrichment_failed` field in the dashboard. Each is scoped in the README. Read [`CONTRIBUTING.md`](https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline/blob/main/CONTRIBUTING.md), pick one, and open an issue so we do not duplicate effort.

Two lines I will hold: no auto-remediation, and no alert field ever reaches a model that decides escalation.

If you work in a SOC and think I have got the fail-closed trade wrong, tell me in the comments or the issues. A good argument is worth more than a star.

**Repo:** https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline
