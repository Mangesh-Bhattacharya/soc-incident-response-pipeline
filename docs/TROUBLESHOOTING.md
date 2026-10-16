# Troubleshooting

**Start here, on any OS:**

```bash
python launch.py --doctor        # Windows: py launch.py --doctor
```

It checks Python, Docker, Compose v2, port 8080 and your `.env`, and prints the exact fix for each failure. `python launch.py --fix` creates a missing `.env` safely. `python launch.py` starts everything and opens the dashboard once it is healthy.

If you still need help, open an issue and paste the output of `python launch.py --doctor --json`. It contains no secrets, usernames, paths or hostnames.

## Docker

| Symptom | Cause | Fix |
|---|---|---|
| `docker: command not found` / `'docker' is not recognized` | Docker not installed, or terminal opened before install | Install Docker Desktop (Windows/macOS) or Docker Engine plus the Compose plugin (Linux). Reopen the terminal. |
| `Cannot connect to the Docker daemon` / `error during connect` | Daemon not running | Start Docker Desktop and wait for it to settle. Linux: `sudo systemctl start docker`. |
| `permission denied ... /var/run/docker.sock` (Linux) | User not in the `docker` group | `sudo usermod -aG docker $USER`, then log out and back in. |
| `docker: 'compose' is not a docker command` | Compose v2 plugin missing (v1 `docker-compose` is not supported) | Update Docker Desktop, or install `docker-compose-plugin`. |
| `env file ... .env not found` | `docker-compose.yml` requires `.env` | `python launch.py --fix`, or `cp .env.example .env`. Blank keys mean demo mode. |
| `port is already allocated` / `address already in use` on 8080 | Another program owns the port | Windows: `netstat -ano \| findstr :8080`. macOS/Linux: `lsof -i :8080`. Stop it, or change the left side of `"127.0.0.1:8080:8080"` in `docker-compose.yml`. |
| Build fails with TLS or certificate errors | Corporate proxy intercepting traffic | Configure the proxy in Docker Desktop settings and add your corporate CA. Do not disable certificate verification. |
| Containers restart or show `unhealthy` | API failed to start | `docker compose ps`, then `docker compose logs api`. Include the last 30 lines in an issue. |
| First build is very slow | Pulling base images and `npm ci` | Normal on the first run only. Later runs use the layer cache. |

On **Windows**, use Docker Desktop with the WSL 2 backend and run commands from PowerShell or a WSL shell inside the cloned folder. Keep the clone on the Linux filesystem when using WSL; cloud-synced folders (OneDrive, Dropbox) break `npm install`.

## Dashboard

| Symptom | Fix |
|---|---|
| Browser did not open | Go to `http://localhost:8080`. `python launch.py` only opens it after the health check passes. |
| Page loads but alerts do not run / `502 Bad Gateway` | API container is down: `docker compose logs api`. Test the proxy: `curl http://localhost:8080/api/health` should return `{"status":"ok"}`. |
| Blank page | Hard refresh (Ctrl+Shift+R). If it persists, `docker compose up --build` to rebuild the dashboard image. |
| No Docker available | `python launch.py` falls back to the demo dashboard through Node (`npm install && npm run dev`). It uses five precomputed scenarios and no backend. |

## Python (no Docker)

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: socpipeline` | Run from the repository root with `python cli.py ...`; it adds `src/` to the path for you. |
| `ModuleNotFoundError: requests` / `fastapi` | `pip install -r requirements-dev.txt` |
| Syntax or type errors on startup | Python 3.10 or newer is required. `python --version` |
| Windows: `python -m venv` produces an environment without a working `pip` | Skip the venv: `py -m pip install --user -r requirements-dev.txt`. |
| `pytest` finds no tests | Run it from the repository root: `pytest tests/ -v` |

## Scores and enrichment

| Symptom | Meaning |
|---|---|
| `0/100 (INFO)` plus "Enrichment incomplete" | An API key is missing or a lookup failed. This is deliberate: a failed lookup is not a clean verdict, so it is ticketed at Medium. Add keys to `.env`, or ignore it in demo mode. |
| `VirusTotal returned HTTP 429` | Free-tier rate limit. Wait a minute, or use a paid key. |
| `AbuseIPDB returned HTTP 401/403` | Wrong or missing key. |
| Jira ticket creation fails | Check `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` and that `JIRA_PROJECT_KEY` has an `Incident` issue type. `--dry-run` shows what would be filed. |

## Using it from a phone or another computer

The default setup listens on `127.0.0.1` only, so nothing else on your network can reach it. To opt in:

1. In `docker-compose.yml` change `"127.0.0.1:8080:8080"` to `"8080:8080"`.
2. Allow port 8080 through your OS firewall (commands for each OS are in [`docker.md`](docker.md)).
3. On the phone, on the same Wi-Fi, open `http://<computer-LAN-IP>:8080`.
4. Optional: use the browser's **Add to Home screen** to pin it. The dashboard ships a web app manifest and icons for this. Full offline installation needs HTTPS, which this setup does not provide.

The dashboard has **no authentication**. Use this on a trusted network only, never port-forward it to the internet, and put an authenticating reverse proxy in front before sharing it more widely.
